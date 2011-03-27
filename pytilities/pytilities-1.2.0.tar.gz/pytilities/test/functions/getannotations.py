# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

import unittest
from pytilities.functions import get_annotations

class GetAnnotationsTestCase(unittest.TestCase):

    def setUp(self):
        class A(object):
            @property
            def x(self): return 'anything'

            def f(self): pass

        self.A = A

    def test_class(self):
        self.then_annotations_work_on(self.A)

    def test_property(self):
        self.then_annotations_work_on(self.A.x)

    def test_function(self):
        self.then_annotations_work_on(self.A.f)

    def then_annotations_work_on(self, obj):
        self.then_can_get_dict(obj)
        self.then_dict_changes_are_persisted(obj)

    def then_can_get_dict(self, obj):
        annotations = get_annotations(obj)
        self.assertIsNotNone(annotations)
        self.assertIs(annotations, get_annotations(obj))

    def then_dict_changes_are_persisted(self, obj):
        annotations = get_annotations(obj)
        annotations['name'] = 'value'
        self.assertEqual('value', get_annotations(obj)['name'])

