## Script (Python) "get_plonesubscription_ftests"
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

selenium.addUser(id = 'sampleadmin',fullname='Sample Admin',roles=['Member', 'Manager',])
selenium.addUser(id = 'samplemember',fullname='Sample Member',roles=['Member',])

test_logout = suite.TestLogout()
test_admin_login  = suite.TestLoginPortlet('sampleadmin')
test_member_login  = suite.TestLoginPortlet('samplemember')
test_switch_language = suite.TestSwitchToLanguage()

plone21 = selenium.getPloneVersion() > "2.0.5"

if plone21:
    delete_from_folder = "/folder_delete?paths:list=" + suite.getTest().base + '/'
else:
    delete_from_folder = "/folder_delete?ids:list="

suite.addTests("Admin Folder Subscription",
    'Login as Sample Admin',
    test_admin_login,
    test_switch_language,
    'Add subscription',
    suite.open("/"),
    suite.open("/front-page/addSubscription"),
    suite.verifyTextPresent("Subscription(s) added."),
    'Subscription cleanup',
    suite.open('/my_subscriptions'),
    suite.click("selectButton"),
    suite.clickAndWait("form.button.Remove"),
    'My Subscriptions action hidden',
    suite.open('/'),
    suite.verifyTextNotPresent("My subscriptions"),
    'Add subscription',
    suite.open("/"),
    suite.open("/front-page/addSubscription"),
    suite.verifyTextPresent("Subscription(s) added."),
    'My Subscriptions action shown',
    suite.open('/'),
    suite.verifyTextPresent("My subscriptions"),
    'Edit Subscription',
    suite.open("/"),
    suite.clickAndWait("link=My subscriptions"),
    suite.verifyTextPresent("Welcome to Plone"),
    suite.clickAndWait("name=edit_subscription"),
    )

suite.addTests("Member Folder Subscription",
    'Login as Sample Member',
    test_member_login,
    test_switch_language,
    'Add subscription',
    suite.open("/"),
    suite.open("/front-page/addSubscription"),
    suite.verifyTextPresent("Subscription(s) added."),
    'Subscription cleanup',
    suite.open('/my_subscriptions'),
    suite.click("selectButton"),
    suite.clickAndWait("form.button.Remove"),
    'My Subscriptions action hidden',
    suite.open('/'),
    suite.verifyTextNotPresent("My subscriptions"),
    'Add subscription',
    suite.open("/"),
    suite.open("/front-page/addSubscription"),
    suite.verifyTextPresent("Subscription(s) added."),
    'My Subscriptions action shown',
    suite.open('/'),
    suite.verifyTextPresent("My subscriptions"),
    "Member can't edit Subscription by default",
    suite.open("/"),
    suite.clickAndWait("link=My subscriptions"),
    suite.verifyTextPresent("Welcome to Plone"),
    suite.verifyElementNotPresent("name=edit_subscription"),
    )

suite.addTests("Anonymous Folder Subscription",
    "Logout",
    test_logout,
    'Add subscription',
    suite.open("/"),
    suite.open("/events/subscription_form?subscribe=1"),
    suite.type("title", "SampleAnonymous"),
    suite.type("email", "sampleanonymous@sampleanonymous.com"),
    suite.clickAndWait("form.button.Subscribe"),
    suite.verifyTextPresent("Subscription(s) added."),
    'Login as Sample Admin',
    test_admin_login,
    test_switch_language,
    "Subscription Management",
    suite.open("/events/subscription_management"),
    suite.verifyTextPresent("sampleanonymous@sampleanonymous.com"),
    "Logout",
    test_logout,
    'Remove subscription',
    suite.open("/"),
    suite.open("/events/subscription_form?subscribe=0"),
    suite.type("email", "sampleanonymous@sampleanonymous.com"),
    suite.clickAndWait("form.button.Unsubscribe"),
    suite.verifyTextPresent("Subscription(s) removed."),
    'Login as Sample Admin',
    test_admin_login,
    test_switch_language,
    "Subscription Management",
    suite.open("/events/subscription_management"),
    suite.verifyTextNotPresent("sampleanonymous@sampleanonymous.com"),
    )

