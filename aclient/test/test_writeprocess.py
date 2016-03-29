import os
import signal
import tempfile

from twisted.test import proto_helpers
from twisted.trial import unittest
from twisted.internet import reactor

from aclient.writeprocessprotocol import WriteProcessProtocol

class WriteProcessTestCase(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(mode='w')
        self.cmd = ['tail', '-f', self.test_file.name]
        self.proto = WriteProcessProtocol('tail', '/tmp')

    def test_init(self):
        self.assertFalse(self.proto.is_running)

    def test_running(self):
        p = reactor.spawnProcess(self.proto, self.cmd[0], self.cmd)
        self.assertTrue(self.proto.is_running)
        self.assertTrue(os.path.exists(self.proto.filestdout.name))
        self.assertTrue(os.path.exists(self.proto.filestderr.name))
        p.loseConnection()

if __name__ == "__main__":
	unittest.main()
