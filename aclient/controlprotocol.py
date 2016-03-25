from twisted.protocols import basic

class ControlProtocol(basic.LineReceiver):
    """This abstract protocol handles acontrol messages"""
    VERSION = '0'

    def __init__(self):
        self.delimiter = b'\n'
    
    def lineReceived(self, line):
        split = line.split()

        if ControlProtocol.VERSION != split[0] or len(split) < 2:
            print "Error: Invalid protocol version"
            self.sendFailure()
            return

        print "Received command {}".format(split[1])
        if split[1] == "START":
            self.start(" ".join(split[2:]))
        elif split[1] == "STOP":
            self.stop()
        else:
            print "Invalid command"
            self.sendFailure()
            
    def sendSuccess(self):
        self.transport.write('OK')

    def sendFailure(self):
        self.transport.write('NOK')

    def connectionLost(self, reason):
        print "Disconnected, reason: {}".format(reason.getErrorMessage())

    def connectionMade(self):
        print "Connected to '{}'".format(self.transport.getPeer())

    def start(self, argv):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError
