from django.db import models
from taggit.managers import TaggableManager
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from os.path import join, abspath, dirname, basename
import datetime
from hashlib import sha224
import random
from django.db.models.signals import pre_delete, pre_save
from shutil import rmtree

def get_upload_to(instance, filename):
    dirs = datetime.datetime.now().strftime("photos/%y/%j/%H/%M/%S")
    praefix = instance.hash
    return join(dirs, praefix, filename)

def get_hash():
    return sha224(str(random.random())).hexdigest()

class Photo(models.Model):
    photo = models.ImageField(_('Photo'), upload_to=get_upload_to, height_field='height', width_field='width', max_length=250)
    height = models.PositiveIntegerField(_('Height'), editable=False)
    width = models.PositiveIntegerField(_('Width'), editable=False)
    display = models.BooleanField(_('Display'), default=True, help_text=_('Enable to display this photo.'))
    name = models.CharField(_('Name'), max_length=250, help_text=_('If no name is given, it is created from filename.'), blank=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    user = models.ForeignKey(User, editable=False, blank=True, null=True)
    tags = TaggableManager()
    timestamp_created = models.DateTimeField(_('Timestamp created'), auto_now_add=True, editable=False)
    timestamp_edited = models.DateTimeField(_('Timestamp edited'), auto_now=True, editable=False)
    hash = models.CharField(_('Hash'), editable=False, default=get_hash, max_length=64)
    
    def get_albums(self):
        return self.album_set.filter(display=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta(object):
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')
        ordering = ('-timestamp_created', )
        
    @models.permalink
    def get_absolute_url(self):
        return ('photo-detail', [self.id])
        
class Album(models.Model):
    display = models.BooleanField(_('Display'), default=True, help_text=_('Disable to not display this gallery.'))
    name = models.CharField(_('Name'), max_length=250)   
    description = models.TextField(_('Description'), blank=True, null=True)
    photos = models.ManyToManyField(Photo, verbose_name=_('Photos'))
    tags = TaggableManager()
    user = models.ForeignKey(User, editable=False, blank=True, null=True)
    timestamp_created = models.DateTimeField(_('Timestamp created'), auto_now_add=True, editable=False)
    timestamp_edited = models.DateTimeField(_('Timestamp edited'), auto_now=True, editable=False)
    
    def get_photos(self):
        return self.photos.filter(display=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta(object):
        verbose_name = _('Album')
        verbose_name_plural = _('Albums')
        ordering = ('-timestamp_created', )
        
    @models.permalink
    def get_absolute_url(self):
        return ('album-detail', [self.id])

def pre_save_photo(*args, **kwargs):
    instance = kwargs['instance']
    path = instance.photo.path
    if not instance.name:
        name = basename(path).rsplit(".", 1)[0]
        instance.name = name
    
pre_save.connect(pre_save_photo, sender=Photo)

def pre_delete_photo(*args, **kwargs):
    instance = kwargs['instance']
    try:
        path = instance.photo.path
    except ValueError, e:
        pass # silently
    else:
        rmtree(path=abspath(dirname(path)), ignore_errors=True)

pre_delete.connect(pre_delete_photo, sender=Photo)
    