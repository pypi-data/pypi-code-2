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

from dbresolver import get_registered_views
from dbresolver.models import URLPattern


class URLPatternForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(URLPatternForm, self).__init__(*args, **kwargs)
        view_choices = [(view_id, view['label']) for view_id, view in get_registered_views()]
        self.fields['view_path'] = forms.ChoiceField(choices=view_choices)

    class Meta:
        model = URLPattern
