from django.db import models
from taggit.managers import TaggableManager
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

class Photo(models.Model):
    photo = models.ImageField(_('Photo'), upload_to='%y/%j/%H/%M/%S', height_field='height', width_field='width', max_length=250)
    height = models.PositiveIntegerField(_('Height'))
    width = models.PositiveIntegerField(_('Width'))
    display = models.BooleanField(_('Display'), default=True, help_text=_('Disable to not display this photo.'))
    name = models.CharField(_('Name'), max_length=250)
    description = models.TextField(_('Description'), blank=True, null=True)
    user = models.ForeignKey(User, editable=False, blank=True, null=True)
    tags = TaggableManager()
    timestamp_created = models.DateTimeField(_('Timestamp created'), auto_now_add=True, editable=False)
    timestamp_edited = models.DateTimeField(_('Timestamp edited'), auto_now=True, editable=False)
    
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
