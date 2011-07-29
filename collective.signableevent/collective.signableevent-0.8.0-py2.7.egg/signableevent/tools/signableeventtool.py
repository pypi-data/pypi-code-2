"""
FIXME

$Id: SignableEventTool.py 18 2008-01-18 17:23:23Z frederic.dupre $
"""

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import implements

from collective.signableevent.interfaces import ISignableEventTool
from collective.signableevent.workflowgraph import MultiWorkflowGraph
from collective.signableevent.csvsigners import exportSignersToCsv

import os

ID = 'portal_signable_event'
TITLE = 'Signable tool'
META_TYPE = 'SignableTool'

_www = os.path.join(os.path.dirname(__file__), '..', 'www')


class SignableEventTool(UniqueObject, SimpleItem, PropertyManager):
    """
    Tool for handling SignableEvent related features
    For now, only contains migration code, but later on may contain
    reminders, ...
    """
    id = ID
    title = TITLE
    meta_type = META_TYPE
    
    implements(ISignableEventTool)

    manage_options = (PropertyManager.manage_options +
                      ({ 'label'  : 'Migrate events',
                         'action' : 'manage_migrateEventsForm',
                         },)
                      + SimpleItem.manage_options)


    ## Security shortcuts
    security = ClassSecurityInfo()

    security.declareProtected("Manage portal", 'manage_migrateEventsForm')
    manage_migrateEventsForm = PageTemplateFile('manage_migrateEventsForm',
                                                _www)


    security.declareProtected("Manage portal", 'manage_migrateEvents')
    def manage_migrateEvents(self):
        """
	Migrate Eents to SignableEvents
        """
        commitsize = int(self.REQUEST.get("commitsize", "200"))
        delete = int(self.REQUEST.get("delete", "0"))
        signable = int(self.REQUEST.get("signable", "1"))
        end = self.REQUEST.get("end", "None")
        n = 0

        portal = getToolByName(self, "portal_url").getPortalObject()
        wftool = getToolByName(portal, "portal_workflow")
        wfgraph = MultiWorkflowGraph(portal)
        catalog = getToolByName(portal, "portal_catalog")
        brains = catalog(portal_type="Event")

        for brain in brains:
            n += 1
            obj = brain.getObject()
            objid = obj.getId()

            folder = obj.aq_inner.getParentNode()
            # First, rename old object
            oldid = objid
            i = 0
            while hasattr(folder, oldid):
                oldid = objid + ".old-%02d" % i
                i += 1
            obj.setId(oldid)

            # Then, create new object
            folder.invokeFactory("SignableEvent", objid)
            newobj = getattr(folder, objid)
            # Copy old attributes
            attrs = obj.schema.keys()
            for attr in attrs:
                if attr == "id":
                    continue
                try:
                    value = getattr(obj, attr)
                    if not callable(value):
                        setattr(newobj, attr, value)
                except AttributeError:
                    pass
            newobj.setDescription(obj.Description())
            newobj.setText(obj.getText())
            newobj.setCreators(obj.Creators())
            newobj.setSubject(obj.Subject())
            
            # Copy local roles
            for userid,roles in newobj.get_local_roles():
                newobj.manage_delLocalRoles([ userid ])
            for userid,roles in obj.get_local_roles():
                newobj.manage_setLocalRoles(userid, roles)
            # Set specific attributes
            newobj.setSignable(signable)
            if end == "start":
                newobj.setSignup_end_date(newobj.start())
            elif end == "end":
                newobj.setSignup_end_date(newobj.end())

            # Synchronize workflow
            state = wftool.getInfoFor(obj, "review_state")
            wfgraph.set_to(newobj, state)

            # Ensure the catalog is up to date
            newobj.reindexObject()
            
            # Finally, destroy old object if asked for
            if delete:
                folder.manage_delObjects([ oldid ])

            if n % commitsize  == 0:
                transaction.commit()
        
        return self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_migrateEventsForm?portal_status_message=%d+events+migrated' % n)

    def exportAllSignupCsv(self):
        pc = getToolByName(self,'portal_catalog')
        brains = pc.searchResults(portal_type='EventSignup')
        csvdata = exportSignersToCsv(brains)
        return csvdata


InitializeClass(SignableEventTool)
