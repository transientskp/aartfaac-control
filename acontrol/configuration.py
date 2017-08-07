import time
import datetime
import math
import copy
import os
from twisted.python import log
import string
import subprocess
import numpy as np

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
        self.start_time = datetime.datetime.now() + datetime.timedelta(seconds=2)
        if (self._config["starttime"] != "now"):
            ts = time.strptime(self._config["starttime"], "%Y-%m-%d %H:%M:%S")
            self.start_time = datetime.datetime( ts.tm_year, ts.tm_mon,
                    ts.tm_mday, ts.tm_hour, ts.tm_min, ts.tm_sec)


    def is_valid(self):
        return True


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
        for k in A:
            C[k] = A[k]
        return C

    def setstation_subbands (self):
        # The ordered set of the subband numbers as specified in the AARTFAAC 
        # configuration file need to be translated into the order to be
        # written to the hardware. This is dependent upon the order in which 
        # the correlator instances are defined in the AARTFAAC config file.

        # if the subbands as reported by the hardware (rspctl) are labelled 
        # from sb00-sb35 (16-bit mode), then
        # In 16b mode:  
        # agc002 = [sb00-sb07], 
        # agc001 = [sb18-sb25]
        # In  8b mode:  
        # agc002 = [sb00, sb36, sb01, sb37, sb02, sb38, sb03, sb39, 
        #           sb04, sb40, sb05, sb41, sb06, sb42, sb07, sb43]
        # agc001 = [sb18, sb54, sb19, sb55, sb20, sb56, sb21, sb57, 
        #           sb22, sb58, sb23, sb59, sb24, sb60, sb25, sb61]
        if self._config['bitmode'] == 16:
            subbands = ",".join(
                     self._config['subbands'][8:16] + 
          ["0"]*10 + self._config['subbands'][0:8]  +
          ["0"]*10)

        elif self._config['bitmode'] == 8:
            subbands=",".join(
                    self._config['subbands'][ 0:2:16] +
         ["0"]*10 + self._config['subbands'][16:2:32] + 
         ["0"]*10 + self._config['subbands'][ 1:2:16] +
         ["0"]*10 + self._config['subbands'][17:2:32])

        log.msg("---> Checking currently set station SDO Subbands.")

        # Send rspctl command over ssh; 
        res = subprocess.check_output("\
           pssh -i -O StrictHostKeyChecking=no -O UserKnownHostsFile=/dev/null \
               -O GlobalKnownHostsFile=/dev/null -h ~/psshaartfaac.cfg \
                /opt/lofar/bin/rspctl --sdo | grep SUCCESS -A 3",
                stderr=subprocess.STDOUT, shell=True)

        # Check if the currently set subbands match what we need to set.
        ind = 0
        sblist = {}
        do_setsub = 0
        for stn in range (0,12):
            ind += string.find (res[ind:], 'CS0')
            stname = res[ind:ind+6]
            ind += string.find (res[ind:], 'RCU[ 0]')
            # discard end square brackets.
            sblist = res[ind:].split('\n')[1][2:-2].split(' ') 
            
            # Check for consistency with current settings.
            currsdo = ",".join (sblist[0:8] + ["0"]*10 + sblist[18:26] + ["0"]*10)
            newsdo  = ",".join([str(x) for x in (np.array ([int(x) for x in subbands.split(',')]) * 2)])
            if newsdo != currsdo:
                log.msg ("---> Discrepancy found in station %s!" % stname)
                log.msg ("  Sb. reported by hardware: %s" % currsdo)
                log.msg ("  Sb. in config file      : %s" % newsdo)
                do_setsub = 1
                log.msg(res)
                break
            else:
                log.msg ("---> Station %s is already set.\n   \
                Current sb: %s\n   \
                Desired sb: %s" % (stname, currsdo, newsdo))

        if do_setsub:
            log.msg(" ------ Setting SDO subbands: ------  ")
            res = subprocess.check_output("\
                pssh -i -O StrictHostKeyChecking=no \
                -O UserKnownHostsFile=/dev/null \
                -O GlobalKnownHostsFile=/dev/null -h ~/psshaartfaac.cfg \
                /opt/lofar/bin/rspctl --sdo=%s" % subbands, 
                stderr=subprocess.STDOUT, shell=True)
            log.msg(res)
    
            # We need to wait for some time to let the registers settle before 
            # reading them back.
            log.msg ('... Waiting 10s ...')
            time.sleep (10);
            log.msg(" ------ Current SDO subbands: ------  ")
            res = subprocess.check_output("\
                pssh -i -O StrictHostKeyChecking=no \
                -O UserKnownHostsFile=/dev/null \
                -O GlobalKnownHostsFile=/dev/null -h ~/psshaartfaac.cfg \
                /opt/lofar/bin/rspctl --sdo | grep SUCCESS -A 3", \
                stderr=subprocess.STDOUT, shell=True)

            log.msg(res)
        
    
    def correlators(self, obs):
        correlators = []

        if "correlators" not in self._config["programs"]:
            log.msg ('correlators: Not found')
            return correlators
        else:
            log.msg ('<-- Found correlators in config file.')

        configs = self._config["programs"]["correlators"]

        if "pipelines" in self._config["programs"]:
            outputsink = self._config["programs"]["pipelines"]["instances"]
            noutputsink= len(outputsink)/len(configs["instances"])

        elif "vissinks" in self._config["programs"]:
            outputsink = self._config["programs"]["vissinks"]["instances"]
            noutputsink= len(outputsink)/len(configs["instances"])

        else:
            log.msg ("### No output sinks for correlator data specified! Aborting...")
            return 

        for i,cfg in enumerate(configs["instances"]):
            address = cfg["address"].split(':')

            if not cfg.has_key("argv"):
                cfg["argv"] = {}

            outputs = []
            for v in outputsink[i*noutputsink:(i+1)*noutputsink]:
                ip, port = v["input"].split(':')
                outputs.append("%s:%i" % (ip, int(port)))

            argv = Configuration.merge(configs["argv"], cfg["argv"])
            argv["o"] = ",".join(["tcp:%s" % (addr) for addr in outputs])
            argv["r"] = obs.duration.seconds
            cmd = " ".join(["-%s %s" % (str(k), str(v)) for k,v in argv.iteritems()])
            correlators.append((cfg["name"], address[0], int(address[1]), cmd))

        return correlators


