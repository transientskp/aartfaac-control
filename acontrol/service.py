import sys

from acontrol.queue import Queue
from acontrol.observation import Observation

from twisted.internet import reactor
from twisted.internet import inotify
from twisted.internet.task import LoopingCall
from twisted.python import filepath
from twisted.python import usage
from twisted.application.service import Service, MultiService

class Options(usage.Options):
    optParameters = [
        ["dir", "d", "/opt/lofar/var/run", "Directory to monitor for parsets"]
    ]


class Enqueuer(object):
    def __init__(self, queue):
        self._queue = queue

    def __call__(self, ignored, filepath, mask):
#        print filepath.path
#        obs = Observation(filepath.path)
#        print obs.duration
#        self._queue.add(obs)
        self._queue.add(Observation(filepath.path))
#        print "event %s on %s" % (
#            ', '.join(inotify.humanReadableMask(mask)), filepath)
#        #self._queue.add(obj)


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
    POLL_INTERVAL = 1
    POLL_LOOKAHEAD = 10

    def __init__(self, queue):
        self.queue = queue
        self.poll_loop = LoopingCall(self.check_queue)
        self.busy = False

    def startService(self):
        self.poll_loop.start(self.POLL_INTERVAL)

    def stopService(self):
        self.poll_loop.stop()

    def check_queue(self):
        if self.busy:
            return
        upcoming = self.queue.upcoming(self.POLL_LOOKAHEAD)
        if upcoming:
            print "Got upcoming observation"
            self.poll_loop.stop()
            self.busy = True


def makeService(config):
    acontrol_service = MultiService()

    queue = Queue()

    notifier_service = NotifyService(
        filepath.FilePath(config['dir']),
        mask=inotify.IN_CHANGED,
        callbacks=[Enqueuer(queue)]
    )
    notifier_service.setName("Notifier")
    notifier_service.setServiceParent(acontrol_service)

    worker_service = WorkerService(queue)
    worker_service.setName("Worker")
    worker_service.setServiceParent(acontrol_service)

    return acontrol_service
