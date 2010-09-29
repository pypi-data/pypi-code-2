"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
# from webhelpers.html.tags import checkbox, password
# from webhelpers.html import literal
# from webhelpers.html.tags import *

from pylons import url, request, response

from webflash import Flash

# WebFlash is used to flash messages to the user. Flashed messages
#   will survive redirects and will only be displayed once.
#   Use the flash_ok(), flash_info() & flash_alert() convenience
#   functions to flash messages.

flash = Flash(
    get_response=lambda: response,
    get_request=lambda: request
)

def flash_ok(message):
    flash(message, status='ok')

def flash_info(message):
    flash(message, status='info')

def flash_alert(message):
    flash(message, status='alert')


def user():
    """Return the currently logged-in user object
    or None if not logged in.
    """
    identity = request.environ.get('repoze.who.identity')
    if identity is not None:
        # Get some data associated with the user. (Eg. the user object that was assigned in UserModelPlugin.)
        user = identity.get('user')
    else:
        user = None
    return user

