from datetime import datetime

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from magneto import cache_key


def get_current_site():
    return Site.objects.get_current().pk


class Group(models.Model):
    name = models.CharField(_("Name"), unique=True, max_length=100)

    def __unicode__(self):
        return self.name


class Template(models.Model):

    TYPE_CHOICES = (
        ("text/html", "Web Page"),
        ("text/plain", "Template"),
        ("text/css", "CSS Stylesheet"),
        ("text/javascript", "Javascript"),
        ("application/json", "JSON"),
        ("text/xml", "XML"),
    )

    name = models.CharField(_("Name"), unique=True, max_length=200)
    content_type = models.CharField(max_length=32, choices=TYPE_CHOICES,
        default="text/html")
    content = models.TextField(_("Content"), blank=True)
    group = models.ForeignKey("magneto.Group")
    site = models.ForeignKey("sites.Site", default=get_current_site)
    visible = models.BooleanField(default=False)
    date_created = models.DateTimeField( _("Date Created"),
        default=datetime.now)
    date_changed = models.DateTimeField(_('Date Changed'),
        default=datetime.now)
    last_modified_by = models.ForeignKey("auth.User",
        blank=True, null=True)

    objects = models.Manager()
    on_site = CurrentSiteManager("site")

    class Meta:
        ordering = ("name", )
        unique_together = ("name", "site")
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")

    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.name = self.name.strip("/")
        self.date_changed = datetime.now()
        super(Template, self).save(*args, **kwargs)
        cache.delete(cache_key(self.name))

    @models.permalink
    def get_absolute_url(self):
        if self.name == "index":
            return ("magneto.detail.index", )
        else:
            return ("magneto.detail", [self.name])
