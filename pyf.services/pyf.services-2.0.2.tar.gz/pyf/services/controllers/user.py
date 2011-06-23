from pyf.services.model import User, Group, Permission
from pyf.services.controllers.crud import (SecureCrudRestController, DataGrid,
                                     render_boolean, render_link_field,
                                     has_model_permission)
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller
from sprox.tablebase import TableBase

from pyf.services.controllers.crud import FancyTableFiller as TableFiller
from tg.decorators import expose

from tw.forms import TextField

from formencode.validators import Email

class UserController(SecureCrudRestController):
    model = User
    __order_by__ = 'user_name'
    __desc__ = False

    class new_form_type(AddRecordForm):
        __model__ = User
        __field_order__ = ['user_id', 'user_name', 'display_name', 'password',
                           'email_address', 'created', 'groups']
        __omit_fields__ = ['history', '_password']
        
        display_name = TextField('display_name')
        email_address = TextField('email_address',
                                  validator=Email(not_empty=True))

    class edit_form_type(EditableForm):
        __model__ = User
        __field_order__ = ['user_id', 'user_name', 'display_name', 'password',
                           'email_address', 'created', 'groups']
        
        display_name = TextField('display_name')
        email_address = TextField('email_address',
                                  validator=Email(not_empty=True))
        

    class edit_filler_type(EditFormFiller):
        __model__ = User

    class table_type(TableBase):
        __base_widget_type__ = DataGrid
        __model__ = User
        __omit_fields__ = ['history', '_password']
        __xml_fields__ = ['groups']
    
    class table_filler_type(TableFiller):
        __model__ = User
        
        groups = render_link_field('/groups/%s/edit', 'groups', 'group_name')
        
    @has_model_permission('edit')
    @expose('pyf.services.templates.user.edit')
    def edit(self, *args, **kwargs):
        return super(UserController, self).edit(*args, **kwargs)
        
#        layers = render_link_field('/layers/%s/edit', 'layers', 'display_name')
#        dispatchs = render_link_field('/dispatchs/%s', 'dispatchs', 'display_name')
#        active = render_boolean('active')
#        needs_source = render_boolean('needs_source')

class GroupController(SecureCrudRestController):
    model = Group
    __order_by__ = 'group_name'
    __desc__ = False

    class new_form_type(AddRecordForm):
        __model__ = Group

    class edit_form_type(EditableForm):
        __model__ = Group

    class edit_filler_type(EditFormFiller):
        __model__ = Group

    class table_type(TableBase):
        __base_widget_type__ = DataGrid
        __model__ = Group
        __xml_fields__ = ['permissions']
    
    class table_filler_type(TableFiller):
        __model__ = Group
        permissions = render_link_field('/permissions/%s/edit', 'permissions',
                                        'permission_name',
                                        display_name_property='permission_name')
        
class PermissionController(SecureCrudRestController):
    model = Permission
    __order_by__ = 'permission_name'
    __desc__ = False

    class new_form_type(AddRecordForm):
        __model__ = Permission

    class edit_form_type(EditableForm):
        __model__ = Permission

    class edit_filler_type(EditFormFiller):
        __model__ = Permission

    class table_type(TableBase):
        __base_widget_type__ = DataGrid
        __model__ = Permission
        __xml_fields__ = ['groups']
    
    class table_filler_type(TableFiller):
        __model__ = Permission
        groups = render_link_field('/groups/%s/edit', 'groups', 'group_name')