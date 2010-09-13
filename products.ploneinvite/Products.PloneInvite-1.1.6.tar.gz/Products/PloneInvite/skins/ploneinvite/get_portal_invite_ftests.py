## Script (Python) "get_plone_invite_ftests"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

selenium = context.portal_selenium
suite = selenium.getSuite()
target_language='en'
suite.setTargetLanguage(target_language)

selenium.addUser(id='sampleadmin', fullname='Sample Admin', roles=['Member',
                                                                   'System Coordinator',])
TestLogout = suite.TestLogout
TestLoginPortlet  = suite.TestLoginPortlet

def testInvite():
    t = suite.getTest()   
    t.open("/")
    t.clickAndWait("link=Login")
    t.type("__ac_name", "rufo")
    t.type("__ac_password", "rufog")        
    t.clickAndWait("//input[@type='submit' and @value='Log in']")
    t.open("/")
    t.verifyTextPresent("rufo")    
    t.clickAndWait("link=Site Setup")
    t.verifyTextPresent("Member Invites")
    t.open("/user_invites")
    t.type("users.num:records", "5")
    t.click("//input[@name='enforce:list' and @value='rufo']")
    t.clickAndWait("//input[@type='submit' and @value='Add Invites']")
    t.clickAndWait("link=Invite Status")
    t.clickAndWait("link=My Home")
    t.verifyTextPresent("Send Invite")
    t.clickAndWait("link=Send Invite")
    t.verifyTextPresent("5")
    t.type("invite_to_address", "test@partecs.com")
    t.type("message", "Please join the network.")
    t.clickAndWait("//input[@type='submit' and @value='Invite']")
    t.verifyTextPresent("Invite sent.")
    t.verifyTextPresent("test@partecs.com")
    t.clickAndWait("link=Groups")
    t.clickAndWait("//a[contains(text(),'Start creating your group')]")
    t.type("title", "Admin")
    t.clickAndWait("//input[@type='submit' and @value='Save']")
    t.clickAndWait("link=My Home")
    t.clickAndWait("link=Send Invite")
    t.verifyTextPresent("Assign potential user as coordinator to the following groups")
    t.type("invite_to_address", "anothertest@partecs.com")
    t.type("message", "please accept role as coordinator in group area admin")
    t.clickAndWait("//input[@type='submit' and @value='Invite']")
    t.verifyTextPresent("Invite sent.")
    t.verifyTextPresent("anothertest@partecs.com")
    t.clickAndWait("link=Logout")
    return t
    

suite.addTests("Test Portal Ivites",
               "System Coordinator Assigns and Sends Invites",
               TestLogout(),               
               testInvite(),
               TestLogout(),
               )
    
return suite

