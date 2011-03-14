from OFS.interfaces import IPropertyManager
from zExceptions import BadRequest

from zope.interface import implementedBy, Interface, Invalid
from zope import schema
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode

from z3c.form import field, button, form
from z3c.form.interfaces import DISPLAY_MODE, ITextAreaWidget, IErrorViewSnippet
from plone.z3cform.crud import crud
from plone.z3cform.layout import wrap_form

from collective.properties import messageFactory as _
from collective.properties.config import PROPERTY_TYPES, \
    TEXT_FIELD_WIDGET_DIMENSIONS
from collective.properties.propertytypes import PROPERTY_MAP, IProperty


class IsPropertyManagerView(BrowserView):
    """Checks if context object provides IPropertyManager interface"""
    
    def __call__(self):
        return IPropertyManager.providedBy(self.context)

class IAddProperty(Interface):

    id = schema.ASCIILine(
        title=_(u"Property Id"),
        description=u'',
        required=True)

    ptype = schema.Choice(
        title=_(u"Property Type"),
        description=u'',
        required=True,
        values=PROPERTY_TYPES,
        default='string')
    
    # TODO: add optional 'selection variable' string field for selection types

class EditSubForm(crud.EditSubForm):
    """Override this form to get different form for every property type
    and to have some widget a bit prettier.
    """
    
    @property
    def fields(self):
        # here we override update schema based on property type
        fields = field.Fields(self._select_field())

        crud_form = self.context.context
        
        # if we're aware of this property type then render it's
        # dedicated update form, otherwise render base property
        # update form w/o value field
        ptype = self.getContent().ptype
        if ptype in PROPERTY_MAP:
            update_schema = implementedBy(PROPERTY_MAP[ptype]).interfaces(
                ).next()
        else:
            update_schema = crud_form.update_schema
        
        if update_schema is not None:
            fields += field.Fields(update_schema)

        view_schema = crud_form.view_schema
        if view_schema is not None:
            view_fields = field.Fields(view_schema)
            for f in view_fields.values():
                f.mode = DISPLAY_MODE
                # This is to allow a field to appear in both view
                # and edit mode at the same time:
                if not f.__name__.startswith('view_'):
                    f.__name__ = 'view_' + f.__name__
            fields += view_fields

        return fields

    def updateWidgets(self):
        super(EditSubForm, self).updateWidgets()
        # enlarge all text field widgets
        for wid, widget in self.widgets.items():
            if ITextAreaWidget.providedBy(widget):
                widget.cols, widget.rows = TEXT_FIELD_WIDGET_DIMENSIONS

class EditForm(crud.EditForm):
    editsubform_factory = EditSubForm

class AddForm(crud.AddForm):

    @button.buttonAndHandler(_('Add'), name='add')
    def handle_add(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = form.AddForm.formErrorsMessage
            return
        try:
            item = self.context.add(data)
        except schema.ValidationError, e:
            # notify form about error so that status message will be
            # displayed in red and keep previously entered field values
            error = getMultiAdapter((Invalid(e), self.request, None,
                None, self, self.context.context), IErrorViewSnippet)
            error.update()
            self.widgets.errors += (error,)
            self.status = form.AddForm.formErrorsMessage
        else:
            notify(ObjectCreatedEvent(item))
            self.status = _(u"Item added successfully.")

class ManagePropertiesForm(crud.CrudForm):
    """Properties management view"""
    
    # default update_schema for those property types we're not aware of;
    # actually not used, instead we skip any property types we don't
    # have appropriate handlers for
    update_schema = IProperty
    
    # add schema is the same for all property types, we don't include
    # value field here and adding all property types with default predefined
    # values, so that user has to update it after addition
    add_schema = IAddProperty
    
    # we override it here in order to have different update schemas for
    # different property types
    editform_factory = EditForm
    
    # override add form to display validation problem as error message
    # during addition; currently standard CRUD form displays it as info
    # message
    addform_factory = AddForm
    
    def get_items(self):
        props = []
        get = self.context.getPropertyType
        for pid, pvalue in self.context.propertyItems():
            ptype = get(pid)
            
            # skip any non-defined property types
            if ptype not in PROPERTY_MAP:
                continue
            
            props.append((pid,
                PROPERTY_MAP[ptype](self.context, pid, pvalue, ptype)))
        
        return tuple(props)
    
    def add(self, data):
        # TODO: handle separately selection fields where we have one more field
        #       in add schema: selection variable
        ptype = data['ptype']
        
        # if we don't know how to handle this property type then try adding it
        # with empty string as default initial value
        if ptype not in PROPERTY_MAP:
            value = ''
        else:
            value = PROPERTY_MAP[ptype].default
        
        # catch all errors during property addition and display it in
        # user-friendly manner on form as invalid message
        try:
            self.context.manage_addProperty(data['id'], value, ptype)
        except Exception, e:
            raise schema.ValidationError(safe_unicode(e.args[0]))
    
    def remove(self, (id, item)):
        # TODO: check property mode and:
        #         * prohibit deletion if needed (disable checkbox)
        #         * prohibit update if needed (add readonly true to input)
        self.context._delProperty(id)

ManagePropertiesView = wrap_form(ManagePropertiesForm)
