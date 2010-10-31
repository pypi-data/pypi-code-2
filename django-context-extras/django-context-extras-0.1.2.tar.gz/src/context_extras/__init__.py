# -*- coding: utf-8 -*-
#
#  This file is part of django-context-extras.
#
#  django-context-extras provides some extra context processors for Django
#  projects.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-context-extras
#
#  Sponsored by:
#    - http://www.g-loaded.eu/
#    - http://www.codetrax.org/
#
#  Copyright (c) 2010 George Notaras <gnot@g-loaded.eu>
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

VERSION = (0, 1, 2, 'final', 0)

def get_version():
    version = '%d.%d.%d' % (VERSION[0], VERSION[1], VERSION[2])
    return version


long_description = """
This is a fairly simple Django application that provides some extra context
processors which are often needed by many other Django applications.

Currently, two extra context processors are available:

*current_site*
  Adds the current ``site`` instance to the template context.
*project_settings*
  Adds the project's ``settings`` object to the template context, so you can
  access the project settings from within the templates.

More information about the installation, configuration and usage of this app
can be found in the **README** file inside the distribution package or in the
project's `wiki <http://www.codetrax.org/projects/django-context-extras/wiki>`_.

Spotted a bug or have a feature request? Feel free to file a report at the
project's `issue tracker <http://www.codetrax.org/projects/django-context-extras/issues>`_.

"""
