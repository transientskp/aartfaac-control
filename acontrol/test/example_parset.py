import unittest
import textwrap
import tempfile

EXAMPLE_PARSET = """
    ObsSW.Observation.antennaArray=HBA
    ObsSW.Observation.antennaSet=HBA_DUAL_INNER
    ObsSW.Observation.bandFilter=HBA_110_190
    ObsSW.Observation.startTime=2013-08-24 14:18:00
    ObsSW.Observation.stopTime=2013-08-24 14:29:00
    ObsSW.Observation.sampleClock=200
    ObsSW.Observation.antennaArray=LBA
    ObsSW.Observation.antennaSet=LBA_OUTER
"""

EXAMPLE_PARSET = textwrap.dedent(EXAMPLE_PARSET).strip()

class TestWithParset(unittest.TestCase):
    def setUp(self):
        self.parset_file = tempfile.NamedTemporaryFile(mode='w')
        self.parset_file.write(EXAMPLE_PARSET)
        self.parset_file.seek(0)

    def tearDown(self):
        self.parset_file.close()
