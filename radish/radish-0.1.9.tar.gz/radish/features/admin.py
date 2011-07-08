from lettuce import *
from radish.features import base
from radish.settings import *

from django.core.urlresolvers import reverse

# NAVIGATION

@step(u'I navigate to the admin page')
def i_navigate_to_the_admin_page(step):
    step.given('I access the URL "%s"' % (reverse('admin:index')))

@step(u'I am not logged in(?:| as an admin)$')
def i_am_not_logged_in_as_an_admin(step):
    step.given('I navigate to the admin page')
    step.given('I click on the "Log out" link if exists')

@step(u'I am logged in(?:| as an admin)$')
def i_am_logged_in_as_an_admin(step):
    step.given('I navigate to the admin page')
    try:
        step.given('I should see the administration panel')
    except:
        step.given('I fill the "username" field with "%s"' % ADMIN_LOGIN)
        step.given('I fill the "password" field with "%s"' % ADMIN_PASSWORD)
        step.given('I click the "Log in" button')

# PAGE ELEMENTS

@step(u'I should see the administration panel')
def i_am_on_the_administration_panel(step):
    step.given('I should see the message "Site administration"')
