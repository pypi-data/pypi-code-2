# vim:fileencoding=utf-8
from urllib import urlencode
import json

USER_TIMELINE_URI = 'http://api.mixi-platform.com/2/voice/statuses/@me/user_timeline'
FRIENDS_TIMELINE_URI = 'http://api.mixi-platform.com/2/voice/statuses/friends_timeline/%s'

def _get_user_timeline(self, count=20, start_index=0):
    params = {
            'count': count,
            'startIndex': start_index,
            }
    res = self.send_api_request(USER_TIMELINE_URI, params)
    return json.loads(res)

def _get_friends_timeline(self, group_id='', count=20, start_index=0):
    params = {
            'count': count,
            'startIndex': start_index,
            }
    uri = FRIENDS_TIMELINE_URI % str(group_id)
    res = self.send_api_request(uri, params)
    return json.loads(res)


API_METHODS = {
        'get_user_timeline'    : _get_user_timeline,
        'get_friends_timeline' : _get_friends_timeline,
        }
