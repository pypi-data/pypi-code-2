import urllib
import re
import logging
from urlparse import urljoin
import time

from tools.email.errors import EmailNotFound, AbuseError

def find_message(login, anchor, log_file=None, debug=False, timeouts=[]):
    timeouts = list(timeouts) + [0]
    url = 'http://mailinator.com/maildir.jsp?email=%s' % login

    while timeouts:
        body = urllib.urlopen(url).read()
        if log_file:
            open(log_file, 'w').write(body)
        if 'Welcome to the Mailinator Abuse page' in body:
            raise AbuseError('Login %s is banned by mailinator' % login)
        re_link = re.compile('<tr>.+?<a href=(/displayemail\.jsp[^>]+)>[^<]+</a>', re.S)
        found = None
        for match in re_link.finditer(body):
            if debug:
                logging.debug('Mailinator message: %s' % match.group(0))
            if anchor in match.group(0):
                found = match.group(1)

        if not found:
            timeout = timeouts.pop(0)
            if timeouts:
                time.sleep(timeout)
                print 'NO MAIL: sleeping for %d' % timeout
            else:
                raise EmailNotFound('Could not found email in inbox')
        else:
            return urllib.urlopen('http://mailinator.com' + found).read()

