# Copyright (c) 2008-2010 by Yaco Sistemas <precio@yaco.es>
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.template import Library
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from oot.models import WriterTemplate
register = Library()


@register.inclusion_tag('writer_templates.html')
def writer_templates(obj):
    result = {'obj_id': obj.id}
    content_type = ContentType.objects.get_for_model(obj)
    templates = WriterTemplate.objects.filter(content_type=content_type)
    result['templates'] = templates
    return result


@register.inclusion_tag('render_image.xml')
def render_image(image_path):
    if image_path[:4] != 'http':
        domain = Site.objects.all()[0].domain
        image_path = 'http://%s%s' % (domain, image_path)
    return {'image_path': image_path}
