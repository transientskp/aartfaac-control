import unittest

from acontrol.mailnotify import MailNotify

class MailNotifyTestCase(unittest.TestCase):
  def setUp(self):
    self.email = MailNotify()

  def tearDown(self):
    pass

  def test_mail(self):
    self.email.send("test", "acontrol unittest")

if __name__ == "__main__":
  unittest.main()
