#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User, Group 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast

class UnderAccessControlEntity(models.Model):
    """Set a model Class under access control to enable Helmholtz Permission system."""
    entity = models.OneToOneField(ContentType, primary_key=True)
    can_be_downloaded = models.NullBooleanField(null=True, blank=True)
    
    class Meta :
        verbose_name_plural = "under access control entities"
    
    def __unicode__(self):
        return self.entity.model_class().__name__

class Permission(Cast):
    """Define permission types of a user or group Permission on an object."""
    can_view = models.BooleanField(verbose_name='view', default=True, null=False)
    can_modify = models.BooleanField(verbose_name='modify', default=False, null=False)
    can_delete = models.BooleanField(verbose_name='delete', default=False, null=False)
    can_download = models.BooleanField(verbose_name='download', default=False, null=False)
    can_modify_permission = models.BooleanField(verbose_name='is_owner', default=False, null=False)
    
    class Meta:
        ordering = ['id']
    
    def __unicode__(self):
        code = self.get_code()
        return "%s" % (code)
    
    def get_code(self):
        """Return a string resuming all permission types."""
        rights = ''
        rights += str(int(self.can_view))
        rights += str(int(self.can_modify))
        rights += str(int(self.can_delete))
        rights += str(int(self.can_download))
        rights += str(int(self.can_modify_permission))
        return rights

class IntegerPermission(Permission):
    """Link a Permission to an object having integer as primary key."""
    content_type = models.ForeignKey(ContentType, related_name="integer_permissions") 
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id') 
    
    def get_rights(self):
        """Return a string resuming all permission types for the relative object."""
        rights = self.get_code()
        st = u'(%s,%s)' % (rights, self.object) if rights else None       
        return st

class CharPermission(Permission):
    """Link a Permission to an object having text as primary key."""
    content_type = models.ForeignKey(ContentType, related_name="char_permissions") 
    object_id = models.TextField()
    object = generic.GenericForeignKey('content_type', 'object_id') 
    
    def get_rights(self):
        """Return a string resuming all permission types for the relative object."""
        rights = self.get_code()
        st = u'(%s,%s)' % (rights, self.object) if rights else None       
        return st

class IntegerUserPermission(IntegerPermission):
    """Define User Permission on an object having integer as primary key."""
    user = models.ForeignKey(User, null=True, related_name="integer_user_permission_set")
    
    def __unicode__(self):
        rights = self.get_rights()
        return "%s %s" % (self.user, rights)
    
    class Meta:
        ordering = ['user__username']
        verbose_name = "user permission on integer pk object"
        verbose_name_plural = "user permissions on integer pk objects"

class CharUserPermission(CharPermission):
    """Define User Permission on an object having text as primary key."""
    user = models.ForeignKey(User, null=True, related_name="char_user_permission_set")
    
    def __unicode__(self):
        rights = self.get_rights()
        return "%s %s" % (self.user, rights)
    
    class Meta:
        ordering = ['user__username']
        verbose_name = "user permission on char pk object"
        verbose_name_plural = "user permissions on char pk objects"

class IntegerGroupPermission(IntegerPermission):
    """Define User Permission on an object having integer as primary key."""
    group = models.ForeignKey(Group, null=True, related_name="integer_group_permission_set")
    
    def __unicode__(self):
        rights = self.get_rights()
        return "%s %s" % (self.group, rights)
    
    class Meta:
        ordering = ['group__name']
        verbose_name = "group permission on integer pk object"
        verbose_name_plural = "group permissions on integer pk objects"

class CharGroupPermission(CharPermission):
    """Define Group Permission on an object having text as primary key."""
    group = models.ForeignKey(Group, null=True, related_name="char_group_permission_set")
    
    def __unicode__(self):
        rights = self.get_rights()
        return "%s %s" % (self.group, rights)
    
    class Meta:
        ordering = ['group__name']
        verbose_name = "group permission on char pk object"
        verbose_name_plural = "group permissions on char pk objects"
