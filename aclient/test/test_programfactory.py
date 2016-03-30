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
        self.assertRaises(NotImplementedError, self.proto.dataReceived, '{} START\n'.format(ControlProtocol.VERSION))

    def test_wrongversion(self):
        self.proto.dataReceived('X START\n')
        self.assertEqual(self.tr.value(), 'NOK\n')

    def test_invalidcmd(self):
        self.proto.dataReceived('{} WRONG\n'.format(ControlProtocol.VERSION))
        self.assertEqual(self.tr.value(), 'NOK\n')

    def test_stop(self):
        self.assertRaises(NotImplementedError, self.proto.dataReceived, '{} STOP\n'.format(ControlProtocol.VERSION))

if __name__ == "__main__":
	unittest.main()
