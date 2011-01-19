from django.conf.urls.defaults import patterns, include, url
from django_comments_rss.feeds import CommentsFeed

urlpatterns = patterns('',
    url(r'^$', CommentsFeed())
)
