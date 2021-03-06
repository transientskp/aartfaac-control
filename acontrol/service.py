import os
import fnmatch
import time, datetime
import glob

from acontrol.observation import Observation
from acontrol.controlprotocol import ControlProtocol, ControlFactory
from acontrol.configuration import Configuration
from acontrol.mailnotify import *
from acontrol.test.example_config import EXAMPLE_CONFIG, LOCAL_CONFIG

from twisted.internet import reactor
from twisted.internet import inotify
from twisted.internet import protocol
from twisted.internet import defer
from twisted.internet.task import LoopingCall
from twisted.python import filepath
from twisted.python import usage
from twisted.python import log
from twisted.application.service import Service, MultiService
import numpy as np

FIVE_MINUTES = 300
SECONDS_IN_DAY = 86400
US_IN_SECOND = 1e6

def start(name, host, port, argv):
    d = defer.Deferred()
    f = ControlFactory(name, argv, d, True)
    reactor.connectTCP(host, port, f)
    log.msg ('<-- start: name: %s, argv %s' % (name, argv))
    return d

def stop(name, host, port, argv):
    d = defer.Deferred()
    f = ControlFactory(name, argv, d, False)
    reactor.connectTCP(host, port, f)
    return d


def call_at(start_datetime, f, *args, **kwargs):
    """
    Run f(*args, **kwargs) at datetime.
    """
    delta = start_datetime - datetime.datetime.now()
    seconds_ahead = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND
    if seconds_ahead > 0:
        log.msg("Calling '%s' in %d seconds" % (f.__name__, seconds_ahead))
        return reactor.callLater(seconds_ahead, f, *args, **kwargs)
    else:
        log.msg("Not scheduling; call '%s' is in the past" % (f.__name__))
    return None


def call_at_to(start_datetime, end_datetime, f, *args, **kwargs):
    """
    Run f(*args, **kwargs) at datetime.
    """
    delta = start_datetime - datetime.datetime.now()
    seconds_ahead = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND
    delta = end_datetime - datetime.datetime.now()
    seconds_before_end = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND
    delta = end_datetime - start_datetime
    seconds_duration = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND

    if seconds_ahead > 0 and seconds_duration > FIVE_MINUTES:
        log.msg("Will call in %d seconds" % (seconds_ahead))
        return reactor.callLater(seconds_ahead, f, *args, **kwargs)
    elif seconds_before_end > FIVE_MINUTES:
        log.msg("Obs in progress, starting now!")
        return reactor.callLater(1, f, *args, **kwargs)
    else:
        log.msg("Not scheduling; Obs in the past or too short")

    return None


class Options(usage.Options):
    optParameters = [
        ["lofar-dir", None, "/opt/lofar/var/run", "Directory to monitor for lofar parsets"],
        ["lofar-pattern", None, "mcu001*", "Glob lofar pattern to select usable parsets"],
        ["config-dir", None, "/opt/aartfaac/var/run", "Directory to monitor for lofar parsets"],
        ["config-pattern", None, "AARTFAAC*", "Glob aartfaac pattern to select usable parsets"],
    ]


class NotifyService(Service):
    """
    Watch for events on @path@ according to @mask@ and run @callbacks@ as
    appropriate.
    """
    def __init__(self, path, mask, callbacks):
        self.notifier = inotify.INotify()
        self.notifier.watch(path, mask=mask, callbacks=callbacks)

    def startService(self):
        self.notifier.startReading()

    def stopService(self):
        self.notifier.stopReading()


