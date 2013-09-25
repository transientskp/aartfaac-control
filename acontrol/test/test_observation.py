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

if __name__ == "__main__":
    unittest.main()
