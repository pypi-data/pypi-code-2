"""Blog unit tests"""

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import CubicWebTC, MAILBOX


class BlogTestsCubicWebTC(CubicWebTC):
    """test blog specific behaviours"""

    def test_notifications(self):
        req = self.request()
        cubicweb_blog = req.create_entity('Blog', title=u'cubicweb',
                                          description=u"cubicweb c'est beau")
        blog_entry_1 = req.create_entity('BlogEntry', title=u"hop", content=u"cubicweb hop")
        blog_entry_1.set_relations(entry_of=cubicweb_blog)
        blog_entry_2 = req.create_entity('BlogEntry', title=u"yes",  content=u"cubicweb yes")
        blog_entry_2.set_relations(entry_of=cubicweb_blog)
        self.assertEqual(len(MAILBOX), 0)
        self.commit()
        self.assertEqual(len(MAILBOX), 0)
        blog_entry_1.cw_adapt_to('IWorkflowable').fire_transition('publish')
        self.commit()
        self.assertEqual(len(MAILBOX), 1)
        mail = MAILBOX[0]
        self.assertEqual(mail.subject, '[data] hop')
        blog_entry_2.cw_adapt_to('IWorkflowable').fire_transition('publish')
        self.commit()
        self.assertEqual(len(MAILBOX), 2)
        mail = MAILBOX[1]
        self.assertEqual(mail.subject, '[data] yes')


if __name__ == '__main__':
    unittest_main()
