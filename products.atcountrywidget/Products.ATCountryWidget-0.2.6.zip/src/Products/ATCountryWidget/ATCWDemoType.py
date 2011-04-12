#AT
from Products.Archetypes.public import registerType
from Products.Archetypes.public import BaseContent, StringField, Schema, BaseSchema

#siblings
from Products.ATCountryWidget.Widget import CountryWidget, AreaWidget, MultiCountryWidget

DemoSchema = BaseSchema + Schema ((
    StringField('country',
                widget=CountryWidget()),
    StringField('multicountry',
                widget=MultiCountryWidget()),
    StringField('area',
                widget=AreaWidget()),
))


class ATCWDemoType(BaseContent):
    schema = DemoSchema
    archetype_name = portal_type = meta_type = 'ATCWDemoType'

registerType(ATCWDemoType)
