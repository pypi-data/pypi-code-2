# -*- coding: latin-1 -*-

"""parsefile - this module will parse test case, use case, and test suites files 

@author: Adrián Deccico
"""

import logging
import re
import os

import util.files
import util.strings
import util.arges_util

GLOBAL= "GLOBAL"
GLOBAL_LIST = [GLOBAL]

class ParseFile:
    def __init__(self):
        self.TEST_SUITE = "tsuite"
        self.TEST_SUITE_COLUMNS_LEN = 2
        self.TEST_CASE = "tcase"
        self.TEST_CASE_COLUMNS_LEN = 5
        self.TEST_DATA = "tdata"
        self.TEST_DATA_COLUMNS_LEN = 2
        self.ESCAPED = '"'
        self.SEP = ","
        self.SEVERITY_SEPARATOR = "|"
        self.ASSIGNMENT_SEPARATOR = "="
        self.OK = 1
        self.LIMIT_OF_DEPENDENCIES_ITERATIONS_IN_TDATA = 10000
        self.MAX_LINE_LENGTH = 99999 # Arbitrary number.
        
        # This are used when iterating through an enumeration
        self.NUMBER = 0
        self.VALUE = 1
   
    def getTestSteps(self, file):
        """return the steps of a test case
        
        preconditions: valid test case file
        """
        
        #get the absolute path
        file = os.path.abspath(file)
        
        #decide if it is a valid file.
        #@todo: also accept paths
        if not util.files.isFile(file):
            #lanzo excepción
            raise NameError, str(file) + " is not a valid file" 

        #decide which type of file is being processed
        #and extract all its steps
        extension = util.files.getExtension(file)
        if extension == self.TEST_CASE:
            return self.getTestCaseSteps(file)
        elif extension == self.TEST_SUITE:
            return self.getTestSuiteSteps(file)
        else:
            raise NameError, str(extension) + " is not a recognized extension" 

    def getTestCaseSteps(self, filename, tsuite_name = None, ucase_name = None, section = None):
        """ Return the list of test steps belonging to a test case 
        this method should not be called directly, unless you know what you are doing
        """
        
        logging.info("getTestCaseSteps: " + str(filename))
        
        #list of steps to be returned
        steps = []

        file = open(filename)
        
        tstep_name = os.path.basename(os.path.normpath(file.name))
        
        for line in enumerate(file):
            line_value = line[self.VALUE]
            
            if util.arges_util.have_to_continue(line_value):
                continue
            
            logging.debug("processing line: %s %s" % (line[self.NUMBER], str(line_value)))
            line_value = util.strings.clean_line(line_value)
            line = (line[self.NUMBER], line_value)
                
            command_name = self.__getCommandName(line)
           
            retVal = self.__getRetVal(line)
                        
            severity = self.__get_severity(line) or "fatal"
            
            param1, param2 = self.__getParams(line)
            
            # Get Section
            values = [command_name, param1, param2, retVal,
                      severity, tsuite_name or "",
                      tstep_name]
            
            
            steps.append(values)

        file.close()
        return steps 

    def getTestData(self, test_data_file, test_file):
        """return the parameters of a test data
        
        preconditions: valid test data file
        """
        logging.info("getTestData: " + str(test_data_file))
        
        if test_data_file == None: 
            logging.info("data file is None, returning None")
            return None

        if util.files.getExtension(test_data_file) != self.TEST_DATA:
            msg = "'" + str(util.files.getExtension(test_data_file)) + "' is not a valid extension."
            msg = msg +  " for a test data file " 
            logging.error(msg)
            raise NameError, msg
        
        #search and validate test case file
        possible_test_case_file_name = []
        #try to open the test case file name as:
        #in the test case directory (where it should be found) 
        possible_test_case_file_name.append(
                                            util.files.getFileDir(test_file) 
                                            + os.path.sep
                                            + ".." 
                                            + os.path.sep
                                            + self.TEST_CASE
                                            + os.path.sep
                                            + util.files.getFileName(test_data_file)
                                            )
        #within the same use case directory
        possible_test_case_file_name.append(
                                            util.files.getFileDir(test_file) 
                                            + os.path.sep 
                                            + util.files.getFileName(test_data_file))

        #the first option option is always the passed parameter
        possible_test_case_file_name.insert(0, test_data_file)

        #try to load the test data file
        found = False
        for location in possible_test_case_file_name:
            if util.files.isFile(location):
                found = True
                break #once the file is found, process the next line
            
        if not found:
            raise NameError, str(test_data_file) + " is not a valid file" 

        #extract all the parameters
        return self.getTestDataParameters(location)

    def getTestDataParameters(self, file):
        """return the dictionary of test data parameters from a test data file 
        this method should not be called directly, unless you know what you are doing
        """
        #list of steps to be returned
        parameters = {}
        
        logging.info("using test data file: " + str(file))

        file = open(file)
        i = 0 #line number
        
        for line in file:
            #if the line is a comment or is blank, continue
            i = i+1 
            if self.lineIsComment(line): continue
            if self.lineIsBlank(line): continue
            
            line = self.removeComment(line) #strip comment of the line

            #validate if it is a valid command
            values = line.split("=") 
            if len(values) != self.TEST_DATA_COLUMNS_LEN:
                msg = "line: " + str(i) + " " + str(line) + " of test data file: " 
                msg = msg + str(file) + " is not valid. There are not: " 
                msg = msg + str(self.TEST_DATA_COLUMNS_LEN) + " values"
                logging.error(msg)
                raise NameError, msg

            #iterate over the list to replace blank values for nulls 
            for j in range(len(values)):
                if re.search(r"""^[\W]*$""", values[j]):
                    values[j] = "" 
                #trim all the blanks
                values[j] = util.strings.trim(values[j])
            
            #check duplicated keys
            if values[0] in parameters.keys():
                msg = "Duplicated parameter in line " + str(i) + ": " + str(line)  
                msg = msg + " of test data file: " + str(file)
                logging.error(msg) 
                raise NameError, msg
            
            #check if it is a valid parameter
            if not self.isValidParameter(values[0]):
                msg = str(values[0]) + " is an invalid parameter. Should be something like ${PARAM}"
                msg = msg + " line " + str(i) + ": " + str(line)
                msg = msg + " of test data file: " + str(file)
                logging.error(msg) 
                raise NameError, msg
                
            #save the parameter with the correct format
            #@todo: support escapped','
            list_values = values[1].split(",")
            parameters[util.strings.formatTestParameter(values[0])] = list_values   
            
        return parameters
    
    def lineIsComment(self, line):
        """return True if the line is a comment"""
        return util.files.lineIsComment(line) 
    
    def lineIsBlank(self, line):
        """return True if the line is a comment"""
        return util.files.lineIsBlank(line)    
    
    def isValidParameter(self, param):
        """return is param is a valid paramater, i.e. something like $ANY"""
        return re.match(r"^\$\{\w+\}$", param)
    
    def combine(self, d):
        if not d:
            return []
        elif len(d)==1:
            return d.values()[0]
        else:
            keys = d.keys()
            keys.sort()
            leftKeys = keys[0:len(keys)//2]
            rightKeys = keys[len(keys)//2:]
            leftDict = dict((key, d[key]) for key in leftKeys)
            rightDict = dict((key, d[key]) for key in rightKeys)
            return [x+","+y for x in self.combine(leftDict) for y in self.combine(rightDict)]
    
    def combineParams(self, params):
        logging.info("combining %s", "params")
        ret_params = []

        if params != None:
            dic_params = {}
            combined_params = self.combine(params)
            
            keys = params.keys()
            keys.sort()
    
            for i in range(len(combined_params[:])):
                params[i] = combined_params[i].split(",")
                for j, v in enumerate(params[i]):
                    dic_params[keys[j]] = v
                ret_params.append(dic_params.copy())
                dic_params.clear()
        else:
            ret_params.append({})
        
        #expand parameters in paramaters values
        for dict in ret_params:
            iter_again = True
            i = 0
            #iter many times to expand linked dependencies
            while iter_again and i < self.LIMIT_OF_DEPENDENCIES_ITERATIONS_IN_TDATA:
                iter_again = False
                i = i + 1
                for key in dict.keys():
                    #@todo: detect if the value has something replaceable to speed the algorithm. 
                    #        Took that value and use it as a key.
                    #@todo: detect circular dependencies 
                    if self.replaceParametersInParametersValues(dict, key):
                        iter_again = True
        
        return ret_params

    def replaceParametersInParametersValues(self, parameters, original_key):
        """given the parameter list, this function replace it's values
        by the previous parameters values
        
        return true if the value has changed
        """
        logging.debug("replacing parameters in parameters values")
        #track if something changed
        original_value = parameters[original_key]
        something_changed = False
        
        for key in parameters.keys():
            #we don't want to replace the list parameters 
            #with a value from the same list
            if key == original_key or parameters[original_key]==None: 
                continue
            parameters[original_key] = re.sub(key, parameters[key], parameters[original_key])
            if original_value != parameters[original_key]:
                something_changed = True
        
        return something_changed
        
    def getTestSuiteSteps(self, file):
        """return the list of test steps belonging to a use case 
        this method should not be called directly, unless you know what you are doing
        """
        logging.info("getTestSuiteSteps: " + str(file))
        
        #list of steps to be returned
        steps = []

        path = file
        file = open(file)
        i = 0 #line number
        
        for line in file:
            #if the line is a comment or is blank, continue
            i = i+1  #@todo: use enumerate
            if self.lineIsComment(line): continue
            if self.lineIsBlank(line): continue
            
            line = self.removeComment(line) #strip comment of the line

            #trim the line
            line = util.strings.trim(line)

            #validate extension
            extension = util.files.getExtension(line).split(",")[0]
            if extension != self.TEST_CASE: 
                msg = "'" + str(util.files.getExtension(line)) + "' is not a valid extension."
                msg = msg +  " of test case file: " 
                msg = msg + str(util.files.getExtension(line))
                msg = msg +  " line: " + str(i) + " file: " + str(path) 
                logging.error(msg)
                raise NameError, msg

            #search and validate test case file
            possible_test_case_file_name = []
            #try to open the test case file name as:
            #1. in the test case or use case directory (where it should be found) 
            possible_test_case_file_name.append(
                                                util.files.getFileDir(path) 
                                                + os.path.sep
                                                + ".." 
                                                + os.path.sep
                                                + extension
                                                + os.path.sep
                                                + util.files.getFileName(line)
                                                )
            
            #2. within the same use case directory
            possible_test_case_file_name.append(
                                                util.files.getFileDir(path) 
                                                + os.path.sep 
                                                + util.files.getFileName(line))
            #3. an absolute path
            possible_test_case_file_name.append(line)

            #try to add the steps
            found = False
            for location in possible_test_case_file_name:
                if util.files.isFile(location):
                    found = True
                    if extension == self.TEST_CASE:
                        steps = steps + self.getTestCaseSteps(location)
                    elif extension == self.USE_CASE:
                        steps = steps + self.getUseCaseSteps(location)
                    break #once the file is found, process the next line
            
            if not found:
                msg = "line: " + str(i) + " " + str(line) + " of use case file: " 
                msg = msg + str(file) + " is not valid. '" 
                msg = msg + str(line) + "' is not a valid test case file."
                logging.error(msg)
                raise NameError, msg
                
        return steps 
    
    def removeComment(self, line):
        """remove comment of the line"""
        return re.sub(r"""\B#.*$""", "", line)

    def __getCommandName(self, line):
        """ This function returns the name of the command that is being read."""
        
        if not self.__hasCommand(line):
            return ""
        
        line_value = line[self.VALUE]
        
        first_parenthesis_idx = line_value.find("(")
        first_equals_idx = line_value.find(self.ASSIGNMENT_SEPARATOR)
        
        if not self.__hasRetValue(line):
            command_name = line_value[:first_parenthesis_idx].strip() if first_parenthesis_idx > 0 else None
        else:
            command_name = line_value[first_equals_idx + 1:first_parenthesis_idx].strip() if first_parenthesis_idx > first_equals_idx else None
        
        if self.__valid_command_name(command_name) is self.OK:
            return command_name

    def __hasCommand(self, line):
        """ This method just returns whether the line has a command. It does
        certain verifications to accomplish this task.
        """
        line_value = line[self.VALUE].strip() 

        # I'll find these chars: '(', '=', 'self.SEP' and the first ascii
        equals_idx = line_value.find('=')if line_value.find('=') != -1 else self.MAX_LINE_LENGTH
        parenthesis_idx = line_value.find('(') if line_value.find('(') != -1 else self.MAX_LINE_LENGTH
        escape_idx = line_value.find('"')  if line_value.find('"') != -1 else self.MAX_LINE_LENGTH
        regex = re.compile('\w+')
        res = regex.search(line_value)
        if res is not None:
            ascii_idx = res.start()
                
        if ascii_idx < equals_idx and ascii_idx < parenthesis_idx and ascii_idx < escape_idx:
            # This means that the line is like 'a = ...' or 'a... (' or 'a..."'
            
            if parenthesis_idx < equals_idx and parenthesis_idx < escape_idx:
                # This means that following the ascii, there is a '('.
                # So, it has to be a function.
                return True
            
            elif equals_idx < parenthesis_idx and equals_idx < escape_idx:
                # This means that line is of the form 'a = ...'
                # It can be a function or a value
                if parenthesis_idx < escape_idx:
                    return True
                else:
                    # It's not a function, it's a value
                    return False
            else:
                raise NameError, "Malformed line: line number %s - %s" % (line[self.NUMBER], line_value)
        else:
            raise NameError, "Malformed line: line number %s - %s" % (line[self.NUMBER], line_value)

    def __hasRetValue(self, line):
        line_value = line[self.VALUE]
        first_parenthesis_idx = line_value.find('(')
        
        first_equals_idx = line_value.find(self.ASSIGNMENT_SEPARATOR)
        
        if first_parenthesis_idx != -1:
            equals_before_parenthesis = first_equals_idx < first_parenthesis_idx
            return first_equals_idx >= 0 and equals_before_parenthesis
        else:
            return first_equals_idx >= 0

    def __valid_command_name(self, command_name):
        """ Validates that the command name is not an empty value and that it doesn't contain
        certain values, such as '=' """
        if command_name is None:
            raise NameError, "Please provide a command name. %s not valid. " % command_name
        elif command_name.find(self.ASSIGNMENT_SEPARATOR) >= 0:
            raise NameError, "I'm sorry, but the command name must not have the '=' character.  %s not valid." % command_name
        
        return self.OK


    def __getRetVal(self, line):
        """ This method just returns the name of the retValue."""
        line_value = line[self.VALUE]
        if self.__hasRetValue(line):
            first_equals_idx = line_value.find(self.ASSIGNMENT_SEPARATOR)
            retVal = line_value[:first_equals_idx].strip()  
                      
            if self.__valid_retVal(retVal) is self.OK:
                return retVal
        
        return None
 
    def __get_severity(self,line):
        """ This function just returns the severity of the command. """
        
        if not self.__hasCommand(line):
            return None
        
        line_value = line[self.VALUE]
        last_parenthesis_idx = line_value.rfind(")")
        
        if last_parenthesis_idx < 0:
            msg = """ There is no ')' character closing the function call!.
            line number :%s 
            line content : %s
            """ % (line[self.NUMBER], line_value)
            raise NameError, msg
        
        severity_sep_idx = line_value.rfind(self.SEVERITY_SEPARATOR)
        
        
        return line_value[severity_sep_idx + 1:].strip() if severity_sep_idx > last_parenthesis_idx else None

    def __getParams(self,line):
        
        line_value = line[self.VALUE]
       
        if not self.__hasCommand(line):
            param_idx = line_value.find('=')

            # just return the value that is next to the '=' char
            if param_idx != -1:
                return line_value[param_idx+1:].strip(), None
            else:
                return None, None
            
        # I'll just work with the params part.
        first_parenthesis_idx = line_value.find("(")
        last_parenthesis_idx = line_value.rfind(")")

        if first_parenthesis_idx == -1 or last_parenthesis_idx == -1:
            raise NameError, "I'm sorry, but no function call was found. The function call are the '()' chars"
        
        params_line = line_value[first_parenthesis_idx + 1:last_parenthesis_idx].strip()

        if len(params_line) == 0:
            return None,None

        first_param = ""
        second_param = ""
        sep_idx = None

        # Here I get the first param
        if not self.__startsEscaped(params_line):
            sep_idx = len(params_line) if params_line.find(self.SEP) == -1 else params_line.find(self.SEP)            
            first_param = params_line[:sep_idx]
        else:
            sep_idx = self.__findSepIdx(params_line)            
            first_param = self.__getEscapedParam(params_line, sep_idx or len(params_line))


        # if there's a second param ... 
        if sep_idx is not None and sep_idx != len(params_line):
            params_line = params_line[sep_idx + 1:]
            
            if self.__startsEscaped(params_line):
                second_param = self.__getEscapedParam(params_line)
            else:
                second_param = params_line

        return first_param.strip() if len(first_param.strip()) > 0 else None , second_param.strip() if len(second_param.strip()) > 0 else None 

    def __startsEscaped(self,line):
        return True if line.lstrip().startswith('"') else False

    def __findSepIdx(self,line):
        """ This method find the separator that is located between the params """

        regex = re.compile('"%s*%s'% (self.ESCAPED,self.SEP))
        match = regex.search(line)
        
        if match is not None:
            return match.start() + 1
        else:
            return None

    def __getEscapedParam(self,line, sep_idx = None):
        """ This method should return the escaped param. 
        The line should have the form self.ESCAPE...self.ESCAPE
        """
        
        # This is just to see if it's the first or second param
        if sep_idx is None:
            sep_idx = len(line)
            
        line = line[line.find(self.ESCAPED) + 1:sep_idx -1 ]
        regex = re.compile('%s%s' % (self.ESCAPED,self.ESCAPED))
        line = regex.sub('%s' % self.ESCAPED, line)
        return line

    def __valid_retVal(self, retVal):
        """ Validates the retVal value is not an empty value, or that it doesn't contain some 
        crazy chars, such as '=' and '(' or ')' """
        illegal_chars = '!@#%^&*()+=-`~°|'
         
        if len(retVal.strip()) == 0:
            raise NameError, "Please provide a return value or remove the '=' character."
        else:
            for c in illegal_chars:
                if retVal.find(c) >= 0:
                    raise NameError, "The return value must not contain the '%s' character" % c
        
        return self.OK
