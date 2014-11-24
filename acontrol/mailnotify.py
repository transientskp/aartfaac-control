import smtplib
from email.MIMEText import MIMEText

FROM = "acontrol@mcu001.control.lofar"
TO = "folkerthuizinga@gmail.com"

class MailNotify:
    def __init__(self, mfrom=FROM, mto=TO):
        self.mail_from = mfrom
        self.mail_to = mto

    def send(self, subject, msg):
        """
        Sends a standard email with a subject and msg
        """
        mail = MIMEText(msg)
        mail['Subject'] = subject
        mail['From'] = self.mail_from
        mail['To'] = self.mail_to
        s = smtplib.SMTP()
        s.connect()
        s.sendmail(self.mail_from, [self.mail_to], mail.as_string())
        s.close()

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
