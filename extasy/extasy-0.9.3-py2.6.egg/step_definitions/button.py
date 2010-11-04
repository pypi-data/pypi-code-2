import extasy
from extasy import *

def _getxpath( label ):
    return r"(%(scope_xpath)s//input[(@value='%(label)s') and (@type='button' or @type='submit')])|(%(scope_xpath)s//button[.='%(label)s'])" % {
        'scope_xpath' : extasy.scope.get_xpath(),
        'label' : label
    }
    

@Given( 'I click on "$label" button' )
@When( 'I click on "$label" button' )
@Then( 'I click on "$label" button' )
def click( context, label ):
    xpath = 'xpath=%s' % _getxpath( label = label )
    
    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" button should exists and be visible' % ( label )
        raise StepFailure( message )
    
    extasy.selenium.getDriver().click_element(xpath)
