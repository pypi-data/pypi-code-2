import extasy.selenium
from extasy import *
import time

@Given( 'I go to page "$url"' )
@When( 'I go to page "$url"' )
@Then( 'I go to page "$url"' )
def go_to( context, url = None ):
    extasy.selenium.getDriver().page_open( url )
    extasy.selenium.getDriver().wait_for_page()
    
    
@Given( 'I see "$title" title' )
@When( 'I see "$title" title' )
@Then( 'I see "$title" title' )
def see_title( context, title = None ):
    actual_title = extasy.selenium.getDriver().get_title()
    assert actual_title == title, 'Page title is "%(actual_title)s" when it should be "%(expected_title)s"' %  {
        'actual_title' : actual_title,
        'expected_title' : title
    }

    
@Given( 'I see that current page contains "$markup"' )
@When( 'I see that current page contains "$markup"' )
@Then( 'I see that current page contains "$markup"' )
def contains_markup( context, markup = None ):
    page_html = extasy.selenium.getDriver().get_html_source()
    assert markup in page_html, 'Page should contain "%(markup)s", but it does\'t' %  {
        'markup' : markup
    }

@Given( 'I see that current page does not contain "$markup"' )
@When( 'I see that current page does not contain "$markup"' )
@Then( 'I see that current page does not contain "$markup"' )
def does_not_contain_markup( context, markup = None ):
    page_html = extasy.selenium.getDriver().get_html_source()
    assert markup not in page_html, 'Page should not contain "%(markup)s", but it does' %  {
        'markup' : markup
    }
    


@Given( 'I wait for the page to load for $timeout seconds' )
@When( 'I wait for the page to load for $timeout seconds' )
@Then( 'I wait for the page to load for $timeout seconds' )
def wait_page_load_for_seconds( context, timeout ):
    timeout = float(timeout)
    
    if timeout:
        extasy.selenium.getDriver().wait_for_page(timeout * 1000)
    else:
        extasy.selenium.getDriver().wait_for_page()


@Given( 'I wait for the page to load' )
@When( 'I wait for the page to load' )
@Then( 'I wait for the page to load' )
def wait_page_load( context ):
    extasy.selenium.getDriver().wait_for_page()
        

@Given( 'I wait for $timeout seconds' )
@When( 'I wait for $timeout seconds' )
@Then( 'I wait for $timeout seconds' )
def wait_seconds( context, timeout = None ):
    try:
        timeout = float(timeout)
    except Exception:
        raise StepFailure( "The specified time cannot be parsed into a float number: %s" % timeout )

    time.sleep(timeout)

