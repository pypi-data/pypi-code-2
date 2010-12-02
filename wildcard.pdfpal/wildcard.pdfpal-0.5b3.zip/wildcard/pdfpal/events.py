from zope.component import getUtility
from logging import getLogger
from ocr import index_pdf
from thumbnail import create_thumbnails
from settings import PDFPalConfiguration

logger = getLogger('wc.pageturner')

try:
    from plone.app.async.interfaces import IAsyncService
    async_installed = True
except:
    async_installed = False

def handle_file_creation(object, event):
    if object.getContentType() not in ('application/pdf', 'application/x-pdf', 'image/pdf'):
        return

    config = PDFPalConfiguration(object)
        
    queued = False
    if async_installed:
        try:
            async = getUtility(IAsyncService)
            if config.ocr_enabled:
                job = async.queueJob(index_pdf, object)
            if config.thumbnail_gen_enabled:
                job = async.queueJob(create_thumbnails, object)
            queued = True
        except:
            logger.exception("Error using plone.app.async with wildcard.pdfpal. Converting pdf without plone.app.async...")
            
    if not queued: # using async didn't work. Do it manually.
        if config.ocr_enabled:
            index_pdf(object)
        if config.thumbnail_gen_enabled:
            create_thumbnails(object)