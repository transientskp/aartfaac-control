import unittest
import textwrap
import tempfile

EXAMPLE_CONFIG = """
[general]
starttime = 2015-02-02 22:47:00
tracklist = [("CasA", "23:23:26", "58:48:00"), ("Jupiter", None, None), ("Sun", None, None)]

[commands]
# (program, ip, port, arguments)
atv = ("atv.py", "localhost", 5000, "--antpos=/usr/local/share/aartfaac/antennasets/%s.dat --freq=%0.1f --channels=%s --output=/data/atv --snapshot=/var/www/")
correlator = ("AARTFAAC", "localhost", 5000, "-p0 -n288 -t3072 -c64 -d0 -g0,1 -b16 -s8 -R1 -r%i -i 1.1.10.1:538,10.15.10.1:576,1.1.10.1:2,1.1.10.1:53292,1.15.10.1:500,1.19.10.1:508 -o tcp:1.4.6.1:50,tcp:1.14.0.2:400,null:,null:,null:,null:,null:,null: 2>&1 | tee acontrol.log")
server = (None,None,None,None)
pipeline = (None,None,None,None)

[lba]
# [(central freq, bandwidth), ...] in Hz
obs = [(56e6, 1.92e5), (42e6, 9e3)]
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
