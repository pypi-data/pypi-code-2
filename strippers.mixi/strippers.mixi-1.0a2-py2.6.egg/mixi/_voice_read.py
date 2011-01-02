# vim:fileencoding=utf-8
from urllib import urlencode
import json

USER_TIMELINE_URI = 'http://api.mixi-platform.com/2/voice/statuses/%s/user_timeline'
FRIENDS_TIMELINE_URI = 'http://api.mixi-platform.com/2/voice/statuses/friends_timeline/%s'

def _get_user_timeline(self, user_id='@me', count=20, startIndex=0):
    params = {
            'count': count,
            'startIndex': startIndex,
            }
    uri = USER_TIMELINE_URI % str(user_id)
    res = self.send_api_request(uri, params)
    return json.loads(res)

def _get_friends_timeline(self, group_id='', count=20, startIndex=0):
    params = {
            'count': count,
            'startIndex': startIndex,
            }
    uri = FRIENDS_TIMELINE_URI % str(group_id)
    res = self.send_api_request(uri, params)
    return json.loads(res)


API_METHODS = {
        'get_user_timeline'    : _get_user_timeline,
        'get_friends_timeline' : _get_friends_timeline,
        }
