"""
A simple example to test simple addition.
"""

import inputgen


class Adder(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return '<Adder, left: %s, right: %s>' % (self.left, self.right)

    def add(self):
        return self.left + self.right


class AddTest(inputgen.TestCase):

    @staticmethod
    def repOK(factory):
        obj = factory.adder
        if not isinstance(obj.left, int):
            return False
        if not isinstance(obj.right, int):
            return False
        return True

    @staticmethod
    def fin():#(min_size, max_size):
        f = inputgen.Factory()
        adder = f.create(Adder)
        f.set('adder', adder)

        values = [0, 1, 2]
        adder.set('left', values)
        adder.set('right', values)
        return f

    def run_method(self, factory):
        obj = factory.adder
        self.assertEquals(obj.add(), obj.left + obj.right)
        return obj


if __name__ == "__main__":
    import unittest
    unittest.main()
