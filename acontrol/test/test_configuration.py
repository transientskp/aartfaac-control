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
        self.start = datetime.datetime(2015, 2, 2, 22, 47, 00)


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
        self.assertEqual(subbands, [215, 286, 287])
        L = channels[1] + channels[2]
        centre_channel = L[int(round((len(L)+1)/2.0))] + 1
        centre_freq_approx = Configuration.sub2freq(286)+CHANNEL_WIDTH*centre_channel
        centre_freq = self.config.lba_mode[0][0]
        self.assertTrue(abs(centre_freq_approx-centre_freq) < CHANNEL_WIDTH)


    def test_atv(self):
        cmd = self.config.atv(self.obs)

    def test_correlator(self):
        cmd = self.config.correlator(self.obs)


if __name__ == "__main__":
    unittest.main()
