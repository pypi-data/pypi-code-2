from django.conf.urls.defaults import *
from django_mailchimp_forms.views import chimpy_register, chimpy_unregister

urlpatterns = patterns('',
    url(r'^register/$', chimpy_register, name="chimpy_register"),
    url(r'^unregister/$', chimpy_unregister, name="chimpy_unregister"),
)
