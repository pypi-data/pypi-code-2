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

from unittest import TestCase, skip

from pytilities.geometry import (Vector as V, Rectangle as R, 
    DiscreteRectangle, verbose_rectangle_aspect)

class RectangleCtorTestCase(TestCase):
    def test_ctor_points(self):
        r = R(V(2.0, 3.0), V(3.0, 4.0))
        self.assertEqual(r.bounds, (2, 3, 3, 4))

        r = R(V(-2.0, -3.0), V(3.0, 4.0))
        self.assertEqual(r.bounds, (-2, -3, 3, 4))

    def test_ctor_nums(self):
        r = R(2.0, 3.0, 4.0, 4.0)
        self.assertEqual(r.bounds, (2, 3, 4, 4))

        r = R(-5.0, -5.0, 2.0, 2.0)
        self.assertEqual(r.bounds, (-5, -5, 2, 2))


class RectangleTestCase(TestCase):
    # called for every test method in here
    def setUp(self):
        self.r = R(-3.0, 2.0, 6.0, 7.0)

    def test_nums(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.left, -3)
        self.assertEqual(self.r.top, 2)
        self.assertEqual(self.r.right, 6)
        self.assertEqual(self.r.bottom, 7)

        self.r.left = 2.0
        self.r.top = 1.0
        self.r.right = 3.0
        self.r.bottom = 4.0

        self.assertEqual(self.r.left, 2)
        self.assertEqual(self.r.top, 1)
        self.assertEqual(self.r.right, 3)
        self.assertEqual(self.r.bottom, 4)
        
    def test_points(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.top_left.xy, (-3, 2))
        self.assertEqual(self.r.top_right.xy, (6, 2))
        self.assertEqual(self.r.bottom_left.xy, (-3, 7))
        self.assertEqual(self.r.bottom_right.xy, (6, 7))

    def test_boundness_1(self):
        # R(-3, 2, 6, 7)
        self.r.top_left.x = 3.0
        self.r.top_left.y = -2.0
        self.r.bottom_right.x = -6.0
        self.r.bottom_right.y = -7.0

        self.assertEqual(self.r.top_left.xy, (3, -2))
        self.assertEqual(self.r.top_right.xy, (-6, -2))
        self.assertEqual(self.r.bottom_left.xy, (3, -7))
        self.assertEqual(self.r.bottom_right.xy, (-6, -7))

    def test_boundness_2(self):
        # R(-3, 2, 6, 7)
        self.r.top_right.x = -6.0
        self.r.top_right.y = -2.0
        self.r.bottom_left.x = 3.0
        self.r.bottom_left.y = -7.0

        self.assertEqual(self.r.top_left.xy, (3, -2))
        self.assertEqual(self.r.top_right.xy, (-6, -2))
        self.assertEqual(self.r.bottom_left.xy, (3, -7))
        self.assertEqual(self.r.bottom_right.xy, (-6, -7))

    def test_diagonal_points1(self):
        # R(-3, 2, 6, 7)
        self.r.top_left = V(1.0, 2.0)
        self.r.bottom_right = V(4.0, 3.0)

        self.assertEqual(self.r.top_left.xy, (1, 2))
        self.assertEqual(self.r.top_right.xy, (4, 2))
        self.assertEqual(self.r.bottom_left.xy, (1, 3))
        self.assertEqual(self.r.bottom_right.xy, (4, 3))

    def test_diagonal_points2(self):
        # R(-3, 2, 6, 7)
        self.r.top_right = V(4.0, 2.0)
        self.r.bottom_left = V(1.0, 3.0)

        self.assertEqual(self.r.top_left.xy, (1, 2))
        self.assertEqual(self.r.top_right.xy, (4, 2))
        self.assertEqual(self.r.bottom_left.xy, (1, 3))
        self.assertEqual(self.r.bottom_right.xy, (4, 3))

    def test_center(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.center.xy, (1.5, 4.5))

        size = self.r.size.copy()
        pos = self.r.top_left.copy()

        self.r.center = self.r.center # should have no effect on r
        self.assertEqual(pos, self.r.top_left)
        self.assertEqual(size, self.r.size)

        self.r.center = V(0.0, 0.0)

        self.assertEqual(self.r.bounds, (-4.5, -2.5, 4.5, 2.5))
        self.assertEqual(size, self.r.size)  # size musn't change

    def test_size(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.size.xy, (9, 5))

        top_left = self.r.top_left.copy()
        self.r.size = V(2.0, 2.0)

        self.assertEqual(self.r.size.xy, (2, 2))
        self.assertEqual(self.r.bottom_right.xy, (-1, 4))
        self.assertEqual(top_left, self.r.top_left)

    def test_boundness_size(self):
        # R(-3, 2, 6, 7)
        top_left = self.r.top_left.copy()

        self.r.size.x = 2.0
        self.r.size.y = 2.0

        self.assertEqual(self.r.size.xy, (2, 2))
        self.assertEqual(self.r.bottom_right.xy, (-1, 4))
        self.assertEqual(top_left, self.r.top_left)

    def test_bounds(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.bounds, (-3, 2, 6, 7))

        self.r.bounds = (-5.0, -5.0, 2.0, 2.0)
        self.assertEqual(self.r.bounds, (-5, -5, 2, 2))

        self.r.bounds = (V(-2.0, -3.0), V(3.0, 4.0))
        self.assertEqual(self.r.bounds, (-2, -3, 3, 4))
    
    def test_contains(self):
        # R(-3, 2, 6, 7)
        self.assertTrue(self.r.contains(V(0,3)))
        self.assertTrue(self.r.contains(V(-3,2)))
        self.assertFalse(self.r.contains(V(-4,0)))
        self.assertFalse(self.r.contains(V(0,8)))

    def test_overlaps(self):
        # R(-3, 2, 6, 7)
        self.assertTrue(self.r.overlaps(R(0.0, 0.0, 8.0, 8.0)))

        # should be false, even if just touching
        self.assertFalse(self.r.overlaps(R(-4.0, 1.0, -3.0, 2.0)))

    def test_inflate(self):
        # R(-3, 2, 6, 7)
        bounds = self.r.bounds

        self.r.inflate(2.0)
        self.assertEqual(self.r.bounds, (-5, 0, 8, 9))

        self.r.inflate(-2.0)
        self.assertEqual(self.r.bounds, bounds)

        self.r.inflate(V(2.0, 1.0))
        self.assertEqual(self.r.bounds, (-5, 1, 8, 8))

    def test_move_to(self):
        # R(-3, 2, 6, 7)
        self.r.move_to(V(5.0, 8.0))
        self.assertEqual(self.r.bounds, (5, 8, 14, 13))

    def test_move_by(self):
        # R(-3, 2, 6, 7)
        self.r.move_by(V(4.0, -1.0))
        self.assertEqual(self.r.bounds, (1, 1, 10, 6))

    def test_independence(self):
        # R(-3, 2, 6, 7)
        # modifying one rect shouldn't modify another
        r2 = R(1.0, 1.0, 50.0, 50.0)
        self.r.move_to(V(4.0, -1.0))
        self.assertEqual(r2.bounds, (1, 1, 50, 50))


