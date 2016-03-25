import os
import signal

from twisted.internet import reactor

from aclient.controlprotocol import ControlProtocol
from aclient.writeprocessprotocol import WriteProcessProtocol

class AtvProtocol(ControlProtocol):
    process = None
    def start(self, argv):
        if not AtvProtocol.process or not AtvProtocol.process.is_running:
            print "Starting atv with args: {}".format(argv)
            cmd = ["atv.py"] + argv.split()
            AtvProtocol.process = WriteProcessProtocol(cmd[0], self.factory.config['logdir'])
            reactor.spawnProcess(AtvProtocol.process, cmd[0], cmd, env=os.environ)
            self.sendSuccess()
        else:
            print "Error: Atv is already running, stop first"
            self.sendFailure()

    def stop(self):
        try:
            if AtvProtocol.process and AtvProtocol.process.is_running:
                AtvProtocol.process.transport.signalProcess(signal.SIGTERM)
                self.sendSuccess()
            else:
                print "Error: Process already exited"
                self.sendFailure()
        except OSError as e:
            print "Error: Unable to kill {}".format(AtvProtocol.process.pid)
            self.sendFailure()
