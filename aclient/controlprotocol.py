from twisted.protocols import basic
from twisted.python import log

class ControlProtocol(basic.LineReceiver):
    """This abstract protocol handles acontrol messages"""
    VERSION = '0'

    def __init__(self):
        self.delimiter = b'\n'
    
    def lineReceived(self, line):
        split = line.split()

        if len(split) < 2 or ControlProtocol.VERSION != split[0]:
            log.err("Invalid protocol version")
            self.sendFailure()
            return

        log.msg("Received command {}".format(split[1]))
        if split[1] == "START":
            self.start(" ".join(split[2:]))
        elif split[1] == "STOP":
            self.stop()
        else:
            log.err("Invalid command")
            self.sendFailure()
            
    def sendSuccess(self):
        self.sendLine('OK')

    def sendFailure(self):
        self.sendLine('NOK')

    def connectionLost(self, reason):
        log.msg("Disconnected, reason: {}".format(reason.getErrorMessage()))

    def connectionMade(self):
        log.msg("Connected to '{}'".format(self.transport.getPeer()))

    def start(self, argv):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError
