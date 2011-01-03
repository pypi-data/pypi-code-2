# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from plone.app.blob.field import BlobField
from collective.flowplayercaptions.interfaces import IFlowplayerCaptionsLayer

from Products.Archetypes import atapi

from collective.flowplayer.interfaces import IVideo 
from collective.flowplayercaptions import captionsMessageFactory as _

class ExtensionBlobCaptionField(ExtensionField, BlobField):
    """ derivative of blobfield for extending schemas """


class CaptionsExtender(object):
    adapts(IVideo)
    implements(ISchemaExtender)

    fields = [
        ExtensionBlobCaptionField('captions',
            widget=atapi.FileWidget(
                label=_(u"Captions file"),
                description=_(u"caption_file_description",
                              default=u"The captions file in Subrip format, to be used for captioning"),
            ),
            required=False,
            schemata='subtitles',
            validators=('isNonEmptyFile'),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        if IFlowplayerCaptionsLayer.providedBy(self.context.REQUEST):
            return self.fields
        return []

