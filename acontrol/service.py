import os
import fnmatch
import datetime
import glob

from acontrol.observation import Observation
from acontrol.imagingServer import ImagingServer
from acontrol.imagingPipeline import ImagingPipeline

from twisted.internet import reactor
from twisted.internet import inotify
from twisted.internet.task import LoopingCall
from twisted.python import filepath
from twisted.python import usage
from twisted.application.service import Service, MultiService

SECONDS_IN_DAY = 86400
US_IN_SECOND = 1e6

def call_at_time(target_datetime, f, *args, **kwargs):
    """
    Run f(*args, **kwargs) at datetime.
    """
    delta = target_datetime - datetime.datetime.now()
    seconds_ahead = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND
    if seconds_ahead > 0:
        print "Will call in %d seconds" % (seconds_ahead,)
        return reactor.callLater(seconds_ahead, f, *args, **kwargs)
    else:
        print "Not scheduling; target is in the past"
    return None


class Options(usage.Options):
    optParameters = [
        ["dir", "d", "/opt/lofar/var/run", "Directory to monitor for parsets"],
        ["pattern", "p", "Observation??????", "Glob pattern to select usable parsets"]
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
    LEAD_TIME  = 10 # In seconds
    PRUNE_TIME = 10

    def __init__(self, fnpattern):
        self.availabile = False
        self._parsets = {}
        self._prune_call = LoopingCall(self.prune)
        self._fnpattern = fnpattern
        self.img_server = ImagingServer('ads001')
        self.img_pipelines = ImagingPipeline('ais001')

    def startService(self):
        self.available = True
        self._prune_call.start(self.PRUNE_TIME)

    def stopService(self):
        # Shut down any processing in progress...
        self.available = False
        self._prune_call.stop()

    def processObservation(self, obs):
        # Entry point, spawn all commands
        if self.available and obs.is_valid():
            print "starting to process", obs
            self.img_server.start_server(obs)
            self.img_pipelines.start_pipelines(5, self.img_server.host, self.img_server.port_out, obs)
        else:
            print "Skipping job", obs

    def enqueueObservation(self, ignored, filepath, mask):
        print filepath.basename()
        if fnmatch.fnmatch(filepath.basename(), self._fnpattern):
            obs = Observation(filepath.path)
            call = call_at_time(
                obs.start_time - datetime.timedelta(seconds=self.LEAD_TIME),
                self.processObservation,
                obs
            )
        print "Scheduling"
        if call and filepath.path in self._parsets and self._parsets[filepath.path].active():
            print "... REcheduling!"
            self._parsets[filepath.path].cancel()
            self._parsets[filepath.path] = call
        else:
            print "Ignoring ", filepath.basename()

    def prune(self):
        print "Pruning"
        pruneable = []
        for k, v in self._parsets.iteritems():
            if not v or not v.active():
                pruneable.append(k)
            for k in pruneable:
                del self._parsets[k]
            print "Currently tracking %d observations" % (len(self._parsets),)


def makeService(config):
    acontrol_service = MultiService()
    worker_service = WorkerService(config['pattern'])
    worker_service.setName("Worker")
    worker_service.setServiceParent(acontrol_service)

    # Slurp up any existing parsets
    for file in glob.glob(os.path.join(config['dir'], config['pattern'])):
        reactor.callWhenRunning(
        worker_service.enqueueObservation,
            None, filepath.FilePath(file), None
        )

    notifier_service = NotifyService(
        filepath.FilePath(config['dir']),
        mask=inotify.IN_CHANGED,
        callbacks=[worker_service.enqueueObservation]
    )
    notifier_service.setName("Notifier")
    notifier_service.setServiceParent(acontrol_service)

    return acontrol_service
