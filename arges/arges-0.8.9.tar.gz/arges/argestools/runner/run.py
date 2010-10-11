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
from optparse import OptionParser


import arges.util.ini
ini = arges.util.ini.Ini().getInstance()

def __init(argv=None):
    """init logging from argv options"""
    if argv is None:
        argv = sys.argv[1:]
    # Process command line options
    (options, args) = __getParser(argv)
    #get logger object
    return __getLogger(options)

def __getParser(argv):
    """set the command line parser object"""
    # Setup command line options
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-v", "--loglevel", dest="loglevel", default="info", help="logging level (debug, info, error)")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", help="do not log to console")
    parser.add_option("-c", "--clean", dest="clean", action="store_true", default=False, help="remove old log file")
    # Process command line options
    return parser.parse_args(argv)

def __getLogger(options):
    """set the globbal logger object"""
    #generate log file
    log_file = arges.APP.lower() +  ".log-" + str(datetime.datetime.now())
    log_file = log_file.replace(":", ".").replace(" ", "_")
    last_log_file = arges.util.util.getHomeDir() + os.path.sep + ".arges" + os.path.sep  \
                + "logs" + os.path.sep 
    log_file = last_log_file + log_file
    last_log_file = last_log_file + "arges.log"  
    
    #create the directory log
    arges.util.files.createDir(log_file)
    
    # Setup logger format and output locations
    logger = arges.util.util.initializeLogging(loglevel=options.loglevel.upper(), format=arges.LOG_FORMAT, logfile=log_file, clean=(not options.quiet))
    return logger, log_file, last_log_file

#init logging object
logging, log_file, last_log_file = __init()

import arges.util
import arges.argestools.argesfiles
import arges.argestools.argesfiles.parsefile
import arges.argestools.argesfiles.report
import launcher


def main(argv=None):
    try:
        logging.info("initializing %s, %s " % (arges.APP, arges.VERSION))
        logging.debug("argv: " + str(sys.argv))    

        report = None #declare report object to check if it exist
        finish_with_success = False
        all_steps_run_ok = True
        
        #@todo: make a correct way to send parameters like:
        #    -f testfile|path [-d testdata.tdata]
        #    -f testfile|path -g [testdata_to_be_generated.tdata]
        parseFile = arges.argestools.argesfiles.parsefile.ParseFile()
    
        #get app params
        stopTheBrowserAlways = ini.get(arges.APPCONFIG_SECTION, "stop the browser at the end of the execution", True, True)
        
        #validate parameters
        if len(sys.argv) < 2:
            msg = "test file parameter is missing"
            #logging.error(msg)
            raise Exception(msg)
            #@todo: print the correct invocation mode
            #print "no me imprimas!!!"
        else:
            test_file = sys.argv[1]
            
        if len(sys.argv) > 2:
            data_file = sys.argv[2]
        else:
            #try to open default test data file
            test_file = os.path.abspath(test_file)
            data_dir = os.path.dirname(test_file)
            data_file = arges.util.files.getFileName(test_file)
            data_file = arges.util.files.changeFileExtension(data_file, parseFile.TEST_DATA)
            data_file = data_dir + os.path.sep + data_file
            logging.debug("test data file parameter is empty, trying to open: " + str(data_file))
            #if the file doesn't exist then no default test data files is used
            if not os.path.isfile(data_file):
                data_file = None
            
        #get list of test steps with the format: 
        #command, target, value, criticity, description
        logging.info("getting test steps")
        steps = parseFile.getTestSteps(test_file)
        
        parameters = ini.getOptions(arges.TESTCONFIG_SECTION)  #get application parameters
        parameters.update(parseFile.getTestData(data_file, test_file))  #add test data parameters
        parameters_list =  parseFile.combineParams(parameters)  #combine multiple parameters
        
        report = arges.argestools.argesfiles.report.Reporter(test_file)
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
            launch = launcher.Launcher(steps_list, params)
            
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
        logging.exception("Error while running the steps. Exception info:")
        finish_with_success = False
    finally:
        ini.write()   #write app configuration data
        if arges.util.introspection.isInstance(report):
            report.write("</table>")
            report.writeHtmlFooter()
            report.close(True)
            logging.info("logging file: " + log_file)
            logging.info("report file: " + os.path.abspath(report.file.name))

            #copy log to last log file
            if os.path.isfile(log_file):
                try:
                    logging.info("copying last log file in: " + str(last_log_file))
                    shutil.copy(log_file, last_log_file)
                except:
                    logging.exception("problems copying the file to last log file")
            else:
                logging.warning("Logging file %s does not exist" % log_file)
        ret = 0
        if finish_with_success:
            if successful_execution:
                exec_msg = "All the executions were completed successfully."
            else:
                exec_msg = "Not all the executions were completed successfully."
            logging.info("%s %s has finished OK. %s" % (arges.APP, arges.VERSION, exec_msg))
        else:
            logging.error("%s %s has finished with an error." % (arges.APP, arges.VERSION))
            ret = 1
        
        sys.exit(ret)
    

