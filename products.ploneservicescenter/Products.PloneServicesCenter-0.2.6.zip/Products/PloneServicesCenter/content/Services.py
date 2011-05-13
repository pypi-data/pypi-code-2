from AccessControl import getSecurityManager

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ArchAddOn import public

from Products.PloneServicesCenter.validators import IndustriesValidator
from Products.PloneServicesCenter.content import country

servicesSchema = atapi.BaseSchema + atapi.Schema((

    atapi.StringField('description',
        accessor='Description',
        widget=atapi.TextAreaWidget(
            label='Description',
            label_msgid="label_psc_description",
            description='',
            description_msgid="help_psc_description",
            i18n_domain='ploneservicescenter',
            ),
        required=1,
        searchable=1,
        ),
    atapi.StringField('country',
        vocabulary=country.vocab,
        validateVocabulary=True,
        countries=country.countries,
        widget=atapi.SelectionWidget(
            label='Country',
            label_msgid="label_psc_country_cat",
            description='Select a country',
            description_msgid="help_services_country",
            i18n_domain='ploneservicescenter',
            macro_edit="country_widget"),
        required=0,
        index=('KeywordIndex:schema',),
        ),
    atapi.LinesField('industry',
        validators=IndustriesValidator('validateIndustries'),
        widget=atapi.MultiSelectionWidget(
            label="Industry",
            label_msgid="label_psc_industry_cat",
            description="Select a industry from the below list.",
            description_msgid="help_services_industry",
            i18n_domain='ploneservicescenter',
            ),
        required=0,
        vocabulary='getIndustryVocabulary',
        index=('KeywordIndex:schema',),
        ),
    public.LinkField('url',
        widget=public.LinkWidget(
            label="URL",
            label_msgid="label_services_url",
            description="""\
Enter the web address (URL). You can copy & paste this from a browser
window.""",
            description_msgid="help_services_url",
            i18n_domain='ploneservicescenter',
                ),
        required=1,
        ),
    atapi.IntegerField('rating',
        widget=atapi.SelectionWidget(
            format='select',
            label="Rating",
            label_msgid="label_services_rating",
            description="""\
Select a value of options from the below list by rating.""",
            description_msgid="help_services_rating",
            i18n_domain='ploneservicescenter',),
        required=1,
        default=2,
        vocabulary=atapi.IntDisplayList([(i, i) for i in range(1, 4)]),
        write_permission='Manage portal',
        index=('FieldIndex:schema',),
        ),

    atapi.StringField('contactName',
        widget=atapi.StringWidget(
            label="Contact Name",
            label_msgid="label_services_contactname",
            description="Enter the contact name.",
            description_msgid="help_services_contactname",
            i18n_domain='ploneservicescenter',
            ),
        required=0,
        searchable=1,
        index=('KeywordIndex:schema',),
        ),

    public.EmailField('contactEmail',
        widget=public.EmailWidget(
            label="Email",
            label_msgid="label_services_email",
            description="Enter the email for contacts.",
            description_msgid="help_services_email",
            i18n_domain='ploneservicescenter',
            ),
        required=0,
        searchable=1,
        index=('KeywordIndex:schema',),
        ),

    atapi.ComputedField('sortExpression',
        expression='''\
str(context.getRating()) + " " + str(context.Title()).lower()''',
        mode='r',
        index=('FieldIndex',),
        widget=atapi.StringWidget(
            label='Sort Expression',
            visible={'edit': 'invisible','view': 'invisible'},
            ),
        ),



    ))


class BaseServicesContent(base.ATCTContent):

    _getPossibleRatings = lambda x: range(1, 4)

    global_allow = 0
    _at_rename_after_creation = True

    allow_discussion = True

    def canSeeProvider(self):
        """
        Check if we are allowed to see the provider of the site
        """
        provider = self.getProvider()
        if not provider:
            return False
        user = getSecurityManager().getUser()
        return user.has_permission("View", provider)

    def getProvidersReferences(self):
        """
        Return a sorted list of references
        """
        field = self.getWrappedField('provider')
        providers = list(field._Vocabulary(self).items())
        providers.sort(lambda a, b: cmp(a[1].lower(), b[1].lower()))
        return atapi.DisplayList(providers)

    def getCountry(self, **kw):
        # BBB lowercase to tolerate uppercase values from plone.net
        value = self.getField('country').get(self, **kw)
        if isinstance(value, (str, unicode)):
            return value.lower()
        return value
