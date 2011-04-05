#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Test classes for sleipnir.plugins.marshals"""

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here required modules

__all__ = ['additional_tests']

from sleipnir.testing.data import DATA
from sleipnir.testing.components import create_docsuite
from sleipnir.testing.test import create_suite, run_suite


def setup(test):
    """Register marshals into global's doctest"""

    from sleipnir.heuristics.helpers import marshal
    mso = marshal.MarshalFactory(test.manager)
    uso = marshal.UnMarshalFactory(test.manager)

    tsp_filter = lambda x: x.__class__.__name__.lower().startswith('tsp')
    jsn_filter = lambda x: x.__class__.__name__.lower().startswith('jsn')

    # Now update dictionary
    test.globs.update(
        dict(
            tsp_filter=tsp_filter, jsn_filter=jsn_filter,
            marshal=mso, unmarshal=uso)
        )


def additional_tests():
    """Returns aditional tests"""
    return create_suite([
            create_docsuite(DATA().dct, setup),
            ])

#pylint: disable-msg=C0103
main_suite = additional_tests()

if __name__ == '__main__':
    #pylint: disable-msg=E1120
    run_suite()
