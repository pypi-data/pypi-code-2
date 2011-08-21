# -*- coding: utf-8 -*-
from grab import Grab, DataNotFound
import logging
import time
import re

from tools.captcha import util
from tools.email.errors import EmailNotFound


class AuthError(Exception):
    pass

class SignupError(Exception):
    pass

def form_errors(g):
    return [x.text_content().strip() for x in g.itercss('.signup-error')]


def login(g, username, password, ui='mobile'):
    if ui == 'mobile':
        g.go('https://mobile.twitter.com/session/new')
        g.assert_pattern('Username or email')
        g.set_input('username', username)
        g.set_input('password', password)
        g.submit()
        if g.search('Sign in information is not correct'):
            raise AuthError()
        g.assert_pattern('What\'s happening?')
    elif ui == 'standart':
        g.go('https://twitter.com')
        #if g.search('recaptcha_response_field'):
            #raise AuthError('Captcha found')
        g.set_input('session[username_or_email]', username)
        g.set_input('session[password]', password)
        g.submit()
        if g.search('Sign in information is not correct'):
            raise AuthError()
        if g.search('Remember me') and not g.search('signout-button'):
            raise AuthError()
        g.assert_pattern('signout-button')


def signup(g, username, password, email, fullname):
    logging.debug(u'Processing %s [%s]' % (username, fullname))

    for x in xrange(3):
        g.go('https://mobile.twitter.com/signup')
        g.assert_pattern('Just complete the following information')
        g.set_input('oauth_signup_client[fullname]', fullname)
        g.set_input('oauth_signup_client[screen_name]', username)
        g.set_input('oauth_signup_client[email]', email)
        g.set_input('oauth_signup_client[password]', password)
        solution = util.solve_captcha(g.clone(), g.css('.signup-field img').get('src'))
        g.set_input('captcha_response_field', solution)
        g.submit()
        errors = form_errors(g)
        if 'Screen name has already' in errors:
            raise SignupError('Username exists')
        if 'Email has already been' in errors:
            raise SignupError('Email exists')
        if errors:
            logging.error('SIGNUP ERRORS: %s' % ', '.join(errors))
        else:
            break

    g.assert_pattern('What\'s happening?')
    return g


def confirm(g, username, email, password):
    from tools.email.gmail import Gmail
    gmail = Gmail(email, password)
    msg = gmail.find_message(username)
    rex_confirm = re.compile('<a href="(http://twitter\.com/account/confirm_email[^"]+)"')
    href = rex_confirm.search(msg).group(1)
    g.go(href)


def update_profile(g, name, location, url, description):

    #def assert_size(data, max_size):
        #if len(data) > max_size:
            #raise Exception(u'Data "%s" is too length (>%d)' % (data, max_size))

    #assert_size(name, 20)
    #assert_size(location, 30)
    #assert_size(website, 30)
    #assert_size(bio, 160)

    g.go('/settings/profile')
    g.set_input('user[name]', name)
    g.set_input('user[location]', location)
    g.set_input('user[url]', url)
    g.set_input('user[description]', description)
    g.submit()
    g.assert_pattern(name)


def post(g, message, success_anchor=None):
    if len(message) > 140:
        raise Exception('Message too long')
    g.set_input('tweet[text]', message)
    g.submit()
    if success_anchor:
        g.assert_pattern(success_anchor)
