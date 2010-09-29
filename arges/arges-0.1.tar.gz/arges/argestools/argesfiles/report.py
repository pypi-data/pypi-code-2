# -*- coding: latin-1 -*-

"""report - this module will generate the report files according to each test running instance 

@author: Adrián Deccico
"""

import distutils.dir_util 
import logging
import os
import datetime
import sys
import shutil
import util.files


class Reporter:
    """main class of the report module 
    
    This class will actually will provide the report functionality"""

    def __init__(self, path):
        #constants
        logging.info("initializing report object")
        self.__BASE_DIR__ = "ARGES_WORKAREA"
        self.__TSUITE_ALL_APPS_DIR__ = "TSUITE_ALL_APPLICATIONS"
        self.__TEST_RESULTS__ = "test_results"
        self.EXTENSION = "html"
        self.__CREATION_TRIES__ = 1000
        #init code
        self.file = self.__create_report_file__(path)
        #colors
        self.color_fail = "'#FFBFBF'"
        self.color_success = "'#BFFFBF'"

    def __create_report_file__(self, path):
        """create the report file according to the given path
        
        if a valid path is detected, then the test_results directory is created,
        but if not, the results directory is created as a directory within the 
        given path
        """
        
        #keep file name
        filename = util.files.getFileName(path)
        if not os.path.isfile(path):
            raise NameError, str(path) +  " does not contain a valid file name" 
        
        #decide directory
        path = os.path.dirname(path)
        possible_report_dir = [path + os.path.sep + "reports"]

        #decide if it is a valid ARGES directory
        path_components = os.path.split(path) #decide if it is an application or tsuite directory
        path = path_components[0] #test_planning or application name
        test_dir = path_components[1]
        if path_components[1].upper() == self.__TSUITE_ALL_APPS_DIR__:
            path_components = os.path.split(path_components[0]) # [1]==test_planning directory 
            path_components = os.path.split(path_components[0]) # [1]==ARGES_WORKAREA directory 
            if path_components[1] == self.__BASE_DIR__:
                possible_report_dir.insert(0, 
                                           path_components[0] 
                                           + os.path.sep 
                                           + self.__TEST_RESULTS__
                                           + os.path.sep 
                                           + self.__TSUITE_ALL_APPS_DIR__ 
                                           )
        else:
            path_components = os.path.split(path) #[test_planning,app_name] 
            app_name = path_components[1]
            path = path_components[0] #test_planning dir
            path = os.path.split(path)[1] #ARGES_WORKAREA directory
            if path == self.__BASE_DIR__:
                possible_report_dir.insert(0, 
                                           os.path.split(path)[0] 
                                           + os.path.sep 
                                           + self.__TEST_RESULTS__
                                           + os.path.sep
                                           +
                                           app_name
                                           + os.path.sep
                                           +
                                           test_dir                                            
                                           )
        
        #create directory tree
        for dir in possible_report_dir:
            try:
                dir = os.path.normpath(dir)
                distutils.dir_util.mkpath(dir)
                logging.info("report directory: " + str(dir) + " has been created")
                break
            except:
                logging.warning("problems trying to create report directory: " + str(dir))
                logging.exception("exception info:")
        
        if not os.path.isdir(dir):
            logging.error("report directory could not be created")
            name = ""
        else:
            #decide the name of the report file (take into account that the file may exist)
            name = filename + "__" + str(datetime.datetime.now())
            name = name.replace(":", ".")
            name = name.replace(" ", "_")
            name = dir + os.path.sep + name
        
        #create and return file
        #handle concurrency trying to create the file self.__CREATION_TRIES__ times
        if name == "":
            return None
        
        for i in range(self.__CREATION_TRIES__):
            prefix = str(i)
            prefix = prefix.zfill(len(str(self.__CREATION_TRIES__)) - 1)
            file_name = name + prefix + "." + self.EXTENSION
            try:
                f = open(file_name, 'w')
                logging.info("report file created. Name: " + str(file_name))
                break
            except:
                logging.debug("fail creation of report file: " 
                              + str(file_name) 
                              + " the program will try no more than: " 
                              + str(self.__CREATION_TRIES__)
                              + " times"
                              ) 
                logging.debug("exception info: " + str(sys.exc_info()))
            
        if os.path.isfile(file_name):
            return f
        else:
            return None
    
    def write(self, line):
        """write a line in the report file"""
        #logging.debug("writing report file")
        if self.file != None:
            self.file.write(line + "\n")
        else:
            logging.warning("report file is not valid, try to instanciate this class again")
    
    def writeHtmlHeader(self, title):
        """write html header with title"""
        self.write("<HTML><head><title>" + str(title) + "</title></head>")

    def writeHtmlBody(self, format=""):
        """write html body head"""
        self.write("<body " + format + ">")
        
    def writeHtmlTitle(self, title, level=1):
        """write html header with title"""
        self.write("<h" + str(level) + ">" + str(title) + "</h" + str(level) + ">")
    
    def writeHtmlBreak(self, repetitions=1):
        """write a line break <br> n times"""
        for i in range(repetitions):
            self.write("<br>")

    def writeHtmlLine(self):
        """write a simple line"""
        self.write("<hr>")

    def writeHtmlFooter(self):
        """write the html footer"""
        self.write("</body></HTML>")
    
    def close(self, copyToLastReportFile=False):
        """close the report file and optionally copy it to the 'last report file'    
        """
        logging.debug("closing report file")
        if self.file != None:
            self.file.close()
        
        if copyToLastReportFile:
            try:
                last_report = os.path.dirname(self.file.name) + os.path.sep + "last_report.html"
                logging.info("making last report file in: " + str(last_report))
                shutil.copy(self.file.name, last_report)
            except:
                logging.debug("problems copying the file to last report file")
                logging.debug("exception info: " + str(sys.exc_info()))

    def dictToTable(self, dict, key_title, value_title, table_format="", tr_format="", td_format=""):
        """format a dict into a html table
        pre dict is a table
        """
        logging.debug("writing table")
        self.write("<table " + table_format + ">")
        self.write("<tr " + tr_format + ">")
        self.write("<td " + td_format + ">")
        self.write(key_title)
        self.write("</td>")
        self.write("<td" + td_format + ">")
        self.write(value_title)
        self.write("</td>")
        self.write("</tr>")
        dict_keys = dict.keys()
        dict_keys.sort()
        for k in dict_keys:
            self.write("<tr " + tr_format + ">")
            self.write("<td " + td_format + ">")
            self.write(str(k))
            self.write("</td>")
            self.write("<td " + td_format + ">")
            self.write(str(dict[k]))
            self.write("</td>")
            self.write("</tr>")
        #for k,v in dict.iteritems():
        #    self.write("<tr " + tr_format + ">")
        #    self.write("<td " + td_format + ">")
        #    self.write(str(k))
        #    self.write("</td>")
        #    self.write("<td " + td_format + ">")
        #    self.write(str(v))
        #    self.write("</td>")
        #    self.write("</tr>")
        self.write("</table>")
    
    def writeTRWithColor(self, color):
        """write a true false TR with result"""
        self.write("<tr bgcolor=" + color + ">")

    def writeTDWithColor(self, color):
        """write a true false TR with result"""
        self.write("<td bgcolor=" + color + ">")
