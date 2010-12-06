"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
from pylons import url

from argonaut.model import *
# for some reason forms is not imported even though everything else is ?? fix it with this direct import
from argonaut.model import forms

from argonaut.lib.base import render
import argonaut.lib.timehelpers as timehelpers
import argonaut.lib.authentication as authentication
import argonaut.lib.mailer as mailer

from webhelpers.html import literal
from webhelpers.html.tools import auto_link
from webhelpers.html.tags import *
from webhelpers.text import urlify
from webhelpers.util import *
from webhelpers.html.builder import escape

def format_environ(environ):
    result = []
    keys = environ.keys()
    keys.sort()
    for key in keys:
        result.append("%s: %r"%(key, environ[key]))
    return '\n'.join(result)
