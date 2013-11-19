import bisect
import threading
import datetime

class Queue(object):
    """
    Queue maintains a list of Observations sorted by start time.
    """
    def __init__(self):
        self._observations = []
        self._lock = threading.Lock()

    def add(self, obs):
        # Adds a new observation to the queue.
        self._lock.acquire()
        try:
            i = bisect.bisect(self._observations, obs)
            if ((i > 0 and self._observations[i-1].end_time > obs.start_time) or
                (i < len(self._observations) and self._observations[i].start_time < obs.end_time)):
                print "WARNING: Not inserting overlapping observation"
                return
            else:
                self._observations.insert(i, obs)
        finally:
            self._lock.release()

    def upcoming(self, look_ahead=10):
        # Return the next observation which is less than look_ahead seconds in
        # the future, if any.
        self._lock.acquire()
        try:
            if self._observations and self._observations[0].start_time < (datetime.datetime.now() + datetime.timedelta(seconds=look_ahead)):
                return self._observations.pop(0)
            else:
                return None
        finally:
            self._lock.release()

    def __len__(self):
        return len(self._observations)
