from cubicweb import devtools # set cubes package path
from cubes.tracker.testutils import TrackerBaseTC

class VersionTC(TrackerBaseTC):
    def setup_database(self):
        super(VersionTC, self).setup_database()
        self.v = self.create_version(u'0.0.0').get_entity(0, 0)

    def test_status_change_hook_create_testinstances(self):
        self.create_project('hop')
        ceid, = self.execute('INSERT Card C: C title "test card", C synopsis "test this", '
                             'C content "do thiss then that", C test_case_of P WHERE P name "cubicweb"')[0]
        self.execute('INSERT Card C: C title "test card2", C synopsis "test that", '
                     'C content "do that then this", C test_case_of P WHERE P name "hop"')[0]
        self.commit()
        iworkflowable = self.v.cw_adapt_to('IWorkflowable')
        iworkflowable.fire_transition('start development')
        self.commit()
        rset = self.execute('Any X,C WHERE X for_version V, X instance_of C, V eid %s' % self.v.eid)
        self.assertEquals(len(rset), 1)
        self.assertEquals(rset.description[0], ('TestInstance', 'Card'))
        self.assertEquals(rset.rows[0][1], ceid)
        # check no interference with 'hop' project
        self.assertEquals(len(self.execute('TestInstance X')), 1)
        # test they are not copied twice when version get back to open then dev state
        iworkflowable.fire_transition('stop development')
        self.commit()
        iworkflowable.fire_transition('start development')
        self.commit()
        rset = self.execute('Any X,C WHERE X for_version V, X instance_of C, V eid %s' % self.v.eid)
        self.assertEquals(len(rset), 1)
        # test that if we delete the version, the test instance is deleted
        self.execute('DELETE Version V')
        self.commit()
        rset = self.execute('TestInstance X')
        self.assertEquals(len(rset), 0)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
