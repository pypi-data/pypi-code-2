# -*- coding: utf-8 -*-
#
#  This file is part of django-postgresql-manager.
#
#  django-postgresql-manager is a Django based management interface for PostgreSQL users and databases.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-postgresql-manager
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-postgresql-manager
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#


from django.contrib import admin
from django.db.models.loading import cache
from django.db.utils import DatabaseError, IntegrityError
from django.contrib import messages

from postgresql_manager.forms import PgUserModelForm, PgDatabaseModelForm



class PgUserAdmin(admin.ModelAdmin):

    form = PgUserModelForm
    list_display = ('name', 'is_active', 'connlimit', 'date_created')
    search_fields = ('name', )
    list_filter = ('is_active', )
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:     # This is the add form
            self.fields = ['name', 'password1', 'password2', 'connlimit', 'is_active']
        else:               # This is the change form
            self.fields = ['name', 'password1', 'password2', 'connlimit', 'is_active', 'date_created', 'date_modified']
            if request.user.is_superuser:
                self.fields.append('created_by')
        return super(PgUserAdmin, self).get_form(request, obj, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        if obj is None:     # This is the add form
            self.readonly_fields = []
        else:               # This is the change form
            self.readonly_fields = ['date_created', 'date_modified']
            if request.user.is_superuser:
                self.readonly_fields.append('created_by')
        return super(PgUserAdmin, self).get_readonly_fields(request, obj)
    
    def queryset(self, request):
        qs = super(PgUserAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
    
    def save_model(self, request, obj, form, change):
        PgUser = cache.get_model('postgresql_manager', 'PgUser')
        password = form.cleaned_data.get('password1')
        
        if not change:  # User creation form
            
            assert password != '', 'A password is mandatory for new accounts'
            
            # The ``created_by`` attribute is set once at creation time
            obj.created_by = request.user
            
            attrs = 'LOGIN'
            if not obj.is_active:
                attrs = 'NOLOGIN'
            PgUser.objects.create_role(obj.name, password, attrs)
            
        else:   # This is the change form
            
            if 'name' in form.changed_data:
                PgUser.objects.rename_role(form.initial['name'], obj.name)
            
            if 'connlimit' in form.changed_data:
                PgUser.objects.limit_connections(obj.name, obj.connlimit)
            
            if 'is_active' in form.changed_data:
                PgUser.objects.lock_unlock_role(obj.name, obj.is_active)
            
            if password:
                PgUser.objects.change_password(obj.name, password)
 
        # Save the model
        obj.save()

admin.site.register(cache.get_model('postgresql_manager', 'PgUser'), PgUserAdmin)



class PgDatabaseAdmin(admin.ModelAdmin):

    form = PgDatabaseModelForm
    list_display = ('name', 'owner', 'connlimit', 'date_created')
    search_fields = ('name', 'owner__name')
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:     # This is the add form
            self.fields = ['name', 'owner', 'connlimit']
        else:               # This is the change form
            self.fields = ['name', 'owner', 'connlimit', 'date_created', 'date_modified']
            if request.user.is_superuser:
                self.fields.append('created_by')
        return super(PgDatabaseAdmin, self).get_form(request, obj, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        if obj is None:     # This is the add form
            self.readonly_fields = []
        else:               # This is the change form
            self.readonly_fields = ['date_created', 'date_modified']
            if request.user.is_superuser:
                self.readonly_fields.append('created_by')
        return super(PgDatabaseAdmin, self).get_readonly_fields(request, obj)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        PgUser = cache.get_model('postgresql_manager', 'PgUser')
        if db_field.name == 'owner':
            if not request.user.is_superuser:
                kwargs['queryset'] = PgUser.objects.filter(created_by=request.user)
        return super(PgDatabaseAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
    def queryset(self, request):
        qs = super(PgDatabaseAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
    
    def save_model(self, request, obj, form, change):
        PgDatabase = cache.get_model('postgresql_manager', 'PgDatabase')
        
        if not change:  # Database creation form
            
            # The ``created_by`` attribute is set once at creation time
            obj.created_by = request.user
            
            PgDatabase.objects.create_database(obj.name, obj.owner)
        
        else:   # This is the change form
            
            if 'name' in form.changed_data:
                PgDatabase.objects.rename_database(form.initial['name'], obj.name)
            
            if 'owner' in form.changed_data:
                PgDatabase.objects.set_owner(obj.name, obj.owner)
            
            if 'connlimit' in form.changed_data:
                PgDatabase.objects.limit_connections(obj.name, obj.connlimit)
                
        # Save the model
        obj.save()

admin.site.register(cache.get_model('postgresql_manager', 'PgDatabase'), PgDatabaseAdmin)


