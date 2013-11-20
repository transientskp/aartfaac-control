import sys

from twisted.application import service
from twisted.internet import reactor
from twisted.internet import inotify
from twisted.python import filepath
from twisted.python import usage
from twisted.application.service import MultiService

class Options(usage.Options):
    optParameters = [
        ["dir", "d", "/opt/lofar/var/run", "Directory to monitor for parsets"]
    ]

def notify(ignored, filepath, mask):
    """
    For historical reasons, an opaque handle is passed as first
    parameter. This object should never be used.

    @param filepath: FilePath on which the event happened.
    @param mask: inotify event as hexadecimal masks
    """
    print "event %s on %s" % (
        ', '.join(inotify.humanReadableMask(mask)), filepath)


class NotifyService(service.Service):
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


def makeService(config):
    notifier_service = NotifyService(
	filepath.FilePath(config['dir']), mask=inotify.IN_CHANGED, callbacks=[notify]
    )
    return notifier_service
