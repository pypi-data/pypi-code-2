try:
    import Products.ATContentTypes
except ImportError:
    # XXX Don't require ATCT but if available importing here addresses a
    # bug in LinguaPlone: http://plone.org/products/linguaplone/issues/253
    pass

from backref import BackReferenceWidget
from backref import BackReferenceBrowserWidget
from backref import BackReferenceField

from Products.CMFCore import DirectoryView

DirectoryView.registerDirectory('skins', globals())
