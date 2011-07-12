from lettuce import *
from nose.tools import assert_equals, assert_false, assert_true
from os.path import basename, exists
from pdb import set_trace
import re
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from urllib import urlretrieve
from random_instances import get_or_create_random

from django.contrib.comments import Comment
from django.contrib.contenttypes.models import ContentType
from django.core.mail import outbox
from django.utils.html import strip_tags
from django.db import models

# MODELS

@step(u'there is no (.+?)(?:| with (.+))$')
def no_instances(step, model_name, options):
    model = ContentType.objects.get(model=model_name.lower()).model_class()
    kwargs = eval(options or '{}') # e.g.: extract {"is_current": True}
    model.objects.filter(**kwargs).delete()
    if model_name in world.instances: del(world.instances[model_name])

@step(u'there is an instance of (.+?)(?:| with (.+))$')
def there_is_an_instance(step, model_name, options):
    model = ContentType.objects.get(model=model_name.lower()).model_class()
    kwargs = eval(options or '{}') # e.g.: extract {"is_current": True}
    world.instances[model_name] = get_or_create_random(model,**kwargs)

@step(u'there should be (?:many|(\d+)) instances of (.+)')
def should_have_n_instances(step, count, model_name):
    model = ContentType.objects.get(model=model_name.lower()).model_class()
    model_count = model.objects.count()
    if count:
        assert_equals(model_count, int(count))
    assert_true(model_count >= 1)

# FORMS

@step(u'I fill the "(.*)" field with "(.*)"')
def i_fill_the_field_with_value(step, name, value):
    field = world.browser.find_element_by_name(name)
    field.clear()
    field.send_keys(value)

@step(u'I fill the field labell?ed "(.*)" with "(.*)"')
def i_fill_the_field_with_value(step, label, value):
    pattern = '//input[@id=(//label[text() = "%s"]/@for)]'
    field = world.browser.find_element_by_xpath(pattern % label)
    field.clear()
    field.send_keys(value)

@step(u'I fill with "(.*)" the field with placeholder "(.*)"')
def i_fill_the_field_with_placeholder(step, value, placeholder):
    pattern = '//input[@placeholder="%s"]'
    field = world.browser.find_element_by_xpath(pattern % placeholder)
    field.clear()
    field.send_keys(value)

@step(u'I fill the "(.*)" field with "(.*)" and "(.*)"')
def i_fill_the_field_with_two_values(step, name, value1, value2):
    name1 = '%s_0' % name
    step.given('I fill the "%s" field with "%s"' % (name1, value1))
    name2 = '%s_1' % name
    step.given('I fill the "%s" field with "%s"' % (name2, value2))

@step(u'the "(.+)" field should have value "(.+)"')
def the_field_has_value(step, name, value):
    field = world.browser.find_element_by_name(name)
    field_val = field.get_value()
    assert_true(value==str(field_val))

@step(u'I select that instance of (.+?) from "(.+)"')
def i_select_that_instance(step, model_name, field):
    value = world.instances[model_name].__unicode__()
    step.given('I select "%s" from "%s"' % (value, field))

@step(u'I select "(.+)" from "(.+)"$')
def i_select_the_option_for_field(step, text, select_name):
    select = world.browser.find_element_by_name(select_name)
    # NOTE: This does not work if text contains quotes like "
    option = select.find_element_by_xpath('%s[text() = "%s"]' % ('option', text))
    option.select()

@step(u"I check the field of that (.+)$")
def i_check_that_instance(step, model_name):
    pk = world.instances[model_name].id
    checkbox = world.browser.find_element_by_xpath('//input[@type="checkbox" and @value="%s"]' % pk)
    checkbox.select()

@step(u'I check the "(.+)" field')
def i_check_the_field(step, name):
    field = world.browser.find_element_by_name(name)
    field.select()

@step(u'I click (?:|on )the "(.*)" button')
def i_click_the_button(step, value_or_text):
    try: # NOTE: Is there an XPATH to avoid this try?
        button = world.browser.find_element_by_xpath('//input[@value="%s"]' % value_or_text)
    except NoSuchElementException: # maybe it's a <button> ...
        button = world.browser.find_element_by_xpath('%s[text() = "%s"]' % ('//button', value_or_text))
    button.click()

# NAVIGATION

@step(r'I access the URL "(.*)"')
def access_url(step, url):
    world.browser.get(world.root_url + url)

@step(u"I navigate (?:|to )the page of that (.+)$")
def i_navigate_to_that_instance_page(step, model_name):
    url = world.instances[model_name].get_absolute_url()
    step.given('I access the URL "%s"' % url)

@step(u"I navigate (?:|to )the page of the (.+?) of that (.+)$")
def i_navigate_to_that_parent_instance_page(step, parent_name, model_name):
    url = eval('world.instances["%s"].%s.get_absolute_url()' % (model_name, parent_name))
    step.given('I access the URL "%s"' % url)

