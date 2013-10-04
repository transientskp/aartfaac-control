import unittest
import datetime

from acontrol.test.example_parset import TestWithParset
from acontrol.queue import Queue
from acontrol.observation import Observation

class QueueTestCase(TestWithParset):
    def setUp(self):
        super(QueueTestCase, self).setUp()
        self.queue = Queue()
        self.observation = Observation(self.parset_file.name)

    def test_add_to_queue(self):
        # The queue grows when we add to it
        self.assertEqual(len(self.queue.observations), 0)
        self.queue.add(self.observation)
        self.assertEqual(len(self.queue.observations), 1)

    def test_queue_sorted(self):
        # The queue is always in sorted order
        self.queue.add(self.observation)
        new_obs = Observation(self.parset_file.name)
        new_obs.start_time += datetime.timedelta(10)
        self.queue.add(new_obs)
        new_obs = Observation(self.parset_file.name)
        new_obs.start_time -= datetime.timedelta(10)
        self.queue.add(new_obs)
        self.assert_(self.queue.observations[0] < self.queue.observations[1])
        self.assert_(self.queue.observations[0] < self.queue.observations[2])
        self.assert_(self.queue.observations[1] < self.queue.observations[2])

    def test_upcoming(self):
        # This observation is ready to go and so should be de-queued
        self.observation.start_time = datetime.datetime.now()
        self.queue.add(self.observation)
        self.assertEqual(len(self.queue.observations), 1)
        self.assert_(self.queue.upcoming(look_ahead=10))
        self.assertEqual(len(self.queue.observations), 0)

        # This observation is not, so the queue remains unchanged
        self.observation.start_time = datetime.datetime.now() + datetime.timedelta(days=1)
        self.queue.add(self.observation)
        self.assertEqual(len(self.queue.observations), 1)
        self.assert_(not self.queue.upcoming(look_ahead=10))
        self.assertEqual(len(self.queue.observations), 1)

if __name__ == "__main__":
    unittest.main()
