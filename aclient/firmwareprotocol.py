import os
import signal

from twisted.internet import reactor
from twisted.python import log

from aclient.controlprotocol import ControlProtocol
from aclient.writeprocessprotocol import WriteProcessProtocol

class FirmwareProtocol(ControlProtocol):
    process = None
    def start(self, argv):
        if not FirmwareProtocol.process or not FirmwareProtocol.process.is_running:
            log.msg("Starting firmware reset with args: {}".format(argv))
            cmd = ["%s/reset.sh" % (os.environ['HOME'])] + argv.split()
            FirmwareProtocol.process = WriteProcessProtocol(cmd[0], self.factory.config['logdir'])
            reactor.spawnProcess(FirmwareProtocol.process, cmd[0], cmd, env=os.environ)
            self.sendSuccess()
        else:
            log.err("Firmware reset already running, stop first")
            self.sendFailure()

    def stop(self):
        try:
            if FirmwareProtocol.process and FirmwareProtocol.process.is_running:
                FirmwareProtocol.process.transport.signalProcess(signal.SIGTERM)
                self.sendSuccess()
            else:
                log.err("Process already exited")
                self.sendFailure()
        except OSError as e:
            log.err("Unable to kill {}".format(FirmwareProtocol.process.pid))
            self.sendFailure()
