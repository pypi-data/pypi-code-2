# Send simple emails
import smtplib
import email.MIMEText

# default to localhost and standard port (25)
# [[TODO: have a configuration string for the smtp server]]
smtp = smtplib.SMTP()
COMMASPACE = ', '

def send(from_address, to_addresses, subject, body):
    emailMessage = email.MIMEText.MIMEText(body)
    emailMessage['Subject'] = subject
    emailMessage['From'] = from_address
    emailMessage['To'] = COMMASPACE.join(to_addresses)
    smtp.connect()
    smtp.sendmail(from_address, to_addresses, emailMessage.as_string())
    smtp.close()
