import unittest
import textwrap
import tempfile

EXAMPLE_PARSET = """
# Example Parset Snippet
Observation.antennaArray=LBA
Observation.antennaSet=LBA_OUTER
Observation.bandFilter=LBA_30_90
Observation.claimPeriod=25
Observation.clockMode=<<Clock200
Observation.nrAnaBeams=0
Observation.nrBeams=1
Observation.nrBitsPerSample=16
Observation.nrTBBSettings=0
Observation.preparePeriod=25
Observation.processSubtype=Beam Observation
Observation.processType=Observation
Observation.sampleClock=200
Observation.startTime=2015-02-02 22:47:00
Observation.stopTime=2015-02-02 23:48:00
Observation.ObservationControl.StationControl.aartfaacPiggybackAllowed=true
"""

EXAMPLE_PARSET = textwrap.dedent(EXAMPLE_PARSET).strip()

class TestWithParset(unittest.TestCase):
    def setUp(self):
        self.parset_file = tempfile.NamedTemporaryFile(mode='w')
        self.parset_file.write(EXAMPLE_PARSET)
        self.parset_file.seek(0)

    def tearDown(self):
        self.parset_file.close()
