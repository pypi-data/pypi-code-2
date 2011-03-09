import urllib2

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _


def validate_repository(hostname):
    domain = hostname.split(':')[0]
    base_url = 'http://%s' % hostname
    url = base_url + reverse('check_repository')
    headers = {
        "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
        "Accept-Language": "en-us,en;q=0.5",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Connection": "close",
        "User-Agent": "django-staging",
    }
    url = url.encode('utf-8')
    django_broken_error = ValidationError(
        _(u"The Django server (%s) seems to be not running") % base_url, code='invalid_link')
    hg_broken_error = ValidationError(
        _(u"The remote HG server seems to be not running. The command was like: hg serve -p 8888 --config 'web.allow_push=*' --config 'web.push_ssl=false'"), code='invalid_link')
    try:
        req = urllib2.Request(url, None, headers)
        result = urllib2.urlopen(req).read()
    except ValueError:
        raise ValidationError(_(u'Enter a valid URL.'), code='invalid')
    except:
        raise django_broken_error
    if result != 'ok':
        raise hg_broken_error
