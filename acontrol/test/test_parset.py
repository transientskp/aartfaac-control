import unittest
import tempfile
import datetime
import os

from acontrol.parset import Parset
from acontrol.test.example_parset import TestWithParset

class ParsetTestCase(TestWithParset):
    def test_getdatetime(self):
        ps = Parset()
        ps['ObsSW.Observation.startTime'] = "2013-08-24 14:18:00"
        self.assertEqual(
            ps.get('ObsSW.Observation.startTime'),
            "2013-08-24 14:18:00"
        )
        self.assertEqual(
            ps.getDateTime('ObsSW.Observation.startTime'),
            datetime.datetime(2013, 8, 24, 14, 18, 00)
        )

    def test_read_file(self):
        ps = Parset(self.parset_file.name)
        self.assertEqual(len(ps), 5)

if __name__ == "__main__":
	unittest.main()
