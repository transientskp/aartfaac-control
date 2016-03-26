import os
import fnmatch
import time, datetime
import glob

from acontrol.observation import Observation
from acontrol.configuration import Configuration
from acontrol.mailnotify import MailNotify
from acontrol.connection import Connection
from acontrol.test.example_config import EXAMPLE_CONFIG

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

def call_at(start_datetime, f, *args, **kwargs):
    """
    Run f(*args, **kwargs) at datetime.
    """
    delta = start_datetime - datetime.datetime.now()
    seconds_ahead = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND
    if seconds_ahead > 0:
        print "AARTFAAC config update in %d seconds" % (seconds_ahead,)
        return reactor.callLater(seconds_ahead, f, *args, **kwargs)
    else:
        print "Not scheduling; config is in the past"
    return None


def call_at_to(start_datetime, end_datetime, f, *args, **kwargs):
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
        ["lofar-dir", None, "/opt/lofar/var/run", "Directory to monitor for lofar parsets"],
        ["lofar-pattern", None, "MCU001*", "Glob lofar pattern to select usable parsets"],
        ["config-dir", None, "/opt/aartfaac/var/run", "Directory to monitor for lofar parsets"],
        ["config-pattern", None, "AARTFAAC*", "Glob aartfaac pattern to select usable parsets"],
        ["maillist", "m", "maillist.txt", "Textfile with email addresses, one per line"]
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
        self._available = False
        self._parsets = {}
        self._configs = {}
        self._prune_call = LoopingCall(self.prune)
        self._fnpattern = config['lofar-pattern']
        self._aapattern = config['config-pattern']
        self._email = email
        self._cfg_file = open(config['config-dir'] + '/AARTFAAC:000000.json', 'w')
        self._cfg_file.write(EXAMPLE_CONFIG)
        self._cfg_file.seek(0)
        self._activeconfig = Configuration(self._cfg_file.name)


    def startService(self):
        self._available = True
        self._prune_call.start(self.PRUNE_TIME)


    def stopService(self):
        # Shut down any processing in progress...
        self._available = False
        self._prune_call.stop()
        self._cfg_file.close()


    def processObservation(self, obs):
        """
        Start a pipeline to process the observation
        """
        if self._available and obs.is_valid():
            msg = ""
            success = True

            if not self._activeconfig:
                msg += "No aartfaac configuration loaded\n"
                success = False
            elif not self._activeconfig.is_valid():
                msg += "Invalid aartfaac configuration\n"
                success = False

            hosts = []
            if success:
                msg += "Using aartfaac configuration `%s'\n" % (self._activeconfig.filepath)
                # TODO: Implement setstations()
                # self._activeconfig.setstations(obs)
                hosts.append(self._activeconfig.atv(obs))
                hosts.append(self._activeconfig.server(obs))
                hosts += self._activeconfig.pipelines(obs)
                hosts.append(self._activeconfig.correlator(obs))

            # STOP all running processes
            for host in hosts:
                c = Connection()

                # Try to connect
                if c.connect(host[1], host[2]) != Connection.OK:
                    msg += "Unable to connect to `%s:%i'" % (host[1], host[2])
                    success = False
                    c.close()
                    break

                # First we stop a previous pipeline run, if existing...
                response = c.send("0 STOP\n")
                if response != Connection.OK:
                    msg += "Got `%s' when trying to terminate `%s'\n" % (response, host[0])

                msg += "Connected to %s:%d\n" % (host[1], host[2])
                msg += "Terminated `%s' successfully with arguments:\n" % (host[0])
                msg += "  " + host[3] + "\n"
                c.close()

            time.sleep(2)

            # START all processes
            for host in hosts:
                c = Connection()

                # Try to connect
                if c.connect(host[1], host[2]) != Connection.OK:
                    msg += "Unable to connect to `%s:%i'" % (host[1], host[2])
                    success = False
                    c.close()
                    break

                # Now we (re) start this process
                response = c.send("0 START " + host[3] + "\n")
                if response != Connection.OK:
                    msg += "Got `%s' when trying to execute `%s' with arguments:\n" % (response, host[0])
                    msg += "  " + host[3] + "\n"
                    success = False
                    c.close()
                    break

                msg += "Connected to %s:%d\n" % (host[1], host[2])
                msg += "Executed `%s' successfully with arguments:\n" % (host[0])
                msg += "  " + host[3] + "\n"
                c.close()

            # Next we start the new pipeline run given the observation
            subject = "[-] %s" % (obs)
            if success:
                msg += "All processes started successfully\n"
                subject = "[+] %s" % (obs)
                print "Starting", obs
            else:
                print "Failure when initiating", obs

            print "Log:\n\n\n",msg,"\n\n"

            # Finally we send an email notifying people about the run
            filenames = [obs.filepath]
            if self._activeconfig:
                filenames.append(self._activeconfig.filepath)
            self._email.send(subject, msg, filenames)
        else:
            print "Skipping", obs


    def enqueueObservation(self, ignored, filepath, mask):
        """
        Parse files matching the glob pattern and create future call
        """
        call = None
        if fnmatch.fnmatch(filepath.basename(), self._fnpattern):
            obs = Observation(filepath.path)
            call = call_at_to(
                obs.start_time - datetime.timedelta(seconds=self.PRE_TIME),
                obs.end_time,
                self.processObservation,
                obs
            )

        if call and filepath.path in self._parsets and self._parsets[filepath.path].active():
            print "Rescheduling observation", filepath.path
            self._parsets[filepath.path].cancel()
            self._parsets[filepath.path] = call
        elif call and filepath.path not in self._parsets:
            print "Scheduling observation", filepath.path
            self._parsets[filepath.path] = call
        else:
            print "Ignoring ", filepath.path


    def applyConfiguration(self, config):
        """
        Prepare AARTFAAC telescope for upcomming observations
        """
        self._activeconfig = config
        print "Set AARTFAAC configuration to", config


    def enqueueConfiguration(self, ignored, filepath, mask):
        """
        Parse files matching the glob pattern and create future call
        """
        call = None
        if fnmatch.fnmatch(filepath.basename(), self._aapattern):
            cfg = Configuration(filepath.path)
            call = call_at(
                cfg.start_time - datetime.timedelta(seconds=self.PRE_TIME),
                self.applyConfiguration,
                cfg
            )

        if call and filepath.path in self._configs and self._configs[filepath.path].active():
            print "Rescheduling config update", filepath.path
            self._configs[filepath.path].cancel()
            self._configs[filepath.path] = call
        elif call and filepath.path not in self._configs:
            print "Scheduling config update", filepath.path
            self._configs[filepath.path] = call
        else:
            print "Ignoring config update", filepath.path


    def prune(self):
        """
        Prune parsets/configs that have passed or are inactive
        """
        pruneable = []
        for k, v in self._parsets.iteritems():
            if not v or not v.active():
                pruneable.append(k)
        for k in pruneable:
            del self._parsets[k]
        print "Tracking %d observations, pruned %d" % (len(self._parsets), len(pruneable))

        pruneable = []
        for k, v in self._configs.iteritems():
            if not v or not v.active():
                pruneable.append(k)
        for k in pruneable:
            del self._configs[k]
        print "Tracking %d configurations, pruned %d" % (len(self._configs), len(pruneable))


