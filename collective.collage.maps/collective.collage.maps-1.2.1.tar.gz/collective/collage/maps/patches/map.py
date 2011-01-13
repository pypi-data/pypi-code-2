# Patch the "enabled" method. This patch can be removed when a new
# Products.Maps (> 2.1.0) is released which contains changeset 228464
# (http://dev.plone.org/collective/changeset/228464/Products.Maps/trunk/Products/Maps/browser/map.py)

from Products.Maps.browser.map import FolderMapView

@property
def enabled(self):
    if self.map is None:
        return False
    return True

FolderMapView.enabled = enabled
