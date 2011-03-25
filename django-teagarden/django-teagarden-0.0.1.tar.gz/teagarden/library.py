# -*- coding: utf-8 -*-

"""Module with builtin methods."""


import cgi
import logging

from django import template
from django.contrib.auth.models import User
from django.core.cache import cache
from django.forms import Form
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _

from teagarden.models import Account

register = template.Library()


@register.filter
def all_errors(form):
    """Returns only the general/non-field errors of a form.

    Args:
      :form: A :class:`Form` instance

    Returns:
      List of non field specific errors or an empty string
    """
    assert isinstance(form, Form)
    if "__all__" in form.errors:
        return form.errors["__all__"]
    else:
        return ""


@register.filter
def bool_to_image(val):
    if not val:
        return mark_safe('<img src="/static/img/cross.png">')
    else:
        return mark_safe('<img src="/static/img/tick.png">')


@register.filter
def field_errors(form):
    """Returns all field specific form errors.

    Args:
      :form: A :class:`Form` instance

    Returns:
      List of all field specific error messages
    """
    errors = form.errors.copy()
    if "__all__" in errors:
        del errors["__all__"]
    return errors


@register.filter
def nickname(user):
    """Returns either the user first and last name or the login name."""
    if user.first_name and user.last_name:
        return u"%s %s" % (user.first_name, user.last_name)
    else:
        return user.username


@register.filter
def show_user_link(user_id):
    ret = cache.get("user:%d" % user_id)
    if ret is None:
        logging.debug("Missing cache entry for user:%d", user_id)
        user = User.objects.filter(id=user_id)[0]
        account = Account.get_account_for_user(user)
        ret = """<a onmouseover="JS_showInfoPopup(this, 'userPopupDiv', 'mailto', '/user_popup/')"
        href="/user/%(id)s">%(name)s</a>"""  \
            % {"id": user.id, "name": cgi.escape(account.nickname)}
        cache.set("user:%d" % user_id, ret)
    return mark_safe(ret)
