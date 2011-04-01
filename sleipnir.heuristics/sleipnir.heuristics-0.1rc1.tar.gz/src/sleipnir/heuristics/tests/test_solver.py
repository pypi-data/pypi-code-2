#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Test classes for sleipnir.plugins.solvers"""

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here required modules
from functools import partial

# Testing requiements
from sleipnir.testing.data import DATA
from sleipnir.testing.components import TestCaseLoader
from sleipnir.testing.test import create_suite, run_suite

__all__ = ['TestSolverHelpers', ]

# Test requirements
from sleipnir.heuristics.interfaces.solver import ISolver
from sleipnir.heuristics.helpers.solver import SolverFactory
from sleipnir.heuristics.helpers.problem import ProblemFactory


#pylint: disable-msg=R0903,R0904
class TestSolverHelpers(TestCaseLoader):
    """Check if helpers are operative"""

    def test_solver_factory_existence(self):
        """Check that a valid solver factory is available"""

        from sleipnir.components.components import Component, implements

        class FakeTSP(object):
            """dummy tsp"""
            def query(self, iface):
                return iface == 'ITSP'

        # pylint: disable-msg=W0612
        class FakeSolver(Component):
            """dummy solver"""
            implements(ISolver)

            def __init__(self):
                super(FakeSolver, self).__init__()

            # pylint: disable-msg=R0201
            def can_handle(self, instance):
                """dummy method"""
                assert isinstance(instance, FakeTSP)
                return True

        def ffilter(tso, instance):
            """dummy filter"""
            return instance.can_handle(tso)
        ffilter = partial(ffilter, FakeTSP())

        sol = SolverFactory(self._manager)
        assert sol is not None
        assert len(sol.create(ffilter)) == 1

#pylint: disable-msg=C0103
main_suite = create_suite([TestSolverHelpers])

if __name__ == '__main__':
    # pylint: disable-msg=E1120
    run_suite()
