# -*- coding: utf-8 -*-

import dolmen.content
from dolmen.app.content import icon, IDescriptiveSchema
from dolmen.app.viewselector import IViewSelector
from menhir.contenttype.folder import MCFMessageFactory as _


class IFolder(IDescriptiveSchema, IViewSelector):
    """Schema interface for folders.
    """


class Folder(dolmen.content.OrderedContainer):
    icon('folder.png')
    dolmen.content.schema(IFolder)
    dolmen.content.name(_(u"Folder"))
    selected_view = "folderlisting"
