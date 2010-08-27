#encoding:utf-8
from django.contrib.contenttypes.models import ContentType
from helmholtz.access_control.models import UnderAccessControlEntity
from helmholtz.access_control.lifecycle import get_user_permission, get_group_permission

def is_under_access_control(cls):
    """Return a boolean telling if a class is under access control."""
    entity = ContentType.objects.get_for_model(cls)
    uac_entity = UnderAccessControlEntity.objects.filter(entity=entity)
    return bool(uac_entity.count())

def respect_permission_type(obj, user, field):
    """Return a boolean telling if a user can access to an object."""
    if is_under_access_control(obj.__class__) :
        user_permission = get_user_permission(obj, user)
        if user_permission and getattr(user_permission, field) :
            return True
        for group in user.groups.all() :
            group_permission = get_group_permission(obj, group)
            if group_permission and getattr(group_permission, field) :
                return True
        return False  
    else :
        return True
        
def is_owner(obj, user):
    """Return a boolean telling if a user is one of the owners of an object."""
    return respect_permission_type(obj, user, 'can_modify_permission')

def is_accessible_by(obj, user):
    """Return a boolean telling if a user can access an object."""
    return respect_permission_type(obj, user, 'can_view')
        
def is_deletable_by(obj, user):
    """Return a boolean telling if a user can delete an object."""
    return respect_permission_type(obj, user, 'can_delete')

def is_downloadable_by(obj, user):
    """Return a boolean telling if a user can download an object."""
    return respect_permission_type(obj, user, 'can_download')

def is_editable_by(obj, user):
    """Return a boolean telling if a user can modify an object."""
    return respect_permission_type(obj, user, 'can_modify')
