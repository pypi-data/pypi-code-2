import extasy
import extasy.selenium
import re
from extasy import *


def _getxpath( title = None ):
    if title:
        return r"(%(scope_xpath)s//div[contains(concat(' ',@class, ' '),' x-grid-panel ')]/descendant::span[contains(concat(' ',@class, ' '),' x-panel-header-text ') and .='%(title)s'])[last()]" % {
            'scope_xpath' : extasy.scope.get_xpath(),
            'title' : title
        }
        
    return r"(%(scope_xpath)s//div[contains(concat(' ',@class, ' '),' x-grid-panel ')])[last()]" % {
        'scope_xpath' : extasy.scope.get_xpath()
    }


def _get_line_xpath( title = None, line = None ):
    if title:
        return r"((%(scope_xpath)s//span[contains(concat(' ',@class, ' '),' x-panel-header-text ') and .='%(title)s']/ancestor::div[contains(concat(' ',@class, ' '),' x-grid-panel ')])[last()])/descendant::div[contains(concat(' ',@class, ' '),' x-grid3-row ')][%(line)s]//div[@class=contains( concat( ' ', @class, ' '), ' x-grid3-cell-inner ') ][1]" % {
            'scope_xpath' : extasy.scope.get_xpath(),
            'title' : title,
            'line' : line
        }

    return r"((%(scope_xpath)s//div[contains(concat(' ',@class, ' '),' x-grid-panel ')])[last()])/descendant::div[contains(concat(' ',@class, ' '),' x-grid3-row ')][%(line)s]//div[@class=contains( concat( ' ', @class, ' '), ' x-grid3-cell-inner ') ][1]" % {
        'scope_xpath' : extasy.scope.get_xpath(),
        'line' : line
    }
    
def _get_lines_xpath( title = None ):
    if title:
        return r"((%(scope_xpath)s//span[contains(concat(' ',@class, ' '),' x-panel-header-text ') and .='%(title)s']/ancestor::div[contains(concat(' ',@class, ' '),' x-grid-panel ')])[last()])/descendant::div[contains(concat(' ',@class, ' '),' x-grid3-row ')]" % {
            'scope_xpath' : extasy.scope.get_xpath(),
            'title' : title
        }

    return r"((%(scope_xpath)s//div[contains(concat(' ',@class, ' '),' x-grid-panel ')])[last()])/descendant::div[contains(concat(' ',@class, ' '),' x-grid3-row ')]" % {
        'scope_xpath' : extasy.scope.get_xpath()
    }



def _get_line_accessor( line ):
    line = line.strip()
    
    if extasy.lang.get( 'first' ) == line:
        return 1
    
    if extasy.lang.get( 'last' ) == line:
        return 'last()'
        
    return re.sub( '\D+', '', line )
  
  
def _lines_wait_for_presence( context, title = None, timeout = None ):
    xpath = 'xpath=%s' % _get_lines_xpath( title = title )

    if not timeout:
        timeout = extasy.DEFAULT_WAIT_FOR_PRESENCE_TIMEOUT
    timeout = int( timeout )

    if not extasy.selenium.getDriver().wait_for_element_present(xpath, timeout):
        if title:
            message = 'lines of "%s" grid should appear in %s seconds' % ( title, timeout )
        else:
            message = 'lines of grid should appear in %s seconds' % ( timeout )
        raise StepFailure( message )  
 
    
def _wait_for_presence( context, title = None, timeout = None ):
    xpath = 'xpath=%s' % _getxpath( title = title )

    if not timeout:
        timeout = extasy.DEFAULT_WAIT_FOR_PRESENCE_TIMEOUT
    timeout = int( timeout )

    if not extasy.selenium.getDriver().wait_for_element_present(xpath, timeout):
        if title:
            message = '"%s" grid should appear in %s seconds' % ( title, timeout )
        else:
            message = 'grid should appear in %s seconds' % ( timeout )
        raise StepFailure( message )

    
