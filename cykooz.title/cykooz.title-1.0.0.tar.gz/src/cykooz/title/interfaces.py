# -*- coding: utf-8 -*-
'''
Created on 18.11.2010

@author: cykooz
'''

from zope.interface import Interface
from zope.schema import TextLine

from i18n import MessageFactory as _

class ITitle(Interface) :

    title = TextLine(title=_('Title'),
                     description=_('Title of object'))
