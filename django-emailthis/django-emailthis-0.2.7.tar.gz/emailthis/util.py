import httplib

try:
    # prefer externally maintained version
    import simplejson
except ImportError:
    # use bundled version
    from django.utils import simplejson

from django.conf import settings
from django.http import HttpResponse


def render_to_json(data, status=httplib.OK):
    return HttpResponse(simplejson.dumps(data),
                        mimetype='application/json',
                        status=status)


def clean_errors(djerrors):
    d = {}
    for k, v in djerrors.iteritems():
        d[unicode(k)] = [unicode(x) for x in v]
    return d


try:
    get_subject = settings.EMAILTHIS_SUBJECT_GETTER
except AttributeError:

    def get_subject(item):
        return str(item)

def get_remote_ip(request):
    forward = request.META.get('HTTP_X_FORWARDED_FOR')
    if forward:
        ips = forward.split(',')
        return ips[-1].strip()
    else:
        return request.META.get('REMOTE_ADDR')
