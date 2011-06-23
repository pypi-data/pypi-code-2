# -*- coding:utf-8 -*-
import inspect
from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from zope.event import notify
from zope.app.container.contained import ObjectMovedEvent
from zope.app.container.contained import notifyContainerModified

import OFS.subscribers
from OFS.event import ObjectWillBeMovedEvent
from OFS.CopySupport import sanity_check

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

import transaction

from Acquisition import aq_inner, aq_parent, aq_base
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.contentrules.actions.move import MoveActionExecutor
from sc.contentrules.movebyattribute.interfaces import IMoveByAttributeAction
from sc.contentrules.movebyattribute import MessageFactory as _

class MoveByAttributeAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IMoveByAttributeAction, IRuleElementData)
    
    attribute = ''
    base_folder = ''
    element = 'sc.contentrules.movebyattribute.MoveByAttribute'
    
    @property
    def summary(self):
        return _(u'''Move the content to a folderish object inside ${folder},
                   based on value of attribute ${attribute}''',
                   mapping={'folder' : self.base_folder,
                            'attribute':self.attribute})
    


class MoveByAttributeActionExecutor(MoveActionExecutor):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IMoveByAttributeAction, Interface)
         
    def __call__(self):
        self._pstate = self.context.unrestrictedTraverse('@@plone_portal_state')
        self._portal = self._pstate.portal()
        self._portalPath = list(self._portal.getPhysicalPath())
        
        # Get event object
        obj = self.event.object
        
        attribute = self.element.attribute
        base_folder = self.element.base_folder
        
        # Get base folder object
        folder = self._base_folder(str(base_folder),obj)
        if folder is None:
            # Oopps... base folder object does not exist
            self.error(obj, _(u"Base folder ${target} does not exist.", mapping={'target' : base_folder}))
            return False
        
        # Get the attribute value
        try:
           value = self.valueFromAttribute(obj,attribute)
        except AttributeError:
            # Attribute not found or needed additional parameters
            self.error(obj, _(u"Attribute ${attribute} is not suitable for this object.", 
                            mapping={'attribute' : attribute}))
            return False
        except ValueError:
            # Attribute value was not str, unicode or int
            self.error(obj, _(u"Attribute ${attribute} did not provide a suitable value.", 
                            mapping={'attribute' : attribute}))
            return False
        
        if not value in folder.objectIds():
            # Destination folder do not exist
            self.error(obj, _(u"Id ${value} not found on ${target} folder.", 
                            mapping={'value' : value, 'target':folder}))
            return False
        
        destFolder = folder[value]
        if not destFolder.isPrincipiaFolderish:
            # Destination object is not a folder-like
            self.error(obj, _(u"Object with id ${value} in ${target} is not folderish.", 
                            mapping={'value' : value, 'target':folder}))
            return False
        destFolderRelPath = self._relPathToPortal(destFolder)
        
        self.element.target_folder = '/'.join(destFolderRelPath)
        return super(MoveByAttributeActionExecutor, self).__call__()
    
    def _relPathToPortal(self,obj):
        ''' Given an object we return it's relative path to portal
        '''
        portalPath = self._portalPath
        return list(obj.getPhysicalPath())[len(portalPath):]
    
    def _base_folder(self,base_folder,obj):
        ''' Given a base_folder string and the object triggering the event, we 
            return the base object to be used by this action
        '''
        # Large portions of this code came from Products.ATContentTypes
        # TODO: a package to deal with this kind of stuff (string to object?)
        portalPath = self._portalPath
        # sanitize a bit: you never know, with all those windoze users out there
        relPath = base_folder.replace("\\","/")
        
        if relPath[0]=='/':
            # someone didn't enter a relative path.
            # let's go with it
            path = relPath.split('/')[1:]
        else:
            folders = relPath.split('/')
            
            # set the path to the object path
            path = self._relPathToPortal(aq_parent(obj))
            
            # now construct an aboslute path based on the relative custom path
            # eat away from 'path' whenever we encounter a '..' in the relative path
            # apend all other elements other than ..
            for folder in folders:
                if folder == '..':
                    # chop off one level from path
                    if path == []:
                        # can't chop off more
                        # just return this path and leave the loop
                        break
                    else:
                        path = path[:-1]
                elif folder == '.': 
                    # don't really need this but for being complete
                    # strictly speaking some user may use a . aswell
                    pass # do nothing
                else:
                    path.append(folder)
        
        if not (path == []):
            # As we will traverse from portal, there is no need to
            # have its path in the way
            path = '/'.join(path)
            try:
                baseFolder = self._portal.unrestrictedTraverse(path)
            except AttributeError:
                baseFolder = None
            except KeyError:
                baseFolder = None
        else:
            baseFolder = self._portal
        return baseFolder
    
    def valueFromAttribute(self,obj,attribute):
        ''' Extract the value from the attribute '''
        if not hasattr(obj,attribute):
            raise AttributeError
        value = getattr(obj,attribute)
        if inspect.ismethod(value):
            try:
                value = value()
            except TypeError:
                # This attribute does not support our simple
                # instrospection
                raise AttributeError
        
        if isinstance(value,int):
            # If we get an integer, we simply
            # convert it to a string
            value = str(value)
        
        if isinstance(value,(str,unicode)):
            return value
        raise ValueError
    


class MoveByAttributeAddForm(AddForm):
    """ An add form for Move By Attribute action
    """
    form_fields = form.FormFields(IMoveByAttributeAction)
    label = _(u"Add Move by Attribute action")
    description = _(u"A content rule action to move an item based on a attribute value.")
    form_name = _(u"Configure element")

    def create(self, data):
        a = MoveByAttributeAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class MoveByAttributeEditForm(EditForm):
    """
    An edit form for Move By Attribute action
    """
    form_fields = form.FormFields(IMoveByAttributeAction)
    form_fields['base_folder'].custom_widget = UberSelectionWidget
    label = _(u"Edit Move by Attribute action")
    description = _(u"A content rule action to move an item based on a attribute value.")
    form_name = _(u"Configure element")

