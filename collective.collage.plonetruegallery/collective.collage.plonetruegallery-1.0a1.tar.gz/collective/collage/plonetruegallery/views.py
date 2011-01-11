from collective.plonetruegallery.browser.views.galleryview import GalleryView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class CollageGalleryView(GalleryView):
    """ """
    template = ViewPageTemplateFile('gallery.pt')
