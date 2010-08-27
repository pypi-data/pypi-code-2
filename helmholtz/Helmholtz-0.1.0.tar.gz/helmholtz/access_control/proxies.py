#encoding:utf-8
from django.contrib.auth.models import User
from helmholtz.core.shortcuts import get_class
from helmholtz.access_control.filters import get_downloadable_by

class ProxyUser(User):
    """A Proxy useful to add new method to the base User class."""
    
    class Meta:
        proxy = True
    
    def get_files_filtered_by_state(self, state):
        """Return files corresponding to the specified state."""
        files = self.requests.filter(state=state)
        return files
    
    def get_accessible_files(self):
        """Return accepted files."""
        return self.get_files_filtered_by_state('accepted')
    accepted_files = property(get_accessible_files)
    
    def get_refused_files(self):
        """Return refused files."""
        return self.get_files_filtered_by_state('refused')
    refused_files = property(get_refused_files)
    
    def get_requested_files(self):
        """Return requested files."""
        return self.get_files_filtered_by_state('requested')
    requested_files = property(get_requested_files)
    
    def can_download_file(self, file):
        """Return a boolean telling if someone can download a file."""
        cls = get_class('storage', 'File')
        files = cls.objects.all()
        downloadables = get_downloadable_by(files, self)
        return file in downloadables
    
    def get_owned_files(self):
        pks = [k.object.pk for k in self.integer_user_permission_set.filter(content_type__app_label="storage", content_type__model="file", can_modify_permission=True)]
        group_pks = list()
        for group in self.groups.all() :
            group_pks.extend([k.object.pk for k in group.integer_group_permission_set.filter(content_type__app_label="storage", content_type__model="file", can_modify_permission=True)])
        pks.extend(group_pks)
        cls = get_class("storage", "File")
        files = cls.objects.filter(pk__in=pks, requests__state__in=["requested", "accepted", "refused"]).distinct()
        return files
        
