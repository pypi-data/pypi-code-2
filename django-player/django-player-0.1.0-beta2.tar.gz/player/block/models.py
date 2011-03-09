# Copyright (c) 2010 by Manuel Saelices
#
# This file is part of django-playerlayer.
#
# django-playerlayer is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-playerlayer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-playerlayer.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.utils.translation import ugettext_lazy as _

from player.base.dbfields import ConfigField
from player.block import get_block as get_block_by_path
from player.block.managers import PlacedBlockManager


class PlacedBlock(models.Model):
    name = models.CharField(max_length=200)
    block_path = models.CharField(max_length=200)
    placed_at = models.CharField(max_length=100, db_index=True)
    order = models.PositiveIntegerField(db_index=True)
    is_active = models.BooleanField(default=True)
    config = ConfigField(_('Configuration'), null=True, blank=True)

    objects = PlacedBlockManager()

    class Meta:
        ordering = ('order', )

    def __unicode__(self):
        return self.name

    def get_block(self):
        if hasattr(self, '_block'):
            return self._block  # cached block
        self._block = get_block_by_path(self.block_path, self)
        return self._block

    def show(self, place, request, context):
        return self.get_block().show(place, request, context)

    def render(self, request, context):
        return self.get_block().render(request, context)
