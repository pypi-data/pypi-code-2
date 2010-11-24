# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------------
#
#    Copyright (C) 2008 Caktus Consulting Group, LLC
#
#    This file is part of minibooks.
#
#    minibooks is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of 
#    the License, or (at your option) any later version.
#    
#    minibooks is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    
#    You should have received a copy of the GNU Affero General Public License
#    along with minibooks.  If not, see <http://www.gnu.org/licenses/>.
#


from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic.simple import redirect_to

from caktus.django.views import login, logout, reset_password, change_password

from ledger.admin import books_admin
from crm.xmlrpc import rpc_handler

handler404 = 'caktus.django.views.page_not_found'
handler500 = 'caktus.django.views.server_error'

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^%sbooks-admin/(.*)' % settings.URL_PREFIX, books_admin.root),
    url(r'^%sbooks-admin/$' % settings.URL_PREFIX, books_admin.root, name='books_admin'),
    
    url(r'^%sxml-rpc/' % settings.URL_PREFIX, rpc_handler, name='xml_rpc'),
    
    (r'^%sadmin/(.*)' % settings.URL_PREFIX, admin.site.root),
    
    url(
        r'^%saccount/login/$' % settings.URL_PREFIX,
        login,
        {'redirect_to': settings.LOGIN_REDIRECT_URL},
        name='auth_login',
    ),
    url(
        r'^%saccount/logout/$' % settings.URL_PREFIX,
        logout,
        name='auth_logout',
    ),
    url(
        r'^%saccount/password/change/$' % settings.URL_PREFIX,
        change_password,
        name='change_password',
    ),
    url(
        r'^%saccount/password/reset/$' % settings.URL_PREFIX,
        reset_password,
        {'redirect_to': settings.LOGIN_URL},
        name='reset_password',
    ),
    (r'^%sajax/' % settings.URL_PREFIX, include('ajax_select.urls')),
    
    (r'^%sledger/' % settings.URL_PREFIX, include('minibooks.ledger.urls')),
    (r'^%scrm/' % settings.URL_PREFIX, include('crm.urls')),
    (r'^%scontactinfo/' % settings.URL_PREFIX, include('contactinfo.urls')),
    (r'^%stimepiece/' % settings.URL_PREFIX, include('timepiece.urls')),
    
    # url(
    #     r'^%s(?:home/)?$' % settings.URL_PREFIX,
    #     redirect_to,
    #     kwargs={'url': '/%scrm/dashboard/' % settings.URL_PREFIX}
    # ),
    
    # url(r'^%s' % settings.URL_PREFIX, include('caktus.django.cms.urls')),
    
)

