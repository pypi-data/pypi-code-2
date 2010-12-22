# Copyright (c) 2010 by Yaco Sistemas <pmartin@yaco.es>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import os

from django.db import models

from stdfile.forms.fields import RemovableImageFormField, RemovableFileFormField


class RemovableFileField(models.FileField):

    def delete_file(self, instance, *args, **kwargs):
        if getattr(instance, self.attname):
            image = getattr(instance, '%s' % self.name)
            file_name = image.path
            # If the file exists and no other object of this type references it,
            # delete it from the filesystem.
            if os.path.exists(file_name) and \
                not instance.__class__._default_manager.filter(**{'%s__exact' % self.name: getattr(instance, self.attname)}).exclude(pk=instance._get_pk_val()):
                os.remove(file_name)

    def get_internal_type(self):
        return 'FileField'

    def save_form_data(self, instance, data):
        if data and data[0]: # Replace file
            self.delete_file(instance)
            super(RemovableFileField, self).save_form_data(instance, data[0])
        if data and data[1]: # Delete file
            self.delete_file(instance)
            setattr(instance, self.name, None)

    def formfield(self, **kwargs):
        defaults = {'form_class': RemovableFileFormField}
        defaults.update(kwargs)
        return super(RemovableFileField, self).formfield(**defaults)


class RemovableImageField(models.ImageField, RemovableFileField):

    def formfield(self, **kwargs):
        defaults = {'form_class': RemovableImageFormField}
        defaults.update(kwargs)
        return super(RemovableFileField, self).formfield(**defaults)
