# Copyright (C) 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of django-debian.
#
# django-debian is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# django-debian is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-debian.  If not, see <http://www.gnu.org/licenses/>.

"""
Tests for mocked file system utilities.
"""

from unittest import TestCase

from fs_mock import (
    MockedFileSystem,
    MockedIOError,
    MockedRecordedFile,
    MockedReplayedFile,
)
import os.path


class MockedRecordedFileTests(TestCase):

    _NAME = "name"
    _CONTENT = "content"

    def test_recorded_file_has_name(self):
        stream = MockedRecordedFile(self._NAME)
        self.assertEqual(stream.name, self._NAME)

    def test_final_content_works_after_closing(self):
        stream = MockedRecordedFile(self._NAME)
        stream.write(self._CONTENT)
        stream.close()
        self.assertEqual(stream.final_content, self._CONTENT)

    def test_final_content_works_before_closing(self):
        stream = MockedRecordedFile(self._NAME)
        stream.write(self._CONTENT)
        self.assertEqual(stream.final_content, self._CONTENT)

    def test_close_really_closes_file(self):
        stream = MockedRecordedFile(self._NAME)
        stream.close()
        self.assertTrue(stream.closed)


class MockedReplayedFileTests(TestCase):

    _NAME = "name"
    _CONTENT = "content"

    def setUp(self):
        self.stream = MockedReplayedFile(self._NAME, self._CONTENT)

    def test_write_is_prohibited(self):
        self.assertRaises(IOError, self.stream.write, "text")

    def test_writelines_is_prohibited(self):
        self.assertRaises(IOError, self.stream.writelines, ["text", ])

    def test_truncate_is_prohibited(self):
        self.assertRaises(IOError, self.stream.truncate)


class TestMockedFileSystem(TestCase):

    _NAME = "name"
    _CONTENT = "content"

    def setUp(self):
        self.fs = MockedFileSystem()

    def test_record_tracks_opened_files(self):
        with self.fs.record():
            open(self._NAME, "w").write(self._CONTENT)
        self.assertTrue(self._NAME in self.fs._recorded_files)

    def test_record_prevents_double_open(self):
        with self.fs.record():
            open(self._NAME, "w")
            self.assertRaises(MockedIOError, open, self._NAME, "w")

    def test_record_in_full_isolation_prohibits_accessing_non_mocked_files(
        self):
        with self.fs.record(MockedFileSystem.FULL_ISOLATION):
            self.assertRaises(MockedIOError, open, self._NAME)

    def test_replay_in_full_isolation_prohibits_accessing_non_moked_files(
        self):
        with self.fs.replay(MockedFileSystem.FULL_ISOLATION):
            self.assertRaises(MockedIOError, open, self._NAME)

    def test_record_in_parial_isolation_allows_accessing_existing_files(self):
        # Populate the outer filesystem with mocked file
        outer = MockedFileSystem()
        with outer.record():
            with open(self._NAME, "w") as stream:
                stream.write(self._CONTENT)
        with outer.replay():
            # Using the outer mocked filesystem use another mocked filesystem
            # to access files in partial isolation mode (it should fall-through
            # to the outer filesystem)
            with self.fs.record(MockedFileSystem.PARTIAL_ISOLATION):
                with open(self._NAME) as stream:
                    self.assertEqual(stream.read(), self._CONTENT)

    def test_recorded_files_exist_in_full_isolation_record(self):
        with self.fs.record(MockedFileSystem.FULL_ISOLATION):
            open(self._NAME, "w")
            self.assertTrue(os.path.exists, self._NAME)

    def test_recorded_files_exist_in_full_isolation_replay(self):
        with self.fs.record():
            open(self._NAME, "w")
        with self.fs.replay(MockedFileSystem.FULL_ISOLATION):
            self.assertTrue(os.path.exists, self._NAME)
            
    def test_record_in_partial_isolation_allows_checking_for_existing_files(self):
        outer = MockedFileSystem()
        with outer.record():
            open(self._NAME, "w")
        with outer.replay():
            with self.fs.record(MockedFileSystem.PARTIAL_ISOLATION):
                self.assertTrue(os.path.exists, self._NAME)
            
    def test_replay_in_partial_isolation_allows_checking_for_existing_files(self):
        outer = MockedFileSystem()
        with outer.record():
            open(self._NAME, "w")
        with outer.replay():
            with self.fs.replay(MockedFileSystem.PARTIAL_ISOLATION):
                self.assertTrue(os.path.exists, self._NAME)

    def test_replay_in_partial_isolation_allows_accessing_existing_files(self):
        # Populate the outer filesystem with mocked file
        outer = MockedFileSystem()
        with outer.record():
            with open(self._NAME, "w") as stream:
                stream.write(self._CONTENT)
        with outer.replay():
            # Using the outer mocked filesystem use another mocked filesystem
            # to access files in partial isolation mode (it should fall-through
            # to the outer filesystem)
            with self.fs.replay(MockedFileSystem.PARTIAL_ISOLATION):
                with open(self._NAME) as stream:
                    self.assertEqual(stream.read(), self._CONTENT)
