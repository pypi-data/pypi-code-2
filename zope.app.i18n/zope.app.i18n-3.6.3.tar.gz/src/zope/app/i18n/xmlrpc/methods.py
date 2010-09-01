##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Translation Domain XML-RPC Methods 

$Id: methods.py 116083 2010-09-01 12:11:36Z menesis $
"""
__docformat__ = 'restructuredtext'

from zope.publisher.xmlrpc import XMLRPCView

class Methods(XMLRPCView):

    def getAllLanguages(self):
        return self.context.getAllLanguages()

    def getMessagesFor(self, languages):
        messages = []
        for msg in self.context.getMessages():
            if msg['language'] in languages:
                messages.append(msg)

        return messages
