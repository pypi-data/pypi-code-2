from django.db import models
from multilingual.translation import TranslationModel
from django.utils.translation import ugettext_lazy as _
from tinymce.models import HTMLField

# Create your models here.

class Panorama (models.Model):
    """
      This model stores a panoramic image.
    """
    class Translation(TranslationModel):
        title = models.CharField(name=_('title'), max_length=30)
    image = models.ImageField(name=_('image'), upload_to='panoramas/')

    class Meta:
        verbose_name = _('panorama')
        verbose_name_plural = _('panoramas')

    def __unicode__(self):
        return self.title or 'New Panorama'

    @models.permalink
    def get_absolute_url(self):
        return ('panorama_detail', [str(self.id)])


class PanoramaInfo(models.Model):
    """
      This base model defines the attributes needed to attach info to a
      panorama. Attached info will be seen as rectangles floating over
      panorama.
      
      Not really useful alone, see PanoramaNote, PanoramaExternalLink, etc.
    """
    panorama = models.ForeignKey('Panorama', name=_('panorama'))
    x0 = models.IntegerField(name=u'X0')
    x1 = models.IntegerField(name=u'X1')
    y0 = models.IntegerField(name=u'Y0')
    y1 = models.IntegerField(name=u'Y1')
    type = None
    url = None
    alt = None

    #class Meta:
    #    abstract = True


class PanoramaExternalLink(PanoramaInfo):
    """
      Show a external web inside a iframe when clicked in this
      PanoramaInfo.
    """
    class Translation(TranslationModel):
        title = models.CharField(name=_('title'), max_length=30)
    url = models.CharField(name=u'URL', max_length=200)
    type = 'iframe'
    def __unicode__(self):
        return self.title or 'New Panorama External Link'

    def alt(self):
        return self.title

class PanoramaNote(PanoramaInfo):
    """
      Show a HTML note as a popup when clicked this PanoramaInfo.
    """
    class Translation(TranslationModel):
        title = models.CharField(name=_('title'), max_length=30)
        description = HTMLField(name=_('description'), blank=True)
    type = 'ajax'

    @models.permalink
    def get_absolute_url(self):
        return ('panorama.views.show_note', [str(self.id)])

    def __unicode__(self):
        return self.title or 'New Panorama Note'

    def alt(self):
        return self.title

    def url(self):
        return self.get_absolute_url()
