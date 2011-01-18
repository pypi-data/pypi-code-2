# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: mailto.py 30834 2010-07-02 10:45:20Z nilo $
"""Checker implementation for mailto: links."""

from gocept.lms.interfaces import STATE_OK, STATE_UNAVAILABLE
import gocept.lms.handler
import grok
import re
import urllib


class Mailto(gocept.lms.handler.AbstractURLHandler,
           grok.GlobalUtility):

    grok.name('mailto')

    def check(self, url):
        mailto, value = urllib.splittype(url)
        if re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", value):
            status = STATE_OK
            status_msg = 'Ok'
        else:
            status = STATE_UNAVAILABLE
            status_msg = 'No valid email address.'
        return status, status_msg

    def allow(self, url):
        return True

    def classify(self, url):
        return url
