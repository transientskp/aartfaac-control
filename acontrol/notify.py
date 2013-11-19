import pyinotify
import time
from acontrol import thread

class ControlThread(thread.HaltableThread):
    def __init__(self, path, handler, mask=pyinotify.IN_CLOSE_WRITE):
        super(ControlThread, self).__init__()
        self.path = path
        self.handler = handler
        self.mask = mask

    def run(self):
        wm = pyinotify.WatchManager()
        notifier = pyinotify.ThreadedNotifier(wm, self.handler, read_freq=2)
        notifier.coalesce_events()
        notifier.start()
        wm.add_watch(self.path, self.mask, rec=True)
        while True:
            time.sleep(1)
            if self.stopped:
                print "thread is stopped"
                notifier.stop()
                break
