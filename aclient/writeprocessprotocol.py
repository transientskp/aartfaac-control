import os
import time

from twisted.internet import protocol
from twisted.internet import defer
from twisted.python import log

class WriteProcessProtocol(protocol.ProcessProtocol):
    """This process protocol writes stderr,stdout to file for some process"""
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.dstarted = defer.Deferred()
        self.dstopped = defer.Deferred()
        self.is_running = False

    def connectionMade(self):
        self.is_running = True
        self.pid = self.transport.pid
        filename = os.path.join(self.path, "{}-{}-{}.ERROR".format(self.name, time.strftime("%Y%m%d%H%M", time.gmtime()), self.pid))
        self.filestderr = open(filename, 'w')
        filename = os.path.join(self.path, "{}-{}-{}.INFO".format(self.name, time.strftime("%Y%m%d%H%M", time.gmtime()), self.pid))
        self.filestdout = open(filename, 'w')
        log.msg("Started {}({})".format(self.name, self.pid))
        log.msg("  Writing stderr to {}".format(self.filestderr.name))
        log.msg("  Writing stdout to {}".format(self.filestdout.name))
        self.dstarted.callback("Started (%d)" % (self.pid))

    def outReceived(self, data):
        self.filestdout.write(data)

    def errReceived(self, data):
        self.filestderr.write(data)

    def processEnded(self, status):
        self.is_running = False
        rc = status.value.exitCode
        self.filestderr.close()
        self.filestdout.close()
        log.msg("Ended {}({}) with exit code {}".format(self.name, self.pid, rc))
        self.dstopped.callback("Ended with exit code ({})".format(rc))