@step(u"I click on the (.+?) image of that (.+)$")
def i_click_on_that_instance_s_image(step, attr_name, model_name):
    url = eval('world.instances["%s"].%s' % (model_name, attr_name))
    step.given('I click on the image located at "%s"' % url)

@step(u'the URL should be "(.*)"')
def the_url_should_be(step, url):
    assert_equals(world.browser.get_current_url(), world.root_url + url)

@step(r'I wait for (\d+) seconds')
def i_wait(step, seconds):
    sleep(float(seconds))

@step(u'I (?:navigate|go) to the home(?:| |-)page')
def i_navigate_to_the_admin_page(step):
    step.given('I access the URL "/"')

@step(u'I should see a(?:n|) "(.*)" link')
def then_i_should_see_a_group1_link(step, link_text):
    link = world.browser.find_element_by_link_text(link_text)

@step(u'I should see (\d+) "(.*)" links?')
def then_i_should_see_n_links(step, links_count, link_text):
    links = world.browser.find_elements_by_link_text(link_text)
    assert_equals(int(links_count), len(links))

@step(u'I click (?:|on )the "(.*)" link(| if exists)$')
def i_click_the_link_if_exists(step, link_text, if_exists):
    try:
        link = world.browser.find_element_by_link_text(link_text)
        link.click()
    except NoSuchElementException:
        if if_exists == ' if exists': # don't raise error
            assert True
        else:
            raise

# IMAGES

@step(u'I should see the image located at "(.*)"')
def i_should_see_the_image(step, image_url):
    image = world.browser.find_element_by_xpath('//img[@src="%s"]' % image_url)
    world.that_image = image

@step(u'I should see the (.+?) image of that (.+)$')
def i_should_see_the_image_of_that_model(step, attr_name, model_name):
    url = eval('world.instances["%s"].%s' % (model_name, attr_name))
    step.given('I should see the image located at "%s"' % url)

@step(u"I click on that image$")
def i_click_on_that_image(step):
    world.that_image.click()

@step(u'I click (?:|on )the image located at "(.*)"$')
def i_click_the_image(step, image_url):
    step.given('I should see the image located at "%s"' % image_url)
    step.given('I click on that image')

@step(u'I have the "(.*)" image stored at "(.*)"')
def i_have_the_image(step, url, filename):
    if not exists(filename): # Don't download if the file exists (for speed)
        urlretrieve (url, filename)

@step(u'that image should in the "(.*)" section')
def that_image_should_be_under_header(step, header_text):
    '''
    Check that image is in the section including the provided text in
    the <header>.

    NOTE: This function is being implemented and is not used so far, since
    the XPath code has to be refined to get the exact elements required.
    '''
    section = world.browser.find_element_by_xpath('//header[text() = "%s"]/..' % header_text)
    section.find_element_by_xpath('//img[@src="%s"]' % world.that_image.get_attribute('src'))

# PAGE ELEMENTS

@step(u'I should see the (.+?) of that (.+?) (as|in) the "(.*)"(| element)$')
def i_should_see_that_attribute(step, attr_name, model_name, as_in, tag_name, element):
    value = eval('world.instances["%s"].%s' % (model_name, attr_name))
    step.given('I should see "%s" %s the "%s"%s' % (value, as_in, tag_name, element))

@step(u'I should(| not) see the (?:message|text) "(.*?)"$')
def i_should_see_the_text(step, should_not, text):
    text = re.sub('\\\\"', '"', text) # Fix double quotes
    page_html = world.browser.page_source
    page_text = re.sub('\s+', ' ', strip_tags(page_html)) # Strip HTML and \n
    if should_not:
        assert text not in page_text
    else:
        assert text in page_text
        
@step(u'I should see "(.*)" (in|as) the "(.*?)"(?:| tag)')
def i_should_see_the_text_in_the_tag(step, text, in_as, tag_name):
    page_text = world.browser.find_element_by_tag_name(tag_name).text
    if in_as == 'as':
        assert_equals(page_text, text)
    elif in_as == 'in':
        assert text in page_text

@step(u'I should see "(.*)" (in|as) the "(.*?)" element')
def i_should_see_the_text_in_the_element(step, text, in_as, element_id):
    page_text = world.browser.find_element_by_id(element_id).text
    if in_as == 'as':
        assert_equals(page_text, text)
    elif in_as == 'in':
        assert text in page_text

# E-MAIL

@step(r'an email should be sent to "(.*)"')
def email_sent(step, recipient_email):
    recipients = [rcpt for msg in outbox for rcpt in msg.to]
    assert recipient_email in recipients

# DEBUG

@step(r'I debug')
def i_debug(step):
    set_trace()
    
@step(r'I take a screenshot')
def i_take_a_screenshot(step):
    world.browser.save_screenshot("tmp/screenshot.png")
