# -*- coding: utf-8 -*-

from zope import interface, component
from p4a.subtyper import interfaces
from redturtle.subsites.backend.interfaces import ISubsiteRoot

class SubSiteDescriptor(object):
    interface.implements(interfaces.IPortalTypedFolderishDescriptor)
    title = u'Subsite'
    description = u'A subsite internal to the portal'
    type_interface = ISubsiteRoot
    for_portal_type = 'Folder'

component.provideUtility(SubSiteDescriptor(),
                         name=u'subsite')