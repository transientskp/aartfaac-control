from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols import basic
from twisted.python import log
import signal

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
            wp = WriteProcessProtocol(self.factory.cmd[0], self.factory.config['logdir'])
            wp.dstarted.addCallback(self.sendSuccess)
            self.factory.spawner(wp, self.factory.cmd[0], self.factory.cmd + argv.split(), env=self.factory.env)
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
