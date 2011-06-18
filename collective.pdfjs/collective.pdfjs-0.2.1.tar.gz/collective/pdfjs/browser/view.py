from zope.interface import implements

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.pdfjs import pdfjsMessageFactory as _
from collective.pdfjs.browser.interfaces import IInlinePDFView
from collective.pdfjs.browser.jstemplate import JSTemplateFile


class JavaScript(BrowserView):
    """
    Returns the reader javascript.
    """

    def __call__(self, request=None, response=None):
        tmpl = JSTemplateFile('javascripts/reader.js')
        jscode, _type = tmpl._read_file()
        self.request.response.setHeader("Content-type", _type)
        ref_path = self.request.HTTP_REFERER.split('/')
        dl_path = ["at_download", "file"]
        file_url = "/".join((ref_path[:-1] + dl_path))
        return jscode.replace("@@FILE_ABSOLUTE_URL@@", file_url )

class InlinePDFView(BrowserView):
    """
    Inline PDF View browser view
    """
    implements(IInlinePDFView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
