# -*- coding: utf-8 -*-

from django import http
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json

from desktopnotifications.models import DesktopNotification
from desktopnotifications.forms import SimpleAddNotificationForm

@login_required
def index(request):
    if request.POST:
        form = SimpleAddNotificationForm(request.POST)
        if form.is_valid():
            n = DesktopNotification(user=request.user)
            n.autoclose_delay = form.cleaned_data["autoclose_delay"]
            n.tag = form.cleaned_data["tag"]
            n.content = form.cleaned_data["content"]
            n.save()
    else:
        form = SimpleAddNotificationForm()
    
    notifications = DesktopNotification.objects.all().filter(user=request.user)
    
    return render_to_response('index.html', 
        RequestContext(request, {"form": form,
         "notifications": notifications,
        })
    )

def get_tags(request):
    """ This view will return available tags """ 
    if not request.user or not request.user.is_authenticated():
        return http.HttpResponse('Not logged in.', status = 403)
    
    tagsdict = {}
    for tagid, tagname in getattr(settings, "DESKTOP_NOTIFICATION_TAGS", ()):
        tagsdict[tagid] = tagname
    tags = json.dumps(tagsdict)
    return http.HttpResponse(tags, content_type='application/json')

@login_required(login_url='/notifications/login/')
def get_notification(request, notification_id):
    notification = get_object_or_404(DesktopNotification, pk=notification_id, user=request.user)
    return http.HttpResponse(notification.content, mimetype="text/html")

def check_is_authenticated(request):
    user = request.user
    if user and user.is_authenticated():
        return http.HttpResponse(request.user.username)
    else:
        return http.HttpResponse("0")