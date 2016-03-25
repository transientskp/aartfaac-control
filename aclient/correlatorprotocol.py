import os
import signal

from twisted.internet import reactor

from aclient.controlprotocol import ControlProtocol
from aclient.writeprocessprotocol import WriteProcessProtocol

class CorrelatorProtocol(ControlProtocol):
    process = None
    env = {'DISPLAY':':0', 'GPU_FORCE_64BIT_PTR':'1', 'PLATFORM':'AMD Accelerated Parallel Processing', 'TYPE':'GPU'}
    def start(self, argv):
        if not CorrelatorProtocol.process or not CorrelatorProtocol.process.is_running:
            print "Starting correlator with args: {}".format(argv)
            cmd = ['numactl', '-i',  '0-1', '/home/romein/projects/Triple-A/AARTFAAC/installed/AARTFAAC'] + argv.split()
            CorrelatorProtocol.process = WriteProcessProtocol('correlator', self.factory.config['logdir'])
            reactor.spawnProcess(CorrelatorProtocol.process, cmd[0], cmd, env=CorrelatorProtocol.env)
        else:
            print "Error: Correlator is already running, stop first"

    def stop(self):
        try:
            if CorrelatorProtocol.process and CorrelatorProtocol.process.is_running:
                CorrelatorProtocol.process.transport.signalProcess(signal.SIGTERM)
            else:
                print "Error: Process already exited"
        except OSError as e:
            print "Error: Unable to kill {}".format(CorrelatorProtocol.process.pid)
