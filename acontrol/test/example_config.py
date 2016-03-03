import unittest
import textwrap
import tempfile

EXAMPLE_CONFIG = """
[general]
starttime = 2016-02-26 14:25:00
tracklist = [("CasA", "23:23:26", "58:48:00"), ("Jupiter", None, None), ("Sun", None, None)]

[commands]
# (ip, cmdcli port, program name, program port, cli args)
atv = ("10.144.6.13", 45000, "tv", 5000, {"antpos": "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat", "freq":0.0, "output":"/data/atv", "snapshot":"/var/www/html", "port":5000})
correlator = ("10.144.6.31", 45000, "correlator", 6000, {"p":1, "n":288, "t":768, "c":256, "C":63, "m":9, "d":0, "g":"0-9", "b":16, "s":8, "r":0, "N":"4-11,28-35/16-23,40-47", "A":"0:6", "O":"0:4,1:4", "i":"10.195.100.3:53268,10.195.100.3:53276,10.195.100.3:53284,10.195.100.3:53292,10.195.100.3:53300,10.195.100.3:53308", "o":None})
server = ("10.195.100.30", 45000, "imaging-server", 6000, {"buffer-max-size":58*1024**3, "input-host":"10.195.100.31", "input-port-start":4100})
pipeline = ("10.195.100.40", 45000, "imaging-pipeline", 6000, {"server-host":"10.195.100.30", "ant-sigma":4, "vis-sigma":3, "antpos": "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat"})

[lba]
# [(central freq, bandwidth), ...] in Hz
obs = [(58398437.5, 2e8/1024*8)]
# atv is allowed a single subband only
atv = (57617187.5, 2e8/1024)

# list of antenna indices to flag
# flag = [2, 4, 9, 188]

[hba]
# [(central freq, bandwidth, (ra, dec)), ...] in Hz
obs = [(180e6, 1.92e5, (0.2, 0.7))]
atv = (175e6, 1.92e5, (0.2, 0.7))

# list of antenna indices to flag
flag = [1, 2, 228]
"""

EXAMPLE_CONFIG = textwrap.dedent(EXAMPLE_CONFIG).strip()

class TestWithConfig(unittest.TestCase):
    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(mode='w')
        self.config_file.write(EXAMPLE_CONFIG)
        self.config_file.seek(0)

    def tearDown(self):
        self.config_file.close()