class DiscreteRectangleCtorTestCase(TestCase):
    def test_ctor_points(self):
        r = DiscreteRectangle(V(2, 3), V(3, 4))
        self.assertEqual(r.bounds, (2, 3, 3, 4))

        r = DiscreteRectangle(V(-2, -3), V(3, 4))
        self.assertEqual(r.bounds, (-2, -3, 3, 4))

    def test_ctor_nums(self):
        r = DiscreteRectangle(2, 3, 4, 4)
        self.assertEqual(r.bounds, (2, 3, 4, 4))

        r = DiscreteRectangle(-5, -5, 2, 2)
        self.assertEqual(r.bounds, (-5, -5, 2, 2))


class DiscreteRectangleTestCase(TestCase):
    # called for every test method in here
    def setUp(self):
        self.r = DiscreteRectangle(-3, 2, 6, 7)

    @skip(reason="currently don't check for types here")
    def test_fail(self):
        return
        def setl():
            self.r.left = 2.0

        def sett():
            self.r.top = 2.0

        def setr():
            self.r.right = 7.0

        def setb():
            self.r.bottom = 8.0

        def setp():
            self.r.top_right = V(4.0, 2.0)

        self.assertRaises(AssertionError, setl)
        self.assertRaises(AssertionError, sett)
        self.assertRaises(AssertionError, setr)
        self.assertRaises(AssertionError, setb)
        self.assertRaises(AssertionError, setp)

    def test_nums(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.left, -3)
        self.assertEqual(self.r.top, 2)
        self.assertEqual(self.r.right, 6)
        self.assertEqual(self.r.bottom, 7)

        self.r.left = 2
        self.r.top = 1
        self.r.right = 3
        self.r.bottom = 4

        self.assertEqual(self.r.left, 2)
        self.assertEqual(self.r.top, 1)
        self.assertEqual(self.r.right, 3)
        self.assertEqual(self.r.bottom, 4)
        
    def test_points(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.top_left.xy, (-3, 2))
        self.assertEqual(self.r.top_right.xy, (6, 2))
        self.assertEqual(self.r.bottom_left.xy, (-3, 7))
        self.assertEqual(self.r.bottom_right.xy, (6, 7))

    def test_boundness_1(self):
        # R(-3, 2, 6, 7)
        self.r.top_left.x = 3
        self.r.top_left.y = -2
        self.r.bottom_right.x = -6
        self.r.bottom_right.y = -7

        self.assertEqual(self.r.top_left.xy, (3, -2))
        self.assertEqual(self.r.top_right.xy, (-6, -2))
        self.assertEqual(self.r.bottom_left.xy, (3, -7))
        self.assertEqual(self.r.bottom_right.xy, (-6, -7))

    def test_boundness_2(self):
        # R(-3, 2, 6, 7)
        self.r.top_right.x = -6
        self.r.top_right.y = -2
        self.r.bottom_left.x = 3
        self.r.bottom_left.y = -7

        self.assertEqual(self.r.top_left.xy, (3, -2))
        self.assertEqual(self.r.top_right.xy, (-6, -2))
        self.assertEqual(self.r.bottom_left.xy, (3, -7))
        self.assertEqual(self.r.bottom_right.xy, (-6, -7))

    def test_diagonal_points1(self):
        # R(-3, 2, 6, 7)
        self.r.top_left = V(1, 2)
        self.r.bottom_right = V(4, 3)

        self.assertEqual(self.r.top_left.xy, (1, 2))
        self.assertEqual(self.r.top_right.xy, (4, 2))
        self.assertEqual(self.r.bottom_left.xy, (1, 3))
        self.assertEqual(self.r.bottom_right.xy, (4, 3))

    def test_diagonal_points2(self):
        # R(-3, 2, 6, 7)
        self.r.top_right = V(4, 2)
        self.r.bottom_left = V(1, 3)

        self.assertEqual(self.r.top_left.xy, (1, 2))
        self.assertEqual(self.r.top_right.xy, (4, 2))
        self.assertEqual(self.r.bottom_left.xy, (1, 3))
        self.assertEqual(self.r.bottom_right.xy, (4, 3))

    def test_center(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.center.xy, (1, 4))

        size = self.r.size.copy()
        pos = self.r.top_left.copy()

        self.r.center = self.r.center # should have no effect on r
        self.assertEqual(pos, self.r.top_left)
        self.assertEqual(size, self.r.size)

        self.r.center = V(0, 0)

        self.assertEqual(self.r.bounds, (-4, -2, 5, 3))
        self.assertEqual(size, self.r.size)  # size musn't change

    def test_size(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.size.xy, (10, 6))

        top_left = self.r.top_left.copy()
        self.r.size = V(2, 2)

        self.assertEqual(self.r.size.xy, (2, 2))
        self.assertEqual(self.r.bottom_right.xy, (-2, 3))
        self.assertEqual(top_left, self.r.top_left)

    def test_boundness_size(self):
        # R(-3, 2, 6, 7)
        top_left = self.r.top_left.copy()

        self.r.size.x = 2
        self.r.size.y = 2

        self.assertEqual(self.r.size.xy, (2, 2))
        self.assertEqual(self.r.bottom_right.xy, (-2, 3))
        self.assertEqual(top_left, self.r.top_left)

    def test_bounds(self):
        # R(-3, 2, 6, 7)
        self.assertEqual(self.r.bounds, (-3, 2, 6, 7))

        self.r.bounds = (-5, -5, 2, 2)
        self.assertEqual(self.r.bounds, (-5, -5, 2, 2))

        self.r.bounds = (V(-2, -3), V(3, 4))
        self.assertEqual(self.r.bounds, (-2, -3, 3, 4))
    
    def test_contains(self):
        # R(-3, 2, 6, 7)
        self.assertTrue(self.r.contains(V(0,3)))
        self.assertTrue(self.r.contains(V(-3,2)))
        self.assertFalse(self.r.contains(V(-4,0)))
        self.assertFalse(self.r.contains(V(0,8)))

    def test_overlaps(self):
        # R(-3, 2, 6, 7)
        self.assertTrue(self.r.overlaps(DiscreteRectangle(0, 0, 8, 8)))

        # should be true, this isn't touching, bounds are inclusive and overlap
        # on a size of 1 when some edges are the same
        self.assertFalse(self.r.overlaps(DiscreteRectangle(-4, 1, -3, 2)))

    def test_inflate(self):
        # R(-3, 2, 6, 7)
        bounds = self.r.bounds

        self.r.inflate(2)
        self.assertEqual(self.r.bounds, (-5, 0, 8, 9))

        self.r.inflate(-2)
        self.assertEqual(self.r.bounds, bounds)

        self.r.inflate(V(2, 1))
        self.assertEqual(self.r.bounds, (-5, 1, 8, 8))

    def test_move_to(self):
        # R(-3, 2, 6, 7)
        self.r.move_to(V(5, 8))
        self.assertEqual(self.r.bounds, (5, 8, 14, 13))

    def test_move_by(self):
        # R(-3, 2, 6, 7)
        self.r.move_by(V(4, -1))
        self.assertEqual(self.r.bounds, (1, 1, 10, 6))

    def test_independence(self):
        # R(-3, 2, 6, 7)
        # modifying one rect shouldn't modify another
        r2 = DiscreteRectangle(1, 1, 50, 50)
        self.r.move_to(V(4, -1))
        self.assertEqual(r2.bounds, (1, 1, 50, 50))


class VerboseRectangleTestCase(RectangleTestCase):
    # called for every test method in here
    def setUp(self):
        RectangleTestCase.setUp(self)
        verbose_rectangle_aspect.apply(self.r)

# TODO: test immutable rect view

