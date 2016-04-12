from twisted.internet import defer
from twisted.test import proto_helpers
from twisted.trial import unittest

from acontrol.controlprotocol import ControlProtocol, ControlFactory

class ControlTestCase(unittest.TestCase):
    def setUp(self):
        self.d = defer.Deferred()
        factory = ControlFactory('test', '--help', self.d, True)
        factory.protocol = ControlProtocol
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_start(self):
        self.assertEqual('0 START %s\n' % self.proto.factory.argv, self.tr.value())

        def cb(result):
            self.assertTrue(result)

        self.d.addCallback(cb)
        self.proto.dataReceived('OK\n')
        return self.d


if __name__ == "__main__":
	unittest.main()
