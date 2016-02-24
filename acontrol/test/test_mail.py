import unittest
import tempfile
import os

from acontrol.mailnotify import MailNotify

class MailNotifyTestCase(unittest.TestCase):
    def setUp(self):
        self.file1 = tempfile.NamedTemporaryFile(mode='w')
        self.file2 = tempfile.NamedTemporaryFile(mode='w')
        self.file1.write('Random content\nfile 1.')
        self.file2.write('Random content\nfile 2.')
        self.file1.flush()
        self.file2.flush()
        self.mail_file = tempfile.NamedTemporaryFile(mode='w')
        self.mail_file.write('f.huizinga@uva.nl\n')
        self.mail_file.flush()
        self.email = MailNotify(self.mail_file.name)

    def tearDown(self):
        self.mail_file.close()

    def test_mail(self):
        self.email.send("test", "acontrol unittest", files=[self.file1.name, self.file2.name], dryrun=True)

if __name__ == "__main__":
    unittest.main()
