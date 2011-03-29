from django.conf.urls.defaults import patterns, url

from django.contrib import admin

from bookreader.forms import PageConversionForm, PageURLForm

admin.autodiscover()

book_id_re = '[\S^:]+:[\S^:]+:[\d\./]+'

urlpatterns = patterns('',
    url('^$', 'bookreader.views.book.browse_works', name='bookreader-work-list'),
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
    url('^works/$', 'browse_works', name='bookreader-work-list'),
)

urlpatterns += patterns('bookreader.views.book',
    url('^book/$', 'browse', name='bookreader-book-list'),
    url('^book/(?P<object_id>%s)/$' % (book_id_re,), 'view',
        name='bookreader-book'),
    url('^book/(?P<object_id>%s)/read/$' % (book_id_re,),'read',
        name='bookreader-book-read'),
    url('^book/(?P<object_id>%s)/canonical/$' % (book_id_re,),'view',
        name='bookreader-book-canonical',
        kwargs={'template_name': 'bookreader/book_canonical.html'}),
    url('^book/(?P<object_id>%s)/pages/$' % (book_id_re,), 'pages',
        name='bookreader-book-pages'),    
    url('^book/(?P<object_id>%s)/(?P<sequence>\d+)/$' % (book_id_re,),'page',
        name='bookreader-book-page'),
    url('^book/(?P<object_id>%s)/bitstream_metadata.xml$' % (book_id_re,), 
        'bitstream_metadata', name='bookreader-book-bitstream-metadata'),  
    url('^book/(?P<object_id>%s)/annotations/$' % (book_id_re,), 'annotations',
        name='bookreader-book-annotations'), 
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

urlpatterns += patterns('bookreader.views.pdf',
    url('^book/(?P<object_id>%s)/pdf/$' % (book_id_re,),'compiled',
        name='bookreader-book-pdf'),)

urlpatterns += patterns('bookreader.views.page',
    url('^page/(?P<object_id>\d+)/$', 'view',
        name='bookreader-page'),
    url('^jp2_metadata/$', 'jp2_metadata',
        name='jp2_metadata'),
    url('^page/(?P<object_id>\d+)/annotations/$', 'annotations',
        name='bookreader-page-annotations'),
    url('^page/(?P<object_id>\d+)/print/$', 'printable',
        name='bookreader-page-print'),    
)

urlpatterns += patterns('bookreader.views.editor',
    url('^book/(?P<object_id>%s)/edit/interior/$' % (book_id_re,), 'pages',
        name='bookreader-editor-pages'),
    url('^book/(?P<object_id>%s)/edit/exterior/$' % (book_id_re,), 'exterior',
        name='bookreader-editor-exterior'),
    url('^book/(?P<object_id>%s)/edit/references/$' % (book_id_re,), 'references',
        name='bookreader-editor-references'),
    url('^book/(?P<object_id>%s)/copy-canonical-annotations/$' % (book_id_re,), 'copy_annotations',
        name='bookreader-editor-copy-annotations'),
    url('^book/(?P<object_id>%s)/update-page-order/$' % (book_id_re,), 'update_page_order',
        name='bookreader-editor-update-page-order'),
    url('^book/(?P<object_id>%s)/add-page/$' % (book_id_re,), 'add_page',
        name='bookreader-editor-add-page'),
    url('^book/(?P<object_id>%s)/publish/$' % (book_id_re,), 'publish',
        name='bookreader-publish-book'),
    url('^page/(?P<object_id>\d+)/edit/$', 'edit_page',
        name='bookreader-editor-edit-page'),
    url('^page/(?P<object_id>\d+)/convert/$', 'edit_page',
        name='bookreader-editor-convert-page',
        kwargs={'form_class': PageConversionForm}),
    url('^page/(?P<object_id>\d+)/edit-urls/$', 'edit_page',
        name='bookreader-editor-edit-page-urls',
        kwargs={'form_class': PageURLForm}),
    url('^page/(?P<object_id>\d+)/delete/$', 'delete_page',
        name='bookreader-editor-delete-page'),
    url('^book/(?P<object_id>%s)/add-annotation/$' % (book_id_re,), 'add_annotation',
        name='bookreader-editor-add-annotation'),
    url('^annotation/(?P<object_id>\d+)/edit/$', 'edit_annotation',
        name='bookreader-editor-edit-annotation'),
    url('^annotation/(?P<object_id>\d+)/delete/$', 'delete_annotation',
        name='bookreader-editor-delete-annotation'),
    url('^book/add/$', 'add_book',
        name='bookreader-add-book'),
)
