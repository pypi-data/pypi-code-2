from zope.interface import Interface
from zope import schema


class ICiceroSettings(Interface):
    
    userName = schema.ASCIILine(
        title = u'Cicero API Username'
        )
    
    password = schema.Password(
        title = u'Cicero API Password'
        )

    country = schema.ASCIILine(
        title = u'Default country for lookups',
        default = 'US'
        )
