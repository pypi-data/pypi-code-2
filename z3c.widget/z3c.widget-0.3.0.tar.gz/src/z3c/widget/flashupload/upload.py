from zope.app.container.interfaces import INameChooser
from ticket import validateTicket, invalidateTicket
from zope.security.interfaces import Unauthorized
from zope.publisher.browser import BrowserView
from zope import interface
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.security.proxy import removeSecurityProxy
from zope.filerepresentation.interfaces import IFileFactory
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.container.constraints import checkObject
from zope import event
from zope.app.component.interfaces import ISite

from z3c.widget.flashupload.interfaces import (IFlashUploadForm,
                                               IUploadFileView,
                                               FlashUploadedEvent)

try:
    from zc import resourcelibrary
    haveResourceLibrary = True
except ImportError:
    haveResourceLibrary = False


class FlashUploadVars(BrowserView):
    """simple view for the flashupload.pt
    to configure the flash upload swf"""

    allowedFileTypes = () # empty tuple for all file types



class UploadFile(object):
    """handles file upload for the flash client.
    flash client sends the data via post as u'Filedata'
    the filename gets sent as: u'Filename'
    """
    interface.implements(IUploadFileView)

    def __call__(self):
        ticket = self.request.form.get('ticket',None)

        url = None
        if ticket is None:
            # we cannot set post headers in flash, so get the
            # querystring manually
            qs = self.request.get('QUERY_STRING','ticket=')
            ticket = qs.split('=')[-1] or None
            if ticket is None:
                raise Unauthorized
        else:
            url = absoluteURL(self,self.request)
            if not validateTicket(url,ticket):
                raise Unauthorized
        invalidateTicket(url,ticket)
        if self.request.form.get('Filedata', None) is None:
            # flash sends a emtpy form in a pre request in flash version 8.0
            return ""
        fileUpload = self.request.form['Filedata']
        fileName = self.request.form['Filename']
        contentType = self.request.form.get('Content-Type',None)
        factory = IFileFactory(self.context)
        f = factory(fileName, contentType, fileUpload)

        # get the namechooser for the container by adapting the
        # container to INameChooser
        nameChooser = INameChooser(self.context)

        # namechooser selects a name for us
        name = nameChooser.chooseName(fileName, f)

        # check precondition
        checkObject(self.context, name, f)

        # store the file inside the container
        removeSecurityProxy(self.context)[name]=f

        event.notify(FlashUploadedEvent(f))
        return "filename=%s" %name


class UploadForm(BrowserView):
    """displays the swf for uploading files
    """

    template = ViewPageTemplateFile('uploadform.pt')
    interface.implements(IFlashUploadForm)

    @property
    def configUrl(self):
        return '%s/@@flashuploadvars.xml' % self.siteUrl

    @property
    def siteUrl(self):
        return absoluteURL(ISite(None), self.request)

    def __call__(self, *args, **kw):
        if haveResourceLibrary:
            resourcelibrary.need('z3c.widget.flashupload')
        return self.template(*args, **kw)

