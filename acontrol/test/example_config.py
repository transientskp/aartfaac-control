import unittest
import textwrap
import tempfile

EXAMPLE_CONFIG = """
[general]
starttime = 2015-02-02 22:47:00
tracklist = [("CasA", "23:23:26", "58:48:00"), ("Jupiter", None, None), ("Sun", None, None)]

[commands]
# (ip, cmdcli port, program name, program port, cli args)
atv = ("10.144.6.12", 45000, "tv", 5000, {"antpos": None, "freq":0.0, "output":"/data/atv", "snapshot":"/var/www", "port":5000})
correlator = ("10.144.6.31", 46000, "correlator", 6000, {"p":1, "n":288, "t":768, "c":256, "C":63, "m":9, "d":0, "g":"0-9", "b":16, "s":8, "r":0, "N":"4-11,28-35/16-23,40-47", "A":"0:6", "O":"0:4,1:4", "i":"10.195.100.3:53268,10.195.100.3:53276,10.195.100.3:53284,10.195.100.3:53292,10.195.100.3:53300,10.195.100.3:53308", "o":None})
server = None
pipeline = None

[lba]
# [(central freq, bandwidth), ...] in Hz
obs = [(56e6, 1.92e5), (42e6, 3e3)]
atv = (53.90625e6-3e3*32, 1.92e5)

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
