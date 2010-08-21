# Copyright (c) 2005-2010 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from App.class_init import InitializeClass
from App.Common import package_home
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.ZopePageTemplate import charsetFromMetaEquiv
from Products.PageTemplates.ZopePageTemplate import encodingFromXMLPreamble
from Products.PageTemplates.ZopePageTemplate import convertToUnicode
from Products.PageTemplates.ZopePageTemplate import preferred_encodings
from Products.PageTemplates.ZopePageTemplate import PageTemplate

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMailTemplate import BaseMailTemplate

class MailTemplate(BaseMailTemplate,ZopePageTemplate):
    "A ZPT-like template for sending mails"
    
    security = ClassSecurityInfo()

    meta_type = 'Mail Template'

    _properties = ()
    
    manage_options = ZopePageTemplate.manage_options[0:1] + \
                     ZopePageTemplate.manage_options[2:]

    _default_content_fn = os.path.join(package_home(globals()),
                                       'www', 'default.txt')

    def __init__(self,*args,**kw):
        ZopePageTemplate.__init__(self,*args,**kw)
        self.content_type = 'text/plain'
        
    def pt_edit(self, text, content_type, keep_output_encoding=False):

        text = text.strip()
        
        is_unicode = isinstance(text, unicode)
        encoding = None
        output_encoding = None

        if content_type.startswith('text/xml'):

            if is_unicode:
                encoding = None
                output_encoding = 'utf-8'
            else:
                encoding = encodingFromXMLPreamble(text)
                output_encoding = 'utf-8'

        elif content_type.startswith('text/html'):

            charset = charsetFromMetaEquiv(text)

            if is_unicode:
                if charset:
                    encoding = None
                    output_encoding = charset
                else:
                    encoding = None
                    output_encoding = 'iso-8859-15'
            else:
                if charset:
                    encoding = charset
                    output_encoding = charset
                else:
                    encoding = 'iso-8859-15'
                    output_encoding = 'iso-8859-15'

        elif is_unicode:
            utext = text
            output_encoding = 'utf-8'
        else:
            utext, encoding = convertToUnicode(text,
                                               content_type,
                                               preferred_encodings)
            output_encoding = encoding

        # for content updated through WebDAV, FTP 
        if not keep_output_encoding:
            self.output_encoding = output_encoding

        if not is_unicode:
            text = unicode(text, encoding)

        self.ZCacheable_invalidate()
        PageTemplate.pt_edit(self, text, content_type)
        
    security.declareProtected('View management screens','pt_editForm')
    pt_editForm = PageTemplateFile('www/mtEdit', globals(),
                                   __name__='pt_editForm')
    manage = manage_main = pt_editForm

    security.declareProtected('Change Page Templates','pt_editAction')
    def pt_editAction(self, REQUEST, mailhost, text, content_type, expand):
        """Change the mailhost and document."""
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        self.expand=expand
        self._setPropValue('mailhost',mailhost)
        REQUEST.set('text', self.read()) # May not equal 'text'!
        text = unicode(text, 'utf-8')

        self.pt_edit(text, content_type, True)
        REQUEST.set('text', self.read()) # May not equal 'text'!
        message = "Saved changes."
        if getattr(self, '_v_warnings', None):
            message = ("<strong>Warning:</strong> <i>%s</i>"
                       % '<br>'.join(self._v_warnings))
        return self.pt_editForm(manage_tabs_message=message)

    def om_icons(self):
        """Return a list of icon URLs to be displayed by an ObjectManager"""
        icons = ({'path': 'misc_/MailTemplates/mt.gif',
                  'alt': self.meta_type, 'title': self.meta_type},)
        if not self._v_cooked:
            self._cook()
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif',
                              'alt': 'Error',
                              'title': 'This template has an error'},)
        return icons

    def _exec(self, bound_names, args, kw):
        """Call a Page Template"""
        if not kw.has_key('args'):
            kw['args'] = args
        bound_names['options'] = kw

        security=getSecurityManager()
        bound_names['user'] = security.getUser()

        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = {'here': self._getContext(),
                      'bound_names': bound_names}
            result = self.ZCacheable_get(keywords=keyset)
            if result is not None:
                # Got a cached value.
                return result

        # Execute the template in a new security context.
        security.addContext(self)
        try:
            result = self.pt_render(extra_context=bound_names)
            if keyset is not None:
                # Store the result in the cache.
                self.ZCacheable_set(result, keywords=keyset)
            return result
        finally:
            security.removeContext(self)

InitializeClass(MailTemplate)

    
