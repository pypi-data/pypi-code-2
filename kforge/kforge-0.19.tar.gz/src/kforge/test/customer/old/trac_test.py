from twill import commands as web

siteurl = 'http://test.kforgeproject.com/testprefix/'
# siteurl = 'http://local.kforge.net/'

def create_service(service_post_fix=''):
    svn_service_name = 'svn' + service_post_fix
    trac_service_name = 'trac' + service_post_fix
    url = siteurl + 'login/'
    web.go(url)
    web.code(200)
    # login
    username = 'natasha'
    password = username
    web.find('KForge - Log in') # page title
    formname = 2 # use index as name ('') does not seem to work
    web.fv(formname, 'name', username)
    web.fv(formname, 'password', password)
    web.submit()
    web.code(200)
    web.notfind('Sorry, wrong user name or password.')
    web.find('Logged in')
    web.find('You are now logged in as')
    
    formname = 1
    serviceurl = siteurl + 'project/warandpeace/services/create/'
    web.go(serviceurl)
    print web.showforms()
    web.fv(formname, 'name', svn_service_name)
    web.fv(formname, 'plugin', 'svn')
    web.submit()
    web.find('Service: svn')

    web.go(serviceurl)
    web.fv(formname, 'name', trac_service_name)
    web.fv(formname, 'plugin', 'trac')
    web.submit()
    web.find('Configure new service')
    web.fv(formname, 'svn', svn_service_name)
    web.submit()
    print 'Success'


class TestTrac:

    # siteurl = 'http://project.test.kforgeproject.com/warandpeace/trac/'
    # siteurl = 'http://project.knowledgeforge.net/kforge/trac/'
    siteurl = 'http://project.local.kforge.net/warandpeace/trac/'

    def test_index(self):
        web.go(self.siteurl)
        web.code(200)
        # should have this as not logged in
        web.find('visitor')
    
    def test_newticket_forbidden(self):
        url = self.siteurl + 'newticket'
        web.go(url)
        web.code(200)
        formname = 'newticket'
        web.fv(formname, 'summary', 'spam')
        web.submit('Submit ticket')
        web.code(401)

    def test_editticket(self):
        url = self.siteurl + 'ticket/22'
        web.go(url)
        web.code(200)
        web.fv('', 'comment', 'test')
        web.submit('Submit changes')
        print web.show()
        web.code(401)

import os
import tempfile
def test_subversion(url, username, password):
    basedir = tempfile.mkdtemp(prefix='svn-checkout')
    cmd = 'svn co --username %s --password %s %s ./' % ( name, password, url)
    os.chdir(basedir)
    if os.system(cmd):
        self.fail('Failed to checkout')
    fileName = 'xyz.txt'
    ff = file(fileName, 'w')
    ff.write('hello world')
    ff.close()
    cmd2 = 'svn add %s' % fileName
    cmd3 = 'svn ci %s -m "x"' % fileName
    os.system(cmd2)
    if os.system(cmd3):
        self.fail('Failed to checkin')
    # TODO: try checking in with a bad password


if __name__ == '__main__':
    name = 'test6'
    # create_service(name)
    svn_url = siteurl + 'warandpeace/svn' + name
    test_subversion(svn_url, 'natasha', 'natasha')
