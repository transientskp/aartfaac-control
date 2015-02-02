import smtplib
from email.MIMEText import MIMEText

FROM = "acontrol@mcu001.control.lofar"

class MailNotify:
    def __init__(self, mailfile='maillist.txt', mfrom=FROM):
        self.mail_from = mfrom
        self.filename = mailfile

    def send(self, subject, msg, dryrun=False):
        """
        Sends a standard email with a subject and msg
        """
        mail = MIMEText(msg)
        mail['Subject'] = subject
        mail['From'] = self.mail_from
        f = open(self.filename)
        mailto = filter(self.address, f.read().split('\n'))
        mail['To'] = ', '.join(mailto)

        if dryrun:
            print mail
        else:
            s = smtplib.SMTP()
            s.connect()
            s.sendmail(self.mail_from, mailto, mail.as_string())
            s.close()


    def error(self, msg, dryrun=False):
        """
        We hook this method to the twisted log such that we get the error dict
        See http://twistedmatrix.com/documents/11.1.0/core/howto/logging.html#auto4
        """
        if msg['isError']:
          if msg.has_key('failure'):
            self.send("Processing Error", str(msg), dryrun)
          else:
            self.send("Processing Error", str(msg), dryrun)

    def address(self, addr):
        return len(addr) > 0 and '@' in addr
