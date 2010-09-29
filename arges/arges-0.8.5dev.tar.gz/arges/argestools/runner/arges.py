# -*- coding: latin-1 -*-

"""main - Main module of the Arges application

@author: Adrián Deccico
"""
import logging
import sys
import copy
import datetime
import os
import shutil

#add the application path to be able to import all the packages
app_path = os.path.abspath(os.path.dirname(sys.argv[0]) 
                           + "." + os.path.sep 
                           + ".." + os.path.sep + "..")
sys.path.insert(0, app_path)
VERSION = "0.8.2"

import util
import util.ini

TESTCONFIG_SECTION = "arges_test_files_params"   
APPCONFIG_SECTION = "arges_test_app_params"   

ini = util.ini.Ini().getInstance()

#set the logger object
log_format = ini.get(APPCONFIG_SECTION, 
            "log_format", "", 
            True) 
#log_format = ini.get(APPCONFIG_SECTION, 
#            "log_format", "%(asctime)-15s-L%(levelno)s-%(message)s - %(filename)s-%(lineno)d", 
#            True) 
log_level = int(ini.get(APPCONFIG_SECTION,"log_level",str(logging.INFO)))
log_file = "arges.log-" + str(datetime.datetime.now())
log_file = log_file.replace(":", ".").replace(" ", "_")
last_log_file = util.util.getHomeDir() + os.path.sep + ".arges" + os.path.sep  \
            + "logs" + os.path.sep 
log_file = last_log_file + log_file
last_log_file = last_log_file + "arges.log"  

#create the directory log
util.files.createDir(log_file)
            
logging.basicConfig(level = log_level,
                    #format=log_format,
                    filename= log_file,
                    filemode='a+'
                    )
console_log = logging.StreamHandler()
console_log.setLevel(int(log_level))
console_log.setFormatter(logging.Formatter(log_format))
logging.getLogger("").addHandler(console_log) 

logging.info("initializing ARGES AUTOMATED TESTING, version " + VERSION)
logging.debug("setting app_path: " + app_path)
logging.debug("argv: " + str(sys.argv))

import argestools.argesfiles
import argestools.argesfiles.parsefile
import argestools.argesfiles.report
import argestools.runner.launcher

