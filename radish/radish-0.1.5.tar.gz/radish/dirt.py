from lettuce import before, after, world
from lettuce.django import django_url
import os
from pdb import set_trace

from selenium import webdriver # new since selenium2.05b
from radish.settings import *

@before.harvest
def prepare_browser_driver(variables):
    world.browser = webdriver.Firefox()
    world.root_url = django_url()
    world.instances = {}
    
    # Set up a temporary directory for testing
    if not os.path.exists('tmp'): # to store local images and screenshots
        os.mkdir('tmp')
    
@after.harvest
def shutdown_browser_driver(results):
    # NOTE: A bug in selenium2.05b causes an output error at this point:
    # !!! error running onStopped callback: TypeError: callback is not a function
    # Hopefully this bug will disappear with a new version of selenium
    world.browser.quit()
    # ALTERNATIVE:
    # world.browser.stop() or world.browser.close()
    # TODO: empty and remove the "tmp" dir? Maybe not as it contains test
    # result information

@after.each_scenario
def screenshot_on_error(scenario):
    if scenario.failed:
        if DEBUG:
            set_trace()
        world.browser.save_screenshot("tmp/last_failed_scenario.png")

