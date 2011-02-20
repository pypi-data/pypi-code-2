import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dexy.handler import DexyHandler


class EmailHandler(DexyHandler):
    ALIASES = ['email']

    def process_text(self, input_text):
        me = "nelson.ana@gmail.com"
        you = "ana@ananelson.com"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg['From'] = me
        msg['To'] = you

        html = input_text
        text = input_text # call cssliner to plain text

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # Send the message via local SMTP server.
        s = smtplib.SMTP('smtp.gmail.com')
        s.starttls()
        s.login('nelson.ana', '5hdW22xab')
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(me, you, msg.as_string())
        s.quit()
        return "email sent"
