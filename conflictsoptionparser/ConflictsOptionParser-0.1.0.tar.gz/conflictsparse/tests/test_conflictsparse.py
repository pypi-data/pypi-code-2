#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.

"""Tests for ``conflictsparse.py``"""

import os.path
import sys
import unittest

parpath = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

import conflictsparse


# This is a hack to shut optparse up when it causes a system exit, so
# we're not writing a bunch of junk to STDERR while testing.
class DevNull(object):
    def write(self, x):
        pass

conflictsparse.optparse.sys.stderr = DevNull()


class ConflictsOptionParserTests(unittest.TestCase):
    """Tests for ``ConflictingParsedOptionsError``."""
    def setUp(self):
        self.parser = conflictsparse.ConflictsOptionParser('test')
        self.foo_opt = self.parser.add_option('-f', '--foo')
        self.bar_opt = self.parser.add_option('--bar')
        self.verbose_opt = self.parser.add_option('-v', '--verbose',
                action='store_true', dest='verbose')
        self.q_opt = self.parser.add_option('-q', action='store_false',
                dest='verbose')


    def test_no_conflicts_registered_none_given(self):
        opts, args = self.parser.parse_args(
                ['-f', '1', '--bar', '2', '-v', '42'])
        self.assertEqual(args, ['42'])
        self.assertEqual(opts.foo, '1')
        self.assertEqual(opts.bar, '2')
        self.assertEqual(opts.verbose, True)


    def test_conflicts_registered_none_given(self):
        self.parser.register_conflict((self.verbose_opt, self.q_opt))
        self.parser.register_conflict((self.bar_opt, self.foo_opt))
        opts, args = self.parser.parse_args(
                ['-f', '1', '-v', '42'])
        self.assertEqual(args, ['42'])
        self.assertEqual(opts.foo, '1')
        self.assertEqual(opts.verbose, True)


    def test_conflicts_registered_one_given(self):
        self.parser.register_conflict((self.foo_opt, self.bar_opt))
        self.assertRaises(
                SystemExit,
                self.parser.parse_args,
                ['-f', '1', '--bar', '2', '-v', '42']
        )


    def test_three_conflicting_one_given(self):
        self.parser.register_conflict(
                (self.foo_opt, self.verbose_opt, self.q_opt))
        self.assertRaises(
                SystemExit,
                self.parser.parse_args,
                ['-f', '1', '--bar', '2', '-v', '42']
        )


    def test_conflicts_registered_same_dest(self):
        self.parser.register_conflict((self.verbose_opt, self.q_opt))
        self.assertRaises(
                SystemExit,
                self.parser.parse_args,
                ['--verbose', '-q', '42']
        )


    def test_conflicts_registered_by_flags(self):
        self.parser.register_conflict((u'--verbose', '-f'))
        self.assertRaises(
                SystemExit,
                self.parser.parse_args,
                ['--foo', '1', '--verbose', '42']
        )


    def test_unregister_conflicts(self):
        self.parser.register_conflict((self.verbose_opt, self.foo_opt))
        self.parser.unregister_conflict(('-v', '--foo'))
        opts, args = self.parser.parse_args(
                ['--verbose', '--foo', '1', '42']
        )
        self.assertEqual(args, ['42'])
        self.assertEqual(opts.verbose, True)
        self.assertEqual(opts.foo, '1')


if __name__ == '__main__':
    unittest.main()
