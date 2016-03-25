import time, datetime

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
        cfg = self._config["programs"]["atv"]
        default_args = {"antpos": "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat", "output":"/data/atv", "snapshot":"/var/www/html", "port":5000}
        args = self.merge(cfg["args"], default_args)
        
        if obs.antenna_set.lower() in self._config["lba"]["modes"]:
            args["antpos"] = args["antpos"] % (obs.antenna_set.lower())
            args["freq"] = self.sub2freq(cfg["subband"])
        else:
            raise NotImplementedError

        cmd = " ".join(["--%s=%s" % (str(k), str(v)) for k,v in args.iteritems()])
        address = cfg["address"].split(':')
        return ("atv", address[0], int(address[1]), cmd)


    def correlator(self, obs):
        cfg = self._config["programs"]["correlator"]
        default_args = {"p":1, "n":288, "t":768, "c":256, "C":63, "m":9, "d":0, "g":"0-9", "b":16, "s":8, "r":0, "N":"4-11,28-35/16-23,40-47", "A":"0:6", "O":"0:4,1:4", "i":"10.195.100.3:53268,10.195.100.3:53276,10.195.100.3:53284,10.195.100.3:53292,10.195.100.3:53300,10.195.100.3:53308"}
        args = self.merge(cfg["args"], default_args)
        address = cfg["address"].split(':')

        if obs.antenna_set.lower() in self._config["lba"]["modes"]:
            serverip = self._config["programs"]["server"]["address"].split(':')[0]
            atvip = self._config["programs"]["atv"]["address"].split(':')[0]
            n = self._config["lba"]["subbands"].index(self._config["programs"]["atv"]["subband"])
            N = len(self._config["lba"]["subbands"])
            outputs = ["%s:%i" % (serverip, 4100+i) for i in range(n)]
            outputs += ["%s:%i" % (atvip, self._config["programs"]["atv"]["args"]["port"])]
            outputs += ["%s:%i" % (serverip, 4100+i) for i in range(n, N-1)]
            args["o"] = ",".join(["tcp:%s" % (addr) for addr in outputs])
            args["r"] = obs.duration.seconds
        else:
            raise NotImplementedError

        cmd = " ".join(["-%s %s" % (str(k), str(v)) for k,v in args.iteritems()])
        return ("correlator", address[0], int(address[1]), cmd)

    
    def server(self, obs):
        cfg = self._config["programs"]["server"]
        address = cfg["address"].split(':')
        default_args = {"buffer-max-size":58*1024**3, "input-host":"10.195.100.3", "input-port-start":4100}
        args = self.merge(cfg["args"], default_args)
        subbands = copy.deepcopy(self._config["lba"]["subbands"])
        subbands.remove(self._config["programs"]["atv"]["subband"])
        
        cmd = " ".join(["--%s %s" % (str(k), str(v)) for k,v in args.iteritems()])
        if obs.antenna_set.lower() in self._config["lba"]["modes"]:
            cmd += " " + " ".join(["--stream 63 %i" % (s) for s in subbands])
        else:
            raise NotImplementedError

        a = self._config["lba"]["channels"][0::2]
        b = self._config["lba"]["channels"][1::2]
        cmd += " " + ",".join(["%i-%i" % (t[0],t[1]) for t in zip(a,b)])
        return ("imaging-server", address[0], int(address[1]), cmd)


    def pipelines(self, obs):
        cfg = self._config["programs"]["pipeline"]
        default_args = {"server-host":"10.195.100.30", "ant-sigma":4, "vis-sigma":3, "antenna-positions": "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat"}
        args = self.merge(cfg["args"], default_args)
        args["antenna-positions"] = args["antenna-positions"] % (obs.antenna_set.lower())

        pipelines = []

        if obs.antenna_set.lower() in self._config["lba"]["modes"]:
            for addr in cfg["address"]:
                args["casa"] = "/data/%s" % (obs.start_time.strftime("%Y%m%d-%H%M"))
                cmd = " ".join(["--%s %s" % (str(k), str(v)) for k,v in args.iteritems()])
                a = addr.split(':')
                pipelines.append(("imaging-pipeline", a[0], int(a[1]), cmd))
        else:
            raise NotImplementedError

        return pipelines

    
    def __str__(self):
        return "[CFG - %s]" % (self.start_time)


    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
