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
correlator = ("10.144.6.14", 46000, "correlator", 6000, {"p":0, "n":288, "t":3072, "c":64, "d":0, "g":"0,1", "b":16, "s":8, "r":0, "i":None, "o":None})
server = None
pipeline = None

[lba]
# [(central freq, bandwidth), ...] in Hz
obs = [(56e6, 1.92e5), (42e6, 3e3)]
atv = (53.90625e6-3e3*32, 1.92e5)

# list of antenna indices to flag
flag = [2, 4, 9, 188]

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
