import datetime
import unittest

from acontrol.test.example_parset import TestWithParset
from acontrol.observation import Observation

class ObservationTestCase(TestWithParset):
    def setUp(self):
        super(ObservationTestCase, self).setUp()
        self.observation = Observation(self.parset_file.name)

    def test_times(self):
        self.assertEqual(
            self.observation.start_time,
            datetime.datetime(2013, 8, 24, 14, 18, 00)
        )
        self.assertEqual(
            self.observation.end_time,
            datetime.datetime(2013, 8, 24, 14, 29, 00)
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
