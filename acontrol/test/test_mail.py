import unittest
import os

from acontrol.mailnotify import MailNotify

class MailNotifyTestCase(unittest.TestCase):
  def setUp(self):
    self.fname = '/tmp/maillist.txt'
    f = open(self.fname, 'w')
    f.write('test1@test.com\n')
    f.write('test2@test.com\n')
    f.close()
    self.email = MailNotify(self.fname)

  def tearDown(self):
    os.remove(self.fname)

  def test_mail(self):
    self.email.send("test", "acontrol unittest", True)

if __name__ == "__main__":
  unittest.main()
