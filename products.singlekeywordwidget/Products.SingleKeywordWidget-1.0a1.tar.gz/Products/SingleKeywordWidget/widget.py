from AccessControl import ClassSecurityInfo

from Products.Archetypes.Widget import KeywordWidget, TypesWidget
from Products.Archetypes.Registry import registerWidget

class SingleKeywordWidget(KeywordWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'format': "select", # possible values: select, radio
        'macro' : "singlekeyword",
        'vocab_source' : 'portal_catalog',
        'roleBasedAdd' : True,
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """process keywords from form where this widget has a list of
        available keywords and any new ones"""
        name = field.getName()
        value = form.get('%s_existing_keyword' % name, empty_marker)
        if value is empty_marker:
            value = ''
        new_keyword = form.get('%s_keyword' % name, empty_marker)
        if not new_keyword is empty_marker:
            value = new_keyword

        if not value and emptyReturnsMarker: return empty_marker

        return value, {}

registerWidget(SingleKeywordWidget,
               title='Single Keyword',
               description='Renders a HTML widget for choosing a sinle keyword',
               used_for=('Products.Archetypes.Field.StringField',)
               )
