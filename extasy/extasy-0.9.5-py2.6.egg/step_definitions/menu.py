import extasy
import extasy.selenium
from extasy import *

def _getxpath( title ):
    return r"(//a[contains(concat(' ',@class, ' '),' x-menu-item ')]/span[.='%(title)s'])[last()]/.." % {
        'title' : title
    }
    
def _get_menu_numeric_field_xpath( operator_text ):
    operatorsDict = {
        '=' : 'ux-rangemenu-eq',
        '>' : 'ux-rangemenu-gt',
        '<' : 'ux-rangemenu-lt'
    }
    
    return r"//li[contains(concat(' ',@class, ' '),' x-menu-list-item ')]/img[contains(concat(' ',@class, ' '),' %(class_name)s ')]/../input" % {
        'class_name' : operatorsDict[ operator_text ]
    }
    
def _wait_for_presence( context, title, timeout = None ):
    xpath = 'xpath=%s' % _getxpath( title = title )

    if not timeout:
        timeout = extasy.DEFAULT_WAIT_FOR_PRESENCE_TIMEOUT
    timeout = int( timeout )

    if not extasy.selenium.getDriver().wait_for_element_present(xpath, timeout):
        message = '"%s" menu item should appear in %s seconds' % ( title, timeout )
        raise StepFailure( message )
    

@Given( 'I click on "$title" menu item' )
@When( 'I click on "$title" menu item' )
@Then( 'I click on "$title" menu item' )
def click( context, title ):
    xpath = 'xpath=%s' % _getxpath( title = title )
    
    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" menu item should exists and be visible' % ( title )
        raise StepFailure( message )
    
    extasy.selenium.getDriver().click_element(xpath)


@Given( 'I mouseover "$title" menu item' )
@When( 'I mouseover "$title" menu item' )
@Then( 'I mouseover "$title" menu item' )
def mouseover( context, title ):
    xpath = 'xpath=%s' % _getxpath( title = title )

    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" menu item should exists and be visible' % ( title )
        raise StepFailure( message )

    extasy.selenium.getDriver().mouseover_element(xpath)

    
@Given( 'I wait for "$title" menu item to be present' )
@When( 'I wait for "$title" menu item to be present' )
@Then( 'I wait for "$title" menu item to be present' )
def wait_for_presence( context, title ):
    return _wait_for_presence( context, title )
        

@Given( 'I wait for "$title" menu item to be present for $timout seconds' )
@When( 'I wait for "$title" menu item to be present for $timout seconds' )
@Then( 'I wait for "$title" menu item to be present for $timout seconds' )
def wait_for_presence_timeout( context, title, timeout = None ):
    return _wait_for_presence( context, title, timeout )

    
@Given( 'I type "$value" in "$title" filter menu' )
@When( 'I type "$value" in "$title" filter menu' )
@Then( 'I type "$value" in "$title" filter menu' )
def filter_type( context, title, value = None ):
    xpath = _get_menu_numeric_field_xpath( title )
    
    if not extasy.selenium.getDriver().is_element_visible( 'xpath=%s' % xpath ):
        message = '"%s" menu item should exists and be visible' % ( title )
        raise StepFailure( message )

    extasy.selenium.getDriver().type_text( 'xpath=%s' % xpath, value )
    extasy.selenium.getDriver().type_keys( 'xpath=%s' % xpath, value )
    

@Given( 'I wait for "$title" filter menu to be present', 'I wait for "$title" filter menu to be present for $timeout seconds' )  
@When( 'I wait for "$title" filter menu to be present', 'I wait for "$title" filter menu to be present for $timeout seconds' )  
@Then( 'I wait for "$title" filter menu to be present', 'I wait for "$title" filter menu to be present for $timeout seconds' )  
def filter_wait_for_presence( context, title, timeout = None ):
    xpath = _get_menu_numeric_field_xpath( title )

    if not timeout:
        timeout = extasy.DEFAULT_WAIT_FOR_PRESENCE_TIMEOUT
    timeout = int( timeout )

    if not extasy.selenium.getDriver().wait_for_element_present( 'xpath=%s' % xpath, timeout):
        message = '"%s" filter menu should appear in %s seconds' % ( title, timeout )
        raise StepFailure( message )