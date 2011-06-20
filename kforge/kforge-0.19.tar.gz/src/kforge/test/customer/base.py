from webunit.webunittest import WebTestCase
from kforge.soleInstance import application
from kforge.url import UrlScheme
from kforge.dictionarywords import *
import random

# http://mechanicalcat.net/tech/webunit/README.html

# Check the server is running...
import socket
import urllib2
timeout = 10
socket.setdefaulttimeout(timeout)
siteUrl = ("http://%("+DOMAIN_NAME+")s:%("+HTTP_PORT+")s") % application.dictionary
req = urllib2.Request(siteUrl)
try:
    response = urllib2.urlopen(req)
except Exception, inst:
    raise Exception, "Site not available at %s: %s" % (siteUrl, inst)


class KforgeWebTestCase(WebTestCase):

    registry = application.registry
    dictionary = application.dictionary

    urlScheme = UrlScheme()

    kuiPersonName = None
    kuiProjectName = None
 
    def setUp(self):
        WebTestCase.setUp(self)

        self.server = self.dictionary[DOMAIN_NAME]
        self.port = self.dictionary[HTTP_PORT]

        self.randomInteger = str(random.randint(1, 10**7))
        self.randomInteger2 = str(random.randint(1, 10**7))
        if self.kuiPersonName == None:
            self.kuiPersonName = 'kuitest' + self.randomInteger
        self.kuiPersonPassword = 'kuitest'
        self.kuiPersonEmail    = 'kuitest@appropriatesoftware.net'
        self.kuiPersonFullname = 'kuitestfullname'
        if self.kuiProjectName == None:
            self.kuiProjectName = 'kuitest' + self.randomInteger2
        self.kuiProjectFullname = 'kuitestfullname'
        self.kuiProjectDescription = 'kuitest project description'
        self.kuiProjectLicense = '1'

        self.urlSiteHome = self.url_for('home')
        self.urlLogin = self.url_for('login')
        self.urlLogout = self.url_for('logout')

        self.urlPersons = self.url_for('person', action='index')
        self.urlPersonCreate = self.url_for('person', action='create')
        self.urlPersonRead = self.url_for('person', action='read', id=self.kuiPersonName)
        self.urlPersonUpdate = self.url_for('person', action='edit', id=self.kuiPersonName)
        self.urlPersonDelete = self.url_for('person', action='delete', id=self.kuiPersonName)
        self.urlPersonSearch = self.url_for('person', action='search', id=None)
        self.urlPersonHome = self.url_for('person', action='home')

        self.urlProjects = self.url_for('project', action='index')
        self.urlProjectSearch = self.url_for('project', action='search', id=None)
        self.urlProjectCreate = self.url_for('project', action='create')
        self.urlProjectRead = self.url_for('project', action='read', id=self.kuiProjectName)
        self.urlProjectUpdate = self.url_for('project', action='edit', id=self.kuiProjectName)
        self.urlProjectDelete = self.url_for('project', action='delete', id=self.kuiProjectName)

        self.urlProjectJoin = self.url_for('project', action='join', id=self.kuiProjectName)

        self.urlProjectMembers = self.url_for('project.admin', project=self.kuiProjectName,
            subcontroller='members')
        self.urlProjectMemberCreate = self.url_for('project.admin', project=self.kuiProjectName,
            subcontroller='members', action='create')
        self.urlProjectMemberUpdate = self.url_for('project.admin', project=self.kuiProjectName,
            subcontroller='members', action='edit', id=self.kuiPersonName)
        self.urlProjectMemberDelete = self.url_for('project.admin', project=self.kuiProjectName,
            subcontroller='members', action='delete', id=self.kuiPersonName)

        self.urlProjectServices = self.url_for('project.admin', project=self.kuiProjectName,
            subcontroller='services')
        self.urlProjectServiceCreate = self.url_for('project.admin', project=self.kuiProjectName,
            subcontroller='services', action='create')

    def tearDown(self):
        WebTestCase.tearDown(self)
        if self.randomInteger2 in self.kuiProjectName:
            allProjects = self.registry.projects.getAll()
            if self.kuiProjectName in allProjects:
                project = allProjects[self.kuiProjectName]
                project.delete()
        if self.randomInteger in self.kuiPersonName:
            allPersons = self.registry.persons
            if self.kuiPersonName in allPersons:
                person = allPersons[self.kuiPersonName]
                person.delete()

    def checkPage(self, url, content, code=200):
        #self.getAssertContent(url, content, code=200)
        # Todo: Make these errors meaningful. :-)
        response = self.page(url)
        assert content in response.body, "Content '%s' not in response body: %s" % (content, response.body)
        assert response.code == code, "Response code '%s' is, not '%s'." % (response.code, code)
       
    def setBasicAuthPerson(self):
        self.setBasicAuth(
            self.kuiPersonName,
            self.kuiPersonPassword,
        )

    def registerPerson(self):
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        params['passwordconfirmation'] = self.kuiPersonPassword
        params['fullname'] = self.kuiPersonFullname
        params['email'] = self.kuiPersonEmail
        params['emailconfirmation'] = self.kuiPersonEmail
        url = self.url_for('person', action='create')
        self.postAssertCode(self.urlPersonCreate, params, code=302)
        self.getAssertContent(self.urlPersonRead, self.kuiPersonFullname)

    def changePersonRole(self, personName, roleName):
        role = self.registry.roles[roleName]
        person = self.registry.persons[personName]
        person.role = role
        person.save()

    def changePersonProjectRole(self, roleName):
        role = self.registry.roles[roleName]
        person = self.registry.persons[self.kuiPersonName]
        project = self.registry.projects[self.kuiProjectName]
        membership = person.memberships[project]
        membership.role = role
        membership.save()

    def loginPerson(self, username=None, password=None):
        if username == None:
            username = self.kuiPersonName
        if password == None:
            password = self.kuiPersonPassword
        self.getAssertNotContent(self.urlSiteHome, 'Logged in as')
        self.loginCredentials(username, password) 
        self.getAssertContent(self.urlSiteHome, 'Logged in as')

    def loginCredentials(self, username, password):
        params = {}
        params['name'] = username
        params['password'] = password
        self.postAssertCode(self.urlLogin, params, code=200)
    
    def logoutPerson(self):
        self.getAssertCode(self.urlLogout, code=200)
        self.clearCookies()
        self.clearBasicAuth()
        self.getAssertNotContent(self.urlSiteHome, 'Logged in as')

    def deletePerson(self):
        params = {'Submit':'Delete Person'}
        urlDelete = self.url_for('person', action='delete', id=self.kuiPersonName)
        self.postAssertCode(urlDelete, params)

    def registerProject(self):
        params = {}
        params['name'] = self.kuiProjectName
        params['title'] = self.kuiProjectFullname
        params['licenses'] = self.kuiProjectLicense
        params['description'] = self.kuiProjectDescription
        self.postAssertCode(self.urlProjectCreate, params)
        requiredContent = self.kuiProjectName
        self.getAssertContent(self.urlProjects, requiredContent)
        self.getAssertContent(self.urlProjectRead, requiredContent)

    def deleteProject(self):
        params = {'Submit':'Delete Project'}
        self.postAssertCode(self.urlProjectDelete, params)

    def url_for(self, *args, **kwds):
        path = self.urlScheme.url_for(*args, **kwds)
        path += path[-1] != '/' and '/' or ''
        return path

