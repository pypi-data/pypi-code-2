from kforge.test.customer.kui.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestMemberRegister),
        unittest.makeSuite(TestMemberAdmin),
        unittest.makeSuite(TestMemberJoin),
        unittest.makeSuite(TestMemberLeave),
    ]
    return unittest.TestSuite(suites)


class MemberTestCase(KuiTestCase):

    pass


class TestMemberRegister(MemberTestCase):

    def setUp(self):
        super(TestMemberRegister, self).setUp()
        self.registerPerson()
        self.loginPerson()
        self.registerProject()

    def test_list(self):
        self.getAssertContent(self.urlProjectMembers, 'Project Members')
        # Check the creator of the project is a member of the project.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        # Check Levin is not a member of the project.
        self.getAssertNotContent(self.urlProjectMembers, 'levin')
        self.getAssertNotContent(self.urlProjectMembers, 'Levin')


class TestMemberAdmin(MemberTestCase):

    def setUp(self):
        super(TestMemberAdmin, self).setUp()
        self.registerPerson()
        self.loginPerson('admin', 'pass')
        self.registerProject()

    def test_create(self):
        # Check not already on members page.
        self.getAssertNotContent(self.urlProjectMembers, self.kuiPersonName)
        self.getAssertNotContent(self.urlProjectMembers, 'Friend')
        # Check the 'add' button exists.
        self.getAssertContent(self.urlProjectMemberCreate, 'Add member')
        # Check the form submission redirects.
        postdata = {'person': self.kuiPersonName, 'role': 'Friend'}
        self.postAssertCode(self.urlProjectMemberCreate, postdata, code=302)
        # Check now on members page.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        self.getAssertContent(self.urlProjectMembers, 'Friend')

    def test_update(self):
        # Create the member. 
        postdata = {'person': self.kuiPersonName, 'role': 'Friend'}
        self.postAssertCode(self.urlProjectMemberCreate, postdata, code=302)
        # Check not already on members page as a 'Developer'.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        self.getAssertContent(self.urlProjectMembers, 'Friend')
        self.getAssertNotContent(self.urlProjectMembers, 'Developer')
        # Check the 'edit' button exists.
        self.getAssertContent(self.urlProjectMemberUpdate, 'Edit member')
        # Check the form submission redirects.
        postdata = {'person': self.kuiPersonName, 'role': 'Developer'}
        self.postAssertCode(self.urlProjectMemberUpdate, postdata, code=302)
        # Chekc now on members page as a 'Developer'.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        self.getAssertNotContent(self.urlProjectMembers, 'Friend')
        self.getAssertContent(self.urlProjectMembers, 'Developer')

    def test_delete(self):
        # Create the member. 
        postdata = {'person': self.kuiPersonName, 'role': 'Friend'}
        # Check the 'delete' button exists.
        self.postAssertCode(self.urlProjectMemberCreate, postdata, code=302)
        self.getAssertContent(self.urlProjectMemberDelete, 'Delete member')
        # Check on members page.
        self.getAssertContent(self.urlProjectMembers, self.kuiPersonName)
        # Check the form submission redirects.
        postdata = {'Submit': 'Delete membership'}
        self.postAssertCode(self.urlProjectMemberDelete, postdata, code=302)
        # Check not on members page.
        self.getAssertNotContent(self.urlProjectMembers, self.kuiPersonName)


class TestMemberJoin(MemberTestCase):

    def setUp(self):
        super(TestMemberJoin, self).setUp()
        self.registerPerson()
        self.loginPerson()
        self.registerProject()

    def test_join(self):
        self.logoutPerson()

        # Check not already on members page.
        self.getAssertNotContent(self.urlProjectMembers, 'Levin')

        # Switch to existing user.
        self.loginPerson('levin', 'levin')
        self.getAssertContent(self.urlSiteHome, 'Levin')

        # Check button exists.
        self.getAssertContent(self.urlProjectRead, 'Join this project')
        # Request membership of project.
        self.postAssertContent(self.urlProjectJoin, {}, 'Thank you for your interest')
        # Check button no longer exists.
        self.getAssertNotContent(self.urlProjectRead, 'Join this project')

        # Switch back to newly registered user.
        self.logoutPerson()
        self.loginPerson()

        # Check now on members page.
        self.getAssertContent(self.urlProjectMembers, 'Levin')
        # Check not on project page (since members are).
        self.getAssertNotContent(self.urlProjectRead, 'Levin')

        # Reject join request.
        self.urlProjectMembersReject = self.url_for('project.admin', project=self.kuiProjectName,
            subcontroller='members', action='reject', id='levin')
        self.getAssertContent(self.urlProjectMembersReject, "Please confirm rejection of this member.")
        self.postAssertCode(self.urlProjectMembersReject, {'Submit': 'Reject member'})

        # Check no longer on members page.
        self.getAssertNotContent(self.urlProjectMembers, 'Levin')

        # Switch to existing user.
        self.logoutPerson()
        self.loginPerson('levin', 'levin')

        # Check button exists.
        self.getAssertContent(self.urlProjectRead, 'Join this project')

        # Request membership of project.
        self.postAssertContent(self.urlProjectJoin, {}, 'Thank you for your interest')

        # Switch back to newly registered user.
        self.logoutPerson()
        self.loginPerson()

        # Check now on members page.
        self.getAssertContent(self.urlProjectMembers, 'Levin')
        # Check not on project page (since members are).
        self.getAssertNotContent(self.urlProjectRead, 'Levin')

        # Approve join request.
        self.urlProjectMembersApprove = self.url_for('project.admin', project=self.kuiProjectName,
            subcontroller='members', action='approve', id='levin')
        self.getAssertContent(self.urlProjectMembersApprove, "Please select an appropriate role for this member.")
        self.postAssertCode(self.urlProjectMembersApprove, {'approve-submission': 'submit your changes', 'role': 'Developer'})

        # Check now on members page.
        self.getAssertContent(self.urlProjectMembers, 'Levin')
        # Check now on project page (since members are).
        self.getAssertContent(self.urlProjectRead, 'Levin')


class TestMemberLeave(MemberTestCase):

    def test_join(self):
        self.logoutPerson()


