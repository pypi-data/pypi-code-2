# Create your views here.

from django.shortcuts import render_to_response

from mixpanel_django.backends import mp_backend 

def test_mp_view(request):
    
    mp_backend.trackMixpanelEvent('index page loaded', {'gender':'male'}, request)
    mp_backend.trackMixpanelEvent('index page loaded', {'gender':'female'}, request)
    
    mp_backend.trackfunnelMixpanelEvent('Signup', 1, 'opened front page', {'gender':'male'}, request)
    mp_backend.trackfunnelMixpanelEvent('Signup', 2, 'clicked signup button', {'gender':'male'}, request)
    mp_backend.trackfunnelMixpanelEvent('Signup', 3, 'confirmed email address ', {'gender':'male'}, request)
    return render_to_response('test_mp.html', {})