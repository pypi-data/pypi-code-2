#encoding:utf-8
from copy import copy
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group
from helmholtz.access_control.models import UnderAccessControlEntity, IntegerGroupPermission, CharGroupPermission, IntegerUserPermission, CharUserPermission 

#parameter useful for selecting the kind of Permission subclass
type_container = {int:{User:IntegerUserPermission,
                       Group:IntegerGroupPermission},
                  basestring:{User:CharUserPermission,
                              Group:CharGroupPermission}}

def put_class_under_access_control(cls):
    """Set a class under access control."""
    entity = ContentType.objects.get_for_model(cls)
    assert (entity.model != 'underaccesscontroltable') and (entity.app_label != "access_control"), "class %s.%s cannot be under access control" % (cls.__module__, cls.__name__)
    under_access_control_entity, created = UnderAccessControlEntity.objects.get_or_create(entity=entity)
    return under_access_control_entity, created

#to switch 
def get_pk_type(cls):
    """A convenient function to switch between Integer*Permission and Char*Permission."""
    if isinstance(cls._meta.pk, models.AutoField) or isinstance(cls._meta.pk, models.IntegerField) :
        pk_type = int
    elif isinstance(cls._meta.pk, models.CharField) or isinstance(cls._meta.pk, models.TextField) :
        pk_type = basestring
    elif isinstance(cls._meta.pk, models.OneToOneField) :
        pk_type = get_pk_type(cls._meta.pk.related.parent_model)
    else :
        raise Exception('Cannot manage permissions on object with a primary key type different from AutoField, IntegerField, CharField or TextField.')
    return pk_type  

#to get permissions
def get_permissions(obj, permission_type):
    """Return the permissions relative to an object and permission type."""
    content_type = ContentType.objects.get_for_model(obj)
    permissions = permission_type.objects.filter(content_type__pk=content_type.pk, object_id=obj.pk)
    return permissions

def get_user_permissions(obj):
    """Return the user permissions relative to an object."""
    pk_type = get_pk_type(obj.__class__)
    user_permission_type = type_container[pk_type][User]
    permissions = get_permissions(obj, user_permission_type)
    return permissions
    
def get_group_permissions(obj):
    """Return the group permissions relative to an object."""
    pk_type = get_pk_type(obj.__class__)
    group_permission_type = type_container[pk_type][Group]
    permissions = get_permissions(obj, group_permission_type)
    return permissions

def get_user_permission(obj, user):
    """Return the permission on an object relative to the specified user object."""
    all_permissions = get_user_permissions(obj)
    user_permissions = all_permissions.filter(user=user)
    if user_permissions.count() == 1 :
        return user_permissions[0]
    elif user_permissions.count() == 0 :
        return None
    else :
        raise Exception('user cannot have several permissions on the same object') 

def get_group_permission(obj, group):
    """Return the permission on an object relative to the specified group object."""
    all_permissions = get_group_permissions(obj)
    group_permissions = all_permissions.filter(group=group)
    if group_permissions.count() == 1 :
        return group_permissions[0]
    elif group_permissions.count() == 0 :
        return None
    else :
        raise Exception('group cannot have several permissions on the same object') 

#to create permissions
def create_user_permission(obj, user, **kwargs):
    """Create a new user permission on the specified object."""
    pk_type = get_pk_type(obj.__class__)
    user_permission_type = type_container[pk_type][User]
    user_permission_type.objects.create(user=user, object=obj, **kwargs)

def create_group_permission(obj, group, **kwargs):
    """Create a new group permission on the specified object."""
    pk_type = get_pk_type(obj.__class__)
    group_permission_type = type_container[pk_type][Group]
    group_permission_type.objects.create(group=group, object=obj, **kwargs)

def create_default_permissions(obj, owner):
    """Create a default permission for an object.
    
    NB: 
    
    - Only owner and admin group have a total access to the object.
    - Only File objects could have a can_download parameter set to True.
    """
    parameters = {'can_view':True,
                  'can_modify':True,
                  'can_delete':True,
                  'can_modify_permission':True,
                  'can_download':True if (obj.__class__.__name__ == 'File') else False}
    admin_group, created = Group.objects.get_or_create(name='admin')
    create_group_permission(obj, admin_group, **parameters)
    create_user_permission(obj, owner, **parameters)
    #add basic access to user groups 
    parameters = {'can_view':True,
                  'can_modify':False,
                  'can_delete':False,
                  'can_modify_permission':False,
                  'can_download':False}
    for group in owner.groups.all() :
        create_group_permission(obj, group, **parameters)

def update_permission_parameters(permission, **kwargs):
    """Update permission parameters."""
    for arg in kwargs :
        setattr(permission, arg, kwargs[arg])
    permission.save()

def set_group_permission(obj, group, **kwargs):
    """Set for the specified group the permission on an object."""
    permission = get_group_permission(obj, group)
    if permission :
        update_permission_parameters(permission, **kwargs)    
    else :
        create_group_permission(obj, group, **kwargs) 

def set_user_permission(obj, user, **kwargs):
    """Set for the specified user the permission on an object."""
    permission = get_user_permission(obj, user)
    if permission :
        update_permission_parameters(permission, **kwargs)    
    else :
        create_user_permission(obj, user, **kwargs)

def remove_permission(obj, to_remove):
    """Remove the group or user permission corresponding to the specified group or user and object."""
    if isinstance(to_remove, User) :
        permission = get_user_permission(obj, to_remove)
    else :
        permission = get_group_permission(obj, to_remove)     
    if permission  :
        permission.delete()
    else :
        raise Exception('%s has not any permissions on the object.' % to_remove)        
        
def remove_user_permissions(obj):
    """Remove all user permissions corresponding to a specified object."""
    user_permissions = get_user_permissions(obj)
    user_permissions.delete()

def remove_group_permissions(obj):
    """Remove all group permissions corresponding to a specified object."""
    group_permissions = get_group_permissions(obj)
    group_permissions.delete()

def remove_all_permissions(obj):
    """Remove all kinds of permissions corresponding to a specified object."""
    remove_user_permissions(obj)
    remove_group_permissions(obj)
