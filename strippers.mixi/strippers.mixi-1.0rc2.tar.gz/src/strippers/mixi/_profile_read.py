# vim:fileencoding=utf-8
from urllib import urlencode
try:
    import json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import simplejson as json

PEOPLE_URI = 'http://api.mixi-platform.com/2/people/@me/%s'

def _get_friends(self, group_id='@friends', sort_by=None, sort_order='ascending', count=20, start_index=0):
    params = {
            'count': count,
            'startIndex': start_index,
            'sortOrder': sort_order,
            }
    if sort_by:
        params['sortBy'] = sort_by
    uri = PEOPLE_URI % str(group_id)
    res = self.get(uri, params)
    return json.loads(res)

def _get_myself(self):
    return _get_friends(self, '@self', count=1)


API_METHODS = {
        'get_friends' : _get_friends,
        'get_myself' : _get_myself,
        }
