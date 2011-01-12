import logging
from DateTime import DateTime
from slc.seminarportal.tests.base import SeminarPortalTestCase
from slc.seminarportal.Extensions.create_seminar_test_data import  \
                                                    create_test_seminars
log = logging.getLogger('test_views.py')


class TestViews(SeminarPortalTestCase):
    
    def afterSetUp(self):
        """ Create a Seminar object, and call the relevant event to enable the
            auto-creation of the sub-objects ('speakers', 'speech venues').
        """
        self.loginAsPortalOwner()

    def test_querying(self):
        """ """
        # FIXME: This will fail unless the layer directive is removed for
        # 'seminars-view' in slc.seminarportl.
        #
        # Still figuring out how to fix this...
        views = self.portal.restrictedTraverse('@@seminars-view')
        create_test_seminars(self.portal, 5, False, past=True)
        seminars = views.seminars(past=True)

        self.assertEquals(len(seminars), 5)

        now = DateTime()
        for seminar in seminars:
            self.assertEquals(seminar.end < now, True)

        create_test_seminars(self.portal, 5, False, past=True)
        seminars = views.seminars(past=True)
        self.assertEquals(len(seminars), 10)

        for seminar in seminars:
            self.assertEquals(seminar.end < now, True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestViews))
    return suite
