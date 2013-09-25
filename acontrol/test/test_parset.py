import unittest
import textwrap
import tempfile
import datetime
import os

from acontrol.parset import Parset

EXAMPLE_PARSET = """
    ObsSW.Observation.antennaArray=HBA
    ObsSW.Observation.antennaSet=HBA_DUAL_INNER
    ObsSW.Observation.bandFilter=HBA_110_190
    ObsSW.Observation.startTime=2013-08-24 14:18:00
    ObsSW.Observation.stopTime=2013-08-24 14:29:00
"""
EXAMPLE_PARSET = textwrap.dedent(EXAMPLE_PARSET).strip()

class ParsetTestCase(unittest.TestCase):
    def setUp(self):
        self.parset_file = tempfile.NamedTemporaryFile(mode='w')
        self.parset_file.write(EXAMPLE_PARSET)
        self.parset_file.seek(0)

    def tearDown(self):
        self.parset_file.close()

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
