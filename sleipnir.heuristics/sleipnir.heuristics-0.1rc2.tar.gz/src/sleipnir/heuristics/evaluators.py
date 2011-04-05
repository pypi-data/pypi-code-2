#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Evaluators. A simple class to check if a set of conditions are
satisfied on ISolver implentations
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.
from sleipnir.core.evaluators import Evaluate
from time import time

__all__ = ['All', 'Any']


class SolverEvaluate(Evaluate):
    """A Specific evaluator class for ISolver implementations"""

    def __init__(self, func, iterable):
        super(SolverEvaluate, self).__init__(func, iterable)
        # init defaults
        self._props.setdefault('longest', [None, False, False])
        self._props.setdefault('shortest', [None, False, False])
        self._props.setdefault('percentage', [None, False, False])

    def evaluate(self, **kwargs):
        """Evaluate properties"""
        if 'length' in kwargs:
            length_value = kwargs['length']
            del kwargs['length']
            kwargs.setdefault('longest',  length_value)
            kwargs.setdefault('shortest', length_value)
            kwargs.setdefault('timeout', time())

            return super(SolverEvaluate, self).evaluate(**kwargs)

    def _percentage(self):
        """
        Evaluator method that check if current has reached a multiple
        of init (last) percentage
        """
        stops, current, _ = self._props['percentage']
        if not stops or current != stops[0]:
            return False
        del stops[0]
        return True

    @staticmethod
    def percentage(attr):
        """
        Check if a parameter of the form XX% has been passed to
        constuctor, where XX is an integer between 0 and 100
        """
        try:
            iters, percentage = attr
            if type(iters) not in (int, long,):
                return False
            if type(percentage) not in (str, unicode,):
                return False
            if len(percentage) == 0 or percentage[-1] != '%':
                return False
            if int(percentage[:-1]) > 99 or int(percentage[:-1]) == 0:
                return False
        except ValueError:
            return False
        return range(0, iters, int(iters * float(percentage[:-1]) / 100))[1:]

    def _timeout(self):
        """
        Evaluator method that check if current has reached a multiple
        of init (last) percentage
        """
        timeout, current, _ = self._props['timeout']
        if current < sum(timeout):
            return False
        timeout[1] = current
        return True

    @staticmethod
    def timeout(attr):
        """
        Check if parameter is of the form XXs where XX is number of
        seconds system should stop and raise a partial iteration
        """
        if type(attr) not in (str, unicode,):
            return False
        if len(attr) == 0 or attr[-1] != 's':
            return False
        if int(attr[:-1]) < 1:
            return False
        return [int(attr[:-1]), time()]

    def _longest(self):
        """
        Returns True if current value is longest than previous one
        """
        longest = self._props['longest']
        last, current, _ = longest

        if last and current > last:
            longest[self.LAST] = current
            return True
        return False

    @staticmethod
    def longest(attr):
        """
        Lookup for 'longest' param. If found. ISolver stops whenever a
        longest path was found
        """
        if type(attr) not in (str, unicode):
            return False
        if attr.lower() != 'longest':
            return False
        return True

    def _shortest(self):
        """
        Returns True if current value is shortest than previous one
        """
        shortest = self._props['shortest']
        last, current, _ = shortest

        if last and current > last:
            shortest[self.LAST] = current
            return True
        return False

    @staticmethod
    def shortest(attr):
        """
        Lookup for 'shortest' param. If found. ISolver stops whenever a
        short path was found
        """
        if type(attr) not in (str, unicode):
            return False
        if attr.lower() != 'shortest':
            return False
        return True


class Any(SolverEvaluate):
    """
    A ISolver evaluator that forces stop if solver match ANY of the
    iterable conditions
    """
    def __init__(self, iterable):
        super(Any, self).__init__(any, iterable)


class All(SolverEvaluate):
    """
    A ISolver evaluator that forces stop if solver match ALL iterable
    conditions
    """
    def __init__(self, iterable):
        super(All, self).__init__(all, iterable)
