"template automatic tests"
import os
from logilab.common.testlib import unittest_main
from cubicweb.devtools import BaseApptestConfiguration, testlib
from utils import HERE, osp

class MyConfig(BaseApptestConfiguration):
    sourcefile = 'sources'

class AutomaticWebTest(testlib.AutomaticWebTest):
    configcls = MyConfig
    no_auto_populate = ('Repository', 'Revision', 'VersionedFile',
                        'VersionContent', 'DeletedVersionContent',)
    ignored_relations = set(('at_revision', 'parent_revision',
                             'from_repository', 'from_revision', 'content_for',))

    def custom_populate(self, how_many, cursor):
        self.request().create_entity('Repository', type=u'mercurial',
                                     path=unicode(osp.abspath(osp.join(HERE, 'testrepohg'))),
                                     encoding=u'latin1')

if __name__ == '__main__':
    unittest_main()
