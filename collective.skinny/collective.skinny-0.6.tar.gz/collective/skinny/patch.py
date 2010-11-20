# We patch a 'standard_error_message' into the Plone site.  This frees
# us from having to register a skins directory to override the normal
# 'standard_error_message':
from Products.CMFPlone.Portal import PloneSite

def patch_standard_error_message():
    def standard_error_message(self, **kwargs):
        return self.restrictedTraverse('@@404.html')()
    PloneSite.standard_error_message = standard_error_message

patch_standard_error_message()

# Patch OFS.PropertyManager to return the empty list for
# 'typesUseViewActionInListings' if we're in the public skin.  This
# will allow images to have their Skinny view.
from zope.app.component.hooks import getSite
from OFS.PropertyManager import PropertyManager
from collective.skinny.interfaces import IPublicLayer

def patch_property_manager():
    _save_getProperty = PropertyManager.getProperty
    def getProperty(self, id, d=None):
        if (id == 'typesUseViewActionInListings' and
            IPublicLayer.providedBy(getSite().REQUEST)):
            return ()
        else:
            return _save_getProperty(self, id, d)
    PropertyManager.getProperty = getProperty

patch_property_manager()
