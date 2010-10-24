from Products.validation.interfaces.IValidator import IValidator

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from Products.TimeRangeWidget.utils import getListFromTimeRange

from zope.interface import implements
from zope.i18n import translate

try: # Plone 4 and higher
    import plone.app.upgrade
    USE_BBB_VALIDATORS = False
except ImportError: # BBB Plone 3
    USE_BBB_VALIDATORS = True

class TimeRangeValidator:
    """Validates a timerange
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
        error = translate(_(u"Please enter a valid timerange"), context=kw['instance'].REQUEST)
        try:
            int(value)
        except (ValueError, TypeError):
            return error
        if int(value) == 0:
            return 1
        v = getListFromTimeRange(value)
        if int(v[0][0]) < int(v[1][0]) or (int(v[0][0]) == int(v[1][0]) and int(v[0][1]) < int(v[1][1])):
            return 1
        return error