suite.addTests("Admin Keyword Subscription",
    'Login as Sample Admin',
    test_admin_login,
    test_switch_language,
    'Add subscription',
    suite.open("/"),
    suite.open("/front-page/addSubscription"),
    suite.verifyTextPresent("Subscription(s) added."),
    'Subscription cleanup',
    suite.open('/my_subscriptions'),
    suite.click("selectButton"),
    suite.clickAndWait("form.button.Remove"),
    'Search for a keyword',
    suite.open('/search?SearchableText=Plone'),
    suite.clickAndWait('keyword_subscription'),
    suite.verifyTextPresent("Subscription(s) added."),
    'Subscription verification',
    suite.open('/my_subscriptions'),
    suite.click("selectButton"),
    suite.clickAndWait("form.button.Remove"),
    suite.verifyTextPresent("Subscription(s) removed."),
    )

suite.addTests("Member Keyword Subscription",
    'Login as Sample Member',
    test_member_login,
    test_switch_language,
    'Add subscription',
    suite.open("/"),
    suite.open("/front-page/addSubscription"),
    suite.verifyTextPresent("Subscription(s) added."),
    'Subscription cleanup',
    suite.open('/my_subscriptions'),
    suite.click("selectButton"),
    suite.clickAndWait("form.button.Remove"),
    'Search for a keyword',
    suite.open('/search?SearchableText=Plone'),
    suite.clickAndWait('keyword_subscription'),
    suite.verifyTextPresent("Subscription(s) added."),
    'Subscription verification',
    suite.open('/my_subscriptions'),
    suite.click("selectButton"),
    suite.clickAndWait("form.button.Remove"),
    suite.verifyTextPresent("Subscription(s) removed."),
    )

suite.addTests("Subscription Management",
    'Login as Sample Member',
    test_member_login,
    test_switch_language,
    'Add subscription',
    suite.open("/"),
    suite.open("/front-page/addSubscription"),
    suite.verifyTextPresent("Subscription(s) added."),
    "Member can't manage subscriptions",
    suite.open('/'),
    suite.verifyTextNotPresent("Subscription Management"),
    "Verify direct access to management template not possible",
    suite.open('/subscription_management'),
    suite.verifyTextNotPresent("Subscription Management"),
    'Login as Sample Admin',
    test_admin_login,
    test_switch_language,
    'Add subscription',
    suite.open("/"),
    suite.open("/front-page/addSubscription"),
    suite.verifyTextPresent("Subscription(s) added."),
    "Manager can manage subscriptions",
    suite.open('/'),
    suite.verifyTextPresent("Subscription Management"),
    "Manage Subscriptions",
    suite.open('/'),
    suite.clickAndWait("link=Subscription Management"),
    "Delete all Subscriptions",
    suite.click("selectButton"),
    suite.clickAndWait("folder_delete:method"),
    suite.verifyElementNotPresent("folder_delete:method"),
    )


# Advanced feature: Subscription in View
#
# This advanced feature allows you to subscribe and unsubscribe in the view 
# of a content type instead of doing so by the small action icon. It makes no
# difference if you use the action icon or the link to subscribe.
#
# To make the following test work, you need to put the following
# macro call into a customized version of the event_view.pt template.
#
# The allow_subscribe and allow_unsubscribe variables are used in the macro
# to decide whether the subscribe or unsubscribe action should be shown.
#
# <div metal:use-macro="here/plonesubscription_macros/macros/selfsubscription"
#      tal:define="allow_subscribe python:1;
#                  allow_unsubscribe python:1;">
#     Allow the user to subscribe and unscubscribe.
# </div>

