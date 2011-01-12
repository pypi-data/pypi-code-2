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

from os import path
from StringIO import StringIO
import zipfile

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.template import Template, Context
from django.test import TestCase, Client

from oot.models import WriterTemplate


class OOTTests(TestCase):

    def setUp(self):
        # replace template's storage with my own test storage
        my_media_location = path.join(settings.BASEDIR, 'oot', 'tests_media')
        my_storage = FileSystemStorage(location=my_media_location)
        template_field = WriterTemplate._meta.get_field_by_name('template')[0]
        template_field.storage = my_storage

        # create a WriterTemplate object to be rendered by itself
        self.wt_ct = ContentType.objects.get(app_label='oot',
                                             name='writer template')
        wt = WriterTemplate()
        wt.title = 'Writer Template'
        wt.template = 'writertemplate.odt'
        wt.content_type = self.wt_ct
        wt.save()
        self.wt = wt

    def assertODTContains(self, data):
        data_file = StringIO()
        data_file.write(data)
        odt_file = zipfile.ZipFile(data_file, 'r')
        content = odt_file.read('content.xml')
        odt_file.close()
        data_file.close()
        return self.assert_("Writer Template" in content)

    def test_render_writertemplate_view(self):
        c = Client()
        response = c.get('/oot/render_writer/%s/%s/' % (self.wt.id, self.wt.id))
        self.assertODTContains(response.content)

    def test_templatetag(self):
        t = Template('''{% load oot_templates %}{% writer_templates obj %}''')
        c = Context({'obj': self.wt})
        content = t.render(c)
        self.assert_("Writer Template" in content)
