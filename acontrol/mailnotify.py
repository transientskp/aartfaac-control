import smtplib
from email.MIMEText import MIMEText

FROM = "acontrol@mcu001.control.lofar"
TO = "folkerthuizinga@gmail.com"

class MailNotify:
    def __init__(self, mfrom=FROM, mto=TO):
        self.mail_from = mfrom
        self.mail_to = mto

    def send(self, subject, msg):
        mail = MIMEText(msg)
        mail['Subject'] = subject
        mail['From'] = self.mail_from
        mail['To'] = self.mail_to
        s = smtplib.SMTP()
        s.connect()
        s.sendmail(self.mail_from, [self.mail_to], mail.as_string())
        s.close()

    def error(self, msg):
        if msg['isError']:
          self.send("MCU001 AARTFAAC Error", msg['printed'])
