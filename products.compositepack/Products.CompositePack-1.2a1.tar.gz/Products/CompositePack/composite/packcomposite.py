##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: packcomposite.py 238389 2011-04-30 22:57:12Z hathawsh $
"""
from cgi import escape
from itertools import islice

from ZODB.POSException import ConflictError
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from ComputedAttribute import ComputedAttribute
from Globals import InitializeClass
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName

#from Products.Archetypes.public import *
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseFolder import BaseFolder
from Products.Archetypes.BaseFolder import BaseFolderMixin
from Products.Archetypes.BaseObject import MinimalSchema
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import SelectionWidget
from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.utils import shasattr
from Products.Archetypes import transaction_note

from Products.CompositePage.composite import Composite
from Products.CompositePage.composite import SlotGenerator
from Products.CompositePage.composite import SlotCollection
from Products.CompositePage.interfaces import ICompositeElement
from Products.CompositePage.slot import Slot
from Products.CompositePage.slot import getIconURL
from Products.CompositePage.slot import formatException
from Products.CompositePage.slot import target_tag

from Products.CompositePack.CPpermissions import AddPortalContent
from Products.CompositePack.CPpermissions import DesignCompo
from Products.CompositePack.CPpermissions import View
from Products.CompositePack.config import HAVEAZAX
from Products.CompositePack.config import PROJECTNAME
from Products.CompositePack.config import TOOL_ID
from Products.CompositePack.config import zmi_dir
from Products.CompositePack.design import _plone
from Products.CompositePack.exceptions import CompositePackError

plone_edit_template = PageTemplateFile('edit_tag.pt', _plone)
plone_add_target_template = PageTemplateFile('target_tag.pt', _plone)

actions = ({'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/cp_view',
            'permissions': (View,)
           },
           {'id': 'design',
            'name': 'Design',
            'action': 'string:${object_url}/design_view',
            'permissions': (DesignCompo,)
           },
           )

class PackSlot(Slot):
    """ """
    __occams_gestalt__ = 1  # This is some kind of Gocept versioning flag.
    meta_type = 'Pack Slot'
    security = ClassSecurityInfo()

    def _getPortalTypeName(self):
        # Overriden so we can call invokeFactory from inside here.
        # XXX Maybe subclass PloneFolder?
        return None

    security.declareProtected(AddPortalContent, 'invokeFactory')
    invokeFactory = BaseFolder.invokeFactory.im_func

    security.declareProtected(View, "renderGroups")
    def renderGroups(self, group_size=2, allow_add=True):
        """Iterates over the items rendering one item for each group.
        Each group contains an iterator for group_size elements.
        The last group may be padded out with empty strings.
        """
        it = self.renderIterator(allow_add)
        while 1:
            row = tuple(islice(it, group_size))
            if len(row) == group_size:
                yield row
            else:
                if row:
                    yield row + ('',) * (group_size - len(row))
                break

    security.declareProtected(View, "renderIterator")
    def renderIterator(self, allow_add=True):
        """Iterates over the items rendering one item for each element.
        
        Does minimal decoration of the rendered content.
        Exactly one yield for each item (including add/edit controls where required).
        If allow_add there will be one additional item yielded for the final add.
        """
        composite = aq_parent(aq_inner(aq_parent(aq_inner(self))))
        editing = composite.isEditing()
        items = self.objectItems()
        if editing:
            mypath = escape('/'.join(self.getPhysicalPath()))
            myid = self.getId()
            if hasattr(self, 'portal_url'):
                icon_base_url = self.portal_url()
            elif hasattr(self, 'REQUEST'):
                icon_base_url = self.REQUEST['BASEPATH1']
            else:
                icon_base_url = '/'

        for index, (name, obj) in enumerate(items):

            try:
                assert ICompositeElement.isImplementedBy(obj), (
                    "Not a composite element: %s" % repr(obj))
                text = obj.renderInline()
            except ConflictError:
                # Ugly ZODB requirement: don't catch ConflictErrors
                raise
            except:
                text = formatException(self, editing)

            if editing:
                if allow_add:
                    add = target_tag % (myid, index, mypath, index)
                else:
                    add = ''
                yield add + self._render_editing(obj, text, icon_base_url)
            else:
                yield text

        if editing and allow_add:
            index = len(items)
            yield target_tag % (myid, index, mypath, index)

    def _render_add_target(self, slot_id, index, path, obj_id=''):
        template = plone_add_target_template.__of__(self)
        if index==0:
            target_id = "%s_cp_top" % slot_id
        else:
            target_id = "%s_%s" % (slot_id, obj_id)
        result = template(slot_id=self.getId(),
                             slot_path=path,
                             index=index, target_id=target_id)
        return result

    def getTargetAfterViewlet(self, obj):
        index = self.getObjectPosition(obj.getId())
        path = escape('/'.join(self.getPhysicalPath()))
        return self._render_add_target(self.getId(), index+1, path, obj.getId())

    def _render_editing(self, obj, text, icon_base_url):
        path = escape('/'.join(obj.getPhysicalPath()))
        icon = ""
        title = ""
        allowed_viewlets_ids = ""
        allowed_viewlets_titles = ""
        current_viewlet_id = ""
        full_path = obj.absolute_url()
        try:
            current_viewlet_id = obj.getCurrentViewlet().getId()
            o2 = obj.dereference()
            icon = escape(getIconURL(o2, icon_base_url).encode('utf8'))
            title = escape(o2.title_and_id().encode('utf8'))
            composite_tool = getToolByName(self, TOOL_ID)
            viewlets_info = composite_tool.getViewletsFor(o2)

            allowed_viewlets = []
            if viewlets_info:
                default_id = viewlets_info['default']["id"]
                default_title = viewlets_info['default']["viewlet"].title_or_id()
                allowed_viewlets.append((default_id, default_title))
                for viewlet in viewlets_info['viewlets']:
                    allowed_viewlets.append((viewlet["id"],
                                             viewlet["viewlet"].title_or_id()))
            def vcmp(x, y):
                return cmp(x[1], y[1])
            allowed_viewlets.sort(vcmp)

            allowed_viewlets_ids = [v_id for v_id, v_title in allowed_viewlets]
            allowed_viewlets_ids = " ".join(allowed_viewlets_ids)
            allowed_viewlets_ids = allowed_viewlets_ids.encode('utf8')

            allowed_viewlets_titles = [v_title for v_id, v_title in allowed_viewlets]
            allowed_viewlets_titles = "%".join(allowed_viewlets_titles)
            allowed_viewlets_titles = allowed_viewlets_titles.encode('utf8')
        except:
            text = formatException(self, editing=1)
        template = plone_edit_template.__of__(self)
        result = template(source_path=path,
                             icon=icon,
                             title=title,
                             allowed_viewlets_ids=allowed_viewlets_ids,
                             allowed_viewlets_titles=allowed_viewlets_titles,
                             current_viewlet_id=current_viewlet_id,
                             full_path=full_path,
                             text=text)
        return result

    def getEditingViewlet(self, obj):
        if hasattr(self, 'portal_url'):
            icon_base_url = self.portal_url()
        elif hasattr(self, 'REQUEST'):
            icon_base_url = self.REQUEST['BASEPATH1']
        else:
            icon_base_url = '/'
        text = obj.renderInline()
        return self._render_editing(obj, text, icon_base_url)

        
InitializeClass(PackSlot)

class PackSlotCollection(SlotCollection):
    """ """
    meta_type = 'Pack Slot Collection'

InitializeClass(PackSlotCollection)

class PackTitleCollection(Folder):
    """ """
    meta_type = 'Pack Title Collection'
InitializeClass(PackTitleCollection)

class PackSlotGenerator(SlotGenerator):
    _slot_class = PackSlot
InitializeClass(PackSlotGenerator)

pc_schema = MinimalSchema + Schema((
    StringField('layout',
                accessor='getLayout',
                mutator='setLayout',
                vocabulary='_availableLayouts',
                enforceVocabulary=True,
                widget=SelectionWidget(label='Layout')),
    StringField('template_path',
                accessor='getTemplatePath',
                mutator='setTemplatePath',
                write_permission=DesignCompo,
                widget=StringWidget(label='Template Path'))
))

class PackComposite(Composite, BaseFolderMixin):
    """ """

    slots = PackSlotGenerator()
    security = ClassSecurityInfo()
    meta_type = portal_type = archetype_name = 'Pack Composite'
    filter_content_types  = 1
    allowed_content_types = ('Pack Slot Collection', 'Pack Title Collection')
    global_allow = 0

    schema = pc_schema

    def __init__(self, id='cp_container'):
        BaseFolderMixin.__init__(self, id)

    def _setPortalTypeName(self, pt):
        ret = BaseFolderMixin._setPortalTypeName(self, pt)
        self.initializeSlots()
        return ret

    def initializeSlots(self):
        if getattr(aq_base(self), 'filled_slots', None) is None:
            f = PackSlotCollection('filled_slots')
            self._setObject(f.getId(), f)
            self.generateSlots()
        if getattr(aq_base(self), 'titles', None) is None:
            f = PackTitleCollection('titles')
            self._setObject(f.getId(), f)

    def generateSlots(self):
        if self.getTemplatePath():
            Composite.generateSlots(self)

    manage_afterAdd = BaseFolderMixin.manage_afterAdd
    manage_beforeDelete = BaseFolderMixin.manage_beforeDelete
    manage_afterClone = BaseFolderMixin.manage_afterClone
    _notifyOfCopyTo = BaseFolderMixin._notifyOfCopyTo

    security.declareProtected(View, "parent")
    def parent(self):
        return aq_parent(aq_inner(self))
    parent = ComputedAttribute(parent, 1)


    def generateUniqueIdForCSS(self):
        new_id = self.generateUniqueId()
        new_id = ''.join(new_id.split('.'))
        return new_id

    security.declareProtected(View, "getPathFromPortalToParent")
    def getPathFromPortalToParent(self):
        purl = getToolByName(self, 'portal_url')
        return purl.getRelativeContentURL(self.parent)

    security.declareProtected(View, "getTemplate")
    def getTemplate(self):
        template_path = self.getTemplatePath()
        if not template_path:
            raise CompositePackError("No template set")
        parent_in_context = aq_parent(self)
        __traceback_info__ = (self, parent_in_context, template_path)
        return parent_in_context.restrictedTraverse(str(template_path))

    security.declareProtected('View', 'getLayout')
    def getLayout(self):
        field = self.getField('layout')
        layout_id = field.get(self)
        if not layout_id:
            layout_id = self.getDefaultLayout().id
            self.setLayout(layout_id)
        else:
            # check that layout does exist
            composite_tool = getToolByName(self, TOOL_ID)
            # if not, reset to default layout
            if not composite_tool.getLayoutById(layout_id):
                layout_id = self.getDefaultLayout().id
                self.setLayout(layout_id)
        return layout_id

    security.declareProtected(View, 'getDefaultLayout')
    def getDefaultLayout(self):
        composite_tool = getToolByName(self, TOOL_ID)
        return composite_tool.getDefaultLayoutForType(self.parent.portal_type)

    security.declarePrivate('setLayout')
    def setLayout(self, layout_id):
        composite_tool = getToolByName(self, TOOL_ID)
        layout = composite_tool.getLayoutById(layout_id)
        if layout is None:
            # An invalid layout has been passed. Set to default
            # layout.
            layout_id = self.getDefaultLayout().id
            transaction_note("Select default layout")
        else:
            transaction_note("Select '%s' layout" % layout.title_or_id())
        field = self.getField('layout')
        field.set(self, layout_id)
        self.setTemplatePath()

    security.declareProtected(DesignCompo, 'changeLayout')
    def changeLayout(self, layout_id):
        """Change Layout"""
        self.setLayout(layout_id)
        dest = self.parent.absolute_url() + "/design_view"
        return self.REQUEST.RESPONSE.redirect(dest)

    security.declareProtected(View, 'getTemplatePath')
    def getTemplatePath(self):
        """Get the template path"""
        field = self.getField('template_path')
        path = field.get(self)
        return path

    security.declareProtected(DesignCompo, 'setTemplatePath')
    def setTemplatePath(self, value=None):
        """Set the template path"""
        # Ignore passed in value. Get the template
        # path from the layout selected.
        layout_id = self.getLayout()
        composite_tool = getToolByName(self, TOOL_ID)
        layout = composite_tool.getLayoutById(layout_id)
        path = layout.getSkinMethod()
        template_path = "/".join(path.split('/')[:-1])
        template_id = path.split('/')[-1]
        field = self.getField('template_path')
        field.set(self, template_id)

    security.declareProtected(View, "haveAzax")
    def haveAzax(self):
        return HAVEAZAX

    security.declarePrivate('_availableLayouts')
    def _availableLayouts(self):
        composite_tool = getToolByName(self, TOOL_ID)
        layouts = [(o.Title(), o.getId())
                   for o in composite_tool.layouts.objectValues()]
        return DisplayList(layouts)

    def indexObject(self):
        '''composite container is never catalogued'''
        pass

    def reindexObject(self, idxs=[]):
        '''composite container is never catalogued'''
        pass

    def unindexObject(self):
        '''composite container is never catalogued'''
        pass

registerType(PackComposite, PROJECTNAME)

# methods monkeypatched ClassGen

def _setPortalTypeName(self, pt):
    ret = self.__cp__setPortalTypeName__(pt)
    self.cp_container.initializeSlots()
    return ret
_setPortalTypeName.__cp_method__ = True

def manage_afterAdd(self, item, container):
    if getattr(aq_base(self), 'cp_container', None) is None:
        composite = PackComposite()
        setattr(self, 'cp_container', composite)
        self.cp_container.initializeArchetype()
    composite = getattr(self, 'cp_container')
    self.__cp_manage_afterAdd__(item, container)
    composite.manage_afterAdd(composite, self)
manage_afterAdd.__cp_method__ = True

def manage_beforeDelete(self, item, container):
    composite = getattr(self, 'cp_container')
    composite.manage_beforeDelete(composite, self)
    self.__cp_manage_beforeDelete__(item, container)
manage_beforeDelete.__cp_method__ = True

def manage_afterClone(self, item):
    composite = getattr(self, 'cp_container')
    self.__cp_manage_afterClone__(item)
    composite.manage_afterClone(composite)
manage_afterClone.__cp_method__ = True

def _notifyOfCopyTo(self, container, op=0):
    """OFS.CopySupport notify
    """
    self.__cp__notifyOfCopyTo__(container, op=op)
    composite = getattr(self, 'cp_container')
    composite._notifyOfCopyTo(self, op=op)
_notifyOfCopyTo.__cp_method__ = True

def design_view(self):
    """design view for Plone
    """
    self.REQUEST.set('compositepack_design_view', True)
    return self.cp_container.design(ui='plone')
design_view.__cp_method__ = True

def cp_view(self):
    """Base view"""
    return self.cp_container()
cp_view.__cp_method__ = True

def check_spec(spec=None):
    if spec is not None:
        if isinstance(spec, basestring):
            spec=[spec]
    if (spec is None or
        PackComposite.meta_type in spec):
        return True
    return False

def objectIds(self, spec=None):
    ids = self.__cp_objectIds__(spec)
    if check_spec(spec) and shasattr(self, 'cp_container'):
        ids = list(ids) + ['cp_container']
    return ids
objectIds.__cp_method__ = True

manage_composite_contents = PageTemplateFile('compositeContents.pt',
        zmi_dir)
manage_composite_contents.__cp_method__ = True

methods = {
    '_setPortalTypeName':_setPortalTypeName,
    'manage_afterAdd':manage_afterAdd,
    'manage_beforeDelete':manage_beforeDelete,
    'manage_afterClone':manage_afterClone,
    'design_view':design_view,
    'cp_view':cp_view,
    'manage_composite_contents':manage_composite_contents,
    '_notifyOfCopyTo':_notifyOfCopyTo,
    'objectIds':objectIds,
}
