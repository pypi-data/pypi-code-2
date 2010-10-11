# -*- coding: latin-1 -*-

""" seleniumWrapper - run Selenium commands

Selenium provides a comprehensive api to run commands that will interact
against a web interface. This module will act as a wrapper of the official 
Selenium Python client   
 
@author Adrián Deccico
"""
import logging
import sys
import re
import time

import arges.thirdparty.selenium.selenium
import arges.util.strings
import arges.util.introspection

class SeleniumWrapper:
    
    def __init__(self):
        self.selenium = 0  #init in null in order to detect its type
        self.runners = {} #dictionary of available runners key=name, value=object_runner
        self.runners["self"] = self
        self.INI_SECTION = "selenium"
        self.ini = arges.util.ini.Ini(arges.APP.lower()).getInstance()
        self.started = False
        #constants
        self.START_COMMAND = "start"
        self.STOP_COMMAND = "stop"
        #accepted suffixes
        self.PRE_VERIFIED = "PV"
        self.AND_WAIT = "AndWait"
        self.REFRESH = "Refresh"
        self.command_suffixes = []
        #additional params
        self.params = {}
        #pre verified time out - default 60 seconds
        self.PV_TIME_OUT = arges.util.strings.formatTestParameter("${pv_time_out}") 
        #and wait time - default 30 seconds
        self.AND_WAIT_TIME  = arges.util.strings.formatTestParameter("${and_wait_time_out}") 

    def hasProxiedCommand(self, command):
        #check if the command is within Selenium api or the helper class
        logging.debug("check if: " + str(command) + " is registered in the SeleniumWrapper")
        
        #erase previous suffixes (in order)
        self.command_suffixes = []
        if command.endswith(self.REFRESH):
            logging.debug("registering refresh suffix")
            command = util.strings.cutSuffix(command, self.REFRESH)
            self.command_suffixes.append(self.REFRESH)

        if command.endswith(self.PRE_VERIFIED):
            logging.debug("registering PV (pre verified) suffix")
            command = util.strings.cutSuffix(command, self.PRE_VERIFIED)
            self.command_suffixes.append(self.PRE_VERIFIED)
            
        if command.endswith(self.AND_WAIT):
            logging.debug("registering and wait suffix")
            command = util.strings.cutSuffix(command, self.AND_WAIT)
            self.command_suffixes.append(self.AND_WAIT)
        
        try:
            for x in self.runners.values():
                f = getattr(x, command, 0)
                if  f != 0 and callable(f):
                    logging.info(str(command) + \
                                  " is registered in the SeleniumWrapper")
                    return True
        except:
            #try to find the function in the registered objects, 
            #but no matter if we have no luck
            pass  
        
        logging.debug(str(command) + " is not registered in the SeleniumWrapper")
        self.command_suffixes = []
        return False
    
    def preProcessCommand(self, cmd, target, value):
        """do any required preporcess of the command"""
        #process suffixes (in order)
        if cmd.endswith(self.REFRESH):
            cmd = util.strings.cutSuffix(cmd, self.REFRESH)
        if cmd.endswith(self.PRE_VERIFIED):
            cmd = util.strings.cutSuffix(cmd, self.PRE_VERIFIED)
        if cmd.endswith(self.AND_WAIT):
            cmd = util.strings.cutSuffix(cmd, self.AND_WAIT)
        #set self.started    
        if cmd==self.START_COMMAND:
            self.started = True
        elif cmd==self.STOP_COMMAND:
            self.started = False
        return cmd

    def runProxiedCommand(self, cmd, target, value, additional_parameters):
        #run a command against the SeleniumWrapper.
        #precondition: the hasProxiedCommand command has to be true for this command
        
        self.params = additional_parameters
        cmd = self.preProcessCommand(cmd, target, value)
        
        if not cmd in [self.initBrowser.func_name, self.stopBrowser.func_name] \
        and not util.introspection.isInstance(self.selenium):
            msg = """a command is about to be run but the selenium object 
            has not be initialized. Please run the 'initBrowser' command """
            raise NameError, msg 
        
        #check if the command is within Selenium api or the helper class
        logging.debug("running: " + str(cmd) + " " + str(target) + " " + str(value))
        try:
            #runners_list = self.runners + self.selenium  
            for x in self.runners.values():
                f = getattr(x, cmd, 0)
                if  f != 0 and callable(f):
                    #results of the commands
                    ret = False
                    retPre = True
                    retPost = True
                    #process pre verified command
                    if self.REFRESH in self.command_suffixes:
                        retPre = self.waitForElementPresent(target, value, True)
                    if self.PRE_VERIFIED in self.command_suffixes:
                        retPre = self.waitForElementPresent(target, value)
                    #run the command with the correct number of parameters
                    #this is due to the lack of overloading in Python
                    logging.debug("executing command: " + str(cmd))
                    if target == None and value == None:
                        ret = f()
                    else:
                        if target != None and value == None:
                            ret = f(target)
                        else:
                            ret = f(target, value)
                    #process post commands
                    if self.AND_WAIT in self.command_suffixes:
                        retPost = self.AndWait(value)
                    
                    if ret == None: 
                        #most (or all) the Selenium objects return None
                        #when everything concludes OK
                        ret = True and retPre and retPost
                    elif ret == False:
                        ret = False
                    else:
                        #if the function returns something, then a list with a True and the result is returned
                        ret = [True and retPre and retPost, ret]

                    return ret
        except:
            #try to find the function in the registered objects, 
            #but no matter if we have no luck
            logging.warning("problems running " + str(cmd) + " in the SeleniumWrapper module. ")
            logging.exception("exception info:")
            return False
    
    #-----------------------------------------------------------------------------    
    #commands added to the selenium api------------------------------------
    #-----------------------------------------------------------------------------    
   
    def initBrowser(self, target):
        """initialize the selenium object"""
        target = arges.util.strings.processArgs(target)
        
        if len(target) == 4:
            #given by user: 
            #"*firefox", "http://www.google.com", "localhost", 4444
            host = target[2]
            port = target[3]
            browser = target[0]
            url = target[1] 
        elif len(target) == 2:
            host = self.ini.get(self.INI_SECTION, "host", "localhost") 
            port = int(self.ini.get(self.INI_SECTION, "port", "4444"))
            browser = target[0]
            url = target[1]
        else:
            raise NameError, "initBrowser must be called with this params: 'browser url [host] [port]'" 

        #instanciate and start the selenium object
        logging.info("initializing Selenium object. host:" + str(host) + " port:" + str(port) 
                     + " browser:" + str(browser) + " url:" + str(url))
        self.selenium = arges.thirdparty.selenium.selenium.selenium(host, port, browser, url)
        self.selenium.start()
        self.started = True
        #register the selenium object as a runner
        self.runners["selenium"] = self.selenium 
     
        return util.introspection.isInstance(self.selenium)
    
    def assertTextPresent(self, locator, challenge):
        """look within a locator if a given text is present"""
        try:
            text = self.selenium.get_text(locator)
        except:
            logging.debug("assertText - locator has not been found " 
                          + " locator: " + str(locator) 
                          + " challenge: " + str(challenge))
            return False
        #else:
            #todo ver error de unicode UnicodeEncodeError: 'ascii' codec can't encode character
        #    logging.debug("assertText - text: " + str(text)) 
                          #+ " from locator: " + str(locator) 
                          #+ " challenge: " + str(challenge))
            return re.search(unicode(challenge), text)!=None
        
    def assertTextNotPresent(self, locator, challenge):
        """look within a locator if a given text is not present"""
        res = self.assertTextPresent(locator, challenge)
        return not res

    def stopBrowser(self):
        """stop the browser only if it is necessary"""
        if self.started:
            self.selenium.stop() 
        self.started = False

    def waitForConfirmation(self, pattern, timeout=60):
        """
        Returns: True if the the message of the most recent JavaScript confirmation dialog
        is equal to the pattern. Otherwise returns False.
            
        Retrieves the message of a JavaScript confirmation dialog generated during the previous 
        action.
        By default, the confirm function will return true, having the same effect as manually 
        clicking OK. This can be changed by prior execution of the chooseCancelOnNextConfirmation 
        command. If an confirmation is generated but you do not get/verify it, the next Selenium 
        action will fail.
    
        NOTE: under Selenium, JavaScript confirmations will NOT pop up a visible dialog.
        NOTE: Selenium does NOT support JavaScript confirmations that are generated in a page's 
        onload() event handler. In this case a visible dialog WILL be generated and Selenium will 
        hang until you manually click OK. 
        """
        sel = self.selenium
        for i in range(timeout):
            try:
                if pattern == sel.get_confirmation():
                    break 
            except: pass
            time.sleep(1)
        else: 
            return False
        return True
            
    
    #-----------------------------------------------------------------------------    
    #common suffixes api
    #-----------------------------------------------------------------------------    
    
    def AndWait(self, timeout=-1):
        """and wait common suffix command
        suffix AndWait
        """
        if not util.introspection.isInt(timeout) or timeout < 0:
            timeout = 30 #default value
            if self.params.has_key(self.AND_WAIT_TIME):
                try:
                    timeout = int(self.params[self.AND_WAIT_TIME])
                except ValueError:
                    logging.warning("'" + str(self.params[self.AND_WAIT_TIME]) 
                                    + "' is not a valid number. Using default value: " 
                                    + str(timeout))
                                  
        logging.debug("executing suffix command AndWait, timeout:" + str(timeout) + " seconds")
        self.selenium.wait_for_page_to_load(timeout*1000)
        return True
    
    def waitForElementNotPresent(self, locator, timeout=-1):
        """Returns true if the element is not present, false otherwise
        Verifies that the specified element is somewhere on the page.
        suffix PV and Refresh
        """

        if not util.introspection.isInt(timeout) or timeout < 0: 
            timeout = 60 #default value
            if self.params.has_key(self.PV_TIME_OUT):
                try:
                    timeout = int(self.params[self.PV_TIME_OUT])
                except ValueError:
                    logging.warning("'" + str(self.params[self.PV_TIME_OUT]) 
                                    + "' is not a valid number. Using default value: " 
                                    + str(timeout))
            
        for i in range(timeout):
            try:
                if not self.waitForElementPresent(locator, timeout):
                    break
            except: pass
            time.sleep(1)
        else:
            logging.error("time out waiting for: " + str(locator))
            return False
        return True

    def waitForElementPresent(self, locator, timeout=-1, withRefresh=False):
        """Returns true if the element is present, false otherwise
        Verifies that the specified element is somewhere on the page.
        suffix PV and Refresh
        """
        if not util.introspection.isInt(timeout) or timeout < 0: 
            timeout = 60 #default value
            if self.params.has_key(self.PV_TIME_OUT):
                try:
                    timeout = int(self.params[self.PV_TIME_OUT])
                except ValueError:
                    logging.warning("'" + str(self.params[self.PV_TIME_OUT]) 
                                    + "' is not a valid number. Using default value: " 
                                    + str(timeout))
            
        logging.debug("executing prefix command waitForElementPresent (PV), timeout:" 
                      + str(timeout))
        #@todo: make the timeout work with time instead of number of times
        for i in range(timeout):
            try:
                if self.selenium.is_element_present(locator): break
                if withRefresh: self.selenium.refresh()
            except: pass
            time.sleep(1)
        else:
            logging.error("time out waiting for: " + str(locator))
            return False
        return True
         
    
sel = SeleniumWrapper() #Selenium wrapper object
   
def runProxiedCommand(cmd, target, value, additional_parameters):
    #exposed command to the test api
    return sel.runProxiedCommand(cmd, target, value, additional_parameters)

def hasProxiedCommand(command):
    #exposed command to the test api
    return sel.hasProxiedCommand(command)
