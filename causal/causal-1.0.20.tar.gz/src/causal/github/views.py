""" Handler for URLs for the http://github.com service.
GitHub doesn't really have a decent oauth service so again we
are hitting public json feeds and processing those.
"""

from datetime import datetime
import httplib2
from causal.main.decorators import can_view_service
from causal.main.models import OAuth, RequestToken, AccessToken, UserService
from causal.main.utils.services import get_model_instance, \
        settings_redirect, check_is_service_id, get_url
from causal.main.utils.views import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from datetime import date, timedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

PACKAGE = 'causal.github'

@login_required(redirect_field_name='redirect_to')
def verify_auth(request):
    """Handle reply from github"""
    """Take incoming request and validate it to create a valid AccessToken."""

    try:
        service = get_model_instance(request.user, PACKAGE)
        code = request.GET.get('code')
    
        if code:
            # swap our newly aquired code for a everlasting signed "token"
            reply = get_url('https://github.com/login/oauth/access_token?client_id=%s&client_secret=%s&code=%s' % (
                service.app.auth_settings['consumer_key'], 
                service.app.auth_settings['consumer_secret'], 
                code), json=False, method="POST", disable_ssl=True)
        
            if  not reply.startswith('access_token'):
                raise Exception('Token Failure')
            
            access, perm_type = reply.split('&')
            
            service.auth.access_token = AccessToken.objects.create(
                oauth_token = access.split('=')[1],
                oauth_token_secret = access.split('=')[1],
            )
            
            service.auth.save()
            
            # Mark as setup completed
            service.setup = True    
            service.save()

    except:
        messages.error(
            request,
            'Unable to validate your account with GitHub, please grant permission for gargoyle.me to access your account.'
        )

    return redirect(settings_redirect(request))

@login_required(redirect_field_name='redirect_to')
def auth(request):
    """We dont need a full oauth setup just a username.
    """

    service = get_model_instance(request.user, PACKAGE)
    
    if not service.auth:
        auth = OAuth()
        auth.save()
        service.auth = auth
        service.save()
        
    current_site = Site.objects.get(id=settings.SITE_ID)
    callback = reverse('causal-github-callback')
    callback = "http://%s%s" % (current_site.domain, callback,)

    return redirect('https://github.com/login/oauth/authorize?client_id=%s&redirect_uri=%s' %(
        service.app.auth_settings['consumer_key'],
        callback
    ))

@can_view_service
def stats(request, service_id):
    """Create up some stats.
    """

    service = get_object_or_404(UserService, pk=service_id)
    
    if hasattr(service.auth.access_token, 'username'):
        messages.error(
           request,
           'Please use the settings page to authorise your flickr account.')
        
        return request
         

    if check_is_service_id(service, PACKAGE):
        stats = service.handler.get_stats_items(date.today() - timedelta(days=7))
        if not stats:
            return render(request, {}, 'causal/github/stats.html')
        return render(
            request,
            {
                'events' : stats['events'],
                'commits': stats['commits'],
                'avatar' : stats['avatar'],
                'commit_times' : stats['commit_times'],
                'common_time' : stats['most_common_commit_time'],
                'days_committed' : stats['days_committed'], 
                'max_commits_on_a_day' : stats['max_commits_on_a_day'],
                'repos' : stats['repos']
            },
            'causal/github/stats.html'
        )
    else:
        return redirect('/%s' % (request.user.username,))
