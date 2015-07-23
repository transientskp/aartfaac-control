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
try:
	import subprocess;
except ImportError:
	print 'Module subprocess not found. Quitting.'

FIVE_MINUTES = 300
SECONDS_IN_DAY = 86400
US_IN_SECOND = 1e6
PORT = 45000
HOSTS = [
  ["ads001", "10.144.6.12", 45001, "0 START", "--freq=54000000", "--output=/data/atv", "--snapshot=/var/www/", "--calip=10.144.6.13", "--calport=4200", "--array=lba_outer"],
  ["ads001", "10.144.6.12", PORT, "0 START", "--buffer-max-size 34359738368", "--stream 63 57617187.5 3051.757812 0-62"],
  ["ais001", "10.144.6.13", PORT, "0 START", "--server-host 10.144.6.12", "--monitor-port 4200", "--casa /data/pprasad"],
  ["gpu02",  "10.144.6.14", PORT, "0 STARTPIPE", "-p0", "-n288", "-t3072", "-c64", "-d0", "-g0,1", "-b16", "-s8", "-R1", "-r604800", "-i 10.195.100.1:53268,10.195.100.1:53276,10.195.100.1:53284,10.195.100.1:53292,10.195.100.1:53300,10.195.100.1:53308", "-o tcp:10.144.6.12:5000,tcp:10.144.6.12:4100,null:,null:,null:,null:,null:,null:", "2>&1 | tee acontrol.log"]
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
            print '<-- System available for valid observation.';
            success = True
            msg = ""

            # Set the subbands on all AARTFAAC stations. Ultimately the subbands
            # to set will come from the AARTFAAC parset, but currently we 
            # hardcode them to test out the new runaartfaacrspctl.py script.
            # subbands = '100,150,200,250,300,350,400,450';
            subbands = '295,296,297,298,299,300,301,302';
            stations = ['cs002c', 'cs003c', 'cs004c', 'cs005c', 'cs006c', 'cs007c'];
            runcmd = ['ssh', '-A', '-o', 'NoHostAuthenticationForLocalhost=yes', 'cs002c', 'python' '/opt/lofar/bin/runaartfaacrspctl.py', '--subbands=%s'%subbands];

            p1 = [];
            for ind,station in enumerate(stations):
                # try:
                runcmd[4] = station;
                print 'Ind: %d, runcmd: %s' % (ind, runcmd);
                p1.append(subprocess.Popen (runcmd, stdout=subprocess.PIPE));
                time.sleep(2);
                if (p1[ind].returncode != None):
                    print '### Unable to set subbands on station ', station; 
                else:
                    cmdoutput, err = p1[ind].communicate();
                    print '<-- subband set for %s, output: %s' % (station, cmdoutput);
                
            # Add subband information to command strings
            # Subband 0 goes to atv. Later this can be a separate key in the AARTFAAC parset.
            atv_subband = subbands.split(',')[0];
            atv_freq = obs.subband2freq (int(atv_subband));
            print '<-- Setting atv frequency to 0th subband (%s, %f)' % (atv_subband, atv_freq);
            HOSTS[0][4] = '--freq=%f'%atv_freq;

            serv_subband = subbands.split(',')[1];
            serv_freq = obs.subband2freq(int(serv_subband));
            HOSTS[1][5] = '--stream 63 %f %f 0-62' % (serv_freq, obs.chan_width); 
                
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
                print '<-- Sending command %s to host.' % ' '.join(host[3:]);
                response = c.send(' '.join(host[3:]))
                if response != Connection.OK:
                    msg += "Host %s got `%s' when trying to start\n" % (host[0], response)
                    msg += "  " + host[3] + "\n"
                    success = False
                    c.close()
                    break

                msg += "Host `%s' successfully started\n" % (host[0])
                msg += "  " + ' '.join(host[3:]) + "\n"
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
            print "Skipping", obs, 'available: %s,valid obs: %s'% (self.available, obs.is_valid());

    def enqueueObservation(self, ignored, filepath, mask):
        """
        Parse files matching the glob pattern and create future call
        """
        call = None
        if fnmatch.fnmatch(filepath.basename(), self._fnpattern):
            obs = Observation(filepath.path)

            # Add array configuration information to atv call
            # oldarrayconf = HOSTS[0][3][HOSTS[0][3].find ('--array'):].split('=')[1];
            # HOSTS[0][3]  = HOSTS[0][3].replace (oldarrayconf, obs.antenna_set);
            HOSTS[0][9] = '--array=%s'%obs.antenna_set;
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
