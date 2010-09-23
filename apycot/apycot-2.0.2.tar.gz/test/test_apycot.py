"""cube automatic tests"""

from logilab.common.testlib import unittest_main

from cubicweb.devtools.fill import ValueGenerator
from cubicweb.devtools.testlib import AutomaticWebTest


class MyValueGenerator(ValueGenerator):
    def generate_Any_check_config(self, entity, index):
        return u'pylint_threshold=70\ninstall=python_setup'
    def generate_Any_check_environment(self, entity, index):
        return u'NO_SETUPTOOLS=1'


class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = set(('Repository', 'Revision', 'VersionedFile',
                            'VersionContent', 'DeletedVersionContent',
                            'TestExecution', 'Plan', 'CheckResult', 'CheckResultInfo'))
    ignored_relations = set(('at_revision', 'parent_revision',
                             'from_repository', 'from_revision', 'content_for',
                             'nosy_list', 'execution_of'))

    def setUp(self):
        super(AutomaticWebTest, self).setUp()
        for etype in ('TestExecution', 'CheckResult', 'CheckResultInfo'):
            type_def = self.schema[etype]
            type_def.set_action_permissions('add', ('managers',))
            type_def.set_action_permissions('update', ('managers',))
        for rtype in ('using_config', 'during_execution', 'for_check'):
            for rdef in self.schema[rtype].rdefs.values():
                rdef.set_action_permissions('add', ('managers',))

    def to_test_etypes(self):
        return set(('ProjectEnvironment', 'TestConfig',
                    'TestExecution', 'CheckResult', 'CheckResultInfo'))

    def list_startup_views(self):
        return ()

if __name__ == '__main__':
    unittest_main()
