import os
import fnmatch
import time, datetime
import glob

from acontrol.observation import Observation
from acontrol.mailnotify import MailNotify
from acontrol.connection import Connection

from twisted.internet import reactor
from twisted.internet import inotify
from twisted.internet import protocol
from twisted.internet.task import LoopingCall
from twisted.python import filepath
from twisted.python import usage
from twisted.python import log
from twisted.application.service import Service, MultiService

FIVE_MINUTES = 300
SECONDS_IN_DAY = 86400
US_IN_SECOND = 1e6
PORT = 45000
HOSTS = [
  ("gpu02", "10.144.6.14", PORT, "0 STARTPIPE -p0 -n288 -t3072 -c64 -d0 -g0,1 -b16 -s8 -R1 -r604800 -i 10.195.100.1:53268,10.195.100.1:53276,10.195.100.1:53284,10.195.100.1:53292,10.195.100.1:53300,10.195.100.1:53308 -o tcp:10.144.6.12:5000,null:,null:,null:,null:,null:,null:,null:  2>&1 | tee acontrol.log"), 
  ("ads001","10.144.6.12", PORT, "0 START --antpos=/usr/local/share/aartfaac/antennasets/lba_outer.dat --output=/var/www/rtmon.png --freq=53906250.0")
]


def call_at_time(start_datetime, end_datetime, f, *args, **kwargs):
    """
    Run f(*args, **kwargs) at datetime.
    """
    delta = start_datetime - datetime.datetime.now()
    seconds_ahead = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND
    delta = end_datetime - datetime.datetime.now()
    seconds_before_end = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND
    if seconds_ahead > 0:
        print "Will call in %d seconds" % (seconds_ahead,)
        return reactor.callLater(seconds_ahead, f, *args, **kwargs)
    elif seconds_before_end > FIVE_MINUTES:
        print "Obs in progress, starting now!"
        return reactor.callWhenRunning(f, *args, **kwargs)
    else:
        print "Not scheduling; target is in the past"
    return None


class Options(usage.Options):
    optParameters = [
        ["dir", "d", "/opt/lofar/var/run", "Directory to monitor for parsets"],
        ["pattern", "p", "MCU001*", "Glob pattern to select usable parsets"],
        ["maillist", "m", "maillist.txt", "Textfile with email addresses, one per line"]
    ]

    optFlags = [
        ["dryrun", "r", "Show commands, don't run them, don't connect to other systems"]
    ]


class NotifyService(Service):
    """
    Watch for events on @path@ according to @mask@ and run @callbacks@ as
    appropriate.
    """
    def __init__(self, path, mask, callbacks):
        self.notifier = inotify.INotify()
        self.notifier.watch(path, mask=mask, callbacks=callbacks)

    def startService(self):
        self.notifier.startReading()

    def stopService(self):
        self.notifier.stopReading()


class WorkerService(Service):
    PRE_TIME   = 20  # Start pipeline N seconds before observation starts
    PRUNE_TIME = 10  # Prune observations that are finished every N seconds

    def __init__(self, config, email):
        self.availabile = False
        self._parsets = {}
        self._prune_call = LoopingCall(self.prune)
        self._fnpattern = config['pattern']
        self._dryrun = config['dryrun']
        self.email = email

    def startService(self):
        self.available = True
        self._prune_call.start(self.PRUNE_TIME)

    def stopService(self):
        # Shut down any processing in progress...
        self.available = False
        self._prune_call.stop()

    def processObservation(self, obs):
        """
        Start a pipeline to process the observation
        """
        if self.available and obs.is_valid():
            success = True
            msg = ""
            for host in HOSTS:
                c = Connection()

                # Try to connect
                if c.connect(host[1], host[2]) != Connection.OK:
                    msg += "Unable to connect to `%s:%i'" % (host[1], host[2])
                    success = False
                    c.close()
                    break

                # First we stop a previous pipeline run, if existing...
                response = c.send("0 STOP")
                if response != Connection.OK:
                    msg += "Host %s got `%s' when trying to stop\n" % (host[0], response)
                    success = False
                    c.close()
                    break

                # Now we (re) start this process
                response = c.send(host[3])
                if response != Connection.OK:
                    msg += "Host %s got `%s' when trying to start\n" % (host[0], response)
                    msg += "  " + host[3]
                    success = False
                    c.close()
                    break

                msg += "Host `%s' successfully started\n" % (host[0])
                msg += "  " + host[3]
                c.close()


            # Next we start the new pipeline run given the observation
            if success:
                msg += "All processes started successfully\n"
                print "Starting", obs
            else:
                print "Failure when initiating", obs

            # Finally we send an email notifying people about the run
            self.email.send("Observation %s" % (obs), msg, self._dryrun)
        else:
            print "Skipping", obs

    def enqueueObservation(self, ignored, filepath, mask):
        """
        Parse files matching the glob pattern and create future call
        """
        call = None
        if fnmatch.fnmatch(filepath.basename(), self._fnpattern):
            obs = Observation(filepath.path)
            call = call_at_time(
                obs.start_time - datetime.timedelta(seconds=self.PRE_TIME),
                obs.end_time,
                self.processObservation,
                obs
            )

        if call and filepath.path in self._parsets and self._parsets[filepath.path].active():
            print "Rescheduling ", filepath.path
            self._parsets[filepath.path].cancel()
            self._parsets[filepath.path] = call
        elif call and filepath.path not in self._parsets:
            print "Scheduling ", filepath.path
            self._parsets[filepath.path] = call
        else:
            print "Ignoring ", filepath.path

    def prune(self):
        """
        Prune parsets/observations that have passed or are inactive
        """
        pruneable = []
        for k, v in self._parsets.iteritems():
            if not v or not v.active():
                pruneable.append(k)
        for k in pruneable:
            del self._parsets[k]
        print "Tracking %d observations, pruned %d" % (len(self._parsets), len(pruneable))


def makeService(config):
    acontrol_service = MultiService()
    email = MailNotify(config['maillist'])
    log.addObserver(email.error)
    worker_service = WorkerService(config, email)
    worker_service.setName("Worker")
    worker_service.setServiceParent(acontrol_service)

    # Slurp up any existing parsets
    for file in glob.glob(os.path.join(config['dir'], config['pattern'])):
        reactor.callWhenRunning(
        worker_service.enqueueObservation,
            None, filepath.FilePath(file), None
        )

    # We notify on a file that has been closed in writemode as files are copied
    # over scp, it can take some time for the full file to arrive
    notifier_service = NotifyService(
        filepath.FilePath(config['dir']),
        mask=inotify.IN_CLOSE_WRITE,
        callbacks=[worker_service.enqueueObservation]
    )
    notifier_service.setName("Notifier")
    notifier_service.setServiceParent(acontrol_service)

    return acontrol_service
