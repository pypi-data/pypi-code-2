# -*- coding: utf-8 -*-
#
#  This file is part of django-context-extras.
#
#  django-context-extras provides some extra context processors that are often needed by Django projects.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-context-extras
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-context-extras
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


VERSION = (0, 2, 1, 'final', 0)

def get_version():
    version = '%d.%d.%d' % (VERSION[0], VERSION[1], VERSION[2])
    return version

