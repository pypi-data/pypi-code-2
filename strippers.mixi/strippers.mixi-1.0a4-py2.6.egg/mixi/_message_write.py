# vim:fileencoding=utf-8
from urllib import urlencode
import json

MESSAGE_SEND_URI = 'http://api.mixi-platform.com/2/messages/@me/@self/@outbox'

def _send_message(self, recipient_id, title, body):
    """
    メッセージを送信します。

    @param recipient_id: 宛先ユーザの ID
    @type recipient_id: str
    @param title: 件名
    @type title: str
    @param body: 本文
    @type body: str
    @return: 'id' キーを持つ dict オブジェクト
    @rtype: dict
    """
    params = {
            'title'      : title,
            'body'       : body,
            'recipients' : [recipient_id],
            }
    res = self.send_api_request(MESSAGE_SEND_URI, params, 'POST')
    return json.loads(res)


API_METHODS = {
        'send_message'  : _send_message,
        }
