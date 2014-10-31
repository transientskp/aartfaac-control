import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

FROM = "folkerthuizinga@gmail.com"
TO = "f.huizinga@uva.nl"

class GMailNotify:

    def __init__(self, user, pw):
        self.user = user
        self.password = pw

    def login(self):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.user, self.password)

    def send(self, subject, msg):
        self.login()
        m = MIMEMultipart()
        m['From'] = FROM
        m['To'] = TO
        m['Subject'] = subject
        m.attach(MIMEText(msg, 'plain'))
        self.server.sendmail(FROM, TO, m.as_string())
