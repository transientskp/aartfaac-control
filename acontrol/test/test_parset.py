import unittest
import tempfile
import datetime
import os

from acontrol.parset import Parset
from acontrol.test.example_parset import TestWithParset

class ParsetTestCase(TestWithParset):
    def setUp(self):
        super(ParsetTestCase, self).setUp()
        self.ps = Parset(self.parset_file.name)
        self.assertEqual(len(self.ps), 16)


    def test_getbool(self):
        self.assertTrue(self.ps.getBool('Observation.ObservationControl.StationControl.aartfaacPiggybackAllowed'))


    def test_getfloat(self):
        self.assertEqual(200.0, self.ps.getFloat('Observation.sampleClock'))


    def test_getint(self):
        self.assertEqual(200, self.ps.getInt('Observation.sampleClock'))


    def test_getstring(self):
        self.assertEqual('LBA_OUTER', self.ps.getString('Observation.antennaSet'))


    def test_keywords(self):
        self.assertEqual(16, len(self.ps.keywords()))


    def test_remove(self):
        self.ps.pop('Observation.startTime')
        self.assertEqual(len(self.ps), 15)


    def test_replace(self):
        self.ps.replace('Observation.startTime', '2013-08-24 14:18:00')
        self.assertEqual(self.ps.get('Observation.startTime'), '2013-08-24 14:18:00')


    def test_getdatetime(self):
        self.ps.replace('Observation.startTime', '2013-08-24 14:18:00')
        self.assertEqual(
            self.ps.getDateTime('Observation.startTime'),
            datetime.datetime(2013, 8, 24, 14, 18, 00)
        )


    def test_writefile(self):
        filename = '/tmp/test.parset'
        self.ps.writeFile(filename)
        self.assertTrue(os.path.isfile(filename))
        os.remove(filename)


if __name__ == "__main__":
	unittest.main()
