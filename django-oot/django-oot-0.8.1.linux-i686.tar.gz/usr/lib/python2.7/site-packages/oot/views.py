# -*- coding: utf-8 -*-
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

from cStringIO import StringIO
import zipfile

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template import Context, Template
from django.utils.encoding import smart_str

from oot.models import WriterTemplate


def render(template, object_id):
    """Render the object with the given id in an OpenOffice Writer
    document using the Django template system and return it."""
    obj = template.content_type.get_object_for_this_type(id=int(object_id))

    # Don't recalculate the template if is cached
    output_buffer = StringIO()
    output_file = zipfile.ZipFile(output_buffer, 'w')
    odt_file = zipfile.ZipFile(template.template.path, 'r')
    for file_name in odt_file.namelist():
        data = odt_file.read(file_name)
        if file_name == 'content.xml':
            # hook for Django templates in the contents file
            t = cache.get('oot_template_%s' % template.id)
            if t is None:
                data = data.replace('&quot;', '"')
                t = Template(data)
            else:
                cache.set('oot_template_%s' % template.id, t, 18000)
            c = Context({template.content_type.model: obj})
            data = t.render(c)
        output_file.writestr(file_name, smart_str(data))
    output_file.close()
    odt_file.close()

    return output_buffer.getvalue()


def render_writer_template(request, template_id, object_id):
    template = get_object_or_404(WriterTemplate, id=int(template_id))
    try:
        data = render(template, object_id)
    except ObjectDoesNotExist:
        raise Http404

    file_name = '%s.odt' % smart_str(template.title)
    response = HttpResponse(mimetype="application/vnd.oasis.opendocument.text")
    response['Content-Disposition'] = 'attachment;filename="%s"' % file_name
    response.write(data)
    return response
