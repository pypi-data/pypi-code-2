from zope.interface import implements

from Products.Archetypes import atapi

from Products.PloneServicesCenter.interfaces import ICaseStudy
from Products.PloneServicesCenter.content import Services

schema = Services.servicesSchema + atapi.Schema((

    atapi.TextField('body',
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=atapi.RichWidget(
            label="Detailed information",
            label_msgid="label_psc_detailed_info",
            description="Enter the details description about this case study.",
            description_msgid="help_casestudy_body",
            i18n_domain='ploneservicescenter',
            ),
        required=0,
        searchable=1,
        ),

    atapi.ImageField('logo',
        max_size=(150, 75),
        widget=atapi.ImageWidget(
            label="Logo",
            label_msgid="label_psc_logo",
            description="""\
Add a logo for the case study (normally the customer logo). Max 150x75
pixels (will be resized if bigger).""",
            description_msgid="help_casestudy_logo",
            i18n_domain='ploneservicescenter',
        ),
        ),

    atapi.ReferenceField('provider',
        relationship='providerToCaseStudy',
        allowed_types=('Provider',),
        vocabulary_display_path_bound=-1,
        vocabulary="getProvidersReferences",
        widget=atapi.ReferenceWidget(
            label="Provider",
            label_msgid="label_psc_provider_cat",
            description="""\
Select a provider from the below listing for the case study.""",
            description_msgid="help_casestudy_provider",
            i18n_domain='ploneservicescenter',
        ),
        ),

    ))


class CaseStudy(Services.BaseServicesContent):
    """Shows off a Plone site or project built for a customer."""

    implements(ICaseStudy)
    schema = schema
    archetype_name = "Case study"
    typeDescription = "Shows off a Plone site or project built for a customer."
    typeDescMsgId = "help_casestudy_archetype"

atapi.registerType(CaseStudy, 'PloneServicesCenter')
