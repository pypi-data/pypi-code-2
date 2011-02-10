# Copyright (c) 2010 by Yaco Sistemas <pmartin@yaco.es>
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


def get_objects_of_content_type(request, content_type_id=None, content_type=None):
    content_type = content_type or ContentType.objects.get(pk=content_type_id)
    get = request.GET.copy()
    del(get['content_type_id'])
    request.GET = get
    return content_type.model_class().objects.all()
