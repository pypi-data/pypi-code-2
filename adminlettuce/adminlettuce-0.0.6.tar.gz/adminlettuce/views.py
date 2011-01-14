from django.core import urlresolvers
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response

from lettuce import fs
from lettuce.core import Feature
from lettuce.django import harvest_lettuces

def get_root_path():
    '''Returns the path of the Django admin interface.'''
    try:
        return urlresolvers.reverse('admin:index')
    except urlresolvers.NoReverseMatch:
        from django.contrib import admin
        try:
            return urlresolvers.reverse(admin.site.root, args=[''])
        except urlresolvers.NoReverseMatch:
            return getattr(settings, "ADMIN_SITE_ROOT_URL", "/admin/")

def feature_index(request):
    '''Render the list of lettuce features.'''
    f_list = []
    for path in harvest_lettuces():
        if isinstance(path, tuple) and len(path) is 2:
            path, app_module = path
            feature_files = fs.FeatureLoader(path).find_feature_files()
            f_list.extend([Feature.from_file(f) for f in feature_files])
    return render_to_response('feature_index.html', {
        'features': f_list,
        'root_path': get_root_path(),
    }, context_instance=RequestContext(request))
feature_index = staff_member_required(feature_index)
