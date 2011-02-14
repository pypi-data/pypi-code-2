# -*- coding: utf-8 -*-

import dolmen.content
from dolmen.app.content import icon, IDescriptiveSchema
from dolmen.app.viewselector import IViewSelector
from menhir.contenttype.folder import MCFMessageFactory as _
from zope.interface import implements
from zope.container.interfaces import IContainer


class IFolder(IContainer, IViewSelector):
    """Schema interface for folders.
    """


class Folder(dolmen.content.OrderedContainer):
    icon('folder.png')
    implements(IFolder)
    dolmen.content.schema(IDescriptiveSchema)
    dolmen.content.name(_(u"Folder"))

    selected_view = "folderlisting"
