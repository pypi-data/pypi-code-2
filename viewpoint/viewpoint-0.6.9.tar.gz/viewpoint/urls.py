from django.views.generic.date_based import archive_day, archive_month, \
                                            archive_year, archive_today, \
                                            archive_week, object_detail
from django.conf.urls.defaults import *
from django.conf import settings
from feeds import LatestEntriesByBlog, LatestEntries #, EntryComments
from models import Blog, Entry
from views import generic_blog_entry_view, blog_detail

feeds = {
    'all': LatestEntries,
    'latest': LatestEntriesByBlog,
    #'comments': EntryComments,
}

if 'categories' in settings.INSTALLED_APPS:
    from feeds import LatestEntriesByCategory
    feeds['categories'] = LatestEntriesByCategory


urlpatterns = patterns('django.contrib.syndication.views',
    (r'^feeds/(?P<url>.*)/$', 'feed', {'feed_dict': feeds}),
)

urlpatterns += patterns('',
    # Blog Index (listing of all public blogs)
    url(
        regex = r'^$',
        view = 'django.views.generic.list_detail.object_list',
        kwargs = {
            'template_name': 'viewpoint/index.html',
            'queryset': Blog.objects.filter(public=True)},
        name = "viewpoint_blog_index"
    ),
    # Blog detail (Main page of a blog, shows description and stuff)
    url(
        regex = r'^(?P<slug>[-\w]+)/$', 
        view = blog_detail,
        name='viewpoint_blog_detail'
    ),
    # Listing of blog entries for a given year
    url(
        regex = r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/$', 
        view = generic_blog_entry_view, 
        name='viewpoint_blog_archive_year'
    ),
    # Listing of blog entries for a given month/year
    url(
        regex = r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/$', 
        view = generic_blog_entry_view, 
        name = 'viewpoint_blog_archive_month'
    ),
    # Listing of blog entries for a given week of the year
    url(
        regex = r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<week>\d{1,2})/$',
        view = generic_blog_entry_view,
        name = 'viewpoint_blog_archive_week'
    ),
    # Listing of blog entries for a given day
    url(
        regex = r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$', 
        view = generic_blog_entry_view, 
        name = 'viewpoint_blog_archive_day'
    ),
    # Listing of blog entries for the current date
    url(
        regex = r'^(?P<blog_slug>[-\w]+)/today/$', 
        view = generic_blog_entry_view, 
        name='viewpoint_blog_archive_today'
    ),
    # A blog entry
    url(
        regex = r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$', 
        view = generic_blog_entry_view, 
        name='viewpoint_entry_detail'
    ),
    # A blog comments page
    url(
        regex = r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/comments/$', 
        view = generic_blog_entry_view,
        kwargs = {'template_name':'viewpoint/entry_comments.html'},
        name='viewpoint_entry_comments'
    ),
    # A blog printing page
    url(
        regex = r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/print/$', 
        view = generic_blog_entry_view, 
        kwargs = {'template_name':'viewpoint/entry_print.html'},
        name='viewpoint_entry_print'
    ),
    
)
