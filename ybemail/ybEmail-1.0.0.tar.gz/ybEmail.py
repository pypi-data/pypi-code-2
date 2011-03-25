import smtplib
from email.mime.text import MIMEText

"""
This module will help you send emails from python programs easily. For example, 
if you wrote a report or alert program, this module will help you send that 
informaiton easily.

This module is tested using python3.

example usage:
    sendEmail('test@mail.com', 'computer@mail.com', 'This is a test email', 
                'This message was sent using AlienDevs ybEmail Module')

notes:
    03-24-2011: Attachements not yet supported

"""

################################################################################
#                            Global Settings                                   #
################################################################################
SERVER = 'localhost'


################################################################################
def sendEmail(TO, FROM, SUBJECT, MESSAGE, ATTACH=False):   
################################################################################
    msg = MIMEText(MESSAGE)
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    s = smtplib.SMTP(SERVER)
    s.sendmail(FROM, [TO], msg.as_string())
    s.quit()

