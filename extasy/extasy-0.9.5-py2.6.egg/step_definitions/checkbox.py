import extasy.selenium
from extasy import *

def _getxpath( label, group_label = None):
    if group_label:
        return r"(%(scope_xpath)s//label[contains(concat(' ',@class, ' '),' x-form-item-label ') and .='%(group_label)s']/../descendant::label[contains(concat(' ',@class, ' '),' x-form-cb-label ') and .='%(label)s']/../input[contains(concat(' ',@class, ' '),' x-form-checkbox ')])[last()]" % {
            'scope_xpath' : extasy.scope.get_xpath(),
            'group_label' : group_label,
            'label' : label,
        }
        
    return r"(%(scope_xpath)s//label[contains(concat(' ',@class, ' '),' x-form-cb-label ') and .='%(label)s']/../input[contains(concat(' ',@class, ' '),' x-form-checkbox ')])[last()] | (%(scope_xpath)s//label[contains(concat(' ',@class, ' '),' x-form-item-label ') and .='%(label)s']/../descendant::input[contains(concat(' ',@class, ' '),' x-form-checkbox ')])[last()]" % {
        'scope_xpath' : extasy.scope.get_xpath(),
        'label' : label,
    }


@Given( 'I check "$label" checkbox' )
@When( 'I check "$label" checkbox' )
@Then( 'I check "$label" checkbox' )
def check( context, label ):
    is_not_checked( context, label )
    
    xpath = 'xpath=%s' % _getxpath( label = label )
    extasy.selenium.getDriver().checkbox_check( xpath )


@Given( 'I check "$label" checkbox in "$group_label" group' )
@When( 'I check "$label" checkbox in "$group_label" group' )
@Then( 'I check "$label" checkbox in "$group_label" group' )
def check_in_group( context, label, group_label ):
    is_not_checked_in_group( context, label, group_label )
    
    xpath = 'xpath=%s' % _getxpath( label = label, group_label = group_label )
    extasy.selenium.getDriver().checkbox_check( xpath )
    
    
@Given( 'I uncheck "$label" checkbox' )
@When( 'I uncheck "$label" checkbox' )
@Then( 'I uncheck "$label" checkbox' )
def uncheck( context, label ):
    is_checked( context, label )

    xpath = 'xpath=%s' % _getxpath( label = label )
    extasy.selenium.getDriver().checkbox_check( xpath )


@Given( 'I uncheck "$label" checkbox in "$group_label" group' )
@When( 'I uncheck "$label" checkbox in "$group_label" group' )
@Then( 'I uncheck "$label" checkbox in "$group_label" group' )
def uncheck_in_group( context, label, group_label ):
    is_checked_in_group( context, label, group_label )

    xpath = 'xpath=%s' % _getxpath( label = label, group_label = group_label )
    extasy.selenium.getDriver().checkbox_check( xpath )
    
    

@Given( 'I see that "$label" checkbox is checked' )
@When( 'I see that "$label" checkbox is checked' )
@Then( 'I see that "$label" checkbox is checked' )
def is_checked( context, label ):    
    xpath = 'xpath=%s' % _getxpath( label = label )

    if not extasy.selenium.getDriver().is_element_visible( xpath ) or not extasy.selenium.getDriver().checkbox_is_checked( xpath ):
        message = '"%s" checkbox should exists, be visible and be checked' % ( label )
        raise StepFailure( message )
        

@Given( 'I see that "$label" checkbox in "$group_label" group is checked' )
@When( 'I see that "$label" checkbox in "$group_label" group is checked' )
@Then( 'I see that "$label" checkbox in "$group_label" group is checked' )
def is_checked_in_group( context, label, group_label ):
    xpath = 'xpath=%s' % _getxpath( label = label, group_label = group_label )

    if not extasy.selenium.getDriver().is_element_visible( xpath ) or not extasy.selenium.getDriver().checkbox_is_checked( xpath ):
        message = '"%s" checkbox in "%s" group should exists, be visible and be checked' % ( label, group_label )
        raise StepFailure( message )
        
        

@Given( 'I see that "$label" checkbox is not checked' )
@When( 'I see that "$label" checkbox is not checked' )
@Then( 'I see that "$label" checkbox is not checked' )
def is_not_checked( context, label ):
    xpath = 'xpath=%s' % _getxpath( label = label )

    if not extasy.selenium.getDriver().is_element_visible( xpath ) or extasy.selenium.getDriver().checkbox_is_checked( xpath ):
        message = '"%s" checkbox should exists, be visible and not be checked' % ( label )
        raise StepFailure( message )


@Given( 'I see that "$label" checkbox in "$group_label" group is not checked' )
@When( 'I see that "$label" checkbox in "$group_label" group is not checked' )
@Then( 'I see that "$label" checkbox in "$group_label" group is not checked' )
def is_not_checked_in_group( context, label, group_label ):
    xpath = 'xpath=%s' % _getxpath( label = label, group_label = group_label )

    if not extasy.selenium.getDriver().is_element_visible( xpath ) or extasy.selenium.getDriver().checkbox_is_checked( xpath ):
        message = '"%s" checkbox in "%s" group should exists, be visible not be checked' % ( label, group_label )
        raise StepFailure( message )