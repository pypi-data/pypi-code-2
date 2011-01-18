# Copyright (C) 2011 Luci Stanescu <luci@cnix.ro>. See debian/copyright for details.
#

"""
Logging support for the web application.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['ILogger', 'ApacheLogger']

from mod_python import apache
from zope.interface import Interface, implements


class ILogger(Interface):
    """
    Interface representing a logger. The five methods documented allow the
    components to issue messages for the system administrator.
    """

    def debug(message, *args):
        """
        Send message interpolated with the rest of the positional arguments
        at the DEBUG level.
        """

    def info(message, *args):
        """
        Send message interpolated with the rest of the positional arguments
        at the INFO level.
        """

    def warn(message, *args):
        """
        Send message interpolated with the rest of the positional arguments
        at the WARNING level.
        """

    def error(message, *args):
        """
        Send message interpolated with the rest of the positional arguments
        at the ERROR level.
        """

    def critical(message, *args):
        """
        Send message interpolated with the rest of the positional arguments
        at the CRITICAL level.
        """


class ApacheLogger(object):
    """
    This ILogger implementation uses the apache logging support to issue
    messages.
    """

    implements(ILogger)

    def __init__(self, request):
        self.request = request

    def debug(self, message, *args):
        self.request.log_error((message % args if args else message).encode('utf-8'), apache.APLOG_DEBUG)

    def info(self, message, *args):
        self.request.log_error((message % args if args else message).encode('utf-8'), apache.APLOG_NOTICE)

    def warn(self, message, *args):
        self.request.log_error((message % args if args else message).encode('utf-8'), apache.APLOG_WARNING)

    def error(self, message, *args):
        self.request.log_error((message % args if args else message).encode('utf-8'), apache.APLOG_ERR)

    def critical(self, message, *args):
        self.request.log_error((message % args if args else message).encode('utf-8'), apache.APLOG_CRIT)


