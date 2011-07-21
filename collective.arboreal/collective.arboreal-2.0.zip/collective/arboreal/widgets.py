from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import MultiSelectionWidget, \
        SelectionWidget, TypesWidget
from Products.Archetypes.Registry import registerWidget

class MultiTreeSelectionWidget(MultiSelectionWidget):
    _properties = MultiSelectionWidget._properties.copy()
    _properties.update({
        'macro':'abr_multiselection_widget',
        'format':'checkbox', # One of checkbox, select, collapsed or finder
        })

    security = ClassSecurityInfo()
    
registerWidget(MultiTreeSelectionWidget,
               title='Multi Tree Selection',
               description=('Selection widget that allows you to select multiple items from an Arboreal tree.'),
               used_for=('Products.Arboreal.field.MultiArborealField',)
               )

class TreeSelectionWidget(SelectionWidget):
    _properties = MultiSelectionWidget._properties.copy()
    _properties.update({
        'macro':'abr_selection_widget'
        })

    security = ClassSecurityInfo()
    
registerWidget(TreeSelectionWidget,
               title='Tree Selection',
               description=('Selection widget that allows you to select one item from an Arboreal tree.'),
               used_for=('Products.Arboreal.field.SingleArborealField',)
               )

class ArborealLabledWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({'macro':'arboreallabled_widget'})

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """Basic impl for form processing in a widget"""
        lable = form.get(field.getName()+'_lable', empty_marker)
        text  = form.get(field.getName()+'_value', empty_marker)
        value = (lable, text)

        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == ():
            return empty_marker
        return value, {}

registerWidget(ArborealLabledWidget,
               title='Arboreal Labled widget',
               description=(
                   'This field has a text entry with a single Arboreal selection.'),
               used_for=('Products.Arboreal.field.ArborealLabledField',)
               )
