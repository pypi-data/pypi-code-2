from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin

from bookreader.models import Book, Page

admin.autodiscover()

book_id_re = '[\S^:]+:[\S^:]+:[\d\./]+'

urlpatterns = patterns('',
    url('^$', 'bookreader.views.book.browse', name='bookreader-book-list'),
)

urlpatterns += patterns('bookreader.views.repository',
    url('^repository/$', 'browse', name='bookreader-repository-list'),
    url('^repository/(?P<object_id>\d+)/$', 'view', name='bookreader-repository'),
    url('^repository/(?P<object_id>\d+)/books/$', 'books', name='bookreader-repository-books'),
)

urlpatterns += patterns('bookreader.views.collection',
    url('^collection/$', 'browse', name='bookreader-collection-list'),
    url('^collection/(?P<object_id>\d+)/$', 'view', name='bookreader-collection'),
)

urlpatterns += patterns('bookreader.views.book',
    url('^book/$', 'browse', name='bookreader-book-list'),
    url('^book/(?P<object_id>%s)/$' % (book_id_re,), 'view',
        name='bookreader-book'),
    url('^book/(?P<object_id>%s)/read/$' % (book_id_re,),'read',
        name='bookreader-book-read'),
    url('^book/(?P<object_id>%s)/pages/$' % (book_id_re,), 'pages',
        name='bookreader-book-pages'),    
    url('^book/(?P<object_id>%s)/(?P<sequence>\d+)/$' % (book_id_re,),'page',
        name='bookreader-book-page'),
    #url('^book/(?P<object_id>%s)/reload/$' % (book_id_re,),
    #    'reload', name='bookreader-book-reload'),
    url('^compare/$', 'compare', name='bookreader-book-compare'),
    url('^compare/add/(?P<object_id>%s)/$' % (book_id_re,), 'add_to_compare',
        name='bookreader-book-add-compare'),
    url('^compare/remove/(?P<object_id>%s)/$' % (book_id_re,), 'remove_from_compare',
        name='bookreader-book-remove-compare'),
    url('^compare/reset/$', 'reset_compare', name='bookreader-book-reset-compare'),
    url('^compare/portlet/$', 'compare_portlet', name='bookreader-book-compare-portlet'),
)

urlpatterns += patterns('bookreader.views.page',
    url('page/(?P<object_id>\d+)/', 'view',
        name='bookreader-page'),
    url('^jp2_metadata/', 'jp2_metadata',
        name='jp2_metadata'),
)