def futuremain():
    try:
        log_file, last_log_file = setLog()
        report = None #declare report object to check if it exist
        finish_with_success = False
        all_steps_run_ok = True
        
        #@todo: make a correct way to send parameters like:
        #    -f testfile|path [-d testdata.tdata]
        #    -f testfile|path -g [testdata_to_be_generated.tdata]
        parseFile = arges.argestools.argesfiles.parsefile.ParseFile()
    
        #get app params
        stopTheBrowserAlways = ini.get(arges.APPCONFIG_SECTION, "stop the browser at the end of the execution", True, True)
        
        #validate parameters
        if len(sys.argv) < 2:
            msg = "test file parameter is missing"
            #logging.error(msg)
            raise Exception(msg)
            #@todo: print the correct invocation mode
            #print "no me imprimas!!!"
        else:
            test_file = sys.argv[1]
            
        if len(sys.argv) > 2:
            data_file = sys.argv[2]
        else:
            #try to open default test data file
            test_file = os.path.abspath(test_file)
            data_dir = os.path.dirname(test_file)
            data_file = arges.util.files.getFileName(test_file)
            data_file = arges.util.files.changeFileExtension(data_file, parseFile.TEST_DATA)
            data_file = data_dir + os.path.sep + data_file
            logging.debug("test data file parameter is empty, trying to open: " + str(data_file))
            #if the file doesn't exist then no default test data files is used
            if not os.path.isfile(data_file):
                data_file = None
            
        #get list of test steps with the format: 
        #command, target, value, criticity, description
        logging.info("getting test steps")
        steps = parseFile.getTestSteps(test_file)
        
        parameters = ini.getOptions(arges.TESTCONFIG_SECTION)  #get application parameters
        parameters.update(parseFile.getTestData(data_file, test_file))  #add test data parameters
        parameters_list =  parseFile.combineParams(parameters)  #combine multiple parameters
        
        report = arges.argestools.argesfiles.report.Reporter(test_file)
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
            launch = arges.argestools.runner.launcher.Launcher(steps_list, params)
            
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
        logging.exception("Error while running the steps. Exception info:")
        finish_with_success = False
    finally:
        ini.write()   #write app configuration data
        if arges.util.introspection.isInstance(report):
            report.write("</table>")
            report.writeHtmlFooter()
            report.close(True)
            logging.info("logging file: " + log_file)
            logging.info("report file: " + os.path.abspath(report.file.name))

            #copy log to last log file
            if os.path.isfile(log_file):
                try:
                    logging.info("copying last log file in: " + str(last_log_file))
                    shutil.copy(log_file, last_log_file)
                except:
                    logging.exception("problems copying the file to last log file")
            else:
                logging.warning("Logging file %s does not exist" % log_file)
        ret = 0
        if finish_with_success:
            if successful_execution:
                exec_msg = "All the executions were completed successfully."
            else:
                exec_msg = "Not all the executions were completed successfully."
            logging.info("%s %s has finished OK. %s" % (arges.APP, arges.VERSION, exec_msg))
        else:
            logging.error("%s %s has finished with an error." % (arges.APP, arges.VERSION))
            ret = 1
        
        sys.exit(ret)
    
if __name__ == '__main__':  
    main()
