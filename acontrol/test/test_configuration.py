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
        self.start = datetime.datetime(2016, 2, 26, 14, 25)


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


    def test_subbands(self):
        subbands, channels = self.config.subbands(self.config.lba_mode, SAMPLING_CLOCK)
        self.assertEqual(subbands, [295, 296, 297, 298, 299, 300, 301, 302])


    def test_atv(self):
        cmd = self.config.atv(self.obs)
        print "\n\n\n",cmd,"\n\n"


    def test_correlator(self):
        cmd = self.config.correlator(self.obs)
        print "\n\n\n",cmd,"\n\n"


    def test_stations(self):
        cmd = self.config.stations(self.obs)
        print "\n\n\n",cmd,"\n\n"


    def test_server(self):
        cmd = self.config.server(self.obs)
        print "\n\n\n",cmd,"\n\n"


    def test_pipeline(self):
        cmd = self.config.pipelines(self.obs)
        print "\n\n\n",cmd,"\n\n"


if __name__ == "__main__":
    unittest.main()
