#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from unittest import TestCase
from pydenji.pathtools import get_successive_path_pieces

class TestPathTools(TestCase):
    def test_absolute_file_pieces_are_returned(self):
        self.assertEquals(["/", "/path/", "/path/myfile"],
            get_successive_path_pieces("/path/myfile") )

    def test_absolute_dir_pieces_are_returned(self):
        self.assertEquals(["/", "/path/", "/path/mydir/"],
            get_successive_path_pieces("/path/mydir/") )

    def test_root_is_returned_as_such(self):
        self.assertEquals(["/"],
            get_successive_path_pieces("/") )

    def test_trailing_slash_retained_just_once(self):
        # if the path has a trailing slash it should be retained,
        # but just once, e.g. we don't want to return both path and path/
        self.assertEquals(["/", "/path/"],
            get_successive_path_pieces("/path/") )

    def test_relative_doesnt_work(self):
        self.assertRaises(IOError,
            get_successive_path_pieces, "relative/path" )

    def test_relative_works_if_forced_absolute(self):
        pieces = get_successive_path_pieces("path/myfile", force_absolute=True)
        # I don't like two assertions per test, but I wouldn't know how to
        # change this now without doing strange things.
        self.assertTrue(pieces[-1].endswith("path/myfile"))
        self.assertTrue(pieces[-2].endswith("path/"))




