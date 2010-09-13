# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## User Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext, ugettext_lazy as _
from noc.lib.app import ModelApplication,HasPerm,site
from noc.main.models import Permission
from widgets import AccessWidget

##
##
##
class UserChangeForm(forms.ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    noc_user_permissions=forms.CharField(label="User Access",widget=AccessWidget,required=False)
    class Meta:
        model = User
    def __init__(self,*args,**kwargs):
        super(UserChangeForm,self).__init__(*args,**kwargs)
        if "instance" in kwargs:
            self.initial["noc_user_permissions"]="user:"+self.initial["username"]
        self.new_perms=set()
        if args:
            self.new_perms=set([p[5:] for p in args[0] if p.startswith("perm_")])
    def save(self,commit=True):
        model=super(UserChangeForm,self).save(commit)
        if not model.id:
            model.save()
        Permission.set_user_permissions(model,self.new_perms)
        return model
##
##
##
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('User category'), {'fields': ('is_active', 'is_superuser')}),
        (_('Groups'), {'fields': ('groups',)}),
        (_('Access'), {'fields': ('noc_user_permissions',), "classes":["collapse"]}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name',"is_active","is_superuser")
    list_filter = ('is_superuser', 'is_active')
    filter_horizontal=("groups",)
    form = UserChangeForm
##
##
##
class UserApplication(ModelApplication):
    model=User
    model_admin=UserAdmin
    menu="Setup | Users"
    ##
    ## Change password view
    ##
    def view_change_password(self,request,object_id):
        if not self.admin.has_change_permission(request):
            return self.response_fobidden("Permission denied")
        user=get_object_or_404(self.model,pk=object_id)
        if request.POST:
            form=self.admin.change_password_form(user,request.POST)
            if form.is_valid():
                new_user=form.save()
                self.message_user(request,"Password changed")
                return self.response_redirect("main:user:change",object_id)
        else:
            form=self.admin.change_password_form(user)
        return self.render(request,"change_password.html",{"form":form,"original":user})
    view_change_password.url=r"^(\d+)/password/$"
    view_change_password.access=HasPerm("change")