import smtplib
from types import ListType, TupleType, StringType
from email.MIMEText import MIMEText
from email.Header import Header
from decoder import *

def _sender(fromaddr, toaddrs, msg, smtpserver):
    server = smtplib.SMTP(smtpserver)
    #server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


def send(fromaddr, toaddrs, subject, message_text,
         smtpserver='localhost', charset='utf-8', sender=_sender):

    if type(toaddrs) in (ListType, TupleType):
        pass
    elif type(toaddrs) in (StringType,):
        toaddrs = [x.strip() for x in toaddrs.split(',')]
    else:
        raise TypeError, toaddrs

    default_charset = guess_charset(message_text)
    text = u'\n'.join(safe_decode(x, default_charset)
                      for x in message_text.splitlines())
    msg = buildmail(charset, fromaddr, toaddrs, subject, text)
    return sender(fromaddr, toaddrs, msg.as_string(), smtpserver)


def guess_charset(data):
    f = lambda d, enc: d.decode(enc) and enc

    try: return f(data, 'utf-8')
    except: pass
    try: return f(data, 'cp932')
    except: pass
    try: return f(data, 'shift-jis')
    except: pass
    try: return f(data, 'euc-jp')
    except: pass
    try: return f(data, 'iso2022-jp')
    except: pass
    return None


def safe_decode(data, default=None):
    charset = guess_charset(data) or default
    if charset:
        return data.decode(charset,'replace')
    return data


def buildmail(charset, fromaddr, toaddrs, subject, message):
    m_body = message.encode(charset, 'replace')
    m_subject = subject
    m_subject = Header(m_subject.encode(charset, 'replace'), charset)
    m_from = fromaddr
    m_to = ', '.join(toaddrs)
    message = MIMEText(m_body, 'plain', charset)
    message['Subject'] = m_subject
    message['From'] = m_from
    message['To'] = m_to
    return message


