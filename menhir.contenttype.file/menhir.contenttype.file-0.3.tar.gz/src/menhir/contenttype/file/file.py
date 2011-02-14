# -*- coding: utf-8 -*-

import dolmen.content as content
from dolmen.file import FileField
from dolmen.blob import BlobProperty
from dolmen.app.content import icon, IDescriptiveSchema
from dolmen.app.security import content as security
from menhir.contenttype.file import MF as _


class IFile(IDescriptiveSchema):
    """A simple file object.
    """
    data = FileField(
        title=_(u"File"),
        required=True)


class File(content.Content):
    """A file content type storing the data in blobs.
    """
    icon("file.png")
    content.name(_(u"File"))
    content.schema(IFile)
    content.require(security.CanAddContent)

    data = BlobProperty(IFile['data'])