def makeService(config):
    acontrol_service = MultiService()
    email = MailNotify(config['maillist'])
    log.addObserver(email.error)
    worker_service = WorkerService(config, email)
    worker_service.setName("Worker")
    worker_service.setServiceParent(acontrol_service)

    # Slurp up any existing configs
    for file in glob.glob(os.path.join(config['config-dir'], config['config-pattern'])):
        reactor.callWhenRunning(
        worker_service.enqueueConfiguration,
            None, filepath.FilePath(file), None
        )

    # We notify on a file that has been closed in writemode as files are copied
    # over scp, it can take some time for the full file to arrive
    aartfaac_config_service = NotifyService(
        filepath.FilePath(config['config-dir']),
        mask=inotify.IN_CLOSE_WRITE,
        callbacks=[worker_service.enqueueConfiguration]
    )
    aartfaac_config_service.setName("AARTFAAC Config Notifier")
    aartfaac_config_service.setServiceParent(acontrol_service)

    # Slurp up any existing parsets
    for file in glob.glob(os.path.join(config['lofar-dir'], config['lofar-pattern'])):
        reactor.callWhenRunning(
        worker_service.enqueueObservation,
            None, filepath.FilePath(file), None
        )

    # We notify on a file that has been closed in writemode as files are copied
    # over scp, it can take some time for the full file to arrive
    lofar_parset_service = NotifyService(
        filepath.FilePath(config['lofar-dir']),
        mask=inotify.IN_CLOSE_WRITE,
        callbacks=[worker_service.enqueueObservation]
    )
    lofar_parset_service.setName("LOFAR Notifier")
    lofar_parset_service.setServiceParent(acontrol_service)

    return acontrol_service
