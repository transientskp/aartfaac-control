from twisted.protocols import basic
from twisted.internet import protocol
from twisted.python import log

class ControlProtocol(basic.LineReceiver):
    """This protocol handles aclient messages"""
    VERSION = '0'

    def __init__(self):
        self.delimiter = b'\n'

    def connectionMade(self):
        self.start()

    def connectionLost(self, reason):
        log.msg("Lost connection")

    def lineReceived(self, line):
        split = line.split()

        if split[0] == "OK":
            self.factory.defer.callback((self.factory.name, True))
        elif split[0] == "NOK":
            self.factory.defer.callback((self.factory.name, False))
        else:
            self.factory.defer.errback(RuntimeError("Invalid status"))

    def start(self):
        log.msg("Starting `%s' with arguments: %s" % (self.factory.name, self.factory.argv))
        self.sendLine('%s START %s' % (ControlProtocol.VERSION, self.factory.argv))

    def stop(self):
        log.msg("Stopping `%s'", self.factory.name)
        self.sendLine('%s STOP' % (ControlProtocol.VERSION))


class ControlFactory(protocol.ClientFactory):
    """Persistent information for our protocol"""
    def __init__(self, name, argv, defer):
        self.name = name
        self.argv = argv
        self.defer = defer

    def buildProtocol(self, addr):
        p = ControlProtocol()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        log.err("Connection lost, reason: %s" % reason)

    def clientConnectionFailed(self, connector, reason):
        log.err("Connection failed, reason: %s" % reason)

