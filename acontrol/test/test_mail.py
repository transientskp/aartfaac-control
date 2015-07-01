import unittest
import tempfile
import os

from acontrol.mailnotify import MailNotify

class MailNotifyTestCase(unittest.TestCase):
    def setUp(self):
        self.mail_file = tempfile.NamedTemporaryFile(mode='w')
        self.mail_file.write('test1@test.com\n')
        self.mail_file.write('test2@test.com\n')
        self.mail_file.flush()
        self.email = MailNotify(self.mail_file.name)

    def tearDown(self):
        self.mail_file.close()

    def test_mail(self):
        self.email.send("test", "acontrol unittest", True)

if __name__ == "__main__":
    unittest.main()
