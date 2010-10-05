"""intranet automatic tests"""

from cubicweb.devtools.testlib import AutomaticWebTest
from cubicweb.devtools.fill import ValueGenerator

import random

def random_numbers(size):
    return u''.join(random.choice('0123456789') for i in xrange(size))

class MyValueGenerator(ValueGenerator):
    def generate_Book_isbn10(self, entity, index):
        return random_numbers(10)
    def generate_Book_isbn13(self, entity, index):
        return random_numbers(13)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
