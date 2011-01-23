#!/usr/bin/env python

from conf import settings
import clsexceptions as clsexceptions
import dbobjects as dbobjects

#from vendorxmlxxwriter import VendorXMLXXWriter

# for validation
from selector import HUDHMIS30XMLTest, HUDHMIS28XMLTest, JFCSXMLTest, VendorXMLTest, SVCPOINT406XMLTest, SVCPOINT20XMLTest
from errcatalog import catalog
import os
from queryobject import QueryObject
from conf import outputConfiguration
import clspostprocessing
import fileutils
from emailprocessor import XMLProcessorNotifier
from datetime import datetime
import iniutils
from hmisxml30writer import HMISXMLWriter
from hmisxml28writer import HMISXML28Writer
global hmiscsv30writer_loaded
global hmisxml28writer_loaded
global hmisxml30writer_loaded
global svcptxml20writer_loaded 
global svcptxml406writer_loaded
global jfcsxmlwriter_loaded



hmiscsv30writer_loaded = False
hmisxml28writer_loaded = False
hmisxml30writer_loaded = False
svcptxml20writer_loaded = False
svcptxml406writer_loaded = False
jfcsxmlwriter_loaded = False

class NodeBuilder(dbobjects.DatabaseObjects):

    def __init__(self, queryOptions):
        print "initializing nodebuilder"
        # initialize dbobjects
        dbobjects.DatabaseObjects()
        
        # fixme, need to decipher the query objects against the configuration (table, object, ini, conf..)
        # this should then pull the correct module below and run the process.
        generateOutputformat = outputConfiguration.Configuration[queryOptions.configID]['outputFormat']
        self.transport = outputConfiguration.Configuration[queryOptions.configID]['transportConfiguration']
        
        self.queryOptions = queryOptions
        
        if generateOutputformat == 'svcpoint406':
            #from svcpointxml20writer import SVCPOINTXML20Writer
            # pick the plug-in to import
            try:
                from svcpointxml_406_writer import SVCPOINTXMLWriter 
                svcptxml406writer_loaded = True
                print "import of Svcpt XML Writer, version 4.06 was successful"
            except:
                print "import of Svcpt XML Writer, version 4.06 failed"
                svcptxml406writer_loaded = False
            self.writer = SVCPOINTXMLWriter(settings.OUTPUTFILES_PATH, queryOptions)
            self.validator = SVCPOINT406XMLTest()
            
#        elif generateOutputformat == 'svcpoint20':
#            #from svcpointxml20writer import SVCPOINTXML20Writer
#            # pick the plug-in to import
#            try:
#                from svcpointxml20writer import SVCPOINTXMLWriter 
#                svcptxml20writer_loaded = True
#                print "import of Svcpt XML Writer, version 2.0 was successful"
#            except:
#                print "import of Svcpt XML Writer, version 2.0 failed"
#                svcptxml20writer_loaded = False
#            self.writer = SVCPOINTXMLWriter(settings.OUTPUTFILES_PATH, queryOptions)
#            self.validator = SVCPOINT20XMLTest()
                
        elif generateOutputformat == 'hmisxml28':
            try:
                from hmisxml28writer import HMISXML28Writer
                hmisxml28writer_loaded = True
            except:
                print "import of HMISXMLWriter, version 2.8, failed"
                hmisxml28writer_loaded = False
            if settings.DEBUG:
                print "settings.OUTPUTFILES_PATH is ", settings.OUTPUTFILES_PATH
            self.writer = HMISXML28Writer(settings.OUTPUTFILES_PATH, queryOptions)           
            self.validator = HUDHMIS28XMLTest()
            
        elif generateOutputformat == 'hmisxml30':
            try:
                from hmisxml30writer import HMISXMLWriter
                print "import of HMISXMLWriter, version 3.0 occurred successfully"
                hmisxml30writer_loaded = True
            except Exception as e:
                print "import of HMISXMLWriter, version 3.0, failed", e
                hmisxml30writer_loaded = False
            if settings.DEBUG:
                print "settings.OUTPUTFILES_PATH is ", settings.OUTPUTFILES_PATH
            self.writer = HMISXMLWriter(settings.OUTPUTFILES_PATH, queryOptions)                    
            self.validator = HUDHMIS30XMLTest() 
            
        elif generateOutputformat == 'hmiscsv30':
            try:
                from hmiscsv30writer import HmisCsv30Writer
                hmiscsv30writer_loaded = True
            except:
                hmiscsv30writer_loaded = False
            self.writer = HmisCsv30Writer(settings.OUTPUTFILES_PATH, queryOptions, debug=True)                    
            #self.validator = HmisCsv30Test()           
        elif generateOutputformat == 'jfcsxml':
            print "Need to hook up the JFCSWriter in Nodebuilder"
