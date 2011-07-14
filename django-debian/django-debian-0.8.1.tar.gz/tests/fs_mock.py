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
File system mocking utilities for unit testing
"""

from StringIO import StringIO
from contextlib import contextmanager
import __builtin__
import os.path


class MockedIOError(IOError):
    """
    IOError subclass that is used by MockedFileSystem
    """

    def __init__(self, filename, mode, isolation_level, message):
        super(MockedIOError, self).__init__(filename, mode, isolation_level,
                                            message)
        self.filename = filename
        self.message = message
        self.mode = mode
        self.isolation_level = isolation_level

    def __str__(self):
        return ("Unable to open file %r in mode %r"
                " on in isolation level %r: %s" % (
                    self.filename, self.mode, self.isolation_level,
                    self.message))

    def __repr__(self):
        return ("MockedIOError(filename=%r, mode=%r,"
                " isolation_level=%r, message=%r)" % (
                    self.filename, self.mode, self.isolation_level,
                    self.message))


class StringIOWrapper(object):
    """
    Base class for using StringIO more like a normal file

    Currently it only provides the context management functions
    """

    def __init__(self, content):
        self._content = content

    def __iter__(self):
        """
        We need to directly forward __iter__ to the content object as object
        also has a definition of this function and thus __getattr__ will not
        work
        """
        return iter(self._content)

    def close(self):
        # XXX: Why doesn't __getattr__ pick this up?
        return self._content.close()

    def __getattr__(self, attr):
        return getattr(self._content, attr)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()


class MockedRecordedFile(StringIOWrapper):
    """
    Read-write file that is used during the recording stage of mocked
    filesystem usage.
    """

    def __init__(self, name):
        super(MockedRecordedFile, self).__init__(StringIO())
        self.name = name
        self._final_content = None

    def close(self):
        # We need to store that because StringIO.close() will discard the
        # internal buffer and StringIO.getvalue() will no longer work
        # afterwards.
        self._final_content = self._content.getvalue()
        return super(MockedRecordedFile, self).close()

    @property
    def final_content(self):
        """
        Get the final content of the mocked file.
        """
        if self.closed:
            return self._final_content
        else:
            return self.getvalue()


class MockedReplayedFile(StringIOWrapper):
    """
    Read only file that is used during the replay stage of mocked filesystem
    usage.
    """

    def __init__(self, name, content):
        super(MockedReplayedFile, self).__init__(StringIO(content))
        self.name = name

    def write(self, data):
        self._readonly_error()

    def writelines(self, lines):
        # XXX: Without this method unit tests break. Since writelines is
        # implemented on top of write and write raises IOError then this method
        # should also do that. For some odd reason it does not
        self._readonly_error()

    def truncate(self, size=None):
        self._readonly_error()

    def _readonly_error(self):
        raise IOError("File not open for writing")


class MockedFileSystem(object):
    """
    Helper class for mocking filesystem access.

    Currently it is limited to mocking access to files (directories are not
    supported). For files only file contents can be mocked, any permissions or
    other attributes are not supported.
    """

    FULL_ISOLATION = "full"
    PARTIAL_ISOLATION = "partial"

    def __init__(self):
        self._recorded_files = {}

    def _open_for_record(self, pathname, mode="r", buffering=0):
        if "w" in mode:
            if pathname not in self._recorded_files:
                recorded = MockedRecordedFile(pathname)
                self._recorded_files[pathname] = recorded
                return recorded
            else:
                raise MockedIOError(
                    pathname, mode, self._isolation_level,
                    "Attempt to open the same file for writing twice")
        else:
            if self._isolation_level == self.FULL_ISOLATION:
                raise MockedIOError(
                    pathname, mode, self._isolation_level,
                    "Reading files while recording in FULL_ISOLATION is"
                    "prohibited")
            elif self._isolation_level == self.PARTIAL_ISOLATION:
                return self._true_open(pathname, mode, buffering)

    def _open_for_replay(self, pathname, mode="r", buffering=0):
        if "w" in mode:
            raise MockedIOError(
                pathname, mode, self._isolation_level,
                "Writing to files in replaying in FULL_ISOLATION is"
                " prohibited")
        try:
            recorded = self._recorded_files[pathname]
            return MockedReplayedFile(recorded.name, recorded.final_content)
        except KeyError:
            if self._isolation_level == self.FULL_ISOLATION:
                raise MockedIOError(pathname, mode, self._isolation_level,
                                     "No previously recorded file found")
            elif self._isolation_level == self.PARTIAL_ISOLATION:
                return self._true_open(pathname, mode, buffering)

    def _os_path_exists(self, pathname):
        if self._isolation_level == self.FULL_ISOLATION:
            return pathname in self._recorded_files
        elif self._isolation_level == self.PARTIAL_ISOLATION:
            return (pathname in self._recorded_files or
                    self._true_os_path_exists(pathname))


    @contextmanager
    def record(self, isolation_level=FULL_ISOLATION):
        """
        Context manager for recording mocked files.

        Implemented by monkey-patching __builtin__.open

        Allows open() to be called for writing to arbitrary pathnames, open
        will return a file-like object (StringIO) that retains all the written
        data. The same data will be available when using replay().
        """
        # this is tricky, we _may_ get a non-true open but another overriden
        # value here but this is by design! It is used in unit tests to check
        # partial isolatin in two level mocking setup.
        self._true_open = open
        self._true_os_path_exists = os.path.exists
        self._isolation_level = isolation_level
        __builtin__.open = self._open_for_record
        __builtin__.file = self._open_for_record
        os.path.exists = self._os_path_exists
        yield
        __builtin__.open = self._true_open
        __builtin__.file = self._true_open
        os.path.exists = self._true_os_path_exists
        del self._true_open
        del self._true_os_path_exists
        del self._isolation_level

    @contextmanager
    def replay(self, isolation_level=FULL_ISOLATION):
        """
        Context manager for accessing previously recorded files.

        Implemented by monkey-patching __builtin__.open

        The optional isolation_level argument defines what happens when an
        attempt is made to access file that was _not_ recorded before. In
        FULL_ISOLATION an IOError with an appropriate error is raised. In
        PARTIAL_ISOLATION the call falls back to true open() with the same
        arguments.
        """
        # See the note in record() above
        self._true_open = open
        self._true_os_path_exists = os.path.exists
        self._isolation_level = isolation_level
        __builtin__.open = self._open_for_replay
        __builtin__.file = self._open_for_replay
        os.path.exists = self._os_path_exists
        yield
        __builtin__.open = self._true_open
        __builtin__.file = self._true_open
        os.path.exists = self._true_os_path_exists
        del self._true_open
        del self._true_os_path_exists
        del self._isolation_level
