"template automatic tests"
import os, tarfile, shutil

from logilab.common.testlib import unittest_main
from cubicweb.devtools import BaseApptestConfiguration, testlib
from cubes.vcsfile import bridge

DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def setUpModule():
    hgtest_tgz = tarfile.open(os.path.join(DATADIR, 'hgtest.tgz'))
    hgtest_tgz.extractall(DATADIR)
    hgtest_tgz.close()

def tearDownModule():
    shutil.rmtree(os.path.join(DATADIR, 'hgtest'))

class MyConfig(BaseApptestConfiguration):
    sourcefile = 'sources'

class AutomaticWebTest(testlib.AutomaticWebTest):
    configcls = MyConfig
    # XXX limit no_auto_populate/ignored_relations
    no_auto_populate = ('Repository', 'VersionContent', 'DeletedVersionContent',
                        'Revision', 'VersionedFile')
    #ignored_relations = set(('at_revision',))

    def custom_populate(self, how_many, cursor):
        self.init_repo()

    def init_repo(self):
        req = self.request()
        self.vcsrepo = req.create_entity('Repository', type=u'mercurial',
                                         path=unicode(self.datapath('hgtest')),
                                         encoding=u'utf-8')
        self.commit()
        bridge.import_content(self.session)

    def tearDown(self):
        super(AutomaticWebTest, self).tearDown()
        try:
            os.remove(self.source.dbpath)
        except:
            pass

    def post_populate(self, cursor):
        cursor.execute('SET X filed_under Y WHERE X is VersionedFile, Y is Folder, NOT X filed_under Y')

    def test_startup_views(self):
        # generative test
        for x in super(AutomaticWebTest, self).test_startup_views():
            yield x


if __name__ == '__main__':
    unittest_main()
