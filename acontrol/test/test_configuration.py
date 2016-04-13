import datetime
import tempfile
import unittest

from acontrol.test.example_parset import EXAMPLE_PARSET
from acontrol.test.example_config import TestWithConfig
from acontrol.configuration import Configuration
from acontrol.observation import Observation

SAMPLING_CLOCK = 200e6
NUM_CHANNELS = 64
SUBBAND_WIDTH = SAMPLING_CLOCK / 1024.0
CHANNEL_WIDTH = SUBBAND_WIDTH / NUM_CHANNELS
class ConfigurationTestCase(TestWithConfig):
    def setUp(self):
        super(ConfigurationTestCase, self).setUp()
        self.config = Configuration(self.config_file.name)
        self.parset_file = tempfile.NamedTemporaryFile(mode='w')
        self.parset_file.write(EXAMPLE_PARSET)
        self.parset_file.seek(0)
        self.obs = Observation(self.parset_file.name)
        self.start = datetime.datetime(2016, 3, 7, 4, 12, 47)


    def tearDown(self):
        self.parset_file.close()


    def test_time(self):
        self.assertEqual(
            self.config.start_time,
            self.start
        )


    def test_freq2sub(self):
        self.assertEqual(
            Configuration.freq2sub(54e6, SAMPLING_CLOCK),
            276
        )


    def test_sub2freq(self):
        self.assertEqual(
            Configuration.sub2freq(276, SAMPLING_CLOCK),
            53906250
        )


    def test_sort(self):
        # Configurations are sorted by start time.
        self.assertTrue(self.config == self.config)
        new_cfg = Configuration(self.config_file.name)
        new_cfg.start_time += datetime.timedelta(10)
        self.assertTrue(self.config < new_cfg)
        new_cfg.start_time -= datetime.timedelta(20)
        self.assertTrue(self.config > new_cfg)


    def test_atv(self):
        cmd = self.config.atv(self.obs)
        self.assertEqual(cmd, ('atv', u'10.144.6.13', 45000, '--antpos=/home/fhuizing/soft/release/share/aartfaac/antennasets/lba_outer.dat --freq=58398437.5 --snapshot=/var/www --port=5000 --output=/data/atv'))


    def test_correlator(self):
        cmd = self.config.correlator(self.obs)
        self.assertEqual(cmd, ('correlator', u'10.144.6.31', 45000, '-A 0:6 -C 63 -O 0:4,1:4 -N 4-11,28-35/16-23,40-47 -c 256 -b 16 -d 0 -g 0-9 -i 10.195.100.3:53268,10.195.100.3:53276,10.195.100.3:53284,10.195.100.3:53292,10.195.100.3:53300,10.195.100.3:53308 -m 9 -o tcp:10.195.100.30:4100,tcp:10.195.100.30:4101,tcp:10.195.100.30:4102,tcp:10.195.100.30:4103,tcp:10.144.6.13:5000,tcp:10.195.100.30:4104,tcp:10.195.100.30:4105,tcp:10.195.100.30:4106 -n 288 -p 1 -s 8 -r 3660 -t 768'))


    def test_stations(self):
        cmd = self.config.stations(self.obs)
        self.assertEqual(cmd, 'setsubbands.sh 295,296,297,298,299,300,301,302')


    def test_server(self):
        cmd = self.config.server(self.obs)
        self.assertEqual(cmd, ('server', u'10.195.100.30', 45000, '--buffer-max-size 64424509440 --input-port-start 4100 --input-host 10.195.100.3 --stream 63 295 --stream 63 296 --stream 63 297 --stream 63 298 --stream 63 300 --stream 63 301 --stream 63 302 0-62'))


    def test_pipeline(self):
        cmd = self.config.pipelines(self.obs)
        self.assertEqual(cmd, [('pipeline-0', u'10.144.6.16', 45000, '--vis-sigma 3 --antenna-positions /home/fhuizing/soft/release/share/aartfaac/antennasets/lba_outer.dat --ant-sigma 4 --casa /data/20150202-2247 --server-host 10.195.100.30'), ('pipeline-1', u'10.144.6.17', 45000, '--vis-sigma 3 --antenna-positions /home/fhuizing/soft/release/share/aartfaac/antennasets/lba_outer.dat --ant-sigma 4 --casa /data/20150202-2247 --server-host 10.195.100.30'), ('pipeline-2', u'10.144.6.18', 45000, '--vis-sigma 3 --antenna-positions /home/fhuizing/soft/release/share/aartfaac/antennasets/lba_outer.dat --ant-sigma 4 --casa /data/20150202-2247 --server-host 10.195.100.30'), ('pipeline-3', u'10.144.6.19', 45000, '--vis-sigma 3 --antenna-positions /home/fhuizing/soft/release/share/aartfaac/antennasets/lba_outer.dat --ant-sigma 4 --casa /data/20150202-2247 --server-host 10.195.100.30'), ('pipeline-4', u'10.144.6.20', 45000, '--vis-sigma 3 --antenna-positions /home/fhuizing/soft/release/share/aartfaac/antennasets/lba_outer.dat --ant-sigma 4 --casa /data/20150202-2247 --server-host 10.195.100.30')])


if __name__ == "__main__":
    unittest.main()
