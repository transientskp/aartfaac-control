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


    def test_emaillist(self):
        self.assertEqual(4, len(self.config.emaillist()))


    def test_time(self):
        self.assertTrue(self.config.start_time > self.start)


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


    def test_valid(self):
        self.assertTrue(self.config.is_valid())


    def test_sort(self):
        # Configurations are sorted by start time.
        self.assertTrue(self.config == self.config)
        new_cfg = Configuration(self.config_file.name)
        new_cfg.start_time += datetime.timedelta(10)
        self.assertTrue(self.config < new_cfg)
        new_cfg.start_time -= datetime.timedelta(20)
        self.assertTrue(self.config > new_cfg)


    def test_correlator(self):
        cmd = self.config.correlators(self.obs)
        print cmd
        self.assertEqual(2, len(cmd))


    def test_pipeline(self):
        cmd = self.config.pipelines(self.obs)
        self.assertEqual(16, len(cmd))


if __name__ == "__main__":
    unittest.main()
