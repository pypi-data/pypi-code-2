# -*- coding: utf-8 -*-
#
#  This file is part of django-traxauth.
#
#  django-traxauth adds support for profile management to Django powered projects.
#
#  Copyright (c) 2010 George Notaras <gnot@g-loaded.eu>
#
#  Sponsored by:
#    - http://www.g-loaded.eu/
#    - http://www.codetrax.org/
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-traxauth
#
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-traxauth
#
#  This project has derived from the old self contained and mod-python
#  based traxauth project, which is copyright (c) 2007 George Notaras.
#    - http://www.codetrax.org/projects/traxauth/wiki
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

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}
