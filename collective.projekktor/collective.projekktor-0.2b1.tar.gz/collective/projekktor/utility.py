from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes.interfaces.field import IImageField
from Products.Archetypes.Field import ImageField
from Products.CMFCore.utils import getToolByName
from collective.projekktor.interfaces import IProjekktorUtility
from collective.projekktor.interfaces import IProjekktorVideoConfig
from collective.projekktor.interfaces import IProjekktorAudioConfig

from OFS.SimpleItem import SimpleItem

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('collective.projekktor')

def form_adapter(context):
    """Form Adapter"""
    return getUtility(IProjekktorUtility)

class ProjekktorUtility(SimpleItem):
    """Projekktor Utility"""
    implements(IProjekktorUtility)
    classProvides(
        IProjekktorVideoConfig,
        IProjekktorAudioConfig,
        )
    security = ClassSecurityInfo()

    video_mimetypes = FieldProperty(IProjekktorVideoConfig['video_mimetypes'])
    video_poster = FieldProperty(IProjekktorVideoConfig['video_poster'])
    video_width = FieldProperty(IProjekktorVideoConfig['video_width'])
    video_height = FieldProperty(IProjekktorVideoConfig['video_height'])


    audio_mimetypes = FieldProperty(IProjekktorAudioConfig['audio_mimetypes'])
    audio_poster = FieldProperty(IProjekktorAudioConfig['audio_poster'])
    audio_width = FieldProperty(IProjekktorAudioConfig['audio_width'])
    audio_height = FieldProperty(IProjekktorAudioConfig['audio_height'])

