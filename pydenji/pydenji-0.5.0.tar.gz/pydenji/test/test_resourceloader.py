#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from unittest import TestCase
import os
from tempfile import NamedTemporaryFile
from tempfile import mkdtemp
from shutil import rmtree

from pydenji.resourceloader import ReadResource
from pydenji.resourceloader import OverwritingWriteResource
from pydenji.resourceloader import AppendingWriteResource
from pydenji.resourceloader import NewFileWriteResource
from pydenji.resourceloader import ResourceAccessError
from pydenji.resourceloader import ExecutableResource
from pydenji.resourceloader import enumerateResources

class TestResourceLoader(TestCase):
    # think: existing == accessible, or not?
    def setUp(self):
        temp = NamedTemporaryFile()
        temp.write("hello")
        temp.flush()
        self.temp = temp

    def tearDown(self):
        self.temp.close()
            
    def test_reading_loaded_resource(self):
        # what would I like for this?
        # - since it's a ReadResource, it should raise an exception if it does not
        # exists or if we're unable to read it because of permission issues.
        # - I should be able to specify additional data for the stream(), e.g. b and +
        # the interface can be limited to stream() & filename

        content = ReadResource("file://" + self.temp.name).open().read()
        self.assertEquals("hello", content)

    def test_error_not_existing_resource(self):
        # what would I like for this?
        # - since it's a ReadResource, it should raise an exception if it does not
        # exists or if we're unable to read it because of permission issues.
        # - I should be able to specify additional data for the stream(), e.g. b and +
        # the interface can be limited to stream() & filename

        self.assertRaises(IOError,
            ReadResource, "file://" + "/dmfsdmfdksm/kmfdskmfksdmfksdmfdksm")

    def test_error_unaccessible_resource(self):
        os.chmod(self.temp.name, 0)
        self.assertRaises(ResourceAccessError,
            ReadResource, "file://" + self.temp.name)


class TestWriteResource(TestCase):
    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        rmtree(self.tempdir)

    def test_if_file_exists_but_is_not_writeable_error_raised(self):
        f = open(self.tempdir + os.sep + "newfile", "w")
        f.close()
        os.chmod(self.tempdir + os.sep + "newfile", 0)
        self.assertRaises(ResourceAccessError, OverwritingWriteResource, "file://" + self.tempdir + os.sep + "newfile")
        
    def test_overwriting_resource_allows_writing_if_file_does_not_exist(self):
        resource = OverwritingWriteResource("file://" + self.tempdir + os.sep + "newfile")

    def test_overwriting_resource_allows_writing_if_file_exists(self):
        f = open(self.tempdir + os.sep + "newfile", "w")
        f.write("abc")
        f.flush()
        resource = OverwritingWriteResource("file://" + self.tempdir + os.sep + "newfile")

    def test_overwriting_allows_writing_to_resource(self):
        resource = OverwritingWriteResource("file://" + self.tempdir + os.sep + "newfile")
        stream = resource.open()
        stream.write("abc")
        stream.close()

        f = open(self.tempdir + os.sep + "newfile")
        self.assertEquals("abc", f.read())

    def test_appending_writing_resource_appends_if_file_exists(self):
        f = open(self.tempdir + os.sep + "newfile", "w")
        f.write("asd")
        f.close()

        resource = AppendingWriteResource("file://" + self.tempdir + os.sep + "newfile")
        stream = resource.open()
        stream.write("fgh")
        stream.close()
        
        f = open(self.tempdir + os.sep + "newfile", "r")
        self.assertEquals("asdfgh", f.read())

    def test_appending_writing_resource_creates_if_file_does_not_exist(self):
        resource = AppendingWriteResource("file://" + self.tempdir + os.sep + "newfile")
        stream = resource.open()
        stream.write("fgh")
        stream.close()

        f = open(self.tempdir + os.sep + "newfile", "r")
        self.assertEquals("fgh", f.read())

    def test_newfile_write_resource_creates_if_file_does_not_exist(self):
        resource = NewFileWriteResource("file://" + self.tempdir + os.sep + "newfile")

    def test_newfile_write_resource_raises_error_if_file_exists(self):
        f = open(self.tempdir + os.sep + "newfile", "w")
        f.write("asd")
        f.close()

        self.assertRaises(ResourceAccessError, NewFileWriteResource, "file://" + self.tempdir + os.sep + "newfile")

class TestExecutableResource(TestCase):
    def setUp(self):
        temp = NamedTemporaryFile()
        temp.write("hello")
        temp.flush()
        
        self.temp = temp

    def tearDown(self):
        self.temp.close()

    def test_executable_resource_can_be_loaded(self):
        os.chmod(self.temp.name, 100)
        res = ExecutableResource(self.temp.name)

    def test_not_executable_resource_raies_error(self):
        os.chmod(self.temp.name, 000)
        self.assertRaises(ResourceAccessError, ExecutableResource, self.temp.name)

class TestResourceEnumerator(TestCase):
    def setUp(self):
        self.tempdir = mkdtemp()
        f = open(self.tempdir + os.sep + "a", "w")
        f = open(self.tempdir + os.sep + "b", "w")
        f = open(self.tempdir + os.sep + "c", "w")

    def tearDown(self):
        rmtree(self.tempdir)


    def test_enumerator_returns_resources_from_a_dir(self):
        rs = enumerateResources(ReadResource(self.tempdir))
        self.assertEquals(3, len(rs))

    def test_enumerator_returns_required_type_of_resources(self):
        rs = enumerateResources(ReadResource(self.tempdir), ReadResource)
        for elem in rs:
            self.assert_(isinstance(elem, ReadResource))

    def test_enumerator_returns_same_filename_resource_if_file_passed(self):
        rs = enumerateResources(ReadResource(self.tempdir + os.sep + "a"))
        self.assertEquals(self.tempdir + os.sep + "a", rs[0].filename)

