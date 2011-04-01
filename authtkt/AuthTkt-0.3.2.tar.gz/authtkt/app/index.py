import logging
import datetime

from appdispatch import BaseArea
from httpkit.helper.cookie import set_cookie, delete_cookie
from pipestack.ensure import ensure_method_marble as ensure_action
from dreamweavertemplate.decorator import render_template
from bn import HTMLFragment, AttributeDict
from formbuild import Form
from formconvert import multiDictToDict
from nestedrecord import encode_error
from recordconvert import toRecord
from conversionkit import Conversion, chainPostConverters, set_error, Field, set_result
from stringconvert import unicodeToUnicode
from usermanager.driver.base import NoSuchUserError

log = logging.getLogger(__name__)


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
                    bag.enter(user)
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

class IndexArea(BaseArea):

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
            marble.bag.http_response.header_list.append(dict(name='Set-Cookie', value=cookie))
            return marble.bag.template.render(
                marble.config.template, 
                dict(
                    heading=marble.config.signed_out_heading, 
                    content=marble.config.signed_out_content%{
                        'signin_url': marble.url(area=u'index', action=u'login'),
                    }
                )
            )

    @ensure_action('input', 'query', 'flash')
    @render
    def action_login(self, marble, region):
        flash = ''
        if marble.bag.flash.message:
            # XSS risk in the cookie message?
            flash = '<p>' + marble.bag.flash.message + '</p>'
            marble.bag.flash.remove()
        if marble.bag.environ['REQUEST_METHOD'].lower() != 'post':
            referrer = marble.bag.query.getfirst('referrer')
            if not referrer:
                referrer = ''
            content = self.on_view_form(marble, value=dict(referrer=referrer))
            cookie = set_cookie('auth_tkt', '')
            marble.bag.http_response.header_list.append(dict(name='Set-Cookie', value=cookie))
        else:
            conversion = Conversion(
                marble.bag.input
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
                if not marble.bag.has_key('ticket'):
                    marble.bag.enter('ticket')
                cookie = marble.bag.ticket.sign_in(username=conversion.result['username'])
                if not marble.bag.has_key('user'):
                    marble.bag.enter('user')
                if hasattr(marble.bag.user, 'logged_in'):
                    marble.bag.user.logged_in(conversion.result['username'], marble.bag.environ['REMOTE_ADDR'])
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
                marble.bag.enter('template')
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
        marble.url_parts['query'] = None
        fragment.safe(form.start_with_layout(marble.url(area=marble.vars.area, action='login')))
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

