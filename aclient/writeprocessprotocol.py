import os

from twisted.internet import protocol

class WriteProcessProtocol(protocol.ProcessProtocol):
    """This process protocol writes stderr,stdout to file for some process"""
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.is_running = False

    def connectionMade(self):
        self.is_running = True
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
        self.filestdout.flush()

    def processEnded(self, status):
        self.is_running = False
        rc = status.value.exitCode
        self.filestderr.close()
        self.filestdout.close()
        print "Ended {}({}) with exit code {}".format(self.name, self.pid, rc)
