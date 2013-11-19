import bisect
import threading
import datetime

class Queue(object):
    """
    Queue maintains a list of Observations sorted by start time.
    """
    def __init__(self):
        self.observations = []
        self.lock = threading.Lock()

    def add(self, obs):
        # Adds a new observation to the queue.
        self.lock.acquire()
        try:
            i = bisect.bisect(self.observations, obs)
            if ((i > 0 and self.observations[i-1].end_time > obs.start_time) or
                (i < len(self.observations) and self.observations[i].start_time < obs.end_time)):
                print "WARNING: Not inserting overlapping observation"
                return
            else:
                self.observations.insert(i, obs)
        finally:
            self.lock.release()

    def upcoming(self, look_ahead=10):
        # Return the next observation which is less than look_ahead seconds in
        # the future, if any.
        self.lock.acquire()
        try:
            if self.observations and self.observations[0].start_time < (datetime.datetime.now() + datetime.timedelta(seconds=look_ahead)):
                return self.observations.pop(0)
            else:
                return None
        finally:
            self.lock.release()
