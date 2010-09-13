# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObjectSelector Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication,HasPerm
from noc.sa.models import ManagedObjectSelector
##
## ManagedObjectSelector admin
##
class ManagedObjectSelectorAdmin(admin.ModelAdmin):
    list_display=["name","is_enabled","description"]
    list_filter=["is_enabled"]
    actions=["test_selectors"]
    search_fields=["name"]
    filter_horizontal=["filter_groups","sources"]
    ##
    ## Test selected seletors
    ##
    def test_selectors(self,request,queryset):
        return self.app.response_redirect("test/%s/"%",".join([str(p.id) for p in queryset]))
    test_selectors.short_description="Test selected Object Selectors"
##
## ManagedObjectSelector application
##
class ManagedObjectSelectorApplication(ModelApplication):
    model=ManagedObjectSelector
    model_admin=ManagedObjectSelectorAdmin
    menu="Setup | Object Selectors"
    ##
    ## Test Selectors
    ##
    def view_test(self,request,objects):
        r=[{"name":q.name,"objects":sorted(q.managed_objects,lambda x,y:cmp(x.name,y.name))}
            for q in[get_object_or_404(ManagedObjectSelector,id=int(x)) for x in objects.split(",")]]
        return self.render(request,"test.html",{"data":r})
    view_test.url=r"^test/(?P<objects>\d+(?:,\d+)*)/$"
    view_test.access=HasPerm("change")
