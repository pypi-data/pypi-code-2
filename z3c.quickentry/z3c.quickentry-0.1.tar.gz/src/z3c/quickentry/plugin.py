##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Quick Entry Processor Plugin Implementation

$Id: plugin.py 72509 2007-02-13 09:31:51Z srichter $
"""
__docformat__ = "reStructuredText"
import re
import zope.interface
from z3c.quickentry import interfaces

class BasePlugin(object):
    """An abstract base plugin."""
    zope.interface.implements(interfaces.IPlugin)

    def __init__(self, initialText, position=0):
        self.text = initialText
        self.position = position

    def canProcess(self):
        """See interfaces.IPlugin"""
        raise NotImplementedError

    def process(self, context):
        """See interfaces.IPlugin"""
        raise NotImplementedError

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.text)


class ShortNamePlugin(BasePlugin):
    """Abstract plugin that retrieves a value by short name assignment."""
    # This needs to be overridden by a subclass.
    shortName = 'sn'
    varName = 'shortName'

    def canProcess(self):
        """See interfaces.IPlugin"""
        return self.text.startswith(self.shortName + '=')

    def process(self, context):
        """See interfaces.IPlugin"""
        return {self.varName: unicode(self.text[len(self.shortName)+1:])}

    def __repr__(self):
        return '<%s shortName=%r, varName=%r>' % (
            self.__class__.__name__, self.shortName, self.varName)


class RegexPlugin(BasePlugin):
    """Abstract Plugin that determines the ability to process using a regular
    expression.
    """
    # This needs to be overridden by a subclass.
    regex = None
    varName = ''

    def canProcess(self):
        """See interfaces.IPlugin"""
        return self.regex.match(self.text) is not None

    def process(self, context):
        """See interfaces.IPlugin"""
        if self.regex.match(self.text) is None:
            raise interfaces.ProcessError(
                self.position,
                (u'The regex did match anymore. Probably some text '
                 u'was added later that disrupted the pattern.'))
        return {self.varName: unicode(self.text)}

    def __repr__(self):
        return '<%s varName=%r>' % (self.__class__.__name__, self.varName)


class SetAttributeMixin(object):
    zope.interface.implements(interfaces.IExecutingPlugin)

    def apply(self, context):
        for name, value in self.process(context).items():
            setattr(context, name, value)
