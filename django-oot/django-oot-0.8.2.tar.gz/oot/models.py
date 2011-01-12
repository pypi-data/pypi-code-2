# Copyright (c) 2008-2010 by Yaco Sistemas <precio@yaco.es>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this programe.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class WriterTemplate(models.Model):
    title = models.CharField(_(u'title'), max_length=100)
    template = models.FileField(_(u'template'), upload_to='oot')
    content_type = models.ForeignKey(ContentType,
        verbose_name=_(u'content type'))

    class Meta:
        verbose_name = _(u'writer template')
        verbose_name_plural = _(u'writer templates')

    def __unicode__(self):
        return self.title
