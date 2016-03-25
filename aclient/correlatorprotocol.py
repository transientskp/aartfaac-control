import os
import signal

from twisted.internet import reactor
from twisted.python import log

from aclient.controlprotocol import ControlProtocol
from aclient.writeprocessprotocol import WriteProcessProtocol

class CorrelatorProtocol(ControlProtocol):
    process = None
    env = {'DISPLAY':':0', 'GPU_FORCE_64BIT_PTR':'1', 'PLATFORM':'AMD Accelerated Parallel Processing', 'TYPE':'GPU'}
    def start(self, argv):
        if not CorrelatorProtocol.process or not CorrelatorProtocol.process.is_running:
            log.msg("Starting correlator with args: {}".format(argv))
            cmd = ['numactl', '-i',  '0-1', '/home/romein/projects/Triple-A/AARTFAAC/installed/AARTFAAC'] + argv.split()
            CorrelatorProtocol.process = WriteProcessProtocol('correlator', self.factory.config['logdir'])
            reactor.spawnProcess(CorrelatorProtocol.process, cmd[0], cmd, env=CorrelatorProtocol.env)
            self.sendSuccess()
        else:
            log.err("Correlator is already running, stop first")
            self.sendFailure()

    def stop(self):
        try:
            if CorrelatorProtocol.process and CorrelatorProtocol.process.is_running:
                CorrelatorProtocol.process.transport.signalProcess(signal.SIGTERM)
                self.sendSuccess()
            else:
                log.err("Process already exited")
                self.sendFailure()
        except OSError as e:
            log.err("Unable to kill {}".format(CorrelatorProtocol.process.pid))
            self.sendFailure()