if __name__ == '__main__':  #entry point of the application
    
    try:
        report = None #declare report object to check if it exist
        finish_with_success = False
        all_steps_run_ok = True
        
        #@todo: make a correct way to send parameters like:
        #    -f testfile|path [-d testdata.tdata]
        #    -f testfile|path -g [testdata_to_be_generated.tdata]
        parseFile = argestools.argesfiles.parsefile.ParseFile()
    
        #get app params
        stopTheBrowserAlways = ini.get(APPCONFIG_SECTION, "stop the browser at the end of the execution", True, True)
        
        #validate parameters
        if len(sys.argv) < 2:
            msg = "test file parameter is missing"
            logging.error(msg)
            raise NameError, msg
            #@todo: print the correct invocation mode
        else:
            test_file = sys.argv[1]
            
        if len(sys.argv) > 2:
            data_file = sys.argv[2]
        else:
            #try to open default test data file
            test_file = os.path.abspath(test_file)
            data_dir = os.path.dirname(test_file)
            data_file = util.files.getFileName(test_file)
            data_file = util.files.changeFileExtension(data_file, parseFile.TEST_DATA)
            data_file = data_dir + os.path.sep + data_file
            logging.debug("test data file parameter is empty, trying to open: " + str(data_file))
            #if the file doesn't exist then no default test data files is used
            if not os.path.isfile(data_file):
                data_file = None
            
        #get list of test steps with the format: 
        #command, target, value, criticity, description
        logging.info("getting test steps")
        steps = parseFile.getTestSteps(test_file)
        
        parameters = ini.getOptions(TESTCONFIG_SECTION)  #get application parameters
        parameters.update(parseFile.getTestData(data_file, test_file))  #add test data parameters
        parameters_list =  parseFile.combineParams(parameters)  #combine multiple parameters
        
        report = argestools.argesfiles.report.Reporter(test_file)
        report.writeHtmlHeader("Report File")
        report.writeHtmlTitle("Arges Automated Testing")
        report.writeHtmlBody("bgcolor='#ffffff'")
        report.writeHtmlLine()
        report.write("Test File: " + test_file)
        report.writeHtmlBreak()
        report.write("Data File: " + data_file)
        report.writeHtmlBreak()
        report.write("Running time: " + str(datetime.datetime.now()))
        report.writeHtmlBreak()
        report.writeHtmlLine()
        report.writeHtmlBreak()
        report.write("<table border=1>")
        report.write("<tr bgcolor='#dadada'>")
        report.write("<td><strong>Result&nbsp;</strong></td><td width=70%><strong>Individual Step Result</strong></td>")
        report.write("<td><strong>Parameters:</strong></td></tr>")        
    
        #execute the test for each list of parameters
        for i, params in enumerate(parameters_list):
            #make a deep copy of the mutable step list because a shallow copy like this[:] 
            #is not enough as it copy the reference of the objects within the list
            steps_list = copy.deepcopy(steps) 
            #instance launcher object with passed parameter
            launch = argestools.runner.launcher.Launcher(steps_list, params)
            
            #run launcher to let it execute the commands
            number_of_steps = len(steps_list)
            number_of_results = launch.run(stopTheBrowserAlways)
            
            #decide if it was a successful execution based on the number of results returned 
            #and the result of the last step, because the execution is performed until 
            #a step fail and the last step could also fail. 
            successful_execution = number_of_steps == number_of_results
            #If the last command exist and their criticity is not true or the command is true
            #then the execution was successful
            last_step_index = len(steps_list)-1
            last_step_result = steps_list[last_step_index][0]
            last_step_is_fatal = True
            if len(steps_list[last_step_index]) > launch.CRITICITY_COL+1:
                last_step_is_fatal = launch.isFatal(steps_list[last_step_index][launch.CRITICITY_COL+1])
            successful_execution = successful_execution and (last_step_result or not last_step_is_fatal)
            all_steps_run_ok = successful_execution and successful_execution 
            
            msg = "Set of results: " + str(i+1) + " / " + str(len(parameters_list))
            #write report
            report.writeTRWithColor(report.color_success) if successful_execution else report.writeTRWithColor(report.color_fail)
            report.write("<td valign='top'>")
            report.write("<strong>" + ("Passed" if successful_execution else "Failed") + "<strong>")
            report.write("</td>")

            #print the results  
            logging.info(msg)
            logging.info("Printing " + str(number_of_results) + " results...")
            report.write("<td valign='top'>")
            report.write("<table border=1 valign='top'>")
            for j in range(number_of_results):
                cmd_list = steps_list[j]
                cmd = str(cmd_list[1:]) 
                logging.info("result: " + str(cmd_list[0]) + " for command: " + cmd)
                #set the color of the report
                report.writeTRWithColor(report.color_success) if cmd_list[0] else report.writeTRWithColor(report.color_fail)  
                report.write("<td valign='top'>")
                report.write(str("Passed" if (cmd_list[0]) else "Failed") + " for command: " + cmd)
                report.write("</td>")

            report.write("</table></td>")
            #print parameters
            report.write("<td valign='top'>Set of parameters #" + str(i+1) + "<br>")
            report.dictToTable(params, "Param name", "Param value", "border=1")
            report.write("</td></tr>")
            finish_with_success = True
    except:
        logging.error("exception while running the test steps")
        logging.exception("exception info:")
        finish_with_success = False
    finally:
        ini.write()   #write app configuration data
        if util.introspection.isInstance(report):
            report.write("</table>")
            report.writeHtmlFooter()
            report.close(True)
            logging.info("logging file: " + log_file)
            logging.info("report file: " + os.path.abspath(report.file.name))

            #copy log to last log file
            try:
                logging.info("copying last log file in: " + str(last_log_file))
                shutil.copy(log_file, last_log_file)
            except:
                logging.exception("problems copying the file to last log file")
        
        ret = 0
        if finish_with_success:
            if successful_execution:
                exec_msg = "All the executions were completed successfully."
            else:
                exec_msg = "Not all the executions were completed successfully."
            logging.info("ARGES AUTOMATED TESTING has finished OK. " + exec_msg)
        else:
            logging.error("ARGES AUTOMATED TESTING has finished with error.")
            ret = 1
        
        sys.exit(ret)
        
        
