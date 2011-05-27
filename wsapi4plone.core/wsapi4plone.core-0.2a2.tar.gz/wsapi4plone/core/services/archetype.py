import xmlrpclib

from DateTime import DateTime
from OFS.Image import File
from zope.component import adapts, getUtility
from zope.interface import implements
from zope.event import notify

from Products.ATContentTypes.interface.topic import IATTopic
from Products.Archetypes.BaseUnit import BaseUnit
from Products.Archetypes.interfaces import IBaseFolder, IBaseObject
from Products.Archetypes.event import ObjectInitializedEvent

# from interfaces import IService, IServiceContainer
from wsapi4plone.core.interfaces import IFormatQueryResults
from wsapi4plone.core.services import PloneService, PloneServiceContainer


class ATFolderService(PloneServiceContainer):
    adapts(IBaseFolder)
    # implements(IService)

    def create_object(self, type_name, id_):
        new_id = self.context.invokeFactory(type_name=type_name, id=id_)
        assert new_id == id_, "New id (%s) does not equal the excepted " \
                              "id (%s)." % (new_id, posted_id)
        entry = self.context.get(new_id)
        notify(ObjectInitializedEvent(entry))
        entry.at_post_create_script()
        return id_


class ATObjectService(PloneService):
    adapts(IBaseObject)
    # implements(IService)
