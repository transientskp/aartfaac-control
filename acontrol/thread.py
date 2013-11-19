import threading

class HaltableThread(threading.Thread):
    def __init__(self):
        super(HaltableThread, self).__init__()
        self._halt = threading.Event()

    def halt(self):
        self._halt.set()

    @property
    def stopped(self):
        return self._halt.isSet()
