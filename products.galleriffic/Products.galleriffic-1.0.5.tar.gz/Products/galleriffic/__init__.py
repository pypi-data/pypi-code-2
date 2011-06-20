from zope.i18n import MessageFactory
AbstractGallerifficMessageFactory = MessageFactory('Products.galleriffic')
#
PLONE4 = 0
PLONE3 = 0

# Check for Plone 4.0 or above
try:
    from Products.CMFPlone.factory import _IMREALLYPLONE4
except ImportError:
    PLONE4 = 0
    PLONE3 = 1
else:
    PLONE4 = 1
    
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    pass