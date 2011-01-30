"Models for django-panorama"

from django.db import models
from multilingual.translation import TranslationModel
from django.utils.translation import ugettext_lazy as _
from tinymce.models import HTMLField
from panorama.settings import DIRECTION_CHOICES, CONTROL_DISPLAY_CHOICES

# Create your models here.

class Panorama (models.Model):
    """
      This model stores a panoramic image.
    """
    class Translation(TranslationModel):
        title = models.CharField(name=_('title'), max_length=30)
    image = models.ImageField(name=_('image'), upload_to='panoramas/')
    viewport_width = models.IntegerField(
            name=_('viewport width'),
            help_text=_("Width of the panorama window in pixels."),
            blank=True,
            null=True)
    speed = models.IntegerField(
            name=_('speed'),
            help_text=_("Speed of the panorama rotation. "
                        "Lower value means faster."),
            blank=True,
            null=True)
    direction = models.CharField(
            name=_('direction'),
            max_length=5,
            choices = DIRECTION_CHOICES,
            blank=True,
            null=True)
    control_display = models.CharField(
            name=_('control display'),
            help_text=_("Display rotation controls?"),
            max_length=5,
            choices = CONTROL_DISPLAY_CHOICES,
            blank=True,
            null=True)
    start_position = models.IntegerField(
            name=_('start position'),
            help_text=_("Start position of the panorama, in pixels"),
            blank=True,
            null=True)
    auto_start = models.NullBooleanField(
            name=_('auto start'),
            blank=True,
            null=True)
    mode_360 = models.NullBooleanField(
            name=_('mode 360'),
            help_text=_("Loop over the panorama?"),
            blank=True,
            null=True)

    class Meta:
        verbose_name = _('panorama')
        verbose_name_plural = _('panoramas')

    def __unicode__(self):
        return self.title or _('New Panorama')

    @models.permalink
    def get_absolute_url(self):
        return ('panorama_detail', [str(self.id)])


class PanoramaInfo(models.Model):
    """
      This base model defines the attributes needed to attach info to a
      panorama. Attached info will be seen as rectangles floating over
      panorama.
      
      Not really useful alone, see Note, Link, ExternalLink, etc.
    """
    panorama = models.ForeignKey('Panorama',
                                 name=_('panorama'),
                                 related_name = 'panorama')
    x0 = models.IntegerField(name=u'X0')
    x1 = models.IntegerField(name=u'X1')
    y0 = models.IntegerField(name=u'Y0')
    y1 = models.IntegerField(name=u'Y1')
    type = None
    url = None
    alt = None

    #class Meta:
    #    abstract = True

class ExternalLink(PanoramaInfo):
    """
      Show a external web inside a iframe when clicked in this
      PanoramaInfo.
    """
    class Translation(TranslationModel):
        title = models.CharField(name=_('title'), max_length=30)
    url = models.CharField(name=u'URL', max_length=200)
    type = 'iframe'

    class Meta:
        verbose_name = _('external link')
        verbose_name_plural = _('external links')

    def __unicode__(self):
        return self.title or _('New External Link')

    def alt(self):
        "Show title as img alt attribute"
        return self.title

class Link(PanoramaInfo):
    """
      Link to another Panorama model.
    """
    target_panorama = models.ForeignKey(Panorama, name=_("target panorama"))

    def url(self):
        return self.target_panorama.get_absolute_url()

    def alt(self):
        return self.target_panorama.title

    def __unicode__(self):
        return _(u"Link to panorama %s") % self.target_panorama.title

class Note(PanoramaInfo):
    """
      Show a HTML note as a popup when clicked this PanoramaInfo.
    """
    class Translation(TranslationModel):
        title = models.CharField(name=_('title'), max_length=30)
        description = HTMLField(name=_('description'), blank=True)
    type = 'ajax'

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')

    def __unicode__(self):
        return self.title or _('New Note')

    @models.permalink
    def get_absolute_url(self):
        return ('panorama.views.show_note', [str(self.id)])

    def alt(self):
        "Show title as img alt attribute"
        return self.title

    def url(self):
        "Url where this panoraminfo points"
        return self.get_absolute_url()
