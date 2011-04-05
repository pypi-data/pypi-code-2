# -*- coding: utf-8 -*-

"""
Some basic tests for `pywebuml.initialize.initialize_database`.
"""
from datetime import datetime
from os import remove, mkdir, rmdir, path
from tempfile import gettempdir
from unittest import TestCase

from pywebuml import settings
# this has to be done before any other module uses that setting value
settings.DATABASE_URL = "sqlite:///:memory:/test.db"

from pywebuml.initialize import initialize_database
from pywebuml.main import db
from pywebuml.models import Class

class TestInitializeDatabase(TestCase):

    def setUp(self):
        self.tempdir = path.join(gettempdir(), datetime.now().isoformat())
        mkdir(self.tempdir)
        self.files_to_delete = []
        db.create_all()

    def tearDown(self):
        for filename in self.files_to_delete:
            remove(path.join(self.tempdir, filename))
            if '/' in filename:
                folder = filename[:filename.index('/')]
                rmdir(path.join(self.tempdir, folder))
        remove(path.join(gettempdir(), "test.db"))
        rmdir(self.tempdir)

    def test_all(self):
        data = [
            (
                [
                    "public class MyClass1",
                    "{",
                    "}"
                ],
                "tmp1.cs",
            ),
            (
                [
                    "public class InvalidClass {",
                ],
                "tmp2.cs",
            ),
            (

                [
                    "public class MyClass2",
                    "{",
                        "public class InnerClass1",
                        "{",
                        "}",
                    "}"
                ],
                "tmp3.cs",
            ),
            (
                [
                    "public class MyClass3",
                    "{",
                    "}"
                ],
                "folder1/tmp4.cs"
            ),
            (
                [
                    "public class Ingore1",
                    "{",
                    "}",
                ],
                #choose .svn because I am using hg.
                ".svn/ignore1.cs",
            ),
            (
                [
                    "public class Ignore2",
                    "{",
                    "}"
                ],
                "ingore_by_extension.backup"
            )
        ]
        for file_content, filename in data:
            if '/' in filename:
                folder = filename[:filename.index('/')]
                mkdir(path.join(self.tempdir, folder))


            with open(path.join(self.tempdir, filename), 'w') as output:
                output.write('\n'.join(file_content))
            self.files_to_delete.append(filename)

        initialize_database.parse_folder(self.tempdir)
        klasses = db.session.query(Class).order_by(Class.package).all()
        self.assertEquals(len(klasses), 4)
        self.assertEquals(klasses[0].package, 'global.MyClass1')
        self.assertEquals(klasses[1].package, 'global.MyClass2')
        self.assertEquals(klasses[2].package, 'global.MyClass2.InnerClass1')


