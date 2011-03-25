# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

def set_project(request):
    project_id = request.POST.get("project")
    last_page = request.POST.get("last_page")
    try:
        project_id = int(project_id)
    except (ValueError, TypeError):
        project_id
    request.session["project"] = project_id
    if last_page:
        return HttpResponseRedirect(last_page)
    else:
        return HttpResponseRedirect(reverse("admin:index"))
