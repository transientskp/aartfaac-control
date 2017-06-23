import os
import signal
import tempfile

from twisted.test import proto_helpers
from twisted.trial import unittest
from twisted.internet import reactor

from aclient.writeprocessprotocol import WriteProcessProtocol

class WriteProcessTestCase(unittest.TestCase):
    def setUp(self):
        self.cmd = ['python', '--version']
        self.proto = WriteProcessProtocol('python', '.')

    def test_init(self):
        self.assertFalse(self.proto.is_running)

    def test_run_process(self):
        def result(r):
            self.assertTrue(type(r) == str)

        def stop(r):
            self.assertTrue(self.proto.is_running)
            self.assertTrue(type(r) == str)

        self.proto.dstopped.addCallback(result)
        self.proto.dstarted.addCallback(stop)
        reactor.spawnProcess(self.proto, self.cmd[0], self.cmd)
        return self.proto.dstopped

if __name__ == "__main__":
	unittest.main()
