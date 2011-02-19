#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        test_sylli
# Purpose:     Unit testing
#
# Author:      Luca Iacoponi
#
# Created:     31/12/2010
# Copyright:   (c) Luca Iacoponi 2010
# Licence:     GPL
#-------------------------------------------------------------------------------

import unittest
import doctest

import sylli

class Test(unittest.TestCase):
    """Unit tests for sylli."""

    def test_doctests(self):
        """Run sylli doctests"""
        doctest.testmod(sylli)
        #doctest.testmod(sylli.filepath)
        doctest.testmod(sylli.demo)
        #doctest.testmod(postinst)

if __name__ == "__main__":
    unittest.main()
