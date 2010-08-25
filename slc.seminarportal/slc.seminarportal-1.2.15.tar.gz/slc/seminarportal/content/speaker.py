from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.LinguaPlone.I18NOrderedBaseFolder import I18NOrderedBaseFolder
from Products.Relations.field import RelationField

from slc.seminarportal.config import PROJECTNAME
from slc.seminarportal.interfaces import ISpeaker
from slc.seminarportal.permissions import ASSIGN_SPEAKERS_TO_SPEECHES

SpeakerSchema =  atapi.OrderedBaseFolderSchema.copy() + atapi.Schema((
    atapi.StringField(
        name='firstName',
        widget=atapi.StringWidget(
            label=u"First Name",
            label_msgid='slc.seminarportal_label_firstName',
            i18n_domain='slc.seminarportal',
        ),
        required=True,
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='middleName',
        widget=atapi.StringWidget(
            label=u"Middle Name",
            label_msgid='slc.seminarportal_label_middleName',
            i18n_domain='slc.seminarportal',
        ),
        required=False,
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='lastName',
        widget=atapi.StringWidget(
            label=u"Last Name",
            label_msgid='slc.seminarportal_label_lastName',
            i18n_domain='slc.seminarportal',
        ),
        required=True,
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='suffix',
        widget=atapi.StringWidget(
            label=u"Suffix",
            description="Academic, professional, honorary, and social suffixes.",
            label_msgid='slc.seminarportal_label_suffix',
            description_msgid='slc.seminarportal_description_suffix',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='email',
        user_property=True,
        widget=atapi.StringWidget(
            label=u'Email',
            label_msgid='slc.seminarportal_label_email',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
        searchable=True,
        validators=('isEmail',)
    ),
    
    atapi.LinesField(
        name='jobTitles',
        widget=atapi.LinesField._properties['widget'](
            label=u"Job Titles",
            description="One per line",
            label_msgid='slc.seminarportal_label_jobTitles',
            description_msgid='slc.seminarportal_description_jobTitles',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
        searchable=True
    ),
    
    atapi.StringField(
        name='officeAddress',
        widget=atapi.TextAreaWidget(
            label=u"Office Street Address",
            label_msgid='slc.seminarportal_label_officeAddress',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
        searchable=True
    ),
    
    atapi.StringField(
        name='officeCity',
        widget=atapi.StringWidget(
            label=u"Office City",
            label_msgid='slc.seminarportal_label_officeCity',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
        searchable=True
    ),
    
    atapi.StringField(
        name='officeState',
        widget=atapi.StringWidget(
            label=u"Office State",
            label_msgid='slc.seminarportal_label_officeState',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default"
    ),
    
    atapi.StringField(
        name='officePostalCode',
        widget=atapi.StringWidget(
            label=u"Office Postal Code",
            label_msgid='slc.seminarportal_label_officePostalCode',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default"
    ),
    
    atapi.StringField(
        name='officePhone',
        widget=atapi.StringWidget(
            label=u"Office Phone",
            description="",
            label_msgid='slc.seminarportal_label_officePhone',
            description_msgid='slc.seminarportal_description_officePhone',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
        searchable=True,
    ),
    
    atapi.ImageField(
        name='image',
        schemata="default",
        widget=atapi.ImageWidget(
            label=u'Image',
            label_msgid='slc.seminarportal_label_image',
            i18n_domain='slc.seminarportal',
            default_content_type='image/gif',
            macro="seminarportal_image",
        ),
        original_size=(100, 125),
        sizes={'small': (50,50), 'thumb': (75, 75), 'normal': (200, 250)},
        default_output_type='image/jpeg',
        allowable_content_types=('image/gif','image/jpeg','image/png'),
    ),
    
    atapi.TextField(
        name='biography',
        widget=atapi.RichWidget(
            label=u'Biography',
            label_msgid='slc.seminarportal_label_biography',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        user_property='description'
    ),
    
    atapi.LinesField(
        name='education',
        widget=atapi.LinesField._properties['widget'](
            label=u'Education',
            label_msgid='slc.seminarportal_label_education',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='website',
        widget=atapi.LinesField._properties['widget'](
            label=u"Web Sites",
            label_msgid='slc.seminarportal_label_websites',
            description_msgid='slc.seminarportal_description_websites',
            i18n_domain='slc.seminarportal',
        ),
        schemata="default",
    ),
    RelationField(
        name='speeches',
        widget=ReferenceBrowserWidget(
            label=u'Speeches',
            description=u'Any speeches that this person \
            held or contributed to, can be added here. Please note that \
            speeches have to be created separately and for the seminar \
            at which they were held.',
            label_msgid='slc.seminarportal_label_speeches',
            i18n_domain='slc.seminarportal',
            base_query={'portal_type': 'SPSpeech', 'sort_on': 'sortable_title'},
            allow_browse=1,
            allow_search=1,
            show_results_without_query=1,
            image_portal_types=('SPSpeech',),
            image_method='bullet.gif',
        ),
        write_permission=ASSIGN_SPEAKERS_TO_SPEECHES,
        allowed_types=('Speech'),
        multiValued=1,
        relationship='speaker_speeches'
    ),
    atapi.StringField(
        name='nationality',
        widget=atapi.StringWidget(
            label=u"Nationality",
            label_msgid='slc.seminar_label_speaker_nationality',
            i18n_domain='slc.seminar',
        ),
    ),
    atapi.StringField(
        name='employer',
        widget=atapi.StringWidget(
            label=u"Employer",
            label_msgid='slc.seminar_label_speaker_employer',
            i18n_domain='slc.seminar',
        ),
    ),
    atapi.StringField(
        name='socialPartnerGroup',
        widget=atapi.StringWidget(
            name=u"Social Partner Group",
            label_msgid='slc.seminar_label_speaker_social_partner_group',
            i18n_domain='slc.seminar',
        ),
    ),
    atapi.TextField(
        name='expertise',
        widget=atapi.TextAreaWidget(
            name=u"Expertise",
            label_msgid='slc.seminar_label_speaker_expertise',
            i18n_domain='slc.seminar',
        ),
    ),
))

SpeakerSchema['title'].widget.label = 'Full Name' 
SpeakerSchema['title'].widget.visible = {'edit': 'invisible', 'view': 'visible'}

class SPSpeaker(I18NOrderedBaseFolder ):
    """ Speakers are people who hold speeches at seminars
    """
    implements(ISpeaker)

    meta_type = portal_type = "SPSpeaker"
    schema = SpeakerSchema
    security = ClassSecurityInfo()
    _at_rename_after_creation = True


    security.declareProtected(permissions.View, 'Title')
    def Title(self):
        """Return the Title as firstName middleName(when available) lastName, suffix(when available)"""
        try:
            # Get the fields using the accessors, so they're properly Unicode encoded.
            # We also can't use the %s method of string concatentation for the same reason.
            # Is there another way to manage this?
            fn = self.getFirstName()
            ln = self.getLastName()
        except AttributeError:
            return u"new person" # YTF doesn't this display on the New Person page?  # Couldn't call superclass's Title() for some unknown reason
        
        if self.getMiddleName():
            mn = " " + self.getMiddleName() + " "
        else:
            mn = " "
        
        t = fn + mn + ln
        if self.getSuffix():
            t = t + ", " + self.getSuffix()
        return t

    security.declareProtected(permissions.View, 'getSortableName')
    def getSortableName(self):
        """
        Return a tuple of the person's name. For sorting purposes
        Return them as lowercase so that names like 'von Whatever' sort properly
        """
        return (self.lastName.lower(), self.firstName.lower())


    def get_path(self):
        return '/'.join(self.getPhysicalPath()) 


atapi.registerType(SPSpeaker, PROJECTNAME)


