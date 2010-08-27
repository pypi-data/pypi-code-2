#encoding:utf-8
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.access_control.lifecycle import get_pk_type

def filter_by_permission_type(queryset, user, field):
    """Filter the specified queryset by permission type."""
    objects = queryset.all()
    arguments = {field:True}
    pk_type = get_pk_type(queryset.model)
    u_pks = [cast_object_to_leaf_class(k).object_id for k in getattr(user, "%s_user_permission_set" % ("integer" if (pk_type == int) else "char")).filter(**arguments) if (k.content_type.model_class() == queryset.model)]
    g_pks = list()
    for group in user.groups.all() :
        pks = [cast_object_to_leaf_class(k).object_id for k in getattr(group, "%s_group_permission_set" % ("integer" if (pk_type == int) else "char")).filter(**arguments) if (k.content_type.model_class() == queryset.model)]
        g_pks.extend(pks)
    if u_pks or g_pks :
        pks = list()
        if u_pks :
            pks.extend(u_pks)
        if g_pks :
            pks.extend(g_pks)
        if pks :
            objects = objects.filter(pk__in=pks) if pks else objects.none()
    else :
        objects = objects.none()
    return objects

def get_owned_by(queryset, user):
    """Return objects owned by the specified User."""
    return filter_by_permission_type(queryset, user, 'can_modify_permission')

def get_accessible_by(queryset, user):
    """Return objects that can be accessed by the specified User.""" 
    return filter_by_permission_type(queryset, user, 'can_view')

def get_deletable_by(queryset, user):
    """Return objects that can be deleted by the specified User.""" 
    return filter_by_permission_type(queryset, user, 'can_delete')

def get_downloadable_by(queryset, user):
    """Return objects that can be downloaded by the specified User.""" 
    return filter_by_permission_type(queryset, user, 'can_download')

def get_editable_by(queryset, user):
    """Return objects that can be modified by the specified User.""" 
    return filter_by_permission_type(queryset, user, 'can_modify')
