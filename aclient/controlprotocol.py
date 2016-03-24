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
            self.transport.write('NOK')
            return

        print "Received command {}".format(split[1])
        if split[1] == "START":
            self.start(" ".join(split[2:]))
            self.transport.write('OK')
        elif split[1] == "STOP":
            self.stop()
            self.transport.write('OK')
        else:
            print "Invalid command"
            self.transport.write('NOK')

    def connectionLost(self, reason):
        print "Disconnected, reason: {}".format(reason.getErrorMessage())

    def connectionMade(self):
        print "Connected to '{}'".format(self.transport.getPeer())

    def start(self, args):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError
