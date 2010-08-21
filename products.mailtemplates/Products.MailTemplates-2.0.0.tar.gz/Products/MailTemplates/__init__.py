# Copyright (c) 2005-2010 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from AccessControl import allow_module,allow_class
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.PageTemplateFile import guess_type
from MailTemplate import MailTemplate
from types import ClassType
from urllib import quote

try:
    import Products.CMFCore
except ImportError:
    pass
else:
    import FSMailTemplate
    import Products.CMFCore.utils
    Products.CMFCore.utils.registerIcon(FSMailTemplate.FSMailTemplate,
                                        'www/fsmt.gif', globals())

def initialize( context ):
    context.registerClass(
        MailTemplate,
        # we use the same permission as page templates
        # in order to keep things simple.
        permission='Add Page Templates',
        constructors=(addMailTemplateForm,
                      addMailTemplate),
        icon='www/mt.gif',
        )

addMailTemplateForm = PageTemplateFile(
    'www/mtAdd',
    globals(),
    __name__='addMailTemplateForm'
    )
def addMailTemplate(self, id, mailhost=None, text='', encoding='utf-8',
                    REQUEST=None, submit=None):
    "Add a Mail Template with optional file content."

    filename = ''
    content_type = 'text/html'

    if REQUEST and REQUEST.has_key('file'):
        file = REQUEST['file']
        filename = file.filename
        text = file.read()
        headers = getattr(file, 'headers', None)
        if headers and headers.has_key('content_type'):
            content_type = headers['content_type']
        else:
            content_type = guess_type(filename, text) 


    else:
        if hasattr(text, 'read'):
            filename = getattr(text, 'filename', '')
            headers = getattr(text, 'headers', None)
            text = text.read()
            if headers and headers.has_key('content_type'):
                content_type = headers['content_type']
            else:
                content_type = guess_type(filename, text) 

    # ensure that we pass unicode to the constructor to
    # avoid further hassles with pt_edit()

    if not isinstance(text, unicode):
        text = unicode(text, encoding)

    mt = MailTemplate(id, text, content_type, output_encoding=encoding)
    self._setObject(id, mt)
    ob = getattr(self, id)
    if mailhost:
        ob._setPropValue('mailhost',mailhost)

    if REQUEST is not None:
        if submit == " Add and Edit ":
            u = ob.absolute_url()
        else:
            u = ob.aq_parent.absolute_url()
        REQUEST.RESPONSE.redirect(u+'/manage_main')
    else:
        return ob

# allow all the email module's public bits
import email
for name in email.__all__:
    path = 'email.'+name
    allow_module(path)
    try:
        mod = __import__(path)
    except ImportError:
        pass
    else:
        mod = getattr(mod,name)
        for mod_name in dir(mod):
            obj = getattr(mod,mod_name)
            if isinstance(obj,ClassType):
                allow_class(obj)
    
