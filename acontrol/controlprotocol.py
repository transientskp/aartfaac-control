from twisted.protocols import basic
from twisted.python import log
from twisted.internet import defer

class ControlProtocol(basic.LineReceiver):
    """This protocol handles aclient messages"""
    VERSION = '0'

    def __init__(self):
        self.delimiter = b'\n'
        self.d = defer.Deferred()

    def lineReceived(self, line):
        split = line.split()

        if len(split) < 2 or ControlProtocol.VERSION != split[0]:
            log.err("Invalid protocol version")
            return

        log.msg("Received status '%s'" % split[1])
        if split[1] == "OK":
            self.d.callback(line)
        else split[1] == "NOK":
            self.d.errback(line)

    def start(self, argv=""):
        self.sendLine('%s START %s' % (ControlProtocol.VERSION, argv))

    def stop(self):
        self.sendLine('%s STOP' % (ControlProtocol.VERSION))

    def connectionLost(self, reason):
        log.msg("Disconnected, reason: %s" % (reason.getErrorMessage()))

    def connectionMade(self):
        log.msg("Connected to '%s'" % (self.transport.getPeer()))

