#!/usr/bin/env python
#coding=utf8
#
#       Copyright 2010 Antoine Millet <antoine@inaps.org>
#
#       This file is part of DocBucket.
#       
#       Foobar is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       Foobar is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'^$', 'docbucket.views.home', name='home'),
	url(r'^create/$', 'docbucket.views.create', name='create'),
	url(r'^list/$', 'docbucket.views.list', name='list'),
	url(r'^list/(?P<doc_class>.+)/$', 'docbucket.views.list', name='list'),
	url(r'^manage/$', 'docbucket.views.manage', name='manage'),
	url(r'^show/(?P<doc_id>[a-f0-d]{24})/$', 'docbucket.views.show', name='show'),
	url(r'^download/(?P<doc_id>[a-f0-d]{24})/$', 'docbucket.views.download', name='download'),
	url(r'^search/$', 'docbucket.views.search', name='search'),
	
	url(r'^thumb/(?P<doc_id>[a-f0-d]{24})/(?P<size>.+)/$', 'docbucket.views.document_thumb', name='document_thumb'),
	url(r'^thumb/(?P<filename>.+)/$', 'docbucket.views.thumb', name='thumb'),
)

