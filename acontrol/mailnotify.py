import smtplib
import re
import StringIO
import zipfile
from os.path import basename
import mimetypes

from twisted.python import log
from email import Encoders
from email.Message import Message
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText


COMMASPACE = ', '
class MailNotify:
    FROM = "acontrol@mcu001.control.lofar"
    def __init__(self, mail_file='maillist.txt', dryrun=False):
        self._mail_file = mail_file
        self._mail_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')
        self.dryrun = dryrun


    def send(self, subject, body, files=None, server="127.0.0.1"):
        """
        Sends a standard email with a subject, body and potential attachments
        """
        maillist = filter(self.address, open(self._mail_file, 'r').read().split("\n"))
        msg = MIMEMultipart()
        msg['From']=MailNotify.FROM
        msg['To']=COMMASPACE.join(maillist)
        msg['Subject']=subject
        msg.attach(MIMEText(body))

        if files:
            zipped = StringIO.StringIO()
            zf = zipfile.ZipFile(zipped, 'w', zipfile.ZIP_DEFLATED)
            
            for filename in files:
                f = open(filename, 'r')
                zf.writestr(basename(filename), f.read())
                f.close()

            part = MIMEBase('application', "octed-stream")
            zf.close()
            part.set_payload(zipped.getvalue())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="parsets.zip"')
            msg.attach(part)
            zipped.close()

        if not self.dryrun:
            try:
                smtp = smtplib.SMTP(server)
                smtp.sendmail(MailNotify.FROM, maillist, msg.as_string())
                smtp.close()
            except:
                log.msg("\n\nSubject: %s\n\n%s\n\n" % (subject, body))
        else:
            log.msg("\n\nSubject: %s\n\n%s\n\n" % (subject, body))


    def error(self, msg):
        """
        We hook this method to the twisted log such that we get the error dict
        See http://twistedmatrix.com/documents/11.1.0/core/howto/logging.html#auto4
        """
        if msg.has_key('failure'):
            self.send("Processing Error", msg['failure'].getErrorMessage())
        else:
            self.send("Processing Error", str(msg))


    def address(self, addr):
        return self._mail_regex.match(addr)



class MailLog:
    def __init__(self):
        self._lines = []

    def _generate(self, t, name, msg, argv):
        s = "    [-] "
        if t:
            s = "    [+] "

        a = argv.split()
        prefix = ""
        for c in a[0]:
            if c.isalnum():
                break
            prefix += c

        args = "        "
        for w in a:
            if w.startswith(prefix):
                args += "\n        " + w
            else:
                args += " " + w

        s += name.upper() + " " + msg + args + "\n"
        return s


    def i(self, name, msg, argv):
        s = self._generate(True, name, msg, argv)
        self._lines.append(s)


    def e(self, name, msg, argv):
        s = self._generate(False, name, msg, argv)
        self._lines.append(s)


    def m(self, s):
        self._lines.append(s)


    def flush(self):
        msg = "\n".join(self._lines)
        del self._lines[:]
        return msg

try:
    mlog
except NameError:
    mlog = MailLog()
