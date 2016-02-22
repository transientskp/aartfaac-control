import smtplib
import re
from os.path import basename
import mimetypes

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
    def __init__(self, mail_file='maillist.txt'):
        self._mail_file = mail_file
        self._mail_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')


    def send(self, subject, body, files=None, server="127.0.0.1", dryrun=False):
        """
        Sends a standard email with a subject, body and potential attachments
        """
        maillist = filter(self.address, open(self._mail_file, 'r').read().split("\n"))
        msg = MIMEMultipart(
            From=MailNotify.FROM,
            To=COMMASPACE.join(maillist),
            Subject=subject
        )
        msg.attach(MIMEText(body))

        for f in files or []:
            fil = open(f, "rb")
            msg.attach(MIMEApplication(
                fil.read(),
                Content_Disposition='attachment; filename="%s"' % basename(f)
            ))
            close(fil)

        if not dryrun:
            smtp = smtplib.SMTP(server)
            smtp.sendmail(MailNotify.FROM, maillist, msg.as_string())
            smtp.close()


    def error(self, msg):
        """
        We hook this method to the twisted log such that we get the error dict
        See http://twistedmatrix.com/documents/11.1.0/core/howto/logging.html#auto4
        """
        if msg['isError']:
          if msg.has_key('failure'):
            self.send("Processing Error", str(msg))
          else:
            self.send("Processing Error", str(msg))


    def address(self, addr):
        return self._mail_regex.match(addr)
