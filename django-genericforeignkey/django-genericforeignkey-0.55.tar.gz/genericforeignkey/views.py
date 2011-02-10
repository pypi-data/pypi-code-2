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
from django.shortcuts import render_to_response
from django.template import RequestContext

from genericforeignkey.utils import get_objects_of_content_type


def generic_object_list(request):
    content_type_id = request.GET.get('content_type_id', None)
    content_type = ContentType.objects.get(pk=content_type_id)
    objs = get_objects_of_content_type(request, content_type=content_type)
    return render_to_response('genericforeignkey/object_list.html',
                              {'objs': objs,
                               'content_type': content_type},
                              context_instance=RequestContext(request))
