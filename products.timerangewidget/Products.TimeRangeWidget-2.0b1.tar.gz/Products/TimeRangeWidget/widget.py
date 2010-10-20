from Products.Archetypes.Widget import IntegerWidget
from types import ListType
from AccessControl import ClassSecurityInfo

from Products.TimeRangeWidget.utils import getListFromTimeRange

class TimeRangeWidget(IntegerWidget):
    _properties = IntegerWidget._properties.copy()
    _properties.update({
        'macro' : 'timerange_widget',
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=0,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""
        fname = field.getName()
        value = form.get(fname, empty_marker)
        if value is empty_marker:
            return empty_marker
        if isinstance(value, ListType):
            value = int(''.join(value))
        form[fname] = value
        return value, {}

    security.declarePublic('getFrom')
    def getFrom(self, value):
        return getListFromTimeRange(value)[0]

    security.declarePublic('getTo')
    def getTo(self, value):
        return getListFromTimeRange(value)[1]