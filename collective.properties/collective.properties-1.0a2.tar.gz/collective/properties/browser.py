from OFS.interfaces import IPropertyManager
from zExceptions import BadRequest

from zope.interface import implementedBy, Interface, Invalid
from zope import schema
from zope.schema.interfaces import IBytesLine, IBytes, IChoice
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode

from z3c.form import field, button, form
from z3c.form.interfaces import DISPLAY_MODE, ITextAreaWidget, IErrorViewSnippet
from z3c.form.browser.textarea import TextAreaFieldWidget
from plone.z3cform.crud import crud
from plone.z3cform.layout import wrap_form

from collective.properties import messageFactory as _
from collective.properties.config import PROPERTY_TYPES, \
    TEXT_FIELD_WIDGET_DIMENSIONS
from collective.properties.propertytypes import PROPERTY_MAP, IProperty
from collective.properties.widget import SpecialSelectFieldWidget, \
    SpecialSequenceSelectFieldWidget
from collective.properties.field import IBytesLineTuple


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
    
    select_variable = schema.ASCIILine(
        title=_(u"Select Variable"),
        description=_(u"This field is used only for selection and multiple "
                      "selection property types. It provides the name of a "
                      "property or method which returns a list of strings from "
                      "which the selection can be chosen."),
        required=False,
        default='')

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

        # assign custom widget factories
        for fid, f in fields.items():
            # assign textarea widget to IBytes field, we deliberately
            # keep all string in bytes instead of unicode to be compliant
            # with old good IPropertyManager API
            if IBytes.providedBy(f.field) and \
               not IBytesLine.providedBy(f.field):
                f.widgetFactory = TextAreaFieldWidget
            
            # assign SpecialSelectWidget to Choice fields to prevent breakage on
            # values that are not within current widget terms
            if IChoice.providedBy(f.field):
                f.widgetFactory = SpecialSelectFieldWidget
            
            # assign SpecialSequenceSelectFieldWidget to IBytesLineTuple fields
            # with IChoice field as it's value_type
            if IBytesLineTuple.providedBy(f.field) and \
               IChoice.providedBy(f.field.value_type):
                f.widgetFactory = SpecialSequenceSelectFieldWidget

        return fields

    def updateWidgets(self):
        super(EditSubForm, self).updateWidgets()
        # customize field widgets a bit
        for wid, widget in self.widgets.items():
            # enlarge all text field widgets
            if ITextAreaWidget.providedBy(widget):
                widget.cols, widget.rows = TEXT_FIELD_WIDGET_DIMENSIONS
        
        # disable 'delete' checkbox for non-deletable properties
        mode = self.getContent().mode
        if 'd' not in mode:
            # deselect and disable checkbox
            select = self.widgets['select']
            select.value = ()
            select.disabled = 'disabled'
            # need to update checkbox widget in order to get updated value
            select.update()
        
        # 'value' field set to readonly mode for non-writable properties
        if 'w' not in mode:
            # set to readonly mode
            value = self.widgets['value']
            value.readonly = 'readonly'

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
    
    label = _(u"Manage Properties Form")
    description = _(u"On this form you can add, update and delete "
                    "IPropertyManager related properties for this context "
                    "object. To add property use Adding form at the bottom of "
                    "this page. Firstly fill in property id and pick up it's "
                    "type and only after it's added you'll be able to fill it's"
                    " value in. For selection property types you'll also need "
                    " to enter it's select variable (it provides the name of a "
                    "property or method which returns a list of strings from "
                    "which the selection(s) can be chosen). Some properties "
                    "could be protected so that you won't be able to remove or "
                    "update it. For non-deletable properties 'select' checkbox "
                    "is disabled, and for non-writable ones 'Property Value' "
                    "input is in 'readonly' mode. For more info on property "
                    "types you can manage here, please, refer to "
                    "collective.properties package README.txt.")
    
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
        """Return list of properties assigned to context object."""
        props = []
        context = self.context
        get = context.getPropertyType
        propsdict = context.propdict()
        for pid, pvalue in context.propertyItems():
            ptype = get(pid)
            
            # skip any non-defined property types
            if ptype not in PROPERTY_MAP:
                continue
            
            props.append((pid,
                PROPERTY_MAP[ptype](context, pid, pvalue, ptype,
                    propsdict[pid].get('select_variable'),
                    propsdict[pid].get('mode', 'wd'))))
        
        return tuple(props)
    
    def add(self, data):
        """Adds new property with default value."""
        ptype = data['ptype']
        
        # prepare initial property value based on it's type
        if ptype in ('selection', 'multiple selection'):
            # for selection types initial value will be set by PropertyManager
            # and in a value we should pass to it select_variable to get list
            # of available value options to choose from
            value = data['select_variable']
            if value is None:
                value = ''
        elif ptype not in PROPERTY_MAP:
            # if we don't know how to handle this property type then try adding
            # it with empty string as default initial value
            value = ''
        else:
            # get default value
            value = PROPERTY_MAP[ptype].default
        
        # catch all errors during property addition and display it in
        # user-friendly manner on form as invalid message
        try:
            self.context.manage_addProperty(data['id'], value, ptype)
        except Exception, e:
            raise schema.ValidationError(safe_unicode(e.args[0]))
    
    def remove(self, (id, item)):
        """Removes existing property from context object."""
        context = self.context
        if 'd' not in item.mode or id in context._reserved_names:
            raise schema.ValidationError(u"The property '%s' can not be "
                "deleted." % id)
        context._delProperty(id)

ManagePropertiesView = wrap_form(ManagePropertiesForm)
