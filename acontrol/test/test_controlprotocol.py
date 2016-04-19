from twisted.internet import defer
from twisted.test import proto_helpers
from twisted.trial import unittest

from acontrol.controlprotocol import ControlProtocol, ControlFactory

class ControlTestCase(unittest.TestCase):
    def setUp(self):
        self.d = defer.Deferred()

    def _make_factory(self, start):
        factory = ControlFactory('test', '--help', self.d, start)
        factory.protocol = ControlProtocol
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_start(self):
        self._make_factory(True)
        self.assertEqual('0 START %s\n' % self.proto.factory.argv, self.tr.value())

        def cb(result):
            self.assertEqual(type(result), str)

        self.d.addCallback(cb)
        self.proto.dataReceived('OK\n')
        return self.d

    def test_stop(self):
        self._make_factory(False)
        self.assertEqual('0 STOP\n', self.tr.value())

        def cb(result):
            self.assertEqual(type(result), str)

        self.d.addCallback(cb)
        self.proto.dataReceived('OK\n')
        return self.d

    def test_nok(self):
        msg = 'Invalid'
        self._make_factory(True)

        def e(result):
            self.assertEquals(result.getErrorMessage(), msg)

        self.d.addErrback(e)
        self.proto.dataReceived('NOK %s\n' % (msg))
        return self.d


if __name__ == "__main__":
	unittest.main()
