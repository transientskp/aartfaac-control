import os

from twisted.internet import reactor
from twisted.internet import protocol
from twisted.protocols import basic
from twisted.python import usage
from twisted.python import log
from twisted.application.service import Service
from twisted.application.service import MultiService

class WriteProcessProtocol(protocol.ProcessProtocol):
    """This process protocol writes stderr,stdout to file"""
    def __init__(self, name, path):
        self.name = name
        self.path = path
        if not os.path.exists(path):
            print "Created path '{}' for logging process {}".format(path, name)
            os.makedirs(path)

    def connectionMade(self):
        self.pid = self.transport.pid
        filename = os.path.join(self.path, "{}-{}.ERROR".format(self.name, self.pid))
        self.filestderr = open(filename, 'w')
        filename = os.path.join(self.path, "{}-{}.INFO".format(self.name, self.pid))
        self.filestdout = open(filename, 'w')
        print "Started {}({})".format(self.name, self.transport.pid)
        print "  Writing stderr to {}".format(self.filestderr.name)
        print "  Writing stdout to {}".format(self.filestdout.name)

    def outReceived(self, data):
        self.filestdout.write(data)

    def errReceived(self, data):
        print "Error: {}".format(data)
        self.filestderr.write(data)

    def processEnded(self, status):
        rc = status.value.exitCode
        self.filestderr.close()
        self.filestdout.close()
        print "Ended {}({}) with exit code {}".format(self.name, self.pid, rc)


class ControlProtocol(basic.LineReceiver):
    """This abstract protocol handles acontrol messages"""
    VERSION = '0'

    def __init__(self):
        self.delimiter = b'\n'
    
    def lineReceived(self, line):
        split = line.split()

        if ControlProtocol.VERSION != split[0] or len(split) < 2:
            print "Error: Invalid protocol version"
            self.transport.write('NOK')
            return

        print "Received command {}".format(split[1])
        if split[1] == "START":
            self.start(split[2:])
            self.transport.write('OK')
        elif split[1] == "STOP":
            self.stop(split[2:])
            self.transport.write('OK')
        else:
            print "Invalid command"
            self.transport.write('NOK')

    def connectionLost(self, reason):
        print "Disconnected, reason: {}".format(reason.getErrorMessage())

    def connectionMade(self):
        print "Connected to '{}'".format(self.transport.getPeer())

    def start(self, args):
        pass

    def stop(self, args):
        pass


class Options(usage.Options):
    optParameters = [
        ["port", None, 45000, "Port to listen on for incomming connections"],
        ["program", None, None, "Program to start, one of {server, atv, pipeline, correlator}"]
    ]


def makeService(config):
    aclient_service = MultiService()
    factory = protocol.ServerFactory()
    factory.protocol = ControlProtocol
    reactor.listenTCP(config['port'], factory)

    return aclient_service

