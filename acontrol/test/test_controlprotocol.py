from twisted.internet import defer
from twisted.test import proto_helpers
from twisted.trial import unittest

from acontrol.controlprotocol import ControlProtocol, ControlFactory

class ControlTestCase(unittest.TestCase):
    def setUp(self):
        self.d = defer.Deferred()
        factory = ControlFactory('test', '--help', self.d)
        factory.protocol = ControlProtocol
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_start(self):
        self.proto.start()
        self.assertEqual('0 START %s\n' % self.proto.factory.argv, self.tr.value())

        def cb((name, success)):
            self.assertTrue(success)

        self.d.addCallback(cb)
        self.proto.dataReceived('OK\n')
        return self.d

    def test_stop(self):
        self.proto.stop()
        self.assertEqual('0 STOP\n', self.tr.value())

        def cb((name, failure)):
            self.assertFalse(failure)

        self.d.addCallback(cb)
        self.proto.dataReceived('NOK\n')
        return self.d

    def test_stop(self):
        self.proto.dataReceived('WRONG\n')
        return self.assertFailure(self.d, RuntimeError)


if __name__ == "__main__":
	unittest.main()
