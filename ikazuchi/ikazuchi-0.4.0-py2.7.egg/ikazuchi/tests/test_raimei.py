# -*- coding: utf-8 -*-

from minimock import mock, Mock, restore
from nose.tools import *

# functions for test
from ikazuchi.vim import (raimei, utils)

class TestRaimei(object):

    eval_var = {
        "raimei_api": "google",
        "raimei_from": "en",
        "raimei_to": "ja",
        "&enc": "utf-8",
    }

    def setup(self):
        raimei.vim = None
        mock("raimei.vim")
        raimei.vim.current = Mock("current",
            window=Mock("window",
                cursor=Mock("cursor"),
            ),
            range=Mock("range",
                start=Mock("start"),
                end=Mock("end"),
            ),
        )
        utils.vim = None
        mock("utils.vim")
        _eval_func = lambda var: self.eval_var[var]
        utils.vim.eval = Mock("eval", returns_func=_eval_func)

    def teardown(self):
        restore()

    def test_get_vim_variables(self):
        ret = (
            self.eval_var["raimei_api"],
            self.eval_var["raimei_from"],
            self.eval_var["raimei_to"],
            self.eval_var["&enc"],
        )
        assert_equal(ret, raimei.get_vim_variables())

    def test_remove_imcomplete_line_with_middle(self):
        class Buffer(Mock):
            def __getitem__(self, i):
                return ["previous middle of xxx"][i]
        _enc = self.eval_var["&enc"]
        raimei.vim.current.buffer = Buffer("buffer")
        lines = ["remove sentence.", "first.", "second."]
        assert_equal(lines[1:], raimei.remove_imcomplete_line(lines, 1, _enc))

    def test_remove_imcomplete_line_with_empty(self):
        class Buffer(Mock):
            def __getitem__(self, i):
                return [""][i]
        _enc = self.eval_var["&enc"]
        raimei.vim.current.buffer = Buffer("buffer")
        lines = ["first.", "second.", "third."]
        assert_equal(lines, raimei.remove_imcomplete_line(lines, 1, _enc))

    def test_remove_imcomplete_line_with_complete(self):
        class Buffer(Mock):
            def __getitem__(self, i):
                return ["previous centence."][i]
        _enc = self.eval_var["&enc"]
        raimei.vim.current.buffer = Buffer("buffer")
        lines = ["first.", "second.", "third."]
        assert_equal(lines, raimei.remove_imcomplete_line(lines, 1, _enc))

    def test_get_lines_with_sentence(self):
        class Buffer(Mock):
            def __getitem__(self, i):
                return ["What is the Raimei mean? Year, It is a",
                        "Japanese word. The Raimei means a sounds of",
                        "ikazuchi. Japanese hear the sounds such as",
                        "Goro-goro-goro."][i]
        _enc = self.eval_var["&enc"]
        raimei.vim.current.buffer = Buffer("buffer")
        assert_equal(["The Raimei means a sounds of ikazuchi.",
                      "Japanese hear the sounds such as Goro-goro-goro."],
                     raimei.get_lines_with_sentence(1, 4, _enc))

    def test_get_target_range(self):
        class Buffer(Mock):
            def __getitem__(self, i):
                return ["first line",
                        "second line",
                        "third line",
                        "fourth line",
                        "fifth line",
                        ""][i]
        raimei.vim.current.buffer = Buffer("buffer")
        raimei.vim.current.range.start = 2
        raimei.vim.current.range.end = 2
        raimei.vim.current.window.cursor = (3, 0)
        assert_equal((2, 5), raimei.get_target_range())
        # other line on the cursor, only single line range is specified
        raimei.vim.current.window.cursor = (1, 0)
        assert_equal((2, 3), raimei.get_target_range())
