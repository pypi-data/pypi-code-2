from Products.Archetypes.Widget import TypesWidget
from AccessControl import ClassSecurityInfo

class DimensionWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : 'dimension_widget',
        'size' : '5',
        'maxlength' : '255',
        'blurrable' : True,
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""
        value = form.get(field.getName(), empty_marker)
        value[0] = str(value[0])
        value[1] = str(value[1])
        return value, {}

    security.declarePublic('getWidth')
    def getWidth(self, value):
        try:
            return int(value[0])
        except:
            return 0

    security.declarePublic('getHeight')
    def getHeight(self, value):
        try:
            return int(value[1])
        except:
            return 0