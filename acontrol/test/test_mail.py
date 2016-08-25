import unittest
import textwrap
import tempfile
import smtplib
import os

from acontrol.mailnotify import *

class MailNotifyTestCase(unittest.TestCase):
    def setUp(self):
        self.email = MailNotify(dryrun=True)
        self.email.updatelist(["test1@uva.nl", "test2@uva.nl"])
        self.file = tempfile.NamedTemporaryFile(mode='w')
        self.file.write('junk data')

    def tearDown(self):
        self.file.close()

    def test_mail(self):
        self.email.send("test", "acontrol unittest", files=[self.file.name])

    def test_layout(self):
        mlog.m("subject\n")
        mlog.i("a", "x", "-x 1 -y 2")
        mlog.e("b", "x", "-x 1 -y 2")
        self.assertEqual(type(mlog.flush()), str)

if __name__ == "__main__":
    unittest.main()
