from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols import basic
from twisted.python import log
import signal
import os

from aclient.writeprocessprotocol import WriteProcessProtocol

class ControlProtocol(basic.LineReceiver):
    """This abstract protocol handles acontrol messages"""
    VERSION = '0'
    process = None

    def __init__(self, factory):
        self.delimiter = b'\n'
        self.factory = factory

    
    def lineReceived(self, line):
        split = line.split()

        if len(split) < 2 or ControlProtocol.VERSION != split[0]:
            log.err("Invalid protocol version")
            self.sendFailure("Invalid protocol version")
            return

        log.msg("Received command {}".format(split[1]))
        if split[1] == "START":
            self.start(" ".join(split[2:]))
        elif split[1] == "STOP":
            self.stop()
        else:
            log.err("Invalid command")
            self.sendFailure("Invalid command")
            

    def sendSuccess(self, result):
        self.sendLine('OK %s' % (result))


    def sendFailure(self, result):
        self.sendLine('NOK %s' % (result))


    def connectionLost(self, reason):
        log.msg("Disconnected, reason: {}".format(reason.getErrorMessage()))


    def connectionMade(self):
        log.msg("Connected to '{}'".format(self.transport.getPeer()))


    def start(self, argv):
        if not ControlProtocol.process or not ControlProtocol.process.is_running:
            process_name = os.path.basename(self.factory.cmd[0])
            wp = WriteProcessProtocol(process_name, self.factory.config['logdir'])
            wp.dstarted.addCallback(self.sendSuccess)
            cmd = self.factory.cmd
            if len(self.factory.config["numactl"]) > 0:
                cmd = ['numactl'] + self.factory.config['numactl'].split() + cmd
            self.factory.spawner(wp, cmd[0], cmd + argv.split(), env=self.factory.env)
            ControlProtocol.process = wp
        else:
            self.sendFailure("Still running")


    def stop(self):
        try:
            if ControlProtocol.process and ControlProtocol.process.is_running:
                ControlProtocol.process.dstopped.addCallback(self.sendSuccess)
                ControlProtocol.process.transport.signalProcess(signal.SIGTERM)
            else:
                self.sendFailure("Process already exited")
        except OSError as e:
            self.sendFailure("%s (%i)" % (e, ControlProtocol.process.pid))



class ControlFactory(protocol.ServerFactory):
    """Our own program factory that allows us to pass config"""
    def __init__(self, config, cmd, env, spawner=reactor.spawnProcess):
        self.config = config
        self.cmd = cmd
        self.env = env
        self.spawner = spawner

    def buildProtocol(self, addr):
        p = ControlProtocol(self)
        return p