class WorkerService(Service):
    PRE_TIME   = 20  # Start pipeline N seconds before observation starts
    PRUNE_TIME = 10  # Prune observations that are finished every N seconds


    def __init__(self, options, email, config=EXAMPLE_CONFIG):
        self._available = False
        self._parsets = {}
        self._configs = {}
        self._configobjs = {}
        self._prune_call = LoopingCall(self.prune)
        self._fnpattern = options['lofar-pattern']
        self._aapattern = options['config-pattern']
        self._email = email
        self._cfg_file = open(options['config-dir'] + '/AARTFAAC:000000.json', 'w')
        self._cfg_file.write(config)
        self._cfg_file.seek(0)
        self._activeconfig = Configuration(self._cfg_file.name)
        self._email.updatelist(self._activeconfig.emaillist())


    def startService(self):
        self._available = True
        self._prune_call.start(self.PRUNE_TIME)


    def stopService(self):
        # Shut down any processing in progress...
        self._available = False
        self._prune_call.stop()
        self._cfg_file.close()


    def endObservation(self, obs, connector=stop):
        def stop_clients(V):
            l = [connector(*v) for v in V]
            return defer.DeferredList(l, consumeErrors=True)

        def success(result):
            log.msg("%s" % (result))

        # layer1: [imagers, pipelines, atv, correlators]
        #            |
        #       0-N  |
        #            |
        # layer2: result
        imagers = stop_clients(self._activeconfig.imagers(obs))
        pipelines = stop_clients(self._activeconfig.pipelines(obs))
        vissinks = stop_clients(self._activeconfig.vissinks(obs))
        atv = stop_clients(self._activeconfig.atv(obs))
        correlators = stop_clients(self._activeconfig.correlators(obs))
        result = defer.DeferredList([pipelines, vissinks, correlators, imagers, atv], consumeErrors=True)
        result.addCallback(success)
        

    def processObservation(self, obs, connector=start):
        """
        Start a pipeline to process the observation
        """
        if self._available:
            mlog.m("Using aartfaac configuration `%s'\n\n" % (self._activeconfig.filepath))
            log.msg ("<-- OBSER: Starting Observation %s, Current config %s " % (obs, self._activeconfig.filepath))

            # Set station subbands, in case the hardware config has changed 
            # since the AARTFAAC configuration was applied.
            log.msg ("<-- Imager: Checking subbands.")
            self._activeconfig.setstation_subbands ()

            def pass_1N(result, V):
                s = False
                for v in result:
                    s = s or (type(v) == tuple and v[0])

                if not s:
                    return None

                l = [connector(*v) for v in V]
                return defer.DeferredList(l, fireOnOneCallback=False, consumeErrors=True)

            def success(result):
                s = True
                for v in result:
                    if type(v) == tuple and not v[0]:
                        s = False
                        break
                    if type(v[1]) == list:
                        for x in v[1]:
                            if type(x) == tuple and not x[0]:
                                s = False
                                break

                header = "[-] %s" % (obs)
                if s:
                    header = "[+] %s" % (obs)

                reactor.callLater(self.PRE_TIME, self._email.send, header, mlog.flush(), [obs.filepath, self._activeconfig.filepath])


            # layer1: imagers (flattened list of all imagers)
            #            |
            #       1-N  |
            #            |
            # layer2: [pipelines, atv] (flattened list of all pipelines and atv instances)
            #            |
            #       1-N  |
            #            |
            # layer3: correlators (flattened list of all correlators
            #            |
            #       0-N  |
            #            |
            # layer4: result
            layer1 = [connector (*p) for p in self._activeconfig.imagers(obs)]

            if layer1:
                log.msg ('<-- Initiating calibration pipeline.')
                layer2 = defer.DeferredList(layer1, consumeErrors=True)
                layer2.addCallback(pass_1N, self._activeconfig.pipelines(obs) + self._activeconfig.atv(obs))
                layer3 = defer.DeferredList([layer2], consumeErrors=True)
            else:
                log.msg ('<-- Found no imagers in config file.')
                layer2 = [connector (*p) for p in self._activeconfig.vissinks(obs)]
                layer3 = defer.DeferredList(layer2, consumeErrors=True)

            layer3.addCallback(pass_1N, self._activeconfig.correlators(obs))
            layer4 = defer.DeferredList([layer3], consumeErrors=True)
            layer4.addCallback(success)
        else:
            log.msg("<-- Skipping %s" % (obs))


    def enqueueObservation(self, ignored, filepath, mask):
        """
        Parse files matching the glob pattern and create future call
        """
        call = None
        if fnmatch.fnmatch(filepath.basename(), self._fnpattern):
            obs = Observation(filepath.path)
            if not obs.is_valid():
                log.msg("Invalid %s; ignoring" % (obs))
                return

            key = hash(obs)

            # Special check only for HBA observations.
            if obs.antenna_array == "HBA":
                # Check if the AARTFAAC configuration corresponding to the time of
                # the observation has a matching specification in terms of 
                # antenna array. Added to allow specific HBA observations.
    
                # Find the config among those available, that would be active when
                #  this observation is scheduled.
                log.msg ('<-- Found an HBA observation. Checking for corresponding config.')
                min_timdel= datetime.timedelta.max
                ind = None
                for k, v in self._configs.iteritems():
                    cfgtim = datetime.datetime.fromtimestamp(v.getTime())
                    log.msg ('    cfgtim: %s, obs time: %s' % (cfgtim, obs.start_time));
                    if cfgtim > obs.start_time:
                        break
                    timdel = obs.start_time - cfgtim
                    if timdel < min_timdel:
                        min_timdel = timdel;
                        ind = k;
                    
                if ind:
                    log.msg ('    Closest AARTFAAC config. (%s) is %s seconds before observation. key: %s' % 
                                (str(self._configs[ind]), min_timdel.seconds, ind))

                    # Ignore this observation if no suitable config is found.
                    if not "hba" in self._configobjs[ind]._config:
                        call = None
                        log.msg("    Ignoring config %s: mode: %s. Active config during obs. is not HBA."
                            % (filepath.path, self._configobjs[ind]._config["hba"]["modes"]))
                        return
                else:
                    call = None
                    log.msg("    Ignoring config %s: No suitable HBA AARTFAAC config found." % filepath.path)
                    return
                    
                                   
            if key in self._parsets and self._parsets[key].active():
                log.msg("Already scheduled %s; ignoring" % (obs))
            elif key not in self._parsets:
                call = call_at_to(obs.start_time - datetime.timedelta(seconds=self.PRE_TIME), 
                            obs.end_time, self.processObservation, obs)
                if call:
                    log.msg("Scheduling observation %s (%s)" % (obs, filepath.path))
                    self._parsets[key] = call
                    call_at(obs.end_time - datetime.timedelta(seconds=60), self.endObservation, obs)
        else:
            log.msg("Ignoring %s" % (filepath.path))


    def applyConfiguration(self, config):
        """
        Prepare AARTFAAC telescope for upcomming observations
        """
        if config.is_valid():
            log.msg("<-- CONFIG: Applying AARTFAAC configuration %s" % (config))
            self._activeconfig = config
            self._email.updatelist(self._activeconfig.emaillist())
            log.msg("<-- !CONFIG: Set AARTFAAC configuration to %s" % (config))
        else:
            log.msg("<-- #CONFIG: Invalid config: %s" % config)


    def enqueueConfiguration(self, ignored, filepath, mask):
        """
        Parse files matching the glob pattern and create future call
        """
        call = None
        if fnmatch.fnmatch(filepath.basename(), self._aapattern):
            try:
                cfg = Configuration(filepath.path)
            except Exception as e:
                log.msg ("### Unable to create configuration object from provided config file!")
                log.msg ('### %s' % str(e))
                return

                
            call = call_at(
                cfg.start_time,
                self.applyConfiguration,
                cfg
            )

        if call and filepath.path in self._configs and self._configs[filepath.path].active():
            log.msg("Rescheduling config update %s" % (filepath.path))
            self._configs[filepath.path].cancel()
            self._configs[filepath.path] = call
            self._configobjs[filepath.path] = cfg
        elif call and filepath.path not in self._configs:
            log.msg("Scheduling config update %s" % (filepath.path))
            self._configs[filepath.path] = call
            self._configobjs[filepath.path] = cfg
        else:
            log.msg("Ignoring config update %s" % (filepath.path))


    def prune(self):
        """
        Prune parsets/configs that have passed or are inactive
        """
        pruneable = []
        for k, v in self._parsets.iteritems():
            if not v or not v.active():
                pruneable.append(k)
        for k in pruneable:
            del self._parsets[k]
        log.msg("Tracking %d observations, pruned %d" % (len(self._parsets), len(pruneable)))

        pruneable = []
        for k, v in self._configs.iteritems():
            if not v or not v.active():
                pruneable.append(k)
        for k in pruneable:
            del self._configs[k]
            del self._configobjs[k]
        log.msg("Tracking %d configurations, pruned %d" % (len(self._configs), len(pruneable)))