#    def atv(self, obs):
#        atv = []
#        cfg = self._config["programs"]["atv"]
#        _, port = cfg["input"].split(':')
#        address = cfg["address"].split(':')
#        argv = cfg["argv"]
#        argv["port"] = port
#        argv["duration"] = obs.duration.seconds
#        argv["antpos"] = "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat" % (obs.antenna_set.lower())
#        cmd = " ".join(["--%s=%s" % (str(k), str(v)) for k,v in argv.iteritems()])
#        atv.append((cfg["name"], address[0], int(address[1]), cmd))
#        return atv


    def pipelines(self, obs):
        pipelines = []

        if "pipelines" not in self._config["programs"]:
            log.msg ('pipelines: Not found')
            return pipelines
        else:
            log.msg ('<-- Found pipelines in config file.')

        configs = self._config["programs"]["pipelines"]
        nsubbands = len (self._config['subbands'])

        if nsubbands > len (configs['instances']):
            print "Calibration pipelines specified only for %d of %d subbands." % (len (configs['instances']), nsubbands)
            
        imager = self._config["programs"]["imagers"]["instances"]

        # antcfg = ["lba_outer", "lba_inner", "lba_sparse_even", "lba_sparse_odd"].index(obs.antenna_set.lower())
        antcfg = ["lba_outer"].index(obs.antenna_set.lower())


        for i,cfg in enumerate(configs["instances"]):
            address = cfg["address"].split(':')
            _, port = cfg["input"].split(':')

            if not cfg.has_key("argv"):
                cfg["argv"] = {}

            argv = Configuration.merge(configs["argv"], cfg["argv"])
            argv["antpos"] = "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat" % (obs.antenna_set.lower())
            argv["port"] = port
            argv["antcfg"] = antcfg

            # Break if we run out of specified subbands, 
            # even if we have pipeline specifications.
            if i > nsubbands:
                break;

            argv['subband'] = self._config['subbands'][i]
            argv["output"] = "tcp:%s,file:/data/%i-%s.cal" % (imager[0]["input"], int(argv["subband"]), obs.start_time.strftime("%Y%m%d%H%M"))

            cmd = " ".join(["--%s=%s" % (str(k), str(v)) for k,v in argv.iteritems()])
            pipelines.append((cfg["name"], address[0], int(address[1]), cmd))

        return pipelines

    
    def imagers(self, obs):
        imagers = []

        if "imagers" not in self._config["programs"]:
            log.msg ('### imagers: Not found')
            return imagers
        else:
            log.msg ('<-- Found imager in config file.')

        configs = self._config["programs"]["imagers"]


        # antcfg = ["lba_outer", "lba_inner", "lba_sparse_even", "lba_sparse_odd"].index(obs.antenna_set.lower())
        antcfg = ["lba_outer"].index(obs.antenna_set.lower())

        for i,cfg in enumerate (configs["instances"]):
            address = cfg["address"].split(':')
            _, port = cfg["input"].split(':')

            if not cfg.has_key("argv"):
                cfg["argv"] = {}

            argv = Configuration.merge(configs["argv"], cfg["argv"])
            argv["antpos"] = "/home/fhuizing/soft/release/share/aartfaac/antennasets/%s.dat" % (obs.antenna_set.lower())
            # Add a subdirectory based on the current date, to the file path 
            # specified in the output config keyword, if available.
            outputs = argv["output"].split(',') 
            dirname = datetime.datetime.utcnow().strftime ("%Y%m%d")
            for i,x in enumerate (outputs):
                if "dir" in x:
                    if x[-1] == '/':
                        outputs[i] = x + dirname
                    else:
                        outputs[i] = x + '/' + dirname
            argv["output"] = ','.join(outputs)
            argv["subbands"] = ','.join (self._config['subbands'])
            argv["affinity"] = cfg["argv"]["affinity"]

            cmd = " ".join(["--%s=%s" % (str(k), str(v)) for k,v in argv.iteritems()])
            imagers.append((cfg["name"], address[0], int(address[1]), cmd))

        return imagers 
            

    def vissinks (self, obs):
        vissinks = []

        if "vissinks" not in self._config["programs"]:
            log.msg ('### vissinks: Not found')
            return vissinks
        else:
            log.msg ('<-- Found vissinks in config file.')

        configs = self._config["programs"]["vissinks"]
        nsubbands = len (self._config['subbands'])

        if nsubbands > len (configs['instances']):
            print "Visibility Sinks (via nc) specified only for %d of %d \
                    subbands." % (len (configs['instances']), nsubbands)
            

        for i,cfg in enumerate(configs["instances"]):
            address = cfg["address"].split(':')
            destaddr, port = cfg["input"].split(':')

            if not cfg.has_key("argv"):
                cfg["argv"] = {}

            if not configs.has_key("argv"):
                configs["argv"] = {}

            argv = Configuration.merge(configs["argv"], cfg["argv"])
            argv["port"] = port

            # Break if we run out of specified subbands, 
            # even if we have vissink specifications.
            if i > nsubbands:
                break;

            output_filename = "/data/EoR-%s-Sb%d-%s.vis" % \
             (obs.antenna_set.lower(), int(self._config['subbands'][i]),
                 obs.start_time.strftime("%Y%m%d%H%M"))

            cmd = "%s %s %s" % (destaddr, port, output_filename)
            vissinks.append((cfg["name"], address[0], int(address[1]), cmd))

        return vissinks

    def atv (self, obs):
        atv = []

        if "atv" not in self._config["programs"]:
            log.msg ('atv: Not found')
            return atv
        else:
            log.msg ('<-- Found atv in config file.')

        configs = self._config["programs"]["atv"]

        for i,cfg in enumerate (configs["instances"]):

            if not cfg.has_key("argv"):
                cfg["argv"] = {}

            argv = Configuration.merge(configs["argv"], cfg["argv"])
            address = cfg["address"].split(':')
            cmd = " ".join(["--%s=%s" % (str(k), str(v)) for k,v in argv.iteritems()])
            atv.append((cfg["name"], address[0], int(address[1]), cmd))

        return atv

        
    def __str__(self):
        if "hba" in self._config:
            antarray = "hba"
        elif "lba" in self._config:
            antarray = "lba"
            
        return "[CFG - %s %s]" % (antarray, self.start_time)


    def __cmp__(self, other):
        return cmp(self.start_time, other.start_time)
