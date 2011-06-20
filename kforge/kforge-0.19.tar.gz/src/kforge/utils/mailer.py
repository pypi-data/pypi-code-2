import smtplib
import email.MIMEText

COMMASPACE = ', '

def sendmail(from_addr, to_addrs, subject, body, host=''):
    if type(body) == unicode:
        body = body.encode('utf-8')
    emailMsg = email.MIMEText.MIMEText(body, _charset='utf-8')
    if type(from_addr) == unicode:
        from_addr = from_addr.encode('utf-8')
    emailMsg['From'] = from_addr
    if type(to_addrs) == list:
        to_addrs = [e.encode('utf-8') for e in to_addrs]
        emailMsg['To'] = COMMASPACE.join(to_addrs)
    elif type(to_addrs) == unicode:
        to_addrs = to_addrs.encode('utf-8')
        emailMsg['To'] = to_addrs
    if type(subject) == unicode:
        subject = subject.encode('utf-8')
    emailMsg['Subject'] = subject
    smtp = smtplib.SMTP()
    if host:
        smtp.connect(host)
    else:
        smtp.connect()
    try:
        msg = emailMsg.as_string()
        response = smtp.sendmail(from_addr, to_addrs, msg)
        if response:
            msg = "Couldn't send email to all recipients: %s" % repr(response)
            raise Exception(msg)
    finally:
            smtp.close()
