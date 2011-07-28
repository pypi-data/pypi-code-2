# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 1328 2010-01-09 14:25:15Z mac $

import doctest

def test_all():
    return doctest.DocFileSuite('README.txt')
