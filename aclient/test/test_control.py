from twisted.internet import reactor
from twisted.test import proto_helpers
from twisted.trial import unittest
import os

from aclient.service import Options
from aclient.controlprotocol import ControlProtocol, ControlFactory

class ControlTestCase(unittest.TestCase):
    def setUp(self):
        self.options = Options()
        self.options.parseOptions(['--logdir', '/tmp'])
        factory = ControlFactory(self.options, ['ls'], os.environ)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_wrongversion(self):
        self.proto.dataReceived('X START\n')
        self.assertEqual(self.tr.value().split()[0], 'NOK')

    def test_invalidcmd(self):
        self.proto.dataReceived('{} WRONG\n'.format(ControlProtocol.VERSION))
        self.assertEqual(self.tr.value().split()[0], 'NOK')

if __name__ == "__main__":
	unittest.main()
