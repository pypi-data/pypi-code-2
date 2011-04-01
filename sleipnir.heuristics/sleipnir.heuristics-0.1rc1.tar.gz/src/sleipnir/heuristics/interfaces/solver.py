#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Interface Solver

Required by algorithm which solves TSP problems
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['ISolver']

# Project dependences
from sleipnir.components.entrypoint import Interface


#pylint: disable-msg=W0232
class ISolver(Interface):
    """
    Defined by components that solve, aproximate or find a optimun for
    a valid TSP
    """

    def register_callback(callback):
        """
        Register 'callback' function to be invoked whenever a solution
        cal has been found or a 'partial' argument has been defined
        and reached

        See also -- prepare for details
        """
        raise NotImplementedError

    def register_inprogress(callback):
        """
        Register a 'callback' function to be invoked whenever a
        partial solution is calculated. Intervals are established by
        keyword arguments passed to prepare method

        See also -- prepare for details
        """
        raise NotImplementedError

    def register_errback(callback):
        """
        Register a 'callback' function to be invoked whenever a problem
        is found when a solution is trying to be calculated

        See also -- prepare for details
        """
        raise NotImplementedError

    def prepare(self, problem, **kwargs):
        """
        Prepare a new problem to calculate a solution for 'instance'
        TSP problem

        Keyword arguments:
        iterations -- Number of iterations that should run the
        heuristic to calculate a good minimum
        partial -- interval size, expressed in procecntage, from which
        callbacks should be called to measure progress. Defaults to
        100%

        Returns a task to be executed
        """
        raise NotImplementedError

    def run(self, task):
        """Start a task and wait till ends"""
        raise NotImplementedError

    def is_running(self, task):
        """Check if solver is currently running a task"""
        raise NotImplementedError

    def start(self, task):
        """Start a task in background"""
        raise NotImplementedError

    def stop(self, task):
        """Stop current execution"""
        raise NotImplementedError

    def wait(self, task, remain=None):
        """Wait for task to be finished"""
        raise NotImplementedError

    def wait_any(self):
        """
        Wait for any of tasks runned by this solver to be
        finished. Returns finished task
        """
        raise NotImplementedError

    def wait_all(self):
        """Wait for all tasks runned by this solver to be finished"""
        raise NotImplementedError

    @classmethod
    def can_handle(cls, instance):
        """
        Check if problem described by 'instance' object could be
        managed by this Solver
        """
        raise NotImplementedError

        #sol = ants.calculate(graph, iters=iterations, partial=100)
        #sol = ants.calculate(graph, iters=iterations, partial=(10%,improved,))
        #sol = ants.calculate(graph, iters=iterations,
        #notify={partial:10, when_improved:True})
