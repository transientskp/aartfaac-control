from twisted.internet import reactor
from twisted.test import proto_helpers
from twisted.trial import unittest
import os

from aclient.service import *
from aclient.controlprotocol import ControlProtocol, ControlFactory

def spawner(a, b, c, env):
    pass

class ControlTestCase(unittest.TestCase):
    def setUp(self):
        self.options = Options()
        self.options.parseOptions(['--logdir', '/tmp', '--program', 'pipeline'])
        self.factory = ControlFactory(self.options, ['ls'], os.environ, spawner)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def _make_service(self):
        return makeService(self.options)


    def test_make_service(self):
        service = self._make_service()

    def test_wrongversion(self):
        self.proto.dataReceived('X START\n')
        self.assertEqual(self.tr.value().split()[0], 'NOK')

    def test_invalidcmd(self):
        self.proto.dataReceived('{} WRONG\n'.format(ControlProtocol.VERSION))
        self.assertEqual(self.tr.value().split()[0], 'NOK')

    def test_start(self):
        self.proto.dataReceived('{} START\n'.format(ControlProtocol.VERSION))

    def test_stop(self):
        self.proto.dataReceived('{} STOP\n'.format(ControlProtocol.VERSION))
        self.assertTrue("NOK" in self.tr.value())

if __name__ == "__main__":
	unittest.main()
