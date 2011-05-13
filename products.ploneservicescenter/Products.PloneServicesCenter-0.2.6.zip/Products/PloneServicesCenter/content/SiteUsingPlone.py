from zope.interface import implements

from Products.Archetypes import atapi

from Products.PloneServicesCenter.interfaces import ISiteUsingPlone
from Products.PloneServicesCenter.content import Services

schema = Services.servicesSchema + atapi.Schema((

    atapi.ReferenceField('provider',
        widget=atapi.ReferenceWidget(
            checkbox_bound=0,
            label="Provider",
            label_msgid="label_psc_provider_cat",
            description="""\
Select a provider from the below listing for the Site that Use Plone.""",
            description_msgid="help_siteuseplone_provider",
            i18n_domain='ploneservicescenter',),
        relationship='providerToSiteUsingPlone',
        allowed_types=('Provider',),
        vocabulary_display_path_bound=-1,
        vocabulary="getProvidersReferences",
        ),

    ))


class SiteUsingPlone(Services.BaseServicesContent):
    """Site using Plone.

    Not a full case study, but just a description and URL.
    """
    implements(ISiteUsingPlone)
    schema = schema
    archetype_name = "Site using Plone"
    typeDescription = """\
Site using Plone. Not a full case study, but just a description and URL."""
    typeDescMsgId = "help_siteuseplone_archetype"

atapi.registerType(SiteUsingPlone, 'PloneServicesCenter')
