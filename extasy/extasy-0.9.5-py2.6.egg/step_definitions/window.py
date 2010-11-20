import extasy
import extasy.selenium
from extasy import *

def _getxpath( title = None ):
    if title:
        return r"(//div[contains(concat(' ',@class, ' '),' x-window ')]/descendant::span[contains(concat(' ',@class, ' '),' x-window-header-text ') and .='%(title)s'])[last()]" % {
            'title' : title
        }

    return r"(//div[contains(concat(' ',@class, ' '),' x-window ')])[last()]"

def _get_close_button_xpath( title = None ):
    if title:
        return r"(//span[contains(concat(' ',@class, ' '),' x-window-header-text ') and .='%(title)s']/ancestor::div[contains(concat(' ',@class, ' '),' x-window ')])[last()]/descendant::div[contains(concat(' ',@class, ' '),' x-tool-close ')]" % {
            'title' : title
        }

    return r"(//div[contains(concat(' ',@class, ' '),' x-window ')])[last()]/descendant::div[contains(concat(' ',@class, ' '),' x-tool-close ')]"


    
def _wait_for_presence( context, title = None, timeout = None ):
    xpath = 'xpath=%s' % _getxpath( title = title )

    if not timeout:
        timeout = extasy.DEFAULT_WAIT_FOR_PRESENCE_TIMEOUT
    timeout = int( timeout )

    if not extasy.selenium.getDriver().wait_for_element_present(xpath, timeout):
        message = '"%s" window should appear in %s seconds' % ( title, timeout )
        raise StepFailure( message )

    
def _close( context, title = None ):
    xpath = 'xpath=%s' % _get_close_button_xpath( title = title )

    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        if title :
            message = '"%s" window should exists and be closable' % ( title )
        else:
            message = 'window should exists and be closable'
        raise StepFailure( message )

    extasy.selenium.getDriver().click_element(xpath)
    

@Given( 'I close the window' )
@When( 'I close the window' )
@Then( 'I close the window' )
def close_no_title( context ):
    _close( context )

@Given( 'I close "$title" window' )
@When( 'I close "$title" window' )
@Then( 'I close "$title" window' )
def close( context, title ):
    _close( context, title )

    
@Given( 'I wait for "$title" window to be present' )
@When( 'I wait for "$title" window to be present' )
@Then( 'I wait for "$title" window to be present' )
def wait_for_presence( context, title ):
    return _wait_for_presence( context, title )
        
@Given( 'I wait for window to be present' )
@When( 'I wait for window to be present' )
@Then( 'I wait for window to be present' )
def wait_for_presence_no_title( context ):
    return _wait_for_presence( context )
        

@Given( 'I wait for "$title" window to be present for $timout seconds' )
@When( 'I wait for "$title" window to be present for $timout seconds' )
@Then( 'I wait for "$title" window to be present for $timout seconds' )
def wait_for_presence_timeout( context, title, timeout = None ):
    return _wait_for_presence( context, title, timeout )

@Given( 'I wait for window to be present for $timout seconds' )
@When( 'I wait for window to be present for $timout seconds' )
@Then( 'I wait for window to be present for $timout seconds' )
def wait_for_presence_timeout_no_title( context, timeout = None ):
    return _wait_for_presence( context, None, timeout )