#suite.addTests("Experimental Subscription in View",
#    'Login as Sample Admin',
#    test_admin_login,
#    test_switch_language,
#    'Add subscription',
#    suite.open("/"),
#    suite.open("/front-page/addSubscription"),
#    suite.verifyTextPresent("Subscription(s) added."),
#    'Subscription cleanup',
#    suite.open('/my_subscriptions'),
#    suite.click("selectButton"),
#    suite.click("form.button.Remove"),
#    'Admin deletes event',
#    suite.open("/"),
#    suite.open(delete_from_folder + 'event'),
#    'Admin adds Event',
#    suite.open("/"),
#    suite.clickAndWait( "link=View"),
#    suite.clickAndWait( "link=Event"),
#    suite.type("name=id","event"),
#    suite.type("name=title","Event"),
#    suite.select("eventType","Appointment"),
#    suite.clickAndWait("name=form_submit"),
#    suite.verifyTextPresent("Your changes have been saved."),
#    'Admin subscribes to Event',
#    suite.open("/event"),
#    suite.clickAndWait("link=Subscribe to this event"),
#    'Admin deletes event',
#    suite.open("/"),
#    suite.open(delete_from_folder + 'event'),
#    'Admin adds Events',
#    suite.open("/"),
#    suite.clickAndWait( "link=View"),
#    suite.clickAndWait( "link=Event"),
#    suite.type("name=id","event"),
#    suite.type("name=title","Event"),
#    suite.select("eventType","Appointment"),
#    suite.clickAndWait("name=form_submit"),
#    suite.verifyTextPresent("Your changes have been saved."),
#    'Admin subscribes to Event',
#    suite.open("/event"),
#    suite.clickAndWait("link=Subscribe to this event"),
#    )

# Advanced feature: Subscription Management in View
#
# This advanced feature allows you to manage subscriptions directly in the view
# as a manager. You can see all subscriptions to the content type in the view,
# and decide to delete any of the subscriptions.
#
# To make the following test work, you need to put the following
# macro call into a customized version of the event_view.pt template.
#
# <div metal:use-macro="here/plonesubscription_macros/macros/managesubscriptions">
#     Allow the manager to delete subscriptions.
# </div>
#suite.addTests("Experimental Subscription Management in View",
#    'Login as Sample Admin',
#    test_admin_login,
#    test_switch_language,
#    'Admin adds Event',
#    suite.open(delete_from_folder + 'event'),
#    suite.open("/"),
#    suite.clickAndWait( "link=View"),
#    suite.clickAndWait( "link=Event"),
#    suite.type("name=id","event"),
#    suite.type("name=title","Event"),
#    suite.select("eventType","Appointment"),
#    suite.clickAndWait("name=form_submit"),
#    suite.verifyTextPresent("Your changes have been saved."),
#    'Admin subscribes to Event',
#    suite.open("/event"),
#    suite.clickAndWait("link=Subscribe to this event"),
#    suite.click("selectButton"),
#    suite.clickAndWait("folder_delete:method"),
#    suite.verifyTextPresent("Event has been deleted."),
#    )

# Advanced feature: Send mail to subscribers
#
# This advanced feature allows you to send a mail to the subscribers.
#
# To make the following test work, you need to put the following
# macro call into a customized version of the event_view.pt template.
#
# <div metal:use-macro="here/plonesubscription_macros/macros/mailtosubscribers">
#     Allow the manager to send a mail to the subscribers.
# </div>
#suite.addTests("Experimental Subscription Management in View",
#    'Login as Sample Admin',
#    test_admin_login,
#    test_switch_language,
#    'Admin adds Event',
#    suite.open(delete_from_folder + 'event'),
#    suite.open("/"),
#    suite.clickAndWait( "link=View"),
#    suite.clickAndWait( "link=Event"),
#    suite.type("name=id","event"),
#    suite.type("name=title","Event"),
#    suite.select("eventType","Appointment"),
#    suite.clickAndWait("name=form_submit"),
#    suite.verifyTextPresent("Your changes have been saved."),
#    'Admin subscribes to Event',
#    suite.open("/event"),
#    suite.clickAndWait("link=Subscribe to this event"),
#    suite.click("selectButton"),
#    suite.clickAndWait("folder_delete:method"),
#    suite.verifyTextPresent("Event has been deleted."),
#    )

return suite
