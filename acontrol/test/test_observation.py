import datetime
import unittest

from acontrol.test.example_parset import TestWithParset
from acontrol.observation import Observation

class ObservationTestCase(TestWithParset):
    def setUp(self):
        super(ObservationTestCase, self).setUp()
        self.observation = Observation(self.parset_file.name)
        self.start = datetime.datetime(2015, 2, 2, 22, 47, 00)
        self.stop = datetime.datetime(2015, 2, 2, 23, 48, 00)

    def test_times(self):
        self.assertEqual(
            self.observation.start_time,
            self.start
        )
        self.assertEqual(
            self.observation.end_time,
            self.stop
        )

    def test_duration(self):
        self.assertEqual(
            self.observation.duration.seconds,
            (self.stop - self.start).seconds
        )

    def test_sort(self):
        # Observations are sorted by start time.
        self.assertTrue(self.observation == self.observation)
        new_obs = Observation(self.parset_file.name)
        new_obs.start_time += datetime.timedelta(10)
        self.assertTrue(self.observation < new_obs)
        new_obs.start_time -= datetime.timedelta(20)
        self.assertTrue(self.observation > new_obs)


if __name__ == "__main__":
    unittest.main()
