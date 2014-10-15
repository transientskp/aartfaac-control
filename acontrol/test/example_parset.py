import unittest
import textwrap
import tempfile

EXAMPLE_PARSET = """
    Observation.antennaArray=HBA
    Observation.antennaSet=HBA_DUAL_INNER
    Observation.bandFilter=HBA_110_190
    Observation.startTime=2013-08-24 14:18:00
    Observation.stopTime=2013-08-24 14:29:00
    Observation.sampleClock=200
    Observation.antennaArray=LBA
    Observation.antennaSet=LBA_OUTER
"""

EXAMPLE_PARSET = textwrap.dedent(EXAMPLE_PARSET).strip()

class TestWithParset(unittest.TestCase):
    def setUp(self):
        self.parset_file = tempfile.NamedTemporaryFile(mode='w')
        self.parset_file.write(EXAMPLE_PARSET)
        self.parset_file.seek(0)

    def tearDown(self):
        self.parset_file.close()
