from DateTime import DateTime

from zope.interface import implements

from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.event import ATEventSchema
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.Relations.field import RelationField

from slc.seminarportal import seminarportalMessageFactory as _
from slc.seminarportal.config import PROJECTNAME
from slc.seminarportal.interfaces import ISpeech

SpeechSchema = atapi.OrderedBaseFolderSchema.copy() + ATEventSchema.copy() + atapi.Schema((
    RelationField(
        name='speakers',
        widget=ReferenceBrowserWidget(
            label=u'Speakers',
            label_msgid='slc.seminarportal_label_speakers',
            i18n_domain='slc.seminarportal',
            base_query={'portal_type':'SPSpeaker', 'sort_on':'getSortableName'},
            allow_browse=1,
            allow_search=1,
            show_results_without_query=1,            
            image_portal_types=('SPSpeaker',),
            image_method='image_icon',
            macro='seminarportal_referencebrowser',
        ),
        allowed_types=('SPSpeaker',),
        multiValued=1,
        relationship='speech_speakers',
    ),
))

SpeechSchema['description'].widget.label = 'Abstract'
SpeechSchema['description'].widget.description = \
    'A short abstract, introduction or description of the speech'
SpeechSchema['text'].widget.label = \
    _(u'label_event_announcement', default=u'Conclusions')
SpeechSchema['text'].widget.macro = 'seminar_textarea'
SpeechSchema['location'].widget.label = \
    _(u'label_event_location', default=u'Location')
SpeechSchema['startDate'].widget.format = '%A %d %B %Y %H:%M'
SpeechSchema['startDate'].default_method = 'get_start_date'
SpeechSchema['endDate'].widget.format = '%A %d %B %Y %H:%M'
SpeechSchema['endDate'].default_method = 'get_end_date'

class SPSpeech(atapi.BaseFolder, ATEvent):
    """ Represents a Speech held during a seminar. 
    """ 
    implements(ISpeech)

    meta_type = portal_type = "SPSpeech"
    schema = SpeechSchema

    _at_rename_after_creation = True

    def get_path(self):
        return '/'.join(self.getPhysicalPath()) 

    def get_start_date(self):
        """ Returns the default start date for this speech.
            The default date is the date of the seminar.
        """
        # Use Acquisition to get the seminar's date.
        try:
            return self.get_seminar_start_date()
        except AttributeError:
            return DateTime()

    def get_end_date(self):
        """ Returns the default end date for this speech.
            The default date is the date of the seminar.
        """ 
        try:
            return self.get_seminar_end_date()
        except AttributeError:
            return DateTime()


atapi.registerType(SPSpeech, PROJECTNAME)