def _line_click( context, title = None, line = None, dblclick = False ):
    line = _get_line_accessor( line )
    xpath = 'xpath=%s' % _get_line_xpath( title = title, line = line )

    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        if title :
            message = '"%s" grid should exists and have lines' % ( title )
        else:
            message = 'grid should exists and have lines'
        raise StepFailure( message )

    if dblclick:
        extasy.selenium.getDriver().double_click_element_at(xpath, 1, 1)
    else:
        extasy.selenium.getDriver().click_element_at(xpath, 1, 1)
    

@Given( 'I wait for "$title" grid to be present' )
@When( 'I wait for "$title" grid to be present' )
@Then( 'I wait for "$title" grid to be present' )
def wait_for_presence( context, title ):
    return _wait_for_presence( context, title )
        
@Given( 'I wait for grid to be present' )
@When( 'I wait for grid to be present' )
@Then( 'I wait for grid to be present' )
def wait_for_presence_no_title( context ):
    return _wait_for_presence( context )


@Given( 'I wait for "$title" grid to be present for $timout seconds' )
@When( 'I wait for "$title" grid to be present for $timout seconds' )
@Then( 'I wait for "$title" grid to be present for $timout seconds' )
def wait_for_presence_timeout( context, title, timeout = None ):
    return _wait_for_presence( context, title, timeout )

@Given( 'I wait for grid to be present for $timout seconds' )
@When( 'I wait for grid to be present for $timout seconds' )
@Then( 'I wait for grid to be present for $timout seconds' )
def wait_for_presence_timeout_no_title( context, timeout = None ):
    return _wait_for_presence( context, None, timeout )
    

@Given( 'I wait for "$title" grid lines to be present' )
@When( 'I wait for "$title" grid lines to be present' )
@Then( 'I wait for "$title" grid lines to be present' )
def lines_wait_for_presence( context, title ):
    return _lines_wait_for_presence( context, title )

@Given( 'I wait for grid lines to be present' )
@When( 'I wait for grid lines to be present' )
@Then( 'I wait for grid lines to be present' )
def lines_wait_for_presence_no_title( context ):
    return _lines_wait_for_presence( context )


@Given( 'I wait for "$title" grid lines to be present for $timout seconds' )
@When( 'I wait for "$title" grid lines to be present for $timout seconds' )
@Then( 'I wait for "$title" grid lines to be present for $timout seconds' )
def lines_wait_for_presence_timeout( context, title, timeout = None ):
    return _lines_wait_for_presence( context, title, timeout )

@Given( 'I wait for grid lines to be present for $timout seconds' )
@When( 'I wait for grid lines to be present for $timout seconds' )
@Then( 'I wait for grid lines to be present for $timout seconds' )
def lines_wait_for_presence_timeout_no_title( context, timeout = None ):
    return _lines_wait_for_presence( context, None, timeout )
    
    
@Given( 'I click on $line line of grid' )
@When( 'I click on $line line of grid' )
@Then( 'I click on $line line of grid' )
def line_click_no_title( context, line ):
    return _line_click( context, line=line )
    
@Given( 'I click on $line line of "$title" grid' )
@When( 'I click on $line line of "$title" grid' )
@Then( 'I click on $line line of "$title" grid' )
def line_click( context, line, title ):
    return _line_click( context, title=title, line=line )
    
    
@Given( 'I doubleclick $line line of grid' )
@When( 'I doubleclick $line line of grid' )
@Then( 'I doubleclick $line line of grid' )
def line_doubleclick_no_title( context, line ):
    return _line_click( context, line=line, dblclick = True )


@Given( 'I doubleclick $line line of "$title" grid' )
@When( 'I doubleclick $line line of "$title" grid' )
@Then( 'I doubleclick $line line of "$title" grid' )
def line_doubleclick( context, line, title ):
    return _line_click( context, title=title, line=line, dblclick = True )