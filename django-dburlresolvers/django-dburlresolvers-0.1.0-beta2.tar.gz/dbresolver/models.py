# Copyright (c) 2010 by Manuel Saelices
#
# This file is part of django-urlresolvers.
#
# django-urlresolvers is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-urlresolvers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-urlresolvers.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from surlex import surlex_to_regex
from configfield.dbfields import ConfigField

from dbresolver import reload_urlpatterns

PATTERN_TYPES = (
    ('regex', _('Regular expression')),
    ('surlex', _('Surlex pattern')),
)


class URLPattern(models.Model):
    pattern = models.CharField(
        max_length=200, unique=True,
        help_text=_('It can be a <a href="%(regex_url)s" target="_blank">Django regex</a> or a '
        '<a href="%(surlex_url)s" target="_blank">surlex expression</a>') % {
            'regex_url': 'http://docs.djangoproject.com/en/dev/topics/http/urls/',
            'surlex_url': 'http://codysoyland.com/projects/surlex/documentation/',
        },
    )
    pattern_type = models.CharField(max_length=50, choices=PATTERN_TYPES)
    view_path = models.CharField(max_length=200)
    view_params = ConfigField(null=True, blank=True)

    def __unicode__(self):
        return u'%s -> %s' % (self.pattern, self.view_path)

    def get_regex(self):
        if self.pattern_type == 'surlex':
            return surlex_to_regex(self.pattern)
        return self.pattern

post_save.connect(reload_urlpatterns, sender=URLPattern)
