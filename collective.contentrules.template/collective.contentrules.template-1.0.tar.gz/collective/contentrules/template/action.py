from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from zope.event import notify
from zope.lifecycleevent import ObjectCopiedEvent

import OFS.subscribers
from OFS.event import ObjectClonedEvent

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Acquisition import aq_base
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage

class ICopyFromTemplateAction(Interface):
    """An action used to create a new sub-object based on a template object.
    """
    
    source_object = schema.Choice(title=_(u"Source object"),
                                  description=_(u"As a path relative to the portal root."),
                                  required=True,
                                  source=SearchableTextSourceBinder({}, default_query='path:'))
    
    change_ownership = schema.Bool(title=_(u"Change ownership"),
                                   description=_(u"If selected, the newly created object will "
                                                  "have the same owner as the object that triggered "
                                                  "the content rule."),
                                   required=True,
                                   default=True)

    copy_children = schema.Bool(title=_(u"Copy children of selected content"),
                                   description=_(u"If selected, children of selected content  will be copied. "
                                                  "If not, the selected content itself will be copied "),
                                   default=False)
    
class CopyFromTemplateAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(ICopyFromTemplateAction, IRuleElementData)
    
    source_object = ''
    change_ownership = True
    copy_children = False
    
    element = 'collective.contentrules.template.CopyFromTemplate'
    
    @property
    def summary(self):
        return _(u"Copy from template at ${template}.",
                 mapping=dict(template=self.source_object))
    
class CopyFromTemplateActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, ICopyFromTemplateAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        self.portal_url = portal_url = getToolByName(self.context, 'portal_url', None)
        ct = getToolByName(self.context, 'portal_catalog', None)

        if portal_url is None:
            return False
        
        target = self.event.object
        
        path = self.element.source_object
        if len(path) > 1 and path[0] == '/':
            path = path[1:]

        if self.element.copy_children:
            if ct is None:
                return False
            paths = ct(path={'query': portal_url.getPortalPath() + self.element.source_object, 'depth': 1})
            ret = [self.copy_path(p.getPath(), target) for p in paths ]

            return ret

        return self.copy_path(path, target)

    def copy_path(self, path, target):
        obj = self.portal_url.getPortalObject().unrestrictedTraverse(str(path), None)
        
        if obj is None:
            self.error(obj, _(u"Source object ${source} does not exist.", mapping={'source' : path}))
            return False

        owner = obj.getOwnerTuple()[1]
        source_workflow_history = getattr(obj, 'workflow_history', {}).copy()
        
        try:
            obj._notifyOfCopyTo(target, op=0)
        except ConflictError:
            raise
        except Exception, e:
            self.error(obj, str(e))
            return False
            
        old_id = obj.getId()
        new_id = self.generate_id(target, old_id)
        
        orig_obj = obj
        obj = obj._getCopy(target)
        obj._setId(new_id)
        
        notify(ObjectCopiedEvent(obj, orig_obj))

        target._setObject(new_id, obj)
        obj = target._getOb(new_id)
        obj.wl_clearLocks()

        obj._postCopy(target, op=0)

        OFS.subscribers.compatibilityCall('manage_afterClone', obj, obj)
        
        notify(ObjectClonedEvent(obj))
        
        # Retain owner unless we're being asked to change it
        if self.element.change_ownership:
            owner = target.getOwnerTuple()[1]
        
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.changeOwnershipOf(obj, owner, recursive=True)
        
        # Copy workflow history
        obj.workflow_history = source_workflow_history
        
        # We changed the owner and workflow, so we need to re-index.
        obj.reindexObject()
        
        return True 
        
    def error(self, obj, error):
        request = getattr(self.context, 'REQUEST', None)
        if request is not None:
            title = utils.pretty_title_or_id(obj, obj)
            message = _(u"Unable to copy ${name} as part of content rule 'copy from template' action: ${error}",
                          mapping={'name' : title, 'error' : error})
            IStatusMessage(request).addStatusMessage(message, type="error")
            
    def generate_id(self, target, old_id):
        taken = getattr(aq_base(target), 'has_key', None)
        if taken is None:
            item_ids = set(target.objectIds())
            taken = lambda x: x in item_ids
        if not taken(old_id):
            return old_id
        idx = 1
        while taken("%s.%d" % (old_id, idx)):
            idx += 1
        return "%s.%d" % (old_id, idx)
        
class CopyFromTemplateAddForm(AddForm):
    """An add form for the action.
    """
    form_fields = form.FormFields(ICopyFromTemplateAction)
    form_fields['source_object'].custom_widget = UberSelectionWidget
    label = _(u"Add Copy from Template Action")
    description = _(u"An action to copy an template object into the current folder")
    form_name = _(u"Configure element")
    
    def create(self, data):
        a = CopyFromTemplateAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class CopyFromTemplateEditForm(EditForm):
    """An edit form for the action.
    """
    form_fields = form.FormFields(ICopyFromTemplateAction)
    form_fields['source_object'].custom_widget = UberSelectionWidget
    label = _(u"Edit Copy from Template Action")
    description = _(u"An action to copy an template object into the current folder")
    form_name = _(u"Configure element")
