# -*- coding: utf-8 -*-
from django.views.generic import list_detail
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from txcommon.decorators import one_perm_required_or_403
from projects.models import Project
from projects.permissions import pr_project_view_log
from actionlog.models import LogEntry
from filters import LogEntryFilter

@login_required
def user_timeline(request, *args, **kwargs):
    """
    Present a log of the latest actions of a user.
    
    The view limits the results and uses filters to allow the user to even
    further refine the set.
    """
    log_entries = LogEntry.objects.by_user(request.user)
    f = LogEntryFilter(request.GET, queryset=log_entries)

    return render_to_response("timeline/timeline_user.html",
        {'f': f,
         'actionlog': f.qs},
        context_instance = RequestContext(request))

@login_required
# Only the maintainer should have permissions to access this
@one_perm_required_or_403(pr_project_view_log, 
    (Project, 'slug__exact', 'slug'))
def project_timeline(request, *args, **kwargs):
    """
    Present a log of the latest actions on the project.
    
    The view limits the results and uses filters to allow the user to even
    further refine the set.
    """
    project = get_object_or_404(Project, slug=kwargs['slug'])
    log_entries = LogEntry.objects.by_object(project)
    f = LogEntryFilter(request.GET, queryset=log_entries)
    # The template needs both these variables. The first is used in filtering,
    # the second is used for pagination and sorting.
    kwargs.setdefault('extra_context', {}).update({'f': f,
                                                   'actionlog': f.qs})
    return list_detail.object_detail(request, *args, **kwargs)
