from django.conf.urls.defaults import patterns, include, url
from trawler.views import CampaignDetailView


urlpatterns = patterns('trawler.views',
    url(r'campaign/(?P<pk>\d+)/$',
        CampaignDetailView.as_view(), name='campaign_detail'),
    # note that these two patterns match anything following the last slash... 
    url(r'l/(?P<campaign_id>\d+)/(?P<target_id>\d+)/', 'link_hits',
        name='link_hits'),
    url(r'i/(?P<campaign_id>\d+)/(?P<target_id>\d+)/', 'img_hits',
        name='img_hits'),
)
