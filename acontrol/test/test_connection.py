import unittest

from acontrol.connection import Connection

CMD = "ls"

class ConnectionTestCase(unittest.TestCase):
  def setUp(self):
    self.conn = Connection('localhost')

  def tearDown(self):
    for v in self.conn.channels.items():
      self.conn.stop_program(v)

  def test_cmd(self):
    self.conn.start_program(CMD)
    self.assertTrue(self.conn.channels.has_key(CMD))
    self.conn.stop_program(CMD)
    self.assertFalse(self.conn.channels.has_key(CMD))


if __name__ == "__main__":
  unittest.main()

