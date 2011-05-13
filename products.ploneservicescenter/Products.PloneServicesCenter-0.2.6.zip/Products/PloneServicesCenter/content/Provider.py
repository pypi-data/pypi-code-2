from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from zope.interface import implements

from Products.PloneServicesCenter.interfaces import IProvider
from Products.PloneServicesCenter import PSCMessageFactory as _
from Products.PloneServicesCenter.content import Services


schema = Services.servicesSchema.copy() + atapi.Schema((

    atapi.BooleanField('goodCompany',
        write_permission='Manage portal',
        read_permission='Manage portal',
        widget=atapi.BooleanWidget(
                     label="Good Company?",
                     label_msgid="label_provider_goodcompany",
                     description="""\
Check if this flag if the company is considered to be a good-behaving,
ethical company.""",
                     description_msgid="help_provider_goodcompany",
                     i18n_domain='ploneservicescenter',
                     ),
                 ),

    atapi.ImageField('logo',
        max_size=(150, 75),
        widget=atapi.ImageWidget(
                   label="Logo",
                   label_msgid="label_psc_logo",
                   description="""\
Add a logo for the project (or organization/company) by clicking the
'Browse' button. Max 150x75 pixels (will be resized if bigger).""",
                   description_msgid="help_provider_logo",
                   i18n_domain='ploneservicescenter',
                          ),
        ),

    atapi.TextField('body',
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=atapi.RichWidget(
                   label="Detailed information",
                   label_msgid="label_psc_detailed_info",
                   description="""\
Enter the details description about this provider.""",
                   description_msgid="help_provider_body",
                   i18n_domain='ploneservicescenter',
                         ),
        required=0,
        searchable=1,
        ),

    atapi.IntegerField('employees',
        widget=atapi.IntegerWidget(
                        label="Confidential: Number of employees",
                     label_msgid="label_provider_numemployees",
                     description="""\
Number of full-time employees (Used for statistical purposes only,
will never be made public)""",
                     description_msgid="help_provider_numemployees",
                     i18n_domain='ploneservicescenter',
                            ),
        validators=('isInt',),
        read_permission='Manage portal',
        ),

    atapi.IntegerField('annualRevenues',
        widget=atapi.IntegerWidget(
                        label="Confidential: Annual revenues",
                     label_msgid="label_provider_annualrevenues",
                     description="""\
Estimate in USD (Used for statistical purposes only, will never be
made public)""",
                     description_msgid="help_provider_annualrevenues",
                     i18n_domain='ploneservicescenter',
                            ),
        validators=('isInt',),
        read_permission='Manage portal',
        ),

    atapi.BooleanField('fullTimePlone',
        widget=atapi.BooleanWidget(
                        label="Confidential: Full Time Plone",
                     label_msgid="label_provider_fulltime",
                     description="""\
Are Plone services the majority of your income? (Used for statistical
purposes only, will never be made public)""",
                     description_msgid="help_provider_fulltime",
                     i18n_domain='ploneservicescenter',
                            ),
        read_permission='Manage portal',
        ),

    atapi.BooleanField('sponsor',
        accessor='isSponsor',
        write_permission='Review portal content',
        widget=atapi.BooleanWidget(
                        label="Is this company a sponsor?",
                     label_msgid="label_provider_companysponsor",
                     description="",
                     description_msgid="help_provider_companysponsor",
                     i18n_domain='ploneservicescenter',
                            ),
        index=('FieldIndex:schema',),
        ),

    atapi.BooleanField('premium',
        accessor='isPremium',
        write_permission='Review portal content',
        widget=atapi.BooleanWidget(
                        label="Is this company a premium sponsor?",
                     label_msgid="label_provider_premiumsponsor",
                     description="",
                     description_msgid="help_provider_premiumsponsor",
                     i18n_domain='ploneservicescenter',
                            ),
        index=('FieldIndex:schema',),
        ),

    atapi.StringField('companySize',
        vocabulary='getCompanySizes',
        widget=atapi.SelectionWidget(
                           label="What is the size of the company?",
                       label_msgid="label_provider_companysize",
                       description="",
                       description_msgid="help_provider_companysize",
                       i18n_domain='ploneservicescenter',
                              ),
        ),



    ))

schema['subject'].isMetadata = False
schema['subject'].vocabulary = 'availableServices'
schema.changeSchemataForField('subject', 'default')
schema['subject'].widget = atapi.MultiSelectionWidget(
    format='checkbox',
    label=u'Provided Services',
    description=u'Select all the services the provider offers.')

del schema['industry']
del schema['rating']


class Provider(Services.BaseServicesContent):
    """A company or organization that offers Plone services."""

    implements(IProvider)
    schema = schema

    archetype_name = "Provider"
    typeDescription = "A company or organization that offers Plone services."
    typeDescMsgId = "help_provider_archetype"

    def getCompanySizes(self):
        """
        Get the available company sizes
        Hardcoded for now, but may change later on
        """
        return atapi.DisplayList([("none", _(u"none")),
                                     ("small", _(u"small")),
                                     ("medium", _(u"medium")),
                                     ("large", _(u"large"))])

    def getCaseStudies(self, check_perm=1, **kwargs):
        """
        Return case studies of this provider, orderd by their title (by
        default)
        """

        cases = self._getReferences('providerToCaseStudy', **kwargs)

        if check_perm:
            checkPerm = self.portal_membership.checkPermission
            cases = [c for c in cases if checkPerm('View', c)]

        return cases

    def getSitesUsingPlone(self, check_perm=1, **kwargs):
        """
        Return sites of this provider

        By default, sites are ordered by their title (by default).
        """
        sites = self._getReferences('providerToSiteUsingPlone', **kwargs)

        if check_perm:
            checkPerm = self.portal_membership.checkPermission
            sites = [s for s in sites if checkPerm('View', s)]

        return sites

    def _getReferences(self, relationship, **kwargs):
        """
        Return objects which reference this provider

        Objects are sorted by the title of the object (if there is no
        'sort_on' key in **kwargs). Note that **kwargs is actually
        only provided to the second catalog query. (It is useless to
        provide it to both catalogs, since they likely have different
        indexes.)
        """
        ref_catalog = getToolByName(self, 'reference_catalog')
        refs = ref_catalog.searchResults(targetUID=self.UID(),
                         relationship=relationship)
        if not refs:
            return ()

        refs = [ref.sourceUID for ref in refs]
        uid_catalog = getToolByName(self, 'uid_catalog')
        if 'sort_on' not in kwargs:
            kwargs['sort_on'] = 'Title'
        brains = uid_catalog.searchResults(UID=refs, **kwargs)
        return [b.getObject() for b in brains]

    def __str__(self):
        return self.title_or_id()

    def getSortExpression(self):
        """
        We need to override that
        """
        value = self.Title().lower()
        premium = self.isPremium()
        premium = premium and "1-" or "2-"
        return premium + value

    def getCssClasses(self):
        """
        Get css classes to render ourself
        """
        classes = ["listing-provider level2"]
        if self.isSponsor():
            classes.append("sponsor")
        if self.isPremium():
            classes.append("premium-sponsor")
        return " ".join(classes)

    def availableServices(self):
        return aq_parent(self).Subject()

    def Subject(self, **kw):
        # BBB the deprecated "hostingProvider" field
        value = self.getField('subject').get(self, **kw)
        if (self.__dict__.get('hostingProvider') and
            "Hosting provider" not in value):
            value += ("Hosting provider",)
        return value
    getRawSubject = Subject

atapi.registerType(Provider, 'PloneServicesCenter')
