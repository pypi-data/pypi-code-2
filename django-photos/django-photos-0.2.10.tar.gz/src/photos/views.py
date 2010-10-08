from photos.models import Photo, Album
from django.contrib.auth.models import User
from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import get_object_or_404

def album_list(request, user_id=0, username=None, *args, **kwargs):
    qs = Album.objects.filter(display=True)
    user = None
    
    if user_id > 0:
        user = get_object_or_404(User, id=user_id)
        qs = qs.filter(user=user)
    elif username is not None:
        user = get_object_or_404(User, username=username)
        qs = qs.filter(user=user)
    
    if user:
        extra_context = kwargs.get('extra_context', {})
        extra_context.update({'album_user': user})
        kwargs.update({'extra_context': extra_context})
    
    return object_list(request, queryset=qs, *args, **kwargs)

def photo_list(request, user_id=0, username=None, *args, **kwargs):
    qs = Photo.objects.filter(display=True)
    user = None
    
    if user_id > 0:
        user = get_object_or_404(User, id=user_id)
        qs = qs.filter(user=user)
    elif username is not None:
        user = get_object_or_404(User, username=username)
        qs = qs.filter(user=user)
        
    if user:
        extra_context = kwargs.get('extra_context', {})
        extra_context.update({'photo_user': user})
        kwargs.update({'extra_context': extra_context})
    
    return object_list(request, queryset=qs, *args, **kwargs)

def photo_detail(request, object_id, album_id, *args, **kwargs):
    album = get_object_or_404(Album, id=album_id)
    
    extra_context = kwargs.get('extra_context', {})
    extra_context.update({'album': album})
    kwargs.update({'extra_context': extra_context})
        
    return object_detail(request, object_id=object_id, *args, **kwargs)