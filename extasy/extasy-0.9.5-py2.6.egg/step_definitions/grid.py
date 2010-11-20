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
    
    if extasy.lang.get( 'first' ).decode( 'utf8' ) == line:
        return 1
    
    if extasy.lang.get( 'last' ).decode( 'utf8' ) == line:
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
@Given( 'I click on $line line of grid', 'I click on $line line of "$title" grid' )
@When( 'I click on $line line of grid', 'I click on $line line of "$title" grid' )
@Then( 'I click on $line line of grid', 'I click on $line line of "$title" grid' )
def line_click( context, title = None, line = None ):
    return _line_click( context, title = title, line = line, dblclick = False )

    
@Given( 'I doubleclick $line line of grid', 'I doubleclick $line line of "$title" grid' )
@When( 'I doubleclick $line line of grid', 'I doubleclick $line line of "$title" grid' )
@Then( 'I doubleclick $line line of grid', 'I doubleclick $line line of "$title" grid' )
def line_doubleclick( context, title = None, line = None ):
    return _line_click( context, line=line, dblclick = True )
    

@Given( 'In $line line of grid:', 'In $line line of "$title" grid:' )
@When( 'In $line line of grid:', 'In $line line of "$title" grid:' )
@Then( 'In $line line of grid:', 'In $line line of "$title" grid:' )
def line_enter_scope( context, line = None, title = None ):
    line_accessor = _get_line_accessor( line )
    xpath = _getxpath( title = title )

    if not extasy.selenium.getDriver().is_element_visible( 'xpath=%s' % xpath ):
        if title:
            message = '"%s" grid should exists, be visible and have enough lines' % ( title )
        else:
            message = 'grid should exists, be visible and have enough lines'
        raise StepFailure( message )
        
    scope_info = ( xpath, line_accessor )
    
    extasy.scope.enter( extasy.scope.get_xpath(), context.indentation_level, scope_info = scope_info )


@Given( 'I open "$column" config menu of grid', 'I open "$column" config menu of "$title" grid' )
@When( 'I open "$column" config menu of grid', 'I open "$column" config menu of "$title" grid' )
@Then( 'I open "$column" config menu of grid', 'I open "$column" config menu of "$title" grid' )
def open_column_config_menu( context, title = None, column = None ):
    grid_xpath = _getxpath( title )
    col_xpath = r"(%(grid_xpath)s)//div[ contains( concat( ' ', @class, ' ' ), ' x-grid3-hd-inner ' ) and .='%(column)s']" % {
        'grid_xpath' : grid_xpath,
        'column' : column
    }
    col_config_xpath = r"%(col_xpath)s//a[ contains( concat( ' ', @class, ' ' ), ' x-grid3-hd-btn ' ) ]" % {
        'col_xpath' : col_xpath
    }
    
    extasy.selenium.getDriver().mouseover_element( 'xpath=%s' % col_xpath )
    extasy.selenium.getDriver().click_element( 'xpath=%s' % col_config_xpath )
    
    
@Given( 'I see "$column" column has a text of "$value"' )
@When( 'I see "$column" column has a text of "$value"' )
@Then( 'I see "$column" column has a text of "$value"', '"$column" column should have a text of "$value"' )    
def line_column_has_value( context, column = None, value = None ):
    scope_info = extasy.scope.get_scope_info()
    
    if not isinstance(scope_info, tuple):
        raise StepFailure( 'Context for grid columns should be a grid line' ) 
    
    grid_xpath, line_accessor = scope_info

    gridId = extasy.selenium.getDriver().get_element_id( 'xpath=%s' % grid_xpath )

    script = """(function( gridId, columnHeader, lineAccessor ){
        var grid = selenium.browserbot.getCurrentWindow().Ext.getCmp( gridId );
        
        lineAccessor = parseInt( lineAccessor == 'last()' ? grid.view.getRows().length : lineAccessor ) - 1; 
        
        var column = grid.getColumnModel().getColumnsBy( function( c ){ return c.header == columnHeader } )[0]
        var colIndex = grid.getColumnModel().getIndexById( column.id );
        
        return grid.view.getCell( lineAccessor, colIndex ).firstChild.innerHTML;
    })( '%s', '%s', '%s' )""" % ( gridId, column, line_accessor )
    foundValue = extasy.selenium.getDriver().exec_js( script )

    if foundValue != value:
        raise StepFailure( '"%s" column should have a value of "%s" ("%s" found)' % ( column, value, foundValue ) )
