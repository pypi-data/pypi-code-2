from django.conf.urls.defaults import *
from birdland.conf import settings
from birdland.feeds import rss_feeds, atom_feeds

LIST_ARGUMENTS = {
    'paginate_by': settings.PAGINATE_BY,
}

urlpatterns = patterns('birdland.views.public',
    url(r'^$',
        'entry_list',
        LIST_ARGUMENTS,
        name='blog_latest'),
    url(r'^(?P<year>\d{4})/$',
        'entry_archive_year',
        LIST_ARGUMENTS,
        name='blog_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        'entry_archive_month',
        LIST_ARGUMENTS,
        name='blog_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<week>\d{2})/$',
        'entry_archive_week',
        LIST_ARGUMENTS,
        name='blog_archive_week'),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/$',
        'entry_archive_day',
        LIST_ARGUMENTS,
        name='blog_archive_day'),
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
        'entry_archive_detail',
        name='blog_archive_detail'),
    url(r'^authors/$',
        'author_list',
        LIST_ARGUMENTS,
        name='blog_author_list'),
    url(r'^authors/(?P<username>\w+)/$',
        'entry_archive_author',
        LIST_ARGUMENTS,
        name='blog_archive_author'),
)

urlpatterns = urlpatterns + patterns('django.contrib.syndication.views',
    url(r'^feeds/rss/(?P<url>.*)/$',
        'feed',
        {'feed_dict': rss_feeds},
        name='entry_rss_feed'),
    url(r'^feeds/atom/(?P<url>.*)/$',
        'feed',
        {'feed_dict': atom_feeds},
        name='entry_atom_feed'),
)                      

if settings.TAGGING_ENABLED:
    urlpatterns = urlpatterns + patterns('birdland.views.public',
        url(r'^tags/(?P<tag>[\w-]+)/$',
            'entry_archive_tag',
            LIST_ARGUMENTS,
            name='blog_archive_tag'),
        url(r'^tags/$',
            'entry_tag_list',
            LIST_ARGUMENTS,
            name='blog_tag_list'),
    )
