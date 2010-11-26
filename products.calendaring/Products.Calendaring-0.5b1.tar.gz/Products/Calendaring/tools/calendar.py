# Calendaring is a simple CMF/Plone calendaring implementation.
# Copyright (C) 2004 Enfold Systems
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Some portions of this module are Copyright Shuttleworth Foundation.
# The original copyright statement is reproduced below.
#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2003 Shuttleworth Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
$Id: calendar.py,v 1.4 2005/01/25 01:03:49 dreamcatcher Exp $
"""
import warnings

from Products.CMFCalendar.CalendarTool import calendar
from OFS.PropertyManager import PropertyManager

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized

from Products.Archetypes.utils import mapply
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CalendarTool import CalendarTool as BaseTool

class CalendarTool(BaseTool, PropertyManager):
    """ A Calendar Tool implementation
    for import/export of events.
    """
    security = ClassSecurityInfo()

    event_type = 'Event'
    published_states = ('published',)
    _properties = getattr(BaseTool, '_properties', ()) + (
        {'id':'event_type', 'type': 'string', 'mode':'w'},
        {'id':'published_states', 'type': 'lines', 'mode':'w'},)

    manage_options = BaseTool.manage_options + PropertyManager.manage_options

    def __init__(self):
        if hasattr(BaseTool, '__init__'):
            # Plone 2.1 doesn't seem to have a __init__ anymore.
            BaseTool.__init__(self)

    security.declarePrivate('setMapping')
    def setMapping(self, name):
        warnings.warn("portal_calendar.setMapping has been deprecated."
                      "You do not need to call it anymore.",
                      DeprecationWarning, 2)

    security.declarePublic('getDestination')
    def getDestination(self):
        mt = getToolByName(self, 'portal_membership')
        dest = mt.getHomeFolder()
        if dest is None:
            # User does not have a home folder? Try portal and let it fail!
            pt = getToolByName(self, 'portal_url')
            dest = pt.getPortalObject()
        return dest

    security.declarePublic('importCalendar')
    def importCalendar(self, stream, dest=None, kw_map=None, do_action=False):
        from Products.Calendaring.marshaller import CalendarMarshaller
        mt = getToolByName(self, 'portal_membership')
        if mt.isAnonymousUser():
            raise Unauthorized
        if dest is None:
            dest = self.getDestination()
        marshaller = CalendarMarshaller()

        REQUEST = self.REQUEST
        RESPONSE = REQUEST.RESPONSE
        args = [dest, '']
        items = []
        kwargs = {'file':stream,
                  'context':self,
                  'items': items,
                  'REQUEST':REQUEST,
                  'RESPONSE':RESPONSE}
        mapply(marshaller.demarshall, *args, **kwargs)
        return items

    def exportCalendar(self, events=None, REQUEST=None):
        from Products.Calendaring.marshaller import CalendarMarshaller
        marshaller = CalendarMarshaller()

        ddata = marshaller.marshall(self, events=events,
                                    REQUEST=REQUEST,
                                    RESPONSE=None)
        content_type, length, data = ddata

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Type', content_type)
            REQUEST.RESPONSE.setHeader('Content-Length', length)
            REQUEST.RESPONSE.write(data)
        return data

    security.declarePublic('getPublishedStates')
    def getPublishedStates(self):
        return self.getProperty('published_states')

InitializeClass(CalendarTool)
