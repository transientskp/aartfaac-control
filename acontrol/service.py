import os
import fnmatch
import time, datetime
import glob

from acontrol.observation import Observation
from acontrol.controlprotocol import ControlProtocol, ControlFactory
from acontrol.configuration import Configuration
from acontrol.mailnotify import *
from acontrol.test.example_config import EXAMPLE_CONFIG

from twisted.internet import reactor
from twisted.internet import inotify
from twisted.internet import protocol
from twisted.internet import defer
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.task import LoopingCall
from twisted.python import filepath
from twisted.python import usage
from twisted.python import log
from twisted.application.service import Service, MultiService

FIVE_MINUTES = 300
SECONDS_IN_DAY = 86400
US_IN_SECOND = 1e6

def connect(name, host, port, argv, start):
    d = defer.Deferred()
    f = ControlFactory(name, argv, d, start)
    reactor.connectTCP(host, port, f)
    return d


def call_at(start_datetime, f, *args, **kwargs):
    """
    Run f(*args, **kwargs) at datetime.
    """
    delta = start_datetime - datetime.datetime.now()
    seconds_ahead = delta.days * SECONDS_IN_DAY + delta.seconds + delta.microseconds / US_IN_SECOND
    if seconds_ahead > 0:
        log.msg("AARTFAAC config update in %d seconds" % (seconds_ahead))
        return reactor.callLater(seconds_ahead, f, *args, **kwargs)
    else:
        log.msg("Not scheduling; config is in the past")
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
        return reactor.callWhenRunning(f, *args, **kwargs)
    else:
        log.msg("Not scheduling; Obs in the past or too short")

    return None


class Options(usage.Options):
    optParameters = [
        ["lofar-dir", None, "/opt/lofar/var/run", "Directory to monitor for lofar parsets"],
        ["lofar-pattern", None, "MCU001*", "Glob lofar pattern to select usable parsets"],
        ["config-dir", None, "/opt/aartfaac/var/run", "Directory to monitor for lofar parsets"],
        ["config-pattern", None, "AARTFAAC*", "Glob aartfaac pattern to select usable parsets"],
        ["maillist", "m", "maillist.txt", "Textfile with email addresses, one per line"]
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
        self._prune_call = LoopingCall(self.prune)
        self._fnpattern = options['lofar-pattern']
        self._aapattern = options['config-pattern']
        self._email = email
        self._cfg_file = open(options['config-dir'] + '/AARTFAAC:000000.json', 'w')
        self._cfg_file.write(config)
        self._cfg_file.seek(0)
        self._activeconfig = Configuration(self._cfg_file.name)


    def startService(self):
        self._available = True
        self._prune_call.start(self.PRUNE_TIME)


    def stopService(self):
        # Shut down any processing in progress...
        self._available = False
        self._prune_call.stop()
        self._cfg_file.close()


    def processObservation(self, obs, connector=connect):
        """
        Start a pipeline to process the observation
        """
        if self._available and obs.is_valid():
            global g_email_bdy
            g_email_bdy = "Using aartfaac configuration `%s'\n\n" % (self._activeconfig.filepath)

            def start_clients(result, V):
                if not result:
                    return False
                l = [connector(*v, start=True) for v in V]
                return defer.DeferredList(l, fireOnOneCallback=True, consumeErrors=True)

            def success(result):
                global g_email_hdr, g_email_bdy
                s = True
                for v in result:
                    s = s and v[1][0]

                if s:
                    g_email_hdr = "[+] %s" % (obs)
                else:
                    g_email_hdr = "[-] %s" % (obs)

                reactor.callLater(10, self._email.send, g_email_hdr, g_email_bdy, [obs.filepath, self._activeconfig.filepath])


            atv = connector(*self._activeconfig.atv(obs), start=True)
            server = connector(*self._activeconfig.server(obs), start=True)
            correlator = defer.DeferredList([atv,server], consumeErrors=True)
            server.addCallback(start_clients, self._activeconfig.pipelines(obs))
            correlator.addCallback(start_clients, [self._activeconfig.correlator(obs)])
            result = defer.DeferredList([server,correlator], consumeErrors=True)
            result.addCallback(success)
        else:
            log.msg("Skipping %s" % (obs))


    def enqueueObservation(self, ignored, filepath, mask):
        """
        Parse files matching the glob pattern and create future call
        """
        call = None
        if fnmatch.fnmatch(filepath.basename(), self._fnpattern):
            obs = Observation(filepath.path)
            call = call_at_to(
                obs.start_time - datetime.timedelta(seconds=self.PRE_TIME),
                obs.end_time,
                self.processObservation,
                obs
            )

        if call and filepath.path in self._parsets and self._parsets[filepath.path].active():
            log.msg("Rescheduling observation %s" % (filepath.path))
            self._parsets[filepath.path].cancel()
            self._parsets[filepath.path] = call
        elif call and filepath.path not in self._parsets:
            log.msg("Scheduling observation %s" % (filepath.path))
            self._parsets[filepath.path] = call
        else:
            log.msg("Ignoring %s" %(filepath.path))


    def applyConfiguration(self, config):
        """
        Prepare AARTFAAC telescope for upcomming observations
        """
        if config.is_valid():
            self._activeconfig = config
            # TODO: Implement setstations()
            # self._activeconfig.setstations(obs)
            log.msg("Set AARTFAAC configuration to %s" % (config))
        else:
            log.msg("Invalid config: %s" % config)


    def enqueueConfiguration(self, ignored, filepath, mask):
        """
        Parse files matching the glob pattern and create future call
        """
        call = None
        if fnmatch.fnmatch(filepath.basename(), self._aapattern):
            cfg = Configuration(filepath.path)
            call = call_at(
                cfg.start_time - datetime.timedelta(seconds=self.PRE_TIME),
                self.applyConfiguration,
                cfg
            )

        if call and filepath.path in self._configs and self._configs[filepath.path].active():
            log.msg("Rescheduling config update %s" % (filepath.path))
            self._configs[filepath.path].cancel()
            self._configs[filepath.path] = call
        elif call and filepath.path not in self._configs:
            log.msg("Scheduling config update %s" % (filepath.path))
            self._configs[filepath.path] = call
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
        log.msg("Tracking %d configurations, pruned %d" % (len(self._configs), len(pruneable)))


def makeService(options):
    acontrol_service = MultiService()
    email = MailNotify(options['maillist'], True)
    log.addObserver(email.error)
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
