from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

import os
from core.models import Monitor
from core.models import Host
from core.models import Datastore
"""
Core Views
================

* models supporting the core monitoring infrastructure

"""

def render_response(req, *args, **kwargs):
    """ a variation on render_to_response that inserts the RequestContext 
    into each template context from these views."""
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)
    
# Create your views here.
def index(request):
    """ default web view for the 'front page' of the web application. """
    # user = User.get_by_key_name('admin')
    # if not user or user.username != 'admin' or not (user.is_active and
    #         user.is_staff and user.is_superuser and
    #         user.check_password('admin')):
    #     user = User(key_name='admin', username='admin',
    #         email='admin@localhost', first_name='Boss', last_name='Admin',
    #         is_active=True, is_staff=True, is_superuser=True)
    #     user.set_password('admin')
    #     user.put()
    monitor_list = Monitor.objects.all()
    return render_response(request, 'core/index.html', {'monitor_list':monitor_list})
#
def visual_test(request):
    """ test view """
    context_dict = {}
    context_dict['error'] = "this is an error message"
    context_dict['info'] = "information message"
    message_list = ["message1", "a much longer message 2 is inserted in this location to work the sizing of the format."]
    context_dict['messages'] = message_list
    return render_response(request, 'visualtest.html', context_dict )
#
def host_detail(request, host_id):
    """ detail view of the individual monitor"""
    host = get_object_or_404(Host, pk=host_id)
    return render_response(request, 'core/host_detail.html', {'host': host})
#
def monitor_detail(request, monitor_id):
    """ detail view of the individual monitor"""
    mon = get_object_or_404(Monitor, pk=monitor_id)
    return render_response(request, 'core/monitor_detail.html', {'monitor': mon})
#
def datastore_detail(request, datastore_id):
    """ detail view of the individual monitor"""
    this_ds = get_object_or_404(Datastore, pk=datastore_id)
    return render_response(request, 'core/datastore_detail.html', {'datastore': this_ds})
#
def datastore_image(request, datastore_id):
    """ 
    png result of graphing an individual datastore element
    code thoughts on dynamic generation: http://www.djangosnippets.org/snippets/365/
    """
    this_ds = get_object_or_404(Datastore, pk=datastore_id)
    this_ds.generate_rrd_graph()
    name = "%s.png" % (this_ds.id, )
    png_file = os.path.join(this_ds.png_path, name)
    #
    from django.core.servers.basehttp import FileWrapper
    wrapper = FileWrapper(file(png_file))
    response = HttpResponse(wrapper, content_type='image/png')
    response['Content-Length'] = os.path.getsize(png_file)
    return response