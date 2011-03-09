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

from django import forms

from configfield import params

from dbresolver import get_registered_views, get_view_info
from dbresolver.models import URLPattern


class URLPatternForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(URLPatternForm, self).__init__(*args, **kwargs)
        view_choices = [(view_id, view['label']) for view_id, view in get_registered_views()]
        self.fields['view_path'] = forms.ChoiceField(choices=view_choices)
        instance = kwargs.pop('instance', None)
        if instance and 'view_params' in self.fields.keys():
            config_params = get_view_info(instance.view_path)['params']
            config = params.ConfigDict(config_params, instance.view_params)
            self.fields['view_params'].set_config(config)

    class Meta:
        model = URLPattern
