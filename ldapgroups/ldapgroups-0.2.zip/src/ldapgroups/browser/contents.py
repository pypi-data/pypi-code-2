'''
Created on 14-aug-2009

@author: jm
'''

from zope.publisher.browser import BrowserView
from zope.size.interfaces import ISized
import urllib

class LDAPGroupFolderContents(BrowserView):
    def iteminfos(self):
        return [{'name':k
                 , 'size':ISized(v).sizeForDisplay()
                 ,'url': urllib.quote(k.encode('utf-8'))} \
                 for k,v in self.context.items()]
