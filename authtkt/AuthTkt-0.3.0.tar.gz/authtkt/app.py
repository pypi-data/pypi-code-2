import datetime

from httpkit.helper.cookie import set_cookie, delete_cookie
from pipestack.ensure import ensure_method_marble as ensure_action
from dreamweavertemplate.decorator import render_template
from bn import HTMLFragment, AttributeDict
from formbuild import Form
from formconvert import multiDictToDict
from nestedrecord import encode_error
from recordconvert import toRecord
from conversionkit import Conversion, chainPostConverters, set_error, Field, set_result
from stringconvert import unicodeToUnicode, unicodeToBoolean
from usermanager.driver.base import NoSuchUserError
from authtkt import AuthTkt
from appdispatch import BaseApp, BaseArea
from urlconvert import rule

class AuthApp(BaseApp):
    options = {
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
    }
    urls = [
        rule(u'{*}://{*}:{*}/login', add={u'area': u'index', u'action': u'login'}, extra=dict(area_class="IndexArea")),
        rule(u'{*}://{*}:{*}/logout', add={u'area': u'index', u'action': u'logout'}, extra=dict(area_class="IndexArea")),
    ]

def js():
    return """
    <script type="text/javascript">
        function getFocus() {
          document.forms[1].elements[0].focus();
          document.forms[1].elements[0].select();
        };
    </script>"""

render = render_template(
    template_from_config='auth.template', 
    defaults=dict(head=js()),
)

def validSignIn(user='user'):
    def validSignIn_post_converter(conversion, bag=None):
        if not conversion.children['username'].successful and \
           not conversion.children['password'].successful:
            # Might as well have only one error at once
            set_result(conversion.children['password'], '')
        elif not conversion.successful:
            set_error(conversion, '')
        elif conversion.successful:
            # Now we need to validate the credentials.
            try:
                if not bag.has_key(user):
                    bag.start(user)
                if not bag[user].user_has_password(
                    conversion.result.username,
                    conversion.result.password,
                ):
                    set_error(conversion, 'Invalid credentials')
            except NoSuchUserError:
                set_error(conversion, 'Invalid credentials')
    return validSignIn_post_converter

signin_converter = chainPostConverters(
    toRecord(
        converters = dict(
            username=Field(
                missing_or_empty_error='Please enter a username', 
                converter=unicodeToUnicode()
            ),
            password=Field(
                missing_or_empty_error='Please enter a password', 
                converter=unicodeToUnicode(),
            ),
            referrer=Field(converter=unicodeToUnicode()),
        )
    ),
    validSignIn(),
)

class AuthArea(BaseArea):

    #
    # Actions
    #
 
    @ensure_action('ticket', 'template')
    def action_logout(self, marble):
        if not marble.bag.ticket.get('username'):
            return marble.bag.template.render(
                marble.config.template, 
                dict(heading='Not Signed In', content='You are not signed in.')
            )
        else:
            cookie = delete_cookie('auth_tkt')
            marble.bag.http.response.headers.append(('Set-Cookie', cookie))
            return marble.bag.template.render(
                marble.config.template, 
                dict(heading=marble.config.signed_out_heading, content=marble.config.signed_out_content%{'signin_url':marble.url(area=u'index', action=u'login')})
            )

    @ensure_action('http.input', 'http.query', 'flash')
    @render
    def action_login(self, marble, region):
        flash = ''
        if marble.bag.flash.message:
            # XSS risk in the cookie message?
            flash = '<p>' + marble.bag.flash.message + '</p>'
            marble.bag.flash.remove()
        if marble.bag.http.environ['REQUEST_METHOD'].lower() != 'post':
            referrer = marble.bag.http.query.getfirst('referrer')
            if not referrer:
                referrer = ''
            content = self.on_view_form(marble, value=dict(referrer=referrer))
            cookie = set_cookie('auth_tkt', '')
            marble.bag.http.response.headers.append(('Set-Cookie', cookie))
        else:
            conversion = Conversion(
                marble.bag.http.input
            ).perform(
                multiDictToDict(encoding='utf8'),
                marble.bag,
            )
            params = conversion.result
            conversion = Conversion(
                params
            ).perform(
                signin_converter,
                marble.bag,
            )
            if not conversion.successful:
                error = encode_error(conversion)
                flash = conversion.error
                marble.log.info('Invalid form: %r', error)
                content = self.on_view_form(marble, conversion.value, error)
            else:
                at = AuthTkt(
                    conf=marble.bag.app.option['auth']['filename'], 
                    secret=marble.bag.app.option['auth']['secret'],
                )
                ip_addr=None
                if not at['ignore_ip']:
                    ip_addr = marble.bag.http.environ['REMOTE_ADDR']
                tkt = at.ticket(
                    userid=conversion.result['username'],
                    ip=ip_addr,
                    tokens=['one', 'two', 'three'],
                    user_data='User Data',
                )
                value = tkt.cookie_value().encode('base64')
                cookie = set_cookie('auth_tkt', value.strip().replace('\n',''))
                marble.bag.http.response.headers.insert(0, ('Set-Cookie', cookie))
                return self.on_just_signed_in(marble, conversion.result.referrer)
        region['content'] = content
        region['flash'] = flash
        region['heading'] = marble.config.heading

    def on_just_signed_in(self, marble, referrer=None):
        if referrer and referrer != marble.url(area=u'index', action=u'logout'):
            return [
               '<html><head><title>Redirecting...</title>'
               '<meta http-equiv="REFRESH" content="0;URL=%s">'
               '</head><body></body></html>'%(referrer,)
            ]
        elif marble.config.if_no_referrer_redirect_to != None:
            return [
               '<html><head><title>Redirecting...</title>'
               '<meta http-equiv="REFRESH" content="0;URL=%s">'
               '</head><body></body></html>'%(marble.config.if_no_referrer_redirect_to,)
            ]
        else:
            if not marble.bag.has_key('template'):
                marble.bag.start('template')
            return marble.bag.template.render(
                marble.config.template,
                dict(heading='Signed in', content='You are now signed in')
            )

    def on_view_form(self, marble, value=None, error=None, option=None):
        form = Form(
            value=value,
            error=error,
            option=option,
        )
        fragment = HTMLFragment()
        fragment.safe(form.start_with_layout(''))
        fragment.safe(
            form.field(
                name='username', 
                label=marble.config.username,
                type='text', 
                side=marble.config.side,
                colon=marble.config.colon,
                #required=True,
            )
        )
        fragment.safe(
            form.field(
                name='password', 
                label=marble.config.password,
                type='password', 
                side=marble.config.side,
                colon=marble.config.colon,
                #required=True,
            )
        )
        actions = u'<br />'+form.submit(name='submit', value=marble.config.submit_value)
        fragment.safe(form.action_bar(actions))
        fragment.safe(form.end_with_layout(hidden_field_names=['referrer']))
        return fragment.getvalue()

