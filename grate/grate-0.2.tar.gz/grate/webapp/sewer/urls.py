from django.conf.urls.defaults import *
from views import *
import json_views


urlpatterns = patterns('',
    url(r'^json/admin_groups/', json_views.admin_groups,
        name='json-admin-groups'),
)
urlpatterns += patterns('',
    url(r'^.+/remove/access/([a-zA-Z0-9]+)/$', remove_access),
    url(r'^messages/$', view_messages, name='view-messages'),
    url(r'^repo/(.+)/admin/$', repo_admin, name='repo-admin'),
    url(r'^repo/(.+)/add/access/$', repo_add_access, name='repo-add-access'),
    url(r'^repo/(.+)/set/public/$', repo_set_public, name='repo-set-public'),
    url(r'^repo/(.+)/set/private/$', repo_set_private,
        name='repo-set-private'),
    url(r'^repo/(.+)/$', repo_view, name='repo-view'),
    url(r'^repos/add/$', repo_add, name='repo-add'),
    url(r'^repos/$', repo_index, name='repo-index'),
    url(r'^key/remove/([a-zA-Z0-9]+)/$', key_remove, name='key-remove'),
    url(r'^keys/add/$', key_add, name='key-add'),
    url(r'^keys/$', key_index, name='key-index'),
    url(r'^groups/$', group_index, name='group-index'),
    url(r'^groups/add/$', group_add, name='group-add'),
    url(r'^group/(.+)/add/access/$', group_add_access,
        name='group-add-access'),
    url(r'^group/(.+)/admin/$', group_admin, name='group-admin'),
    url(r'^group/(.+)/$', group_view, name='group-view'),
    url(r'^$', index, name='index'),
)
