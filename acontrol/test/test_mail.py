import unittest
import textwrap
import tempfile
import smtplib
import os

from acontrol.mailnotify import *

class MailNotifyTestCase(unittest.TestCase):
    def setUp(self):
        self.file1 = tempfile.NamedTemporaryFile(mode='w')
        self.file2 = tempfile.NamedTemporaryFile(mode='w')
        self.file1.write('Random content\nfile 1.')
        self.file2.write('Random content\nfile 2.')
        self.file1.flush()
        self.file2.flush()
        self.mail_file = tempfile.NamedTemporaryFile(mode='w')
        self.mail_file.write('folkerthuizinga@gmail.com\n')
        self.mail_file.flush()
        self.email = MailNotify(self.mail_file.name, dryrun=True)

    def tearDown(self):
        self.mail_file.close()
        self.file1.close()
        self.file2.close()

    def test_mail(self):
        self.email.send("test", "acontrol unittest", files=[self.file1.name, self.file2.name])

    def test_layout(self):
        mlog.m("subject\n")
        mlog.i("a", "x", "-x 1 -y 2")
        mlog.e("b", "x", "-x 1 -y 2")
        self.assertEqual(type(mlog.flush()), str)

if __name__ == "__main__":
    unittest.main()
