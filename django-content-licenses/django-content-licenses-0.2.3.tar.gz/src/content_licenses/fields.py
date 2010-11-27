# -*- coding: utf-8 -*-
#
#  This file is part of django-content-licenses.
#
#  django-content-licenses is a Django app that adds support for adding licensing information to content.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-content-licenses
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-content-licenses
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from django.db import models


class LicenseField(models.ForeignKey):
    """The LicenseField makes it possible to select one of the available licenses.
    
    """
    def __init__(self, **kwargs):
        super(LicenseField, self).__init__('content_licenses.License',
            related_name='%(class)s_license', **kwargs)