def makeService(options):
    acontrol_service = MultiService()
    email = MailNotify(dryrun=False)
    #log.addObserver(email.error)
    worker_service = WorkerService(options, email)
    worker_service.setName("Worker")
    worker_service.setServiceParent(acontrol_service)

    # Slurp up any existing configs
    for file in glob.glob(os.path.join(options['config-dir'], options['config-pattern'])):
        reactor.callWhenRunning(
        worker_service.enqueueConfiguration,
            None, filepath.FilePath(file), None
        )

    # We notify on a file that has been closed in writemode as files are copied
    # over scp, it can take some time for the full file to arrive
    aartfaac_config_service = NotifyService(
        filepath.FilePath(options['config-dir']),
        mask=inotify.IN_CLOSE_WRITE,
        callbacks=[worker_service.enqueueConfiguration]
    )
    aartfaac_config_service.setName("AARTFAAC Config Notifier")
    aartfaac_config_service.setServiceParent(acontrol_service)

    # Slurp up any existing parsets
    for file in glob.glob(os.path.join(options['lofar-dir'], options['lofar-pattern'])):
        reactor.callWhenRunning(
        worker_service.enqueueObservation,
            None, filepath.FilePath(file), None
        )

    # We notify on a file that has been closed in writemode as files are copied
    # over scp, it can take some time for the full file to arrive
    lofar_parset_service = NotifyService(
        filepath.FilePath(options['lofar-dir']),
        mask=inotify.IN_CLOSE_WRITE,
        callbacks=[worker_service.enqueueObservation]
    )
    lofar_parset_service.setName("LOFAR Parset Notifier")
    lofar_parset_service.setServiceParent(acontrol_service)

    return acontrol_service
