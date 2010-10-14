from django.conf.urls.defaults import *


urlpatterns = patterns("magneto.views",
    url(r"^$", "detail", dict(name="index"), name="magneto.detail.index"),
    url(r"^(.+?)/?$", "detail", name="magneto.detail"),
)
