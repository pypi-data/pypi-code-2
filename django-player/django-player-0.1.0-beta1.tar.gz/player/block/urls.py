from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('player.block.views',
    url(r'^$', 'block_list', name='block_list'),
    url(r'^add/$', 'block_add', name='block_add'),
    url(r'^(?P<block_id>\d+)/$', 'block_detail', name='block_detail'),
    url(r'^(?P<block_id>\d+)/edit/$', 'block_edit', name='block_edit'),
    url(r'ajax/order/', 'blocks_reorder', name='blocks_reorder'),
    url(r'ajax/config/(?P<block_id>\d+)$', 'generate_blocks_configuration',
        name='generate_blocks_configuration'),
)
