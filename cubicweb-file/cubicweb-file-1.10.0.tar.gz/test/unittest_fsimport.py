from os.path import dirname, join, abspath
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb.server.sources import storages

from cubes.file.fsimport import import_directory

HERE = dirname(__file__)

STORAGE = storages.BytesFileSystemStorage('whatever')

class importDirectoryTC(CubicWebTC):

    def setup_database(self):
        storages.set_attribute_storage(self.repo, 'File', 'data', STORAGE)

    def tearDown(self):
        storages.unset_attribute_storage(self.repo, 'File', 'data')

    def test_folder_bfss(self):
        import_directory(self.session, join(HERE, 'data', 'toimport'),
                         bfss=True, quiet=True)
        self.assertEqual(self.execute('Any COUNT(F) WHERE F is Folder')[0][0], 1)
        self.assertEqual(self.execute('Any COUNT(F) WHERE F is File')[0][0], 2)
        fpath = self.execute('Any fspath(D) WHERE F is File, F data D, F data_name "coucou.txt"')[0][0]
        self.assertEqual(fpath.getvalue(), join(abspath(HERE), 'data', 'toimport', 'coucou.txt'))
        f = self.execute('Any F WHERE F is File, F data_name "coucou.txt"').get_entity(0, 0)
        self.assertEqual(f.data.getvalue(), 'bijour\n')
        self.assertEqual(len(f.filed_under), 1)
        self.assertEqual(f.filed_under[0].name, join(abspath(HERE), 'data', 'toimport'))
        # test reimport
        import_directory(self.session, join(HERE, 'data', 'toimport'),
                         bfss=True, quiet=True)
        self.assertEqual(self.execute('Any COUNT(F) WHERE F is Folder')[0][0], 1)
        self.assertEqual(self.execute('Any COUNT(F) WHERE F is File')[0][0], 2)
        # test import of an unexistant directory
        self.assertRaises(OSError, import_directory, self.session, join(HERE, 'pouet'), bfss=True, quiet=True)
        self.assertEqual(self.execute('Any COUNT(F) WHERE F is Folder')[0][0], 1)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

