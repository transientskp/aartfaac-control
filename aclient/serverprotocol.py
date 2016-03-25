import os
import signal

from twisted.internet import reactor

from aclient.controlprotocol import ControlProtocol
from aclient.writeprocessprotocol import WriteProcessProtocol

class ServerProtocol(ControlProtocol):
    process = None
    def start(self, argv):
        if not ServerProtocol.process or not ServerProtocol.process.is_running:
            print "Starting server with args: {}".format(argv)
            cmd = ["start_server.py"] + argv.split()
            ServerProtocol.process = WriteProcessProtocol(cmd[0], self.factory.config['logdir'])
            reactor.spawnProcess(ServerProtocol.process, cmd[0], cmd, env=os.environ)
            self.sendSuccess()
        else:
            print "Error: Server is already running, stop first"
            self.sendFailure()

    def stop(self):
        try:
            if ServerProtocol.process and ServerProtocol.process.is_running:
                ServerProtocol.process.transport.signalProcess(signal.SIGTERM)
                self.sendSuccess()
            else:
                print "Error: Process already exited"
                self.sendFailure()
        except OSError as e:
            print "Error: Unable to kill {}".format(ServerProtocol.process.pid)
            self.sendFailure()
