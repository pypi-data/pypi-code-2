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
"""Quick Entry Interfaces

$Id: interfaces.py 72509 2007-02-13 09:31:51Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

class IProcessError(zope.interface.Interface):

    position = zope.schema.Int(
        title=u'Position',
        description=u'The position at which the error occured.',
        required=True)

    reason = zope.schema.Text(
        title=u'Reason',
        description=u'The reason for the parse error.',
        required=True)

class ProcessError(Exception):
    zope.interface.implements(IProcessError)

    def __init__(self, position, reason):
        self.position = position
        self.reason = reason

    def __repr__(self):
        return '<%s at pos %r: %r>' %(
            self.__class__.__name__, self.position, self.reason)

    def __str__(self):
        return self.reason + u' (Position %i)' %self.position


class IProcessor(zope.interface.Interface):
    """A processor for a quick entry text."""

    separationCharacter = zope.interface.Attribute(
        'Each value is separated by this character.')

    plugins = zope.interface.Attribute(
        'A sequence of plugin classes that are used to parse the text.')

    def parse(text):
        """Parse the text into a tuple of plugin instances."""

    def process(text, context=None):
        """Process a quick entry text.

        The context can be used by plugins to look up values.

        The returned value should be a dictionary of extracted variables.
        """

class IExecutingProcessor(IProcessor):
    """A processor that can apply the parsed data to a context."""

    def apply(text, context):
        """Apply data once it is parsed.

        The data is applied on the context.
        """


class IPlugin(zope.interface.Interface):
    """A plugin for a particular piece of the quick entry text."""

    text = zope.interface.Attribute(
        'The text that is going to be converted into values. '
        'The processor will fill this attribute after the initial text is set.')

    position = zope.schema.Int(
        title=u'Position',
        description=u'The position at which the text started',
        default=0,
        required=True)

    def canProcess():
        """Determine whether the plugin can handle the text.

        Returns a boolean stating the result.
        """

    def process(context):
        """Process the text to create the varaiable names.

        The result will be a dictionary from variable name to value. While
        plugins often will only produce one variable, they can produce several.

        If processing fails for some reason, a ``ValueError`` with a detailed
        explanation must be raised.
        """

class IExecutingPlugin(IPlugin):
    """A plugin that can apply the parsed data to a context."""

    def apply(text, context=None):
        """Apply data once it is parsed.

        The data is applied on the context.
        """
