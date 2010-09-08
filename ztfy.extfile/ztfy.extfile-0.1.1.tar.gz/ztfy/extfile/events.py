### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
import transaction

# import Zope3 interfaces
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent, IObjectCopiedEvent

# import local interfaces
from ztfy.file.interfaces import IFilePropertiesContainer, IFilePropertiesContainerAttributes
from interfaces import IBaseExtFileInfo, IExtFileModifiedEvent, IExtFileAfterAddedEvent, IExtFileAfterModifiedEvent

# import Zope3 packages
from ZODB.blob import Blob
from zope.component import adapter
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent

# import local packages
from blob import BaseBlobFile


class ExtFileModifiedEvent(ObjectModifiedEvent):
    implements(IExtFileModifiedEvent)


class ExtFileAfterAddedEvent(ObjectEvent):
    implements(IExtFileAfterAddedEvent)


class ExtFileAfterModifiedEvent(ObjectEvent):
    implements(IExtFileAfterModifiedEvent)


def _commitDeletedExtFile(status, object):
    if status:
        object.commitDeletedFile()


@adapter(IBaseExtFileInfo, IObjectAddedEvent)
def handleNewExtFile(object, event):
    # When an external file is added, we define it's filename based on
    # it's parent, it's name and it's name chooser
    try:
        object.moveTempFile()
    except:
        object.deleteFile(temporary=True)
        transaction.get().addAfterCommitHook(_commitDeletedExtFile, kws={'object': object})
        raise
    notify(ExtFileAfterAddedEvent(object))


@adapter(IBaseExtFileInfo, IObjectModifiedEvent)
def handleModifiedExtFile(object, event):
    # When an external file is modified, we have to remove it's content data
    # and move the new file to it's final location like when object is created
    object.deleteFile()
    transaction.get().addAfterCommitHook(_commitDeletedExtFile, kws={'object': object})
    object.moveTempFile()
    notify(ExtFileAfterModifiedEvent(object))


@adapter(IBaseExtFileInfo, IObjectRemovedEvent)
def handleDeletedExtFile(object, event):
    # When an external file is removed, we remove the target file
    object.deleteFile()
    transaction.get().addAfterCommitHook(_commitDeletedExtFile, kws={'object': object})


@adapter(IFilePropertiesContainer, IObjectCopiedEvent)
def handleCopiedFilePropertiesContainer(object, event):
    # When an external file container is copied, we have to update it's blobs
    source = event.original
    for attr in IFilePropertiesContainerAttributes(source).attributes:
        value = getattr(source, attr, None)
        if isinstance(value, BaseBlobFile):
            getattr(object, attr)._blob = Blob()
            getattr(object, attr).data = value.data
