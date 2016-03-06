import ConfigParser
import time, datetime
import copy

class Configuration(object):
    """
    Encapsulates an aartfaac configuration file
    """
    def __init__(self, filepath):
        self._parser = ConfigParser.RawConfigParser()
        self._parser.read(filepath)
        self.filepath = filepath
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
        self.corsim_cmd = eval(self._parser.get("commands", "correlator"))
        self.server_cmd = eval(self._parser.get("commands", "server"))
        self.pipeline_cmd = eval(self._parser.get("commands", "pipeline"))


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


    def stations(self, obs):
        cmd = "setsubbands.sh "

        if obs.antenna_array.lower() in "lba":
            img, _ = self.subbands(self.lba_mode)
            atv, _ = self.subbands([self.lba_atv])
            cmd += ",".join(map(str, atv + img))
        else:
            raise NotImplementedError

        return cmd


    def atv(self, obs):
        args = copy.deepcopy(self.atv_cmd[4])

        if obs.antenna_array.lower() in "lba":
            args["antpos"] = args["antpos"] % (obs.antenna_set.lower())
            args["freq"] = (self.lba_atv[0])
            args["port"] = (self.atv_cmd[3])
        else:
            raise NotImplementedError

        cmd = " ".join(["--%s=%s" % (str(k), str(v)) for k,v in args.iteritems()])
        return (self.atv_cmd[2], self.atv_cmd[0], self.atv_cmd[1], cmd)


    def correlator(self, obs):
        args = self.correlator_cmd[4]

        if obs.antenna_array.lower() in "lba":
            output = [(self.atv_cmd[0], self.atv_cmd[3])]
            subbands, channels = self.subbands(self.lba_mode)
            output += [("10.195.100.30", i+4100) for i in range(1,len(subbands))]
            args["o"] = ",".join(["tcp:%s:%i" % (t[0], t[1]) for t in output])
            args["r"] = obs.duration.seconds

        else:
            raise NotImplementedError

        cmd = " ".join(["-%s %s" % (str(k), str(v)) for k,v in args.iteritems()])
        return (self.correlator_cmd[2], self.correlator_cmd[0], self.correlator_cmd[1], cmd)

    
    def server(self, obs):
        args = self.server_cmd[4]
        streams = ""

        if obs.antenna_array.lower() in "lba":
            subbands, channels = self.subbands(self.lba_mode)
            for i in range(len(subbands)):
                streams += " --stream %i %i" % (channels[i][-1]-channels[i][0]+1, subbands[i])
        else:
            raise NotImplementedError

        cmd = " ".join(["--%s %s" % (str(k), str(v)) for k,v in args.iteritems()])
        cmd += streams + " 0-62"
        return (self.server_cmd[2], self.server_cmd[0], self.server_cmd[1], cmd)


    def pipelines(self, obs):
        pipelines = []

        for pipe in self.pipeline_cmd:
            args = copy.deepcopy(pipe[4])
            if obs.antenna_array.lower() in "lba":
                args["antenna-positions"] = args["antenna-positions"] % (obs.antenna_set.lower())
                args["casa"] = "/data/%s" % (obs.start_time.strftime("%Y%m%d-%H%M"))
            else:
                raise NotImplementedError

            cmd = " ".join(["--%s %s" % (str(k), str(v)) for k,v in args.iteritems()])
            pipelines.append((pipe[2], pipe[0], pipe[1], cmd))

        return pipelines

    
    def __str__(self):
        return "[CFG - %s] %s" % (self.start_time, self.filepath)


    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
