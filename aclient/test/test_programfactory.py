from twisted.test import proto_helpers
from twisted.trial import unittest

from aclient.service import ProgramFactory
from aclient.controlprotocol import ControlProtocol

class ProgramFactoryTestCase(unittest.TestCase):
    def setUp(self):
        factory = ProgramFactory({'logdir':'/tmp'})
        factory.protocol = ControlProtocol
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_start(self):
        self.assertRaises(NotImplementedError, self.proto.dataReceived, '0 START\n')

    def test_wrongversion(self):
        self.proto.dataReceived('X START\n')
        self.assertEqual(self.tr.value(), 'NOK')

    def test_invalidcmd(self):
        self.proto.dataReceived('0 WRONG\n')
        self.assertEqual(self.tr.value(), 'NOK')

    def test_stop(self):
        self.assertRaises(NotImplementedError, self.proto.dataReceived, '0 STOP\n')

if __name__ == "__main__":
	unittest.main()