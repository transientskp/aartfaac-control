import ConfigParser
import time, datetime

class Configuration(object):
    """
    Encapsulates an aartfaac configuration file
    """
    def __init__(self, filepath):
        self._parser = ConfigParser.RawConfigParser()
        self._parser.read(filepath)
        ts = time.strptime(self._parser.get("general", "starttime"), "%Y-%m-%d %H:%M:%S")
        self.start_time = datetime.datetime( ts.tm_year, ts.tm_mon, ts.tm_mday,
                ts.tm_hour, ts.tm_min, ts.tm_sec)
        self.lba_mode = eval(self._parser.get("lba", "obs"))
        self.hba_mode = eval(self._parser.get("hba", "obs"))
        self.lba_atv = eval(self._parser.get("lba", "atv"))
        self.hba_atv = eval(self._parser.get("hba", "atv"))
        self.tracklist = eval(self._parser.get("general", "tracklist"))
        self.atv_cmd = eval(self._parser.get("commands", "atv"))
        self.correlator_cmd = eval(self._parser.get("commands", "correlator"))
        self.atv_server = eval(self._parser.get("commands", "server"))
        self.atv_pipeline = eval(self._parser.get("commands", "pipeline"))


    def is_valid(self):
        return True


    @staticmethod
    def freq2sub(frequency, sample_clock=200e6, nyquist_zone=1):
        """Converts frequency in Hz to lofar subband"""
        subband_width = sample_clock/1024.0
        subband_offset = 512 * (nyquist_zone - 1)
        return int(frequency/subband_width + subband_offset)


    @staticmethod
    def sub2freq(subband, sample_clock=200e6, nyquist_zone=1):
        """Converts lofar subband to frequency in Hz"""
        subband_width = sample_clock/1024.0
        subband_offset = 512 * (nyquist_zone - 1)
        return subband_width * (subband + subband_offset)


    def subbands(self, antenna_mode, sample_clock=200e6, nyquist_zone=1, num_channels=64):
        """Computes subbands and corresponding channels given an obs type"""
        subband_width = sample_clock/1024.0
        channel_width = subband_width/num_channels
        subbands = {}
        for central_freq,bandwidth in antenna_mode:
            start_freq = central_freq - bandwidth/2
            s = Configuration.freq2sub(start_freq, sample_clock, nyquist_zone)
            C = int((start_freq-Configuration.sub2freq(s, sample_clock, nyquist_zone))/channel_width)
            N = int(bandwidth/channel_width + 0.5)
            for i in range(N):
                c = ((i + C) % num_channels)
                if c == 0 and i > 0:
                    s += 1
                if not subbands.has_key(s):
                    subbands[s] = []
                # As the correlator discards the first channel and shifts
                # indices by -1, so do we
                if c - 1 >= 0:
                    subbands[s].append(c-1)

        return subbands.keys(), subbands.values() 


    def atv(self, obs):
        if obs.antenna_array.lower() in "lba":
            _, channels = self.subbands([self.lba_atv], obs.sample_clock*1e6)
            central_frequency = self.lba_atv[0]
            cmd = self.atv_cmd[3] % (obs.antenna_set, central_frequency, str(channels[0]).replace(" ","")[1:-1])
            return (self.atv_cmd[0], self.atv_cmd[1], self.atv_cmd[2], cmd)
        else:
            raise NotImplementedError


    def correlator(self, obs):
        if obs.antenna_array.lower() in "lba":
            cmd = self.correlator_cmd[3] % (obs.duration)
            return (self.correlator_cmd[0], self.correlator_cmd[1], self.correlator_cmd[2], cmd)
        else:
            raise NotImplementedError


    def __str__(self):
        return "[CFG - %s] %s" % (self.start, [x[0] for x in self.tracklist])


    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
