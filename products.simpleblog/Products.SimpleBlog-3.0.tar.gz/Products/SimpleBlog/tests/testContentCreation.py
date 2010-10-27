
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.SimpleBlog.tests import SimpleBlogTC
from DateTime import DateTime
from Products.Archetypes.utils import shasattr

# A test class defines a set of tests
class TestContentCreation(SimpleBlogTC.SimpleBlogTestCase):

    # The afterSetUp method can be used to define test class variables
    # and perform initialisation before tests are run. The beforeTearDown()
    # method can also be used to clean up anything set up in afterSetUp(),
    # though it is less commonly used since test always run in a sandbox
    # that is cleared after the test is run.
    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 1
        self.addMember('fred', 'Fred Flintstone', 'fred@bedrock.com', ['Member', 'Manager'], '2002-01-01')
        self.addMember('barney', 'Barney Rubble', 'barney@bedrock.com', ['Member'], '2002-01-01')
        self.addMember('brubble', 'Bambam Rubble', 'bambam@bambam.net', ['Member'], '2003-12-31')
        self.login('fred')
        self.portal.invokeFactory('Folder', 'f1')
        self.f1 = self.portal.f1


    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})


    def testAddBlog(self):
        self.portal.invokeFactory('Blog', 'blog1')
        blog1 = self.f1.blog1
        blog1.setTitle('A Title')
        blog1.setDescription('A Description')
        blog1.setDisplayItems(5)
        blog1.setWarnForUnpublishedEntries(0)
        blog1.setAllowCrossPosting(0)
        blog1.setCategories(('cat1','cat2','cat3'))

        self.failUnlessEqual(blog1.Title(), 'A Title')
        self.failUnlessEqual(blog1.Description(), 'A Description')
        self.failUnlessEqual(blog1.getDisplayItems(), 5)
        self.failUnlessEqual(blog1.getWarnForUnpublishedEntries(), 0)
        self.failUnlessEqual(blog1.getAllowCrossPosting(), 0)
        self.failUnlessEqual(blog1.getCategories(), ('cat1', 'cat2', 'cat3'))

    def testAddEntry(self):
        self.portal.invokeFactory('Blog', 'blog1')
        self.portal.blog1.invokeFactory('BlogEntry', 'entry1')
        self.portal.blog1.setCategories(('cat1','cat2','cat3'))

        entry1 = self.portal.blog1.entry1
        entry1.setTitle('A Title')
        entry1.setDescription('A Description')
        entry1.setBody('<p>Some text</p>')
        entry1.setAlwaysOnTop(1)
        entry1.setCategories(('cat2', 'cat3'))

        self.failUnlessEqual(entry1.Title(), 'A Title')
        self.failUnlessEqual(entry1.Description(), 'A Description')
        self.failUnlessEqual(entry1.getBody(), '<p>Some text</p>')
        self.failUnlessEqual(entry1.getAlwaysOnTop(), 1)
        self.failUnlessEqual(entry1.EntryCategory(), ('cat2', 'cat3'))
        self.failUnlessEqual(entry1.getIcon(), 'entry_pin.gif')

        entry1.setAlwaysOnTop(0)
        self.failUnlessEqual(entry1.getIcon(), 'entry_icon.gif')

    def testAddBlogFolder(self):
        self.portal.invokeFactory('Blog', 'blog1')
        self.portal.blog1.invokeFactory('BlogFolder', 'folder1')
        self.portal.blog1.setCategories(('cat1','cat2','cat3'))

        folder1 = self.portal.blog1.folder1
        folder1.setTitle('A Title')
        folder1.setDescription('A Description')
        folder1.setCategories(('catx', 'caty'))

        self.failUnlessEqual(folder1.Title(), 'A Title')
        self.failUnlessEqual(folder1.Description(), 'A Description')
        self.failUnlessEqual(folder1.getCategories(), ('catx', 'caty'))

    def testCategoryInheritence(self):
        self.portal.invokeFactory('Blog', 'blog1')
        self.portal.blog1.setCategories(('cat1','cat2','cat3'))
        self.portal.blog1.invokeFactory('BlogFolder', 'folder1')
        folder1 = self.portal.blog1.folder1
        folder1.setCategories(('catx', 'caty'))

        # see if it adds the cats in this context
        folder1.invokeFactory('BlogEntry', 'entry1')
        cats = list(folder1.entry1.listCategories())
        cats.sort()

        self.failUnlessEqual(cats, ['cat1', 'cat2', 'cat3', 'catx', 'caty'])

    def testGetEntries(self):
        self.portal.invokeFactory('Blog', 'blog1')

        for i in range(4):
            self.portal.blog1.invokeFactory('BlogEntry', 'entry' + str(i))
            entry = getattr(self.portal.blog1, 'entry' + str(i))
            entry.reindexObject()

        for i in range(3):
            entry = getattr(self.portal.blog1, 'entry' + str(i))
            entry.content_status_modify(workflow_action='publish')
            entry.setEffectiveDate(DateTime() + i)
            entry.reindexObject()

        self.portal.blog1.entry0.setAlwaysOnTop(1)
        self.portal.blog1.entry0.reindexObject()

        topentries, bottomentries = self.portal.blog1.getEntries()

        self.failUnlessEqual(len(topentries), 1)
        self.failUnlessEqual(topentries[0].id, 'entry0')

        self.failUnlessEqual(len(bottomentries), 2)
        bottomentries = [e.id for e in bottomentries]

        self.failUnlessEqual(bottomentries, ['entry2', 'entry1'])

# This boilerplate method sets up the test suite
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # Add our test class here - you can add more test classes if you wish,
    # and they will be run together.
    suite.addTest(makeSuite(TestContentCreation))
    return suite

if __name__ == '__main__':
    framework()
