# vim:fileencoding=utf-8
from urllib import urlencode
import urllib2
import json
import sys
import re
import logging
import MultipartPostHandler

log = logging.getLogger('graphapi')
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.DEBUG)
log.addHandler(log_handler)

__version__ = '1.0a3'


AUTORIZATION_URI = 'https://mixi.jp/connect_authorize.pl'
TOKEN_URI = 'https://secure.mixi-platform.com/2/token'

# デバイス定数の定義
DEVICE_PC         = 'pc'
DEVICE_SMARTPHONE = 'smartphone'
DEVICE_TOUCH      = 'touch'

# スコープ定数の定義
READ_PROFILE  = 'r_profile'
READ_VOICE    = 'r_voice'
WRITE_VOICE   = 'w_voice'
READ_UPDATES  = 'r_updates'
WRITE_SHARE   = 'w_share'
READ_PHOTO    = 'r_photo'
WRITE_PHOTO   = 'w_photo'
READ_MESSAGE  = 'r_message'
WRITE_MESSAGE = 'w_message'


_api_mappings = {
        READ_VOICE   : 'strippers.mixi._voice_read',
        WRITE_VOICE  : 'strippers.mixi._voice_write',
        READ_PROFILE : 'strippers.mixi._profile_read',
        }

def set_api_module(scope, mod):
    _api_mappings[scope] = mod


class MixiGraphAPI(object):

    def __init__(self, consumer_key, consumer_secret, scopes, access_token=None, refresh_token=None):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret

        self.device = DEVICE_PC
        self.state = None
        self.auto_token_refresh = True
        self._token_updated = False

        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires = None
        self.scopes = tuple(scopes)
        if self._access_token and self._refresh_token and self.scopes:
            self._setup_apis()

    @property
    def tokens(self):
        """現在使われているアクセストークンとリフレッシュトークンのタプルを返します。
        
        """
        return self._access_token, self._refresh_token

    @property
    def access_token(self):
        return self._access_token

    @property
    def refresh_token(self):
        return self._refresh_token

    @property
    def token_updated(self):
        return self._token_updated

    def _setup_apis(self):
        for scope in self.scopes:
            if scope in _api_mappings:
                mod_name = _api_mappings.get(scope)
                if mod_name:
                    __import__(mod_name)
                    mod = sys.modules[mod_name]
                    mappings = getattr(mod, 'API_METHODS')
                    for name, func in mappings.items():
                        if not hasattr(MixiGraphAPI, name):
                            setattr(MixiGraphAPI, name, func)

    def get_auth_url(self, device=None, state=None):
        if device:
            self.device = device
        if state:
            self.state = state
        params = {
                'client_id'     : self._consumer_key,
                'response_type' : 'code',
                'display'       : self.device,
                }
        if self.state:
            params['state'] = self.state
        params['scope'] = ' '.join(self.scopes)
        return AUTORIZATION_URI + '?' + urlencode(params)

    def initialize(self, auth_code, redirect_uri):
        params = {
                'grant_type'    : 'authorization_code',
                'client_id'     : self._consumer_key,
                'client_secret' : self._consumer_secret,
                'code'          : auth_code,
                'redirect_uri'  : redirect_uri
                }
        try:
            res = urllib2.urlopen(TOKEN_URI, urlencode(params)).read()
        except urllib2.HTTPError, e:
            if e.code == 401:
                raise InvalidAuthCodeError('Auth code "%s" is invalid. (It maybe expired.)' % auth_code)
            else:
                raise
        tokens = json.loads(res)
        self._access_token = tokens['access_token']
        self._refresh_token = tokens['refresh_token']
        self._expires = tokens['expires_in']
        self._token_updated = True
        return self.tokens

    def _build_request(self, uri):
        req = urllib2.Request(uri)
        req.add_header('Authorization', 'OAuth ' + self._access_token)
        return req

    def _parse_error(self, e):
        """API アクセスのエラーレスポンスから WWW-Authenticate ヘッダにセットされた情報を名前と値の dict 形式で返します。
        """
        headers = e.info()
        value = headers.getheader('WWW-Authenticate')
        if value:
            value = value[len('OAuth '):]
            value = re.sub(r'["\']', '', value)
            data = [ key_val.split('=') for key_val in value.split(',') ]
            return dict(data)
        return {}

    def send_api_request(self, uri, params={}, http_method='GET', multipart=False, try_count=1):
        # MultipartPostHandler は urlencode() を勝手にやってくれるので、
        # multipart 引数が指定されている場合は urlencode() しない。
        data = params if multipart else urlencode(params)

        if http_method.upper() == 'POST':
            req = self._build_request(uri)
            req.add_data(data)
        else: # GET
            req = self._build_request(uri + '?' + data)

        if multipart:
            opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
        else:
            opener = urllib2.build_opener()
        try:
            return opener.open(req).read()
        except urllib2.HTTPError, e:
            if 400 <= e.code < 500:
                error_info = self._parse_error(e)
                error_msg = error_info.get('error')
                if error_msg == 'expired_token': # アクセストークンの有効期限切れ
                    if self.auto_token_refresh and try_count <= 1: # 念のため無限ループになるのを抑止
                        # アクセストークンを再発行して、再度 API リクエストを送信
                        self.reissue_token()
                        return self.send_api_request(uri, params, http_method, multipart, try_count + 1)
                    raise ExpiredTokenError('Access token is expired.')
                elif error_msg == 'insufficient_scope': # アクセスに必要なスコープが認可されていない
                    raise InsufficientScopeError(error_info.get('scope'))
                elif error_msg == 'invalid_request': # 不正なリクエスト内容
                    raise InvalidRequestError()
                else: # 不正なアクセストークン
                    raise InvalidTokenError()
            else:
                raise

    def reissue_token(self):
        """アクセストークンを再発行します。
        リフレッシュトークンの有効期限切れの場合、再発行は失敗し、ExpiredTokenError を送出します。
        """
        params = {
                'grant_type'    : 'refresh_token',
                'client_id'     : self._consumer_key,
                'client_secret' : self._consumer_secret,
                'refresh_token' : self._refresh_token
                }
        try:
            res = urllib2.urlopen(TOKEN_URI, urlencode(params)).read()
        except urllib2.HTTPError, e:
            if e.code == 401:
                raise ExpiredTokenError('Refresh token is expired.', self.get_auth_url())
            else:
                raise
        tokens = json.loads(res)
        self._access_token = tokens['access_token']
        self._refresh_token = tokens['refresh_token']
        self._expires = tokens['expires_in']
        self._token_updated = True


class MixiGraphAPIError(Exception):
    pass


class InvalidAuthCodeError(MixiGraphAPIError):
    pass


class InvalidRequestError(MixiGraphAPIError):
    pass


class InsufficientScopeError(MixiGraphAPIError):

    def __init__(self, scope):
        self.scope = scope

    def __str__(self):
        return self.scope


class InvalidTokenError(MixiGraphAPIError):
    pass


class ExpiredTokenError(InvalidTokenError):

    def __init__(self, message, auth_url=None):
        self.message = message
        self.auth_url = auth_url

