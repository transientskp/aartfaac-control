import time, datetime
import json
import copy

class Configuration(object):
    """
    Encapsulates an aartfaac configuration file
    """
    def __init__(self, filepath):
        self._config = json.loads(open(filepath,'r').read())
        self.filepath = filepath
        ts = time.strptime(self._config["starttime"], "%Y-%m-%d %H:%M:%S")
        self.start_time = datetime.datetime( ts.tm_year, ts.tm_mon, ts.tm_mday,
                ts.tm_hour, ts.tm_min, ts.tm_sec)


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


    @staticmethod
    def merge(A, B):
        for k,v in A.iteritems():
            B[k] = v
        return B


    def stations(self, obs):
        cmd = "setsubbands.sh "

        if obs.antenna_set.lower() in self._config["lba"]["modes"]:
            cmd += ",".join(map(str, self._config["lba"]["subbands"]))
        else:
            raise NotImplementedError

        return cmd


    def atv(self, obs):
        atvcfg = self._config["programs"]["atv"]
        default_args = {"antpos": "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat", "output":"/data/atv", "snapshot":"/var/www/html", "port":5000}
        args = self.merge(atvcfg["args"], default_args)
        
        if obs.antenna_set.lower() in self._config["lba"]["modes"]:
            args["antpos"] = args["antpos"] % (obs.antenna_set.lower())
            args["freq"] = self.sub2freq(atvcfg["subband"])
        else:
            raise NotImplementedError

        cmd = " ".join(["--%s=%s" % (str(k), str(v)) for k,v in args.iteritems()])
        address = atvcfg["address"][0].split(':')
        return ("atv", address[0], int(address[1]), cmd)


    def correlator(self, obs):
        corrcfg = self._config["programs"]["correlator"]
        default_args = {"p":1, "n":288, "t":768, "c":256, "C":63, "m":9, "d":0, "g":"0-9", "b":16, "s":8, "r":0, "N":"4-11,28-35/16-23,40-47", "A":"0:6", "O":"0:4,1:4", "i":"10.195.100.3:53268,10.195.100.3:53276,10.195.100.3:53284,10.195.100.3:53292,10.195.100.3:53300,10.195.100.3:53308"}
        args = self.merge(corrcfg["args"], default_args)
        address = corrcfg["address"].split(':')

        if obs.antenna_set.lower() in self._config["lba"]["modes"]:
            outputs = [self._config["programs"]["atv"]["address"], 
        else:
            raise NotImplementedError
        """
        args = self.correlator_cmd[4]

        if obs.antenna_array.lower() in "lba":
            output = [(self.atv_cmd[0], self.atv_cmd[3])]
            subbands, channels = self.subbands(self.lba_mode)
            output += [("10.195.100.30", i+4100) for i in range(1,len(subbands))]
            args["o"] = ",".join(["tcp:%s:%i" % (t[0], t[1]) for t in output])
            args["r"] = obs.duration.seconds

        else:
            raise NotImplementedError
        """

        cmd = " ".join(["-%s %s" % (str(k), str(v)) for k,v in args.iteritems()])
        return ("correlator", address[0], int(address[1]), cmd)

    
    def server(self, obs):
        """
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
        """
        return (0,0,0,0)


    def pipelines(self, obs):
        """
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

        """
        return [(0,0,0,0)]

    
    def __str__(self):
        return "[CFG - %s] %s" % (self.start_time, self.filepath)


    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
