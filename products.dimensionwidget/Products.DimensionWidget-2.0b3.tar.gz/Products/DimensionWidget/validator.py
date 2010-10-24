from Products.validation.interfaces.IValidator import IValidator

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from zope.i18n import translate

try: # Plone 4 and higher
    import plone.app.upgrade
    USE_BBB_VALIDATORS = False
except ImportError: # BBB Plone 3
    USE_BBB_VALIDATORS = True

class PositiveDimensionValidator:
    """Validates a Dimension
    """
    if USE_BBB_VALIDATORS: 
        __implements__ = (IValidator,)
    else:
        implements(IValidator)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kw):
        error = str(_(u"Please enter a positive dimension"))
        try:
            int(value[0])
            int(value[1])
        except (ValueError, TypeError):
            return error
        if int(value[0]) < 0 or int(value[1]) < 0:
            return error
        return 1