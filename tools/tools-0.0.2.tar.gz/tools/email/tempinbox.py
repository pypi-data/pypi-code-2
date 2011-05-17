import urllib
import re
import logging
from urlparse import urljoin

from tools.email.errors import EmailNotFound, AbuseError

def find_message(login, anchor):
    url = 'http://www.tempinbox.com/cgi-bin/checkmail.pl?username=%s&button=Check+Mail&terms=on&kw=spam+email+inbox+filter' % login
    body = urllib.urlopen(url).read()
    #if 'Welcome to the Mailinator Abuse page' in body:
        #raise AbuseError('Login %s is banned by mailinator' % login)
    re_link = re.compile('<a\s+href="(/cgi-bin/viewmail\.pl[^"]+)\s*">([^<]+)</a>')
    found = None
    for match in re_link.finditer(body):
        if anchor in match.group(2):
            found = match.group(1)

    if not found:
        raise EmailNotFound('Could not found email in inbox')
    else:
        return urllib.urlopen('http://tempinbox.com' + found).read()


