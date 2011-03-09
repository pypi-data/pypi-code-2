# Copyright (c) 2010 by Yaco Sistemas
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

from django import forms

from player.base.fields import ConfigFormField
from player.base.forms import BaseForm
from player.block import get_registered_blocks
from player.block.models import PlacedBlock


class PlacedBlockForm(BaseForm, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PlacedBlockForm, self).__init__(*args, **kwargs)
        instance = kwargs.pop('instance', None)
        block_choices = [(block_key, '%s (%s)' % (unicode(block['label']), block_key)) for block_key, block in get_registered_blocks()]
        self.fields['block_path'] = forms.ChoiceField(choices=block_choices)
        if instance and 'config' in self.fields.keys():
            config = instance.get_block().get_config()
            config_field = self.fields['config']
            config_field.set_config(config)

    class Meta:
        model = PlacedBlock


class BlockConfigForm(forms.Form):
    config = ConfigFormField()
