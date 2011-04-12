# Copyright (c) 2004 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: Widget.py 236779 2011-04-01 05:51:02Z nilo $


from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget



class CountryWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'provideNullValue': 1,
        'nullValueTitle': '-',
        'macro': 'country_widgets/country',
        'omitCountries': None, # omit paramter for CountryTool.listAreas
        })

class MultiCountryWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
    'macro': 'country_widgets/multicountry',
    'omitCountries': None, # omit paramter for CountryTool.listAreas
    })

class AreaWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'provideNullValue': 1,
        'nullValueTitle': '-',
        'macro': 'country_widgets/area',
        })
    


registerWidget(CountryWidget,
               title="Country",
               description="Provides dropdown with pre-configured country list grouped by areas.",
               used_for=('Products.Archetypes.Field.StringField',))

registerWidget(MultiCountryWidget,
               title="MultiCountry",
               description="Provides dropdown with pre-configured country list grouped by areas. (Multiselect)",
               used_for=('Products.Archetypes.Field.LinesField',))
               
registerWidget(AreaWidget,
               title="Area",
               description="Provides dropdown with pre-configured area list.",
               used_for=('Products.Archetypes.Field.StringField',))


