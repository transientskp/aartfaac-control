import unittest
import textwrap
import tempfile

EXAMPLE_CONFIG = """
[general]
starttime = 2015-02-02 22:47:00
tracklist = [("CasA", "23:23:26", "58:48:00"), ("Jupiter", None, None), ("Sun", None, None)]

[commands]
# (ip, cmdcli port, program name, program port)
atv = ("10.144.6.12", 45000, "tv", 5000)
correlator = ("10.144.6.14", 46000, "correlator", 6000)
server = None
pipeline = None

[lba]
# [(central freq, bandwidth), ...] in Hz
obs = [(56e6, 1.92e5), (42e6, 3e3)]
atv = (53e6, 1.92e5)

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
