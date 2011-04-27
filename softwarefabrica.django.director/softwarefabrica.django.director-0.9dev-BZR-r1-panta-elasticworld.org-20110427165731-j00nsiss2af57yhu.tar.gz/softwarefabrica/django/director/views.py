# views.py
#
# Copyright (C) 2009-2011 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Views for the softwarefabrica.django.director django application.

Copyright (C) 2009-2011 Marco Pantaleoni. All rights reserved.

@author: Marco Pantaleoni
@copyright: Copyright (C) 2009-2011 Marco Pantaleoni
"""

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2009-2011 Marco Pantaleoni"
__license__   = "GPL v2"

from django.conf.urls.defaults import *
from django.http import Http404, HttpRequest
from django.contrib.auth.models import User, Group

from softwarefabrica.django.crud.crud import ViewCall
from softwarefabrica.django.common import views as commonviews
#from softwarefabrica.django.common.views import *

import time
import datetime
import logging

# ------------------------------------------------------------------------
#   CONSTANTS
# ------------------------------------------------------------------------

_NOT_AUTHORIZED_MSG = u"Access not authorized."

# ------------------------------------------------------------------------
#   Utility functions
# ------------------------------------------------------------------------

def request_user(request):
    assert isinstance(request, HttpRequest)

    user = None
    if request.user.is_authenticated():
        user = request.user
    return user

def _get_owner(instance):
    if instance is None:
        return (None, None)
    assert isinstance(instance, models.Model)
    owner_user  = None
    owner_group = None
    if hasattr(instance, 'owner_user'):
        owner_user = instance.owner_user
    if hasattr(instance, 'owner_group'):
        owner_group = instance.owner_group
    logging.info("owner[%s]: %s/%s" % (instance, owner_user, owner_group))
    return (owner_user, owner_group)

def subtract_list(l1, l2):
    l1 = list(l1)
    for item in l2:
        if item in l1:
            l1.remove(item)
    return l1

# -- generic views helpers -----------------------------------------------

# ------------------------------------------------------------------------
#   Views
# ------------------------------------------------------------------------

class CreateObjectView(commonviews.CreateObjectView):
    __doc__ = commonviews.CreateObjectView.__doc__
    def populate_context(self, vcall, request):
        from softwarefabrica.django.director.modelmanager import ModelManager
        assert isinstance(vcall, ViewCall)
        vcall.c_context['manager'] = ModelManager.FromModel(vcall.c_model)
        return super(CreateObjectView, self).populate_context(vcall, request)
class UpdateObjectView(commonviews.UpdateObjectView):
    __doc__ = commonviews.UpdateObjectView.__doc__
    def populate_context(self, vcall, request):
        from softwarefabrica.django.director.modelmanager import ModelManager
        assert isinstance(vcall, ViewCall)
        vcall.c_context['manager'] = ModelManager.FromModel(vcall.c_model)
        return super(UpdateObjectView, self).populate_context(vcall, request)
class ListObjectView(commonviews.ListObjectView):
    __doc__ = commonviews.ListObjectView.__doc__
    def populate_context(self, vcall, request):
        from softwarefabrica.django.director.modelmanager import ModelManager
        assert isinstance(vcall, ViewCall)
        vcall.c_context['manager'] = ModelManager.FromModel(vcall.c_model)
        return super(ListObjectView, self).populate_context(vcall, request)
class DetailObjectView(commonviews.DetailObjectView):
    __doc__ = commonviews.DetailObjectView.__doc__
    def populate_context(self, vcall, request):
        from softwarefabrica.django.director.modelmanager import ModelManager
        assert isinstance(vcall, ViewCall)
        vcall.c_context['manager'] = ModelManager.FromModel(vcall.c_model)
        return super(DetailObjectView, self).populate_context(vcall, request)
class DeleteObjectView(commonviews.DeleteObjectView):
    __doc__ = commonviews.DetailObjectView.__doc__
    def populate_context(self, vcall, request):
        from softwarefabrica.django.director.modelmanager import ModelManager
        assert isinstance(vcall, ViewCall)
        vcall.c_context['manager'] = ModelManager.FromModel(vcall.c_model)
        return super(DeleteObjectView, self).populate_context(vcall, request)
