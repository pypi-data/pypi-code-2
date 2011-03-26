import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

"""
This module will help you send emails from python programs easily. For example, 
if you wrote a report or alert program, this module will help you send that 
informaiton easily.

More Information in the README file
"""

################################################################################
#                            Global Settings                                   #
################################################################################
SERVER = 'localhost'


################################################################################
def sendEmail(TO, FROM, SUBJECT, MESSAGE, ATTACH=False):   
################################################################################
    # Determine type of email
    if ATTACH != False: msg = MIMEMultipart()
    else: msg = MIMEText(MESSAGE) 
    
    # this works for both types of emails
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    if ATTACH != False: 
        # That is what u see if dont have an email reader:
        msg.preamble = 'Multipart massage.\n'
    
        # This is the textual part:
        part = MIMEText("Hello im sending an email from a python program")
        msg.attach(part)
    
        # This is the binary part(The Attachment):
        part = MIMEApplication(open(ATTACH,"rb").read())
        part.add_header('Content-Disposition', 'attachment', filename=ATTACH)
        msg.attach(part)

    s = smtplib.SMTP(SERVER)
    s.sendmail(FROM, [TO], msg.as_string())
    s.quit()






