
from appdispatch import URLMarble, URLPipe
from urlconvert import rule
from stringconvert import unicodeToUnicode, unicodeToBoolean
from conversionkit import Field

class AuthMarble(URLMarble):
    urls = [
        rule(u'{*}://{*}:{*}/login', add={u'area': u'index', u'action': u'login'}, extra=dict(area_class="IndexArea")),
        rule(u'{*}://{*}:{*}/logout', add={u'area': u'index', u'action': u'logout'}, extra=dict(area_class="IndexArea")),
    ]

class AuthApp(URLPipe):
    marble_class = AuthMarble
    options = URLPipe.options.copy()
    options.update({
        'template': Field(
            unicodeToUnicode(),
            missing_or_empty_default = 'main.dwt',
        ),
        'side': Field(
            unicodeToBoolean(),
            missing_or_empty_default = True,
        ),
        'heading': Field(
            unicodeToUnicode(),
            missing_or_empty_default = 'Login'
        ),
        'submit_value': Field(
            unicodeToUnicode(),
            missing_or_empty_default = 'Submit'
        ),
        'username': Field(
            unicodeToUnicode(),
            missing_or_empty_default = 'Username'
        ),
        'password': Field(
            unicodeToUnicode(),
            missing_or_empty_default = 'Password'
        ),
        'colon': Field(
            unicodeToBoolean(),
            missing_or_empty_default = True
        ),
        'signed_out_heading': Field(
            unicodeToUnicode(),
            missing_or_empty_default = 'Signed out'
        ),
        'signed_out_content': Field(
            unicodeToUnicode(),
            missing_or_empty_default = 'You are now signed out. Sign in again <a href="%(signin_url)s">here</a>.',
        ),
        'if_no_referrer_redirect_to': Field(
            unicodeToUnicode(),
            empty_error = 'Please specify a URL for `%(name)s.if_no_referrer_redirect_to\'.',
            missing_default = None,
        ),
    })

