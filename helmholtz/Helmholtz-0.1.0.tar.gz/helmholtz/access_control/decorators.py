#encoding:utf-8
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from helmholtz.access_control.remote_connections import select_authority
from helmholtz.access_control.conditions import is_under_access_control, is_accessible_by

def permission_denied(request, *args, **kwargs):
    """Return the 'permission denied' page."""
    return render_to_response('permission_denied.html', context_instance=RequestContext(request))

def under_access_control(view_func):
    """
     Check if an entity is under access control.
    """
    def modified_function(obj, *args, **kwargs):
        if is_under_access_control(obj):
            return view_func(obj, *args, **kwargs)
        else:
            raise Exception("class %s%s is not under access control" % (obj.__class__.__module__, obj.__class__.__name__))       
    modified_function.__doc__ = view_func.__doc__
    return modified_function

def group_membership_required(*group_list):
    """
    Check if a user belongs to one of the groups supplied in
    group_list, and returns the permission_denied view otherwise.
    """
    def modified_view(view_func):
        def deny_permission_if_not_in_group(request, *args, **kwargs):
            if request.user.groups.filter(name__in=group_list).count():
                return view_func(request, *args, **kwargs)
            else:
                return permission_denied(request)       
        deny_permission_if_not_in_group.__doc__ = view_func.__doc__
        return deny_permission_if_not_in_group
    return modified_view

def create_or_update_foreign_user(main_group):
    """
    Check if a user is a member of a foreign authority
    and create or update the user into the local database :

    - main_group : defines the group that is the owner of the django server, necessary to make 
                   difference between people members of a laboratory and people members of an 
                   foreign one collaborating with it.
                   
    NB: the settings.py file must contain the 'AUTHORITIES' global variable initialized as follow :
    
    from helmholtz.access_control.remote_connection import ForeignAuthority
    
    AUTHORITIES = {'authority_1':('group_name_1','type','protocol','host_1','url_1'),
                   'authority_2':('group_name_2','type','protocol','host_2','url_2'),) 
    } 
    """
    def modified_view(view_func):
        def create_or_update_user(request, template_name):
            if request.method == 'POST' :    
                #test if the user is a facets member that is not in unic 
                username = request.POST['username']
                user_from_unic = User.objects.filter(username=username, groups__name=main_group)
                is_extern = (user_from_unic.count() < 1) 
                if is_extern :
                    password = request.POST['password']
                    #search the server where the user is authenticated
                    authority, access_possible = select_authority(settings.AUTHORITIES, username, password) 
                    if access_possible :
                        group, created = Group.objects.get_or_create(name=authority.group)
                        #if the authorization is detected create or update user 
                        try :
                            #if the user exists, ensure that django db stores the last user password
                            user = User.objects.get(username=username)
                            user.set_password(password) 
                        except :
                            #if the user does not exist, ensure that django db stores the new username and password
                            user = User.objects.create_user(username, '', password)
                        user.groups.add(group)
                        user.save() 
            return view_func(request, template_name)   
        return create_or_update_user
    return modified_view

def class_can_be_downloaded(app, type):
    """docstring needed"""
    def modified_view(view_func) :
        def redirect_if_not_authorized(request, *args, **kwargs) :
            ct = ContentType.objects.get(app_label=app, model=type.lower())
            try :
                uac_entity = ct.underaccesscontrolentity
            except :
                return permission_denied(request)
            if not uac_entity.can_be_downloaded :
                return permission_denied(request)
        return redirect_if_not_authorized
    return modified_view
