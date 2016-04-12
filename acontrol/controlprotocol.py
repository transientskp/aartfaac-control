from twisted.protocols import basic
from twisted.internet import protocol
from twisted.python import log

class ControlProtocol(basic.LineReceiver):
    """
    This protocol handles aclient messages
    """
    VERSION = '0'

    def __init__(self):
        self.delimiter = b'\n'


    def connectionMade(self):
        if self.factory.start:
            self.start()
        else:
            self.stop()


    def connectionLost(self, reason):
        log.msg("Lost connection")


    def lineReceived(self, line):
        split = line.split()

        if split[0] == "OK":
            self.factory.defer.callback("Started %s" % (self.factory.name))
        elif split[0] == "NOK":
            self.factory.defer.errback(Exception("Failed to start %s" % (self.factory.name)))
        else:
            self.factory.defer.errback(Exception("Invalid status"))


    def start(self):
        log.msg("Starting `%s' with arguments: %s" % (self.factory.name, self.factory.argv))
        self.sendLine('%s START %s' % (ControlProtocol.VERSION, self.factory.argv))


    def stop(self):
        log.msg("Stopping `%s'", self.factory.name)
        self.sendLine('%s STOP' % (ControlProtocol.VERSION))



class ControlFactory(protocol.ClientFactory):
    """
    Persistent information for our protocol
    """
    def __init__(self, name, argv, defer, start):
        self.name = name
        self.argv = argv
        self.defer = defer
        self.start = start


    def buildProtocol(self, addr):
        p = ControlProtocol()
        p.factory = self
        return p


    def clientConnectionLost(self, connector, reason):
        log.err("Connection lost, reason: %s" % reason)
        self.defer.errback(Exception("Lost connection (%s)" % (self.name)))


    def clientConnectionFailed(self, connector, reason):
        log.err("Connection failed, reason: %s" % reason)
        self.defer.errback(Exception("Failed to connect (%s)" % (self.name)))

