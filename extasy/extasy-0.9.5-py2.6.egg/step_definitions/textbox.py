import extasy.selenium
from extasy import *

def _getxpath( label ):
    return r"(%(scope_xpath)s//label[contains(concat(' ',@class, ' '),' x-form-item-label ') and .='%(label)s']/..//input)[last()] | (%(scope_xpath)s//label[contains(concat(' ',@class, ' '),' x-form-item-label ') and .='%(label)s']/..//textarea)[last()]" % {
        'scope_xpath' : extasy.scope.get_xpath(),
        'label' : label
    }
    

@Given( 'I type "$text" in "$label" textbox' )
@When( 'I type "$text" in "$label" textbox' )
@Then( 'I type "$text" in "$label" textbox' )
def type( context, label, text ):
    xpath = 'xpath=%s' % _getxpath( label = label )
    
    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" textbox should exists and be visible' % ( label )
        raise StepFailure( message )
    
    extasy.selenium.getDriver().type_text(xpath, text)
    
    
@Given( 'I see that "$label" textbox is empty' )
@When( 'I see that "$label" textbox is empty' )
@Then( 'I see that "$label" textbox is empty' )
def is_empty( context, label ):
    xpath = 'xpath=%s' % _getxpath( label = label )

    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" textbox should exists and be visible' % ( label )
        raise StepFailure( message )

    if not extasy.selenium.getDriver().is_element_empty( xpath ):
        message = '"%s" textbox should be empty' % ( label )
        raise StepFailure( message )
        
@Given( 'I see that "$label" textbox is not empty' )
@When( 'I see that "$label" textbox is not empty' )
@Then( 'I see that "$label" textbox is not empty' )
def is_not_empty( context, label ):
    xpath = 'xpath=%s' % _getxpath( label = label )

    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" textbox should exists and be visible' % ( label )
        raise StepFailure( message )

    if extasy.selenium.getDriver().is_element_empty( xpath ):
        message = '"%s" textbox should not be empty' % ( label )
        raise StepFailure( message )
    
    
@Given( 'I clean "$label" textbox' )
@When( 'I clean "$label" textbox' )
@Then( 'I clean "$label" textbox' )
def clean( context, label ):
    xpath = 'xpath=%s' % _getxpath( label = label )

    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" textbox should exists and be visible' % ( label )
        raise StepFailure( message )

    extasy.selenium.getDriver().clean_input(xpath, text)