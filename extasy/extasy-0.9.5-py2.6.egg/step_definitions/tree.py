#!/usr/bin/python
# -*- coding: utf8 -*-

import extasy
import extasy.selenium
from extasy import *

def _get_node_xpath( title ):
    return r"(%(scope_xpath)s//a[contains(concat(' ',@class, ' '),' x-tree-node-anchor ')]/span[.='%(title)s'])[last()]/.." % {
        'scope_xpath' : extasy.scope.get_xpath(),
        'title' : title
    }

def _get_node_open_button_xpath( title ):
    return r"(%(scope_xpath)s//a[contains(concat(' ',@class, ' '),' x-tree-node-anchor ')]/span[.='%(title)s'])[last()]/ancestor::div[contains(concat(' ',@class, ' '),' x-tree-node-el ')]/descendant::img[contains(concat(' ',@class, ' '),' x-tree-elbow-plus ') or contains(concat(' ',@class, ' '),' x-tree-elbow-end-plus ')]" % {
        'scope_xpath' : extasy.scope.get_xpath(),
        'title' : title
    }
    
def _get_node_close_button_xpath( title ):
    return r"(%(scope_xpath)s//a[contains(concat(' ',@class, ' '),' x-tree-node-anchor ')]/span[.='%(title)s'])[last()]/ancestor::div[contains(concat(' ',@class, ' '),' x-tree-node-el ')]/descendant::img[contains(concat(' ',@class, ' '),' x-tree-elbow-minus ') or contains(concat(' ',@class, ' '),' x-tree-elbow-end-minus ')]" % {
        'scope_xpath' : extasy.scope.get_xpath(),
        'title' : title
    }


    
def _node_wait_for_presence( context, title, timeout = None ):
    xpath = 'xpath=%s' % _get_node_xpath( title = title )

    if not timeout:
        timeout = extasy.DEFAULT_WAIT_FOR_PRESENCE_TIMEOUT
    timeout = int( timeout )

    if not extasy.selenium.getDriver().wait_for_element_present(xpath, timeout):
        message = '"%s" tree node should appear in %s seconds' % ( title, timeout )
        raise StepFailure( message )
    

@Given( 'I click on "$title" tree node' )
@When( 'I click on "$title" tree node' )
@Then( 'I click on "$title" tree node' )
def node_click( context, title ):
    xpath = 'xpath=%s' % _get_node_xpath( title = title )
    
    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" tree node should exists and be visible' % ( title )
        raise StepFailure( message )
    
    extasy.selenium.getDriver().click_element(xpath)


@Given( 'I open "$title" tree node' )
@When( 'I open "$title" tree node' )
@Then( 'I open "$title" tree node' )
def node_open( context, title ):
    xpath = 'xpath=%s' % _get_node_open_button_xpath( title = title )
    
    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" tree node should exists, be a folder and be closed' % ( title )
        raise StepFailure( message )

    extasy.selenium.getDriver().click_element(xpath)


@Given( 'I close "$title" tree node' )
@When( 'I close "$title" tree node' )
@Then( 'I close "$title" tree node' )
def node_close( context, title ):
    xpath = 'xpath=%s' % _get_node_close_button_xpath( title = title )

    if not extasy.selenium.getDriver().is_element_visible( xpath ):
        message = '"%s" tree node should exists, be a folder and be opened' % ( title )
        raise StepFailure( message )

    extasy.selenium.getDriver().click_element(xpath)

    
@Given( 'I wait for "$title" tree node to be present' )
@When( 'I wait for "$title" tree node to be present' )
@Then( 'I wait for "$title" tree node to be present' )
def node_wait_for_presence( context, title ):
    return _node_wait_for_presence( context, title )
        

@Given( 'I wait for "$title" tree node to be present for $timout seconds' )
@When( 'I wait for "$title" tree node to be present for $timout seconds' )
@Then( 'I wait for "$title" tree node to be present for $timout seconds' )
def node_wait_for_presence_timeout( context, title, timeout = None ):
    return _node_wait_for_presence( context, title, timeout )
