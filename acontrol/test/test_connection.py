import unittest

from acontrol.connection import Connection

class ConnectionTestCase(unittest.TestCase):
  CMD = "ls"
  def setUp(self):
    self.conn = Connection('localhost')

  def tearDown(self):
    for v in self.conn.itervalues():
      self.conn.stop_program(v)

  def test_cmd(self):
    self.conn.start_program(cmd)
    self.assertTrue(self.conn.channels.has_key(cmd))
    self.conn.stop_program(cmd)
    self.assertFalse(self.conn.channels.has_key(cmd))


if __name__ == "__main__":
  unittest.main()