#            self.writer = JFCSXMLWriter()                   
#            self.validator = JFCSXMLTest()                 
        else:
            # new error cataloging scheme, pull the error from the catalog, then raise the exception (centralize error catalog management)
            err = catalog.errorCatalog[1001]
            raise clsexceptions.UndefinedXMLWriter, (err[0], err[1], 'NodeBuilder.__init__() ' + generateOutputformat)
            
        #fileStream = open(new_file,'r')
        # validate the file prior to uploading it
        #if self.validator.validate(fileStream):
        
        #setup the postprocessing module    
        self.pprocess = clspostprocessing.ClsPostProcessing(queryOptions.configID)
        
    def run(self):
        '''This is the main method controlling this entire program.'''
        
        # Load the data via dbobjects
        
        
        # try to write the output file and then validate it.
        #for writer,validator in map(None, self.writer, self.validator):
            #result = item.validate(instance_doc)
            # if results is True, we can process against this reader.
        if self.writer.write():
            filesToTransfer = fileutils.grabFiles(os.path.join(settings.OUTPUTFILES_PATH, "*.xml"))
            
            # create a list of valid files to upload
            validFiles = []
            # Loop over each file and validate it.
            for eachFile in filesToTransfer:
                fs = open(eachFile, 'r')
                if self.validator.validate(fs):
                    validFiles.append(eachFile)
                    print 'oK'
                else:
                    pass                # Fixme append invalid files to list and report this.
                
                fs.close()
            
            # upload the valid files
            # how to transport the files (debugging)
            if self.transport == '':
                print 'Output Complete...Please see output files: %s' % filesToTransfer
                
            if self.transport == 'sys.stdout':
                for eachFile in validFiles:
                    fs = open(eachFile, 'r')
                    # open the file and echo it to stdout
                    lines = fs.readlines()
                    fs.close()              # done with file close handle
                    for line in lines:
                        print line        
                        
            if self.transport == 'sftp':
                self.pprocess.processFileSFTP(validFiles)
            elif self.transport == 'email':
                # Loop over the list and each file needs to be emailed separately (size)
                for eachFile in validFiles:
                    self.email = XMLProcessorNotifier("", eachFile)     # fixme (zip and encrypt?)
                    msgBody = self.formatMsgBody()
                    self.email.sendDocumentAttachment('Your report results', msgBody, eachFile)
            elif self.transport == 'vpnftp':
                # SBB20100430 Only upload if we have a validated file(s)
                if len(validFiles) > 0:
                    pd = iniutils.LoadConfig('fileConverter.ini')
                    self.pprocess.setINI(pd)
                    self.pprocess.processFileVPN(validFiles)
            elif self.transport == 'vpncp':
                pass
                    
                #print results
                #print 'This is the result before it goes back to the test_unit:', \
                #results
                #return results
        
    def formatMsgBody(self):
        msgBody = "Your report was requested on %s. /r/n" \
                  'The report criteria is: \r\n' \
                  '\t StartDate: %s /r/n \t EndDate: %s /r/n /t Previously Reported: %s /r/n /t Previously UnReported: %s' % (datetime.today() ,self.queryOptions.startDate, self.queryOptions.endDate, self.queryOptions.reported, self.queryOptions.unreported)

    
    def selectNodes(self, start_date, end_date, nodename):
        pass
    
    def flagNodes(self):
        pass

#if svcptxml20writer_loaded is True:
#    if settings.DEBUG:
#        print "svcptxmlwriter not loaded"
#    class SvcPointXMLwriter(SVCPOINTXMLWriter):
#        
#        def __init__(self):
#            self.xML = SVCPOINTXMLWriter((os.path.join(settings.BASE_PATH, settings.OUTPUTFILES_PATH)))
#    
#        def write(self):
#            self.xML.processXML()
#            self.xML.writeOutXML()
#else: 
#    pass

#if svcptxml406writer_loaded is True:
#    if settings.DEBUG:
#        print "svcptxmlwriter not loaded"
#    class SvcPointXMLwriter(SVCPOINTXMLWriter):
#        
#        def __init__(self):
#            self.xML = SVCPOINTXMLWriter((os.path.join(settings.BASE_PATH, settings.OUTPUTFILES_PATH)))
#    
#        def write(self):
#            self.xML.processXML()
#            self.xML.writeOutXML()
#else: 
#    pass

#if hmiscsv30writer_loaded is True:
#    class HmisCsvWriter(HmisCsv30Writer):     
#         def __init__(self): 
#             self.csv = HmisCsv30Writer((os.path.join(settings.BASE_PATH, settings.OUTPUTFILES_PATH))) 
#    
#         def write(self): 
#             pass
#else: 
#    #if settings.DEBUG:
#        #print "hmiscsv30writer not found in conf yet, so not initializing class: HmisCsvWriter yet"
#    pass

if hmisxml30writer_loaded is True:
    class HmisXmlWriter(HMISXMLWriter):
        
        def __init__(self):
            self.xML = HMISXMLWriter((os.path.join(settings.BASE_PATH, settings.OUTPUTFILES_PATH)))
    
        def write(self):
            pass
else: 
    pass

if hmisxml28writer_loaded is True:
    class HmisXmlWriter(HMISXML28Writer):
        
        def __init__(self):
            self.xML = HMISXML28Writer((os.path.join(settings.BASE_PATH, settings.OUTPUTFILES_PATH)))
    
        def write(self):
            pass
else: 
    pass

if __name__ == '__main__':
    
    optParse = QueryObject()
    options = optParse.getOptions()
    if options != None:
        try:
            NODEBUILDER = NodeBuilder(options)
            RESULTS = NODEBUILDER.run()
            
        except clsexceptions.UndefinedXMLWriter:
            print "Please specify a format for outputting your XML"
            raise
    