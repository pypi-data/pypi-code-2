import urllib
import re
import logging
from urlparse import urljoin

from tools.email.errors import EmailNotFound, AbuseError

def find_message(login, anchor, log_file=None, debug=False):
    url = 'http://mailinator.com/maildir.jsp?email=%s' % login
    body = urllib.urlopen(url).read()
    if log_file:
        open(log_file, 'w').write(body)
    if 'Welcome to the Mailinator Abuse page' in body:
        raise AbuseError('Login %s is banned by mailinator' % login)
    re_link = re.compile('<a href=(/displayemail\.jsp[^>]+)>([^<]+)</a>')
    found = None
    for match in re_link.finditer(body):
        if debug:
            logging.debug('Mailinator message: %s' % match.group(2))
        if anchor in match.group(2):
            found = match.group(1)

    if not found:
        raise EmailNotFound('Could not found email in inbox')
    else:
        return urllib.urlopen('http://mailinator.com' + found).read()

