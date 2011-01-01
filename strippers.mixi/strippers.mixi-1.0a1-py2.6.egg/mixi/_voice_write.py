# vim:fileencoding=utf-8
from urllib import urlencode
import json

STATUS_UPDATE_URI = 'http://api.mixi-platform.com/2/voice/statuses/update'
STATUS_DELETE_URI = 'http://api.mixi-platform.com/2/voice/statuses/destroy/%s'

def _update_status(self, status):
    """つぶやきを投稿します。
    """
    params = { 'status': status }
    res = self.send_api_request(STATUS_UPDATE_URI, params, 'POST')
    return json.loads(res)

def _delete_status(self, id):
    """指定された ID のつぶやきを削除します。

    ID のつぶやきが存在しない場合は HTTPError (404 エラー) を送出します。
    """
    self.send_api_request(STATUS_DELETE_URI % str(id), {}, 'POST')


API_METHODS = {
        'update_status' : _update_status,
        'delete_status' : _delete_status,
        }
