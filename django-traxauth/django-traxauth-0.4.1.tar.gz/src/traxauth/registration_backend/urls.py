

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^register/$', 'traxauth.registration_backend.views.register_recaptcha_view',
        kwargs={'backend': 'traxauth.registration_backend.TraxAuthBackend'},
        name='registration_register'),
    url(r'^', include('registration.backends.default.urls')),
)


# URL patterns for resending activation
#urlpatterns += patterns('',
#    url(r'^activate/resend/$', 'traxauth.registration_backend.views.activate_resend',
#        kwargs = {'backend': 'registration.backends.default.DefaultBackend'},
#        name='registration_activate_resend'),
#    url(r'^activate/resend/complete/$', direct_to_template,
#        {'template': 'registration/activation_complete.html'},
#        name='registration_activation_resend_complete'),
#)

