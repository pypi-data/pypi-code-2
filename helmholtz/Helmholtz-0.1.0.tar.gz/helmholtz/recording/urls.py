from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from helmholtz.recording.admin import recording_admin

urlpatterns = patterns('',
    (r'^admin/', include(recording_admin.urls)),
    url(r'^data/(?P<lab>\w+(\s\S+)*)/(?P<expt>\w[\w\-]*)/(?P<block>\w[\w\-]*)/$', 'helmholtz.recording.views.block_detail', {'template':"block_detail.html", "get_statistics":True}, name='block-detail'),
    
    url(r"""^data/(?P<lab>\w+(\s\S+)*)/(?P<expt>\w[\w\-]*)/(?P<block>\w[\w\-]*)/(?P<protocol>\w+[\w\W]*)/(?P<file>\w+[\w\W]*)/(?P<episode>\d+)/(?P<channel>\d+)/$""", 'helmholtz.recording.views.signal_detail', {'template':"signal_detail.html"}, name='signal-detail'),
    url(r"""^data/(?P<lab>\w+(\s\S+)*)/(?P<expt>\w[\w\-]*)/(?P<block>\w[\w\-]*)/(?P<protocol>\w+[\w\W]*)/$""", 'helmholtz.recording.views.protocol_detail', {'template':"protocol_detail.html"}, name='protocol-detail'),
)
