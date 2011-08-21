import imaplib
import email
import logging

from tools.email.errors import AuthError, EmailNotFound, AbuseError


logger = logging.getLogger('tools.email.gmail')

class Gmail(object):
    def __init__(self, username, password):
        try:
            logger.debug('Logging to imap.gmail.com with %s username' % username)
            box = imaplib.IMAP4_SSL('imap.gmail.com', port=993)
            box.login(username, password)
            box.select()
            self.box = box 
        except imaplib.IMAP4.error, ex:
            raise AuthError(str(ex))

    def find_message(self, anchor):
        typ, ids = self.box.search(None, 'BODY', '"%s"' % anchor)
        ids = ids[0].split()
        if not ids:
            raise EmailNotFound('Imap search command did not find anything')
        typ, data = self.box.fetch(ids[-1], 'RFC822')

        msg = email.message_from_string(data[0][1])
        mapping = {}
        for pay in msg.walk():
            mapping.setdefault(pay.get_content_type(), []).append(pay)
        if 'text/html' in mapping:
            return mapping['text/html'][0].get_payload(decode=True)
        elif 'text/plain' in mapping:
            return mapping['text/plain'][0].get_payload(decode=True)
        else:
            raise EmailNotFound('Could not find text/html or text/plain content')


def find_message(username, password, anchor):
    "Shortcut to Gmail functions"

    box = Gmail(username, password)
    return box.find_message(anchor)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print find_message('default@lorien.name', '7812160DFLT', 'twit')
