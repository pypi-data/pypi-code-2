#encoding:utf-8
from django.conf import settings
from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from helmholtz.access_control.decorators import create_or_update_foreign_user, permission_denied
from helmholtz.access_control.conditions import is_accessible_by
from helmholtz.storage.models import File

@create_or_update_foreign_user(settings.SERVER_OWNER_GROUP)
def login_session(request, template_name='registration/login.html', form_template=None):
    """Decorate the login generic view""" 
    return login(request, template_name)

@login_required
def download_file(request, file_id) :
    """
    Download the file corresponding to the specify id 
    if the user has a 'can_download' permission on it 
    else return the permission denied page.
    """
    format = request.GET.get('format')
    file = File.objects.get(pk=int(file_id))
    if not is_accessible_by(file, request.user) :
        return permission_denied(request) 
    path = file.get_path(format)
    data = open(path, "rb")
    response = HttpResponse(content=data, mimetype="application/octet-stream")
    response['Content-Disposition'] = "attachment; filename = %s.%s" % (file.name, format)
    return response
