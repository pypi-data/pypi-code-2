from zope.interface import Interface
from zope import schema


districtTypes = (
    ('LOCAL', 'Local'),
    ('LOCAL_EXEC', 'Mayor'),
    ('STATE_LOWER', 'State House'),
    ('STATE_UPPER', 'State Senate'),
    ('STATE_EXEC', 'State Governor'),
    ('NATIONAL_LOWER', 'US House'),
    ('NATIONAL_UPPER', 'US Senate'),
    ('NATIONAL_EXEC', 'US President'),
    )

districtTypeVocab = schema.vocabulary.SimpleVocabulary(
    [schema.vocabulary.SimpleTerm(value, token=value, title=title) for value, title in districtTypes]
    )


class IInstanceSettings(Interface):

    label = schema.TextLine(
        title = u'Description of recipient',
        description = u'Displayed to the user prior to lookup.',
        default = u'Cicero Elected Official Lookup',
        )

    districtType = schema.Choice(
        title = u'Type of elected official',
        vocabulary = districtTypeVocab,
        )

    includeAtLarge = schema.Bool(
        title = u'Include at-large officials.',
        description = u'At-Large means the official represents a whole area, like a city or state rather than an individual district.',
        )


class ISharedSettings(Interface):

    allowed_states = schema.Set(
        title = u'Lookup-enabled states',
        description = u'If specified, address -> official lookups will only be performed for addresses in the listed states.  List one per line.',
        value_type = schema.TextLine(),
        required = False,
        )


class IRegistrySettings(ISharedSettings):
    pass


class ICiceroAddressLookup(IInstanceSettings, ISharedSettings):
    pass
