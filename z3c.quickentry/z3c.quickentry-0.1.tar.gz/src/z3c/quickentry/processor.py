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
"""Quick Entry Processor Implementation

$Id: processor.py 72510 2007-02-13 10:13:23Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.interface
from z3c.quickentry import interfaces

class BaseProcessor(object):
    """A base class for a processor."""
    zope.interface.implements(interfaces.IProcessor)

    # See interfaces.IProcessor
    separationCharacter = ' '
    # This needs to be properly implemented in a subclass.
    plugins = ()

    def parse(self, text):
        position = 0
        # Step 0: Get the sequence of all plugins; we store the result
        #         locally, since the lookup might be expensive.
        plugins = self.plugins
        # Step 1: Split the entire text using the separation character
        pieces = text.split(self.separationCharacter)
        # Whenever a plugin is found that can handle a piece of text, it is
        # added to the result list
        result = []
        # Step 2: Now iterate through every piece and try to process them
        for piece in pieces:
            # Step 2.1: Check each plugin to see if it can process the piece
            for pluginClass in plugins:
                plugin = pluginClass(piece, position)
                # Step 2.2: If the plugin can process, add it to the result
                if plugin.canProcess():
                    result.append(plugin)
                    break
            # Step 2.3: If no plugin can handle the piece, it is simply added
            #           to the text of the last plugin's test.
            else:
                if len(result) == 0:
                    raise interfaces.ProcessError(
                        position, u'No matching plugin found.')
                result[-1].text += self.separationCharacter
                result[-1].text += piece
            # Step 2.4: Update the position
            #           (add one for the separation character)
            position += len(piece) + 1
        return result

    def process(self, text, context=None):
        """See interfaces.IProcessor"""
        resultDict = {}
        for plugin in self.parse(text):
            resultDict.update(plugin.process(context))
        return resultDict


class ExecutingBaseProcessor(BaseProcessor):

    def apply(self, text, context):
        """See interfaces.IProcessor"""
        for plugin in self.parse(text):
            plugin.apply(context)
