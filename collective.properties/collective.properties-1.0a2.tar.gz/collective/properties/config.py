import datetime

# property type collective.properties form knows how to handle
PROPERTY_TYPES = ('boolean', 'date', 'float', 'int', 'lines', 'long', 'string',
    'text', 'tokens', 'selection', 'multiple selection')
    
# textarea widget dimensions for text property types on manage properties form
TEXT_FIELD_WIDGET_DIMENSIONS = (60, 10)

# default datetime for date property type field
DEFAULT_DATE_VALUE = datetime.datetime(1984, 06, 17)
