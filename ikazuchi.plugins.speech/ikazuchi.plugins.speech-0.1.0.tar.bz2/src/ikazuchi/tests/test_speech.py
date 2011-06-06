# -*- coding: utf-8 -*-

import os
import tempfile
from os.path import (dirname, join as pathjoin, realpath)
from nose.tools import *

# functions for test
from ikazuchi.plugins.speech import *

class TestHandler(object):
    class Option(object):
        def __init__(self):
            self.api = "google"
            self.command = None
            self.encoding = ["utf-8", "utf-8"]
            self.sentences = ["test", "hello"]
            self.read = None
            self.quiet = False
            self.lang_from = "en"
            self.lang_to = "ja"
            self.post = False
    option = Option()

    def test_post_translated_false(self):
        # when "-p" is False
        h = Handler(self.option)
        assert_equal(h.lang, self.option.lang_from)

    def test_post_translated_true(self):
        # when "-p" is True
        self.option.post = True
        h = Handler(self.option)
        assert_equal(h.lang, self.option.lang_to)
        self.option.post = False  # tear down

    def test_get_target_texts_with_sentences(self):
        # when "-s" is selected
        h = Handler(self.option)
        assert_equal(self.option.sentences, h._get_target_texts())

    def test_get_target_texts_with_file(self):
        # when "-r" is selected
        with tempfile.NamedTemporaryFile(dir=tempfile.tempdir) as f:
            f.write("1st line\n\n3rd line\n")
            f.flush()
            self.option.read = f.name
            h = Handler(self.option)
            assert_equal(["1st line", "3rd line"], h._get_target_texts())
        self.option.read = None  # tear down

class TestPlayer(object):

    def setup(self):
        self.data_dir = realpath(pathjoin(dirname(__file__), "data/speech"))

    def test_play_audio_with_pyglet(self):
        for root, dirs, files in os.walk(self.data_dir):
            for f in files:
                audio = pathjoin(root, f)
                try:
                    play_audio_with_pyglet(audio)
                except Exception as err:
                    # FIXME: how to test play audio?
                    pass

    def test_play_with_ossaudiodev(self):
        for root, dirs, files in os.walk(self.data_dir):
            for f in files:
                audio = pathjoin(root, f)
                try:
                    play_with_ossaudiodev(audio)
                except Exception as err:
                    # FIXME: how to test play audio?
                    pass
