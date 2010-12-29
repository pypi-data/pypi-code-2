from django.conf.urls.defaults import *
from indeed_contactForm.views import contact


urlpatterns = patterns('',
    (r'^$', contact),
)
