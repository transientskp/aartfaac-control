import time
import datetime
import math
import copy

try:
    import json
except ImportError:
    import simplejson as json
import copy


class Configuration(object):
    """
    Encapsulates an aartfaac configuration file
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self._config = json.loads(open(filepath,'r').read())
        self.start_time = datetime.datetime.now()
        if (self._config["starttime"] != "now"):
            ts = time.strptime(self._config["starttime"], "%Y-%m-%d %H:%M:%S")
            self.start_time = datetime.datetime( ts.tm_year, ts.tm_mon,
                    ts.tm_mday, ts.tm_hour, ts.tm_min, ts.tm_sec)


    def is_valid(self):
        return len(self._config["lba"]["subbands"]) == len(self._config["programs"]["pipelines"]["instances"])


    def emaillist(self):
        if self._config.has_key("email"):
            return self._config["email"]
        else:
            return []


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
        C = copy.deepcopy(B)
        for k,v in A.iteritems():
            C[k] = v
        return C

    
    def correlators(self, obs):
        correlators = []
        configs = self._config["programs"]["correlators"]
        pipelines = self._config["programs"]["pipelines"]["instances"]
        npipelines = len(pipelines)/len(configs["instances"])

        for i,cfg in enumerate(configs["instances"]):
            address = cfg["address"].split(':')

            if not cfg.has_key("argv"):
                cfg["argv"] = {}

            outputs = []
            for v in pipelines[i*npipelines:(i+1)*npipelines]:
                ip, port = v["input"].split(':')
                outputs.append("%s:%i" % (ip, int(port)))

            argv = Configuration.merge(configs["argv"], cfg["argv"])
            argv["o"] = ",".join(["tcp:%s" % (addr) for addr in outputs])
            argv["r"] = obs.duration.seconds
            cmd = " ".join(["-%s %s" % (str(k), str(v)) for k,v in argv.iteritems()])
            correlators.append((cfg["name"], address[0], int(address[1]), cmd))

        return correlators

    
    def pipelines(self, obs):
        pipelines = []
        configs = self._config["programs"]["pipelines"]
        subbands = self._config["lba"]["subbands"]

        for i,cfg in enumerate(configs["instances"]):
            address = cfg["address"].split(':')
            _, port = cfg["input"].split(':')

            if not cfg.has_key("argv"):
                cfg["argv"] = {}

            argv = Configuration.merge(configs["argv"], cfg["argv"])
            argv["subband"] = subbands[i]
            argv["antpos"] = "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat" % (obs.antenna_set.lower())
            argv["port"] = port
            argv["output"] = "file:/data/%i-%s.cal" % (subbands[i], obs.start_time.strftime("%Y%m%d%H%M"))
            cmd = " ".join(["--%s=%s" % (str(k), str(v)) for k,v in argv.iteritems()])
            pipelines.append((cfg["name"], address[0], int(address[1]), cmd))

        return pipelines

    
    def __str__(self):
        return "[CFG - %s]" % (self.start_time)


    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
