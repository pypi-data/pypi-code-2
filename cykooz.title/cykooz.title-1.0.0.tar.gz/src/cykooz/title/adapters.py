# -*- coding: utf-8 -*-
'''
Created on 19.11.2010

@author: cykooz
'''

from zope.interface import implements, Interface
from zope.component import adapts
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.dublincore.interfaces import IZopeDublinCore
from zope.container.interfaces import IContained

from interfaces import ITitle


class TitleAdapterBase(object):
    implements(ITitle)
    
    def __init__(self, context):
        self.context = context


class ClassName2TitleAdapter(TitleAdapterBase):
    adapts(Interface)
    
    @property
    def title(self):
        return unicode(self.context.__class__.__name__)


class Contained2TitleAdapter(ClassName2TitleAdapter):
    adapts(IContained)
    
    @property
    def title(self):
        try:
            return IContained(self.context).__name__
        except TypeError:
            return super(Contained2TitleAdapter, self).title
        

class ZDC2TitleAdapter(Contained2TitleAdapter):
    adapts(IAttributeAnnotatable)
    
    @property
    def title(self):
        title = IZopeDublinCore(self.context).title
        if not title:
            try:
                return super(ZDC2TitleAdapter, self).title
            except TypeError:
                return title
        
        return title
