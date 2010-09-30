from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
import mptt

from yama.utils import get_content_types
from yama.settings import VIEWS

class Menu(models.Model):
    MENU_TYPES = (
            ('L', _('Left')),
            ('R', _('Right')),
            ('U', _('Up')),
            ('D', _('Down')),
    )
    name = models.CharField(max_length=100, verbose_name=_('name'))
    type = models.CharField(max_length=1, choices=MENU_TYPES, verbose_name=_('type'))
    visible = models.NullBooleanField(verbose_name=_('visible'), null=True)
    language = models.CharField(max_length = 8, choices = settings.LANGUAGES, verbose_name=_('language'))

    class Meta:
        # we'll make sure that visible is NULL if it's not set, so it's safe
        # to use this constraint here
        unique_together = ('visible', 'type', 'language')
        verbose_name = _('menu')
        verbose_name_plural = _('menus')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.visible:
            self.visible = None
        super(Menu, self).save()

    def all_visible_items(self):
        return self.menuitem_set.filter(visible=True)

    def top_visible_items(self):
        return MenuItem.objects.filter(menu=self, parent__isnull=True, visible=True)

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, verbose_name=_('menu'))
    parent = models.ForeignKey('self', blank=True, null=True, verbose_name=_('parent'), related_name=_('children'))
    caption = models.CharField(_('caption'), max_length = 100)
    link_url = models.CharField(_('URL link'), max_length = 100, null=True, blank=True)
    link_view = models.CharField(_('link to a view'), choices=VIEWS, max_length=100, null=True, blank=True, default=None)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), null=True, blank=True, 
                                     limit_choices_to = {'pk__in' : get_content_types()})
    object_id = models.PositiveIntegerField(_('object id'), null=True, blank=True)
    link_object = generic.GenericForeignKey('content_type', 'object_id')
    open_in_new_window = models.BooleanField(_('open in a new window'))
    visible = models.BooleanField(_('visible'))

    class Meta:
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')

    def __unicode__(self):
        if self.parent:
            return self.parent.caption + u' / ' + self.caption
        else:
            return self.caption

    def get_absolute_url(self):
        return self.link
 
    def save(self):
        # one and only one of [link_url, link_view, link_object] cannot be null
        conditions = [bool(self.link_url), bool(self.link_view), bool(self.content_type) and bool(self.object_id)]
        conditions = sum(map(int, conditions))
        if conditions != 1:
            raise MenuItemException, \
                """One and only one of [link_url, link_view, (content_type and object_id)] must be set: 
                    link_url(%s); link_view(%s), content_type(%s), object_id(%s)""" % \
                        (self.link_url, self.link_view, self.content_type, self.object_id)
        super(MenuItem, self).save()

    @property
    def link(self):
        if self.link_url:
            return self.link_url
        elif self.link_object:
            return self.link_object.get_absolute_url()
        else:
            parts = self.link_view.split()
            app_name, args = parts[0], parts[1:]
            try:
                link = reverse(app_name, args=args)            
            except NoReverseMatch:
                try:
                    project_name = settings.SETTINGS_MODULE.split('.')[0]
                    link = reverse(project_name + '.' + app_name,
                                   args=args)
                except NoReverseMatch, e:
                    # fail gracefully
                    link = ''
            return link

    def has_visible_children(self):
        return self.children.filter(visible=True).count() != 0

    def visible_children(self):
        return self.children.filter(visible=True)

mptt.register(MenuItem)
MenuItem.objects = MenuItem._tree_manager

class MenuItemException(ValidationError):
    """ Improper menu item data """
    pass
