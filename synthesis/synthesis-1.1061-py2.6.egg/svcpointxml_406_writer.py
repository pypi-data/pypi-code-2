import os.path
from interpretpicklist import Interpretpicklist
#our synthesis specific date handling functions
import dateutils
from datetime import timedelta, date, datetime
from time import strptime, time
import xmlutilities
#from mx.DateTime import ISO
# SBB20070920 Adding exceptions class
#from clsexceptions import dataFormatError, ethnicityPickNotFound

#import logging
import logger

from sys import version
from conf import settings
import clsexceptions
import dbobjects
import fileutils
from writer import Writer
from zope.interface import implements

from sqlalchemy import or_, and_, between

# py 2.5 support
# dynamic import of modules
thisVersion = version[0:3]

#if thisVersion  == '2.5':
if float(settings.MINPYVERSION) < float(version[0:3]):
    try:
    	import xml.etree.cElementTree as ET
    	from xml.etree.ElementTree import Element, SubElement, dump
    except ImportError:
    	import xml.etree.ElementTree as ET
    	from xml.etree.ElementTree import Element, SubElement
elif thisVersion == '2.4':
    try:
	# Try to use the much faster C-based ET.
    	import cElementTree as ET
    	from elementtree.ElementTree import Element, SubElement, dump
    except ImportError:
	# Fall back on the pure python one.
    	import elementtree.ElementTree as ET
    	from elementtree.ElementTree import Element, SubElement
else:
    print 'Sorry, please see the minimum requirements to run this Application'
    theError = (1100, 'This application requires Python 2.4 or higher.  You are current using version: %s' % (thisVersion), 'import Error XMLDumper.py')
    raise SoftwareCompatibilityError, theError

def buildWorkhistoryAttributes(element):
    element.attrib['date_added'] = datetime.now().isoformat()
    element.attrib['date_effective'] = datetime.now().isoformat()

class SVCPOINTXMLWriter(dbobjects.DatabaseObjects):
	
    # Writer Interface
    implements (Writer)
    
    hmis_namespace = "http://www.hmis.info/schema/2_8/HUD_HMIS_2_8.xsd" 
    airs_namespace = "http://www.hmis.info/schema/2_8/AIRS_3_0_draft5_mod.xsd"
    nsmap = {"hmis" : hmis_namespace, "airs" : airs_namespace}
    
    svcpt_version = '4.06'
    
    def __init__(self, poutDirectory, processingOptions, debugMessages=None):
    	#print "%s Class Initialized" % self.__name__
    	
    	if settings.DEBUG:
    	    print "XML File to be dumped to: %s" % poutDirectory
    	    
    	    self.log = logger.Logger(configFile='logging.ini', loglevel=40)
    		
    	self.outDirectory = poutDirectory
    	self.pickList = Interpretpicklist()
    	# SBB20070626 Adding the declaration for outcomes list
    	self.options = processingOptions
    	
    	# SBB20070628 adding a buffer for errors to be displayed at the end of the process.
    	self.errorMsgs = []
    	self.iDG = xmlutilities.IDGeneration()
    	self.mappedObjects = dbobjects.DatabaseObjects()
    	
    	#import logging
    	#logging.basicConfig()
    	#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    	#logging.getLogger('sqlalchemy.orm.unitofwork').setLevel(logging.DEBUG)
    
    def write(self):
    	self.startTransaction()
    	self.processXML()
    	self.prettify()
    	xmlutilities.writeOutXML()
    	#self.commitTransaction()
    	return True

    def updateReported(self, currentObject):
	# update the reported field of the currentObject being passed in.  These should all exist.
    	try:
    	    if settings.DEBUG:
                print 'Updating reporting for object: %s' % currentObject.__class__
    	    currentObject.reported = True
    	    #currentObject.update()
    	    #self.session.save(currentObject)
    	    self.commitTransaction()
    	    
    	except:
    	    print "Exception occurred during update the 'reported' flag"
    	    pass

    def prettify(self):
    	FileUtilities.indent(self.root_element)

    def dumpErrors(self):
    	print "Error Reporting"
    	print "-" * 80
    	for row in range(len(self.errorMsgs)):
    	    print "%s %s" % (row, self.errorMsgs[row])
	
    # SBB20071021 Set the systemID value from the DB.
    #rowID = bz.getRowID(dsRec[0]['Client ID'])
    #xML.setSysID(rowID)
    
    def setSysID(self, pSysID):
    	self.sysID = pSysID
        # SBB20071021

    def commitTransaction(self):
    	self.session.commit()
	#self.transaction.commit()
	#pass
	
    def startTransaction(self):
    	# instantiate DB Object layer
    	# Create the transaction
    	# get a handle to our session object
    	self.session = self.mappedObjects.session(echo_uow=True)
    	#self.transaction = self.session.create_transaction()
    	#pass
    	
        # SBB20100402 Querying for configuration information
    def pullConfiguration(self, pExportID):
	# need to use both ExportID and Processing Mode (Test or Prod)
    	source = self.session.query(dbobjects.Source).filter(dbobjects.Source.export_id == pExportID).one()
        #ECJ20100908 Adding some debugging
        #if settings.DEBUG:
            #print "trying to do pullConfiguration"
            #print "source is:", source
            #print "pExportID is", pExportID
            #print "source.source_id is: ", source.source_id
            #print "dbobjects.SystemConfiguration.source_id is ", dbobjects.SystemConfiguration.source_id
            #print "test dbobjects.SystemConfiguration.source_id == source.source_id yields ", assert dbobjects.SystemConfiguration.source_id == source.source_id
            #print "dbobjects.Source.export_id is", dbobjects.Source.export_id
            #print "self.session.query(dbobjects.Source).filter(dbobjects.Source.export_id == pExportID) is: ", self.session.query(dbobjects.Source).filter(dbobjects.Source.export_id == pExportID)
            #print "self.session.query().one() is", self.session.query().one()
        self.configurationRec = self.session.query(dbobjects.SystemConfiguration).filter(and_(dbobjects.SystemConfiguration.source_id == source.source_id, dbobjects.SystemConfiguration.processing_mode == settings.MODE)).one()
	
    def processXML(self): # records represents whatever element you're tacking more onto, like entry_exits or clients
    	if settings.DEBUG:
    	    print "Appending XML to Base Record"
    	
    	# generate the SystemID Number based on the Current Users Data, You must pass in the word 'system' in order to create the current users key.
    	self.SystemID = self.iDG.generateSystemID('system')
    
    	# start the clients
    	
    	self.root_element = self.createDoc() #makes root element with XML header attributes
    	
    	clients = self.createClients(self.root_element)
    	
    	# Clear the session
    	#session.clear()
    	
    	# first get the export object then get it's related objects
    	
    	if self.options.reported == True:
    	    Persons = self.session.query(dbobjects.Person).filter(dbobjects.Person.reported == True)
    	elif self.options.unreported == True:
    	    Persons = self.session.query(dbobjects.Person).filter(or_(dbobjects.Person.reported == False, dbobjects.Person.reported == None))
    	elif self.options.reported == None:
    	    Persons = self.session.query(dbobjects.Person)
    	else:
    	    pass
    	
    	# try to append the filter object to the predefined result set
    	# this works, it now applies the dates to the result set.
    	Persons = Persons.filter(between(dbobjects.Person.person_id_date_collected, self.options.startDate, self.options.endDate))
    	
    	#or_(User.name == 'ed', User.name == 'wendy')
    	#Persons = self.session.query(dbobjects.Person)
    	#Persons = self.session.query(dbobjects.Person).filter(dbobjects.Person.reported == None) (works)
    	
    	
    	for self.person in Persons:
    	    #print "person is: ", self.person
    	    # SBB20100402 Need to load the configuration based on related source table record (via the export record that is related to person)
    	    export = self.person.fk_person_to_export
    	    self.pullConfiguration(export.export_id)
    	    
    	    # update the reported flag for person (This needs to be applied to all objects that we are getting data from)
    	    self.updateReported(self.person)
    	    
    	    self.ph = self.person.fk_person_to_person_historical
    	    self.race = self.person.fk_person_to_races
    	    self.site_service_part = self.person.fk_person_to_site_svc_part
    	    information_releases = self.person.fk_person_to_release_of_information
            #self.service_event = self.person.fk_person_to_service_event
    	    
    	    # Instead of generating a number (above), use the client number that is already provided in the legacy system
    	    # or
    	    self.iDG.initializeSystemID(self.person.id)
    	    self.sysID = self.person.id
            #if settings.DEBUG:
                #print "self.person is:", self.person 
    	    #if not self.person == None and self.outcomes == None:
    	    if self.person:# and not self.person.person_legal_first_name_unhashed == None and not self.person.person_legal_last_name_unhashed == None :
                self.client = self.createClient(clients)
                self.customizeClient(self.client)
                self.customizeClientPersonalIdentifiers(self.client, self.person)
                dynamic_content = self.createDynamicContent(self.client)
                self.customizeDynamicContent(dynamic_content)
    		# EntryExits
    		# SBB20100311 These need to be at Document Level not client level
    		#entry_exits = self.createEntryExits(self.client)
    		# SBB20100826 Putting Needs back to Client level
    	    
            #ECJ20100912 Unlike in SP406 XML, needs can only exist within SiteServiceParticipations (aka Entry-exits) in HMIS XML 2.8
            #ECJ20100912 So, we have to pull Needs out of SiteServiceParticipations/EEs and put them separately right under Client in SP406
            for ssp in self.site_service_part:
                #self.createEntryExit(entry_exits, ssp)
                needData = None
                if not ssp == None:
                    Needs = ssp.fk_participation_to_need
                    # Needs (only create this if we have a 'Need')
#                    if settings.DEBUG:
#                        print "Needs are: ", Needs
                    if Needs:
                        for needRecord in Needs:
#                            if settings.DEBUG:
#                                print "needRecord is: ", needRecord
							#Reporting Update
                            self.updateReported(needRecord)
                            needs = self.createNeeds(self.client)
                            need = self.createNeed(needs, needRecord)
                            self.customizeNeed(need, needRecord)
#                            if settings.DEBUG:
#                                print "needRecord.service_event_idid_num", needRecord.service_event_idid_num
                            
							#ECJ20100912 Now put the service events (aka services in sp408 XML) within each need.  They aren't nested in the XML, so need to query
#                            if settings.DEBUG:
#                                print "dbobjects.ServiceEvent is: ", dbobjects.ServiceEvent
                            
                            ServiceEvents =  self.session.query(dbobjects.ServiceEvent).filter(dbobjects.ServiceEvent.service_event_idid_num == needRecord.service_event_idid_num)
#                            if settings.DEBUG:
#                                print "ServiceEvents are: ", ServiceEvents
#                                for item in ServiceEvents:
#                                    print "service_event is: ", item
                            
                            if ServiceEvents:
                                services = self.createServices(need)
                                for serviceRecord in ServiceEvents:
                                    self.updateReported(serviceRecord)
                                    service = self.createService(serviceRecord, services)
                                    self.customizeService(serviceRecord, service)
                                    
    	    # Release of Information
    	    if len(information_releases) > 0:
    		info_releases = self.createInfo_releases(self.client)
    		for self.IR in information_releases:
    		    
    		    # Reporting Update
    		    self.updateReported(self.IR)
    		    
    		    info_release = self.createInfo_release(info_releases)
    		    self.customizeInfo_release(info_release)
    
    	# Query Mechanism
    	if self.options.reported == True:
    	    #Persons = self.session.query(dbobjects.Person).filter(dbobjects.Person.reported == True)
    	    site_service_part = self.session.query(dbobjects.SiteServiceParticipation).filter(dbobjects.SiteServiceParticipation.reported == True)
    	elif self.options.unreported == True:
    	    #Persons = self.session.query(dbobjects.Person).filter(or_(dbobjects.Person.reported == False, dbobjects.Person.reported == None))
    	    site_service_part = self.session.query(dbobjects.SiteServiceParticipation).filter(or_(dbobjects.SiteServiceParticipation.reported == False, dbobjects.SiteServiceParticipation.reported == None))
    	elif self.options.reported == None:
    	    #Persons = self.session.query(dbobjects.Person)
    	    site_service_part = self.session.query(dbobjects.SiteServiceParticipation)
    	else:
    	    pass
    	
    	# setup the date filter also
    	site_service_part = site_service_part.filter(between(dbobjects.SiteServiceParticipation.site_service_participation_idid_num_date_collected, self.options.startDate, self.options.endDate))
    
    	
    	
    	entry_exits = self.createEntryExits(self.root_element)
    	for EE in site_service_part:
    	    
    	    # SBB20100405 do this to pull the configuration record
    	    person = EE.fk_participation_to_person
    	    export = person.fk_person_to_export
    	    self.pullConfiguration(export.export_id)
    	
    	    # Reporting Update
    	    self.updateReported(EE)
    	    
    	    self.sysID = EE.id
    	    
    	    entry_exit = self.createEntryExit(entry_exits, EE)

    	if self.options.reported == True:
    	    #Persons = self.session.query(dbobjects.Person).filter(dbobjects.Person.reported == True)
    	    Household = self.session.query(dbobjects.Household).filter(dbobjects.Household.reported == True)
    	elif self.options.unreported == True:
    	    #Persons = self.session.query(dbobjects.Person).filter(or_(dbobjects.Person.reported == False, dbobjects.Person.reported == None))
    	    Household = self.session.query(dbobjects.Household).filter(or_(dbobjects.Household.reported == False, dbobjects.Household.reported == None))
    	elif self.options.reported == None:
    	    #Persons = self.session.query(dbobjects.Person)
    	    Household = self.session.query(dbobjects.Household)
    	else:
    	    pass
    	
    	# setup the date filter also
    	Household = Household.filter(between(dbobjects.Household.household_id_num_date_collected, self.options.startDate, self.options.endDate))
    	
    	if Household <> None and Household.count() > 0:
    	    
    	    # SBB20100310 Households need to be same level as clients with new xml
    	    #households = self.createHouseholds(records)
    	    households = self.createHouseholds(self.root_element)
    	    
    	    for self.eachHouse in Household:
    		
    		# Reporting Update
        		self.updateReported(self.eachHouse)
                
        		Members = self.eachHouse.fk_household_to_members
        		household = self.createHousehold(households)
        		self.customizeHousehold(household)
        		# attach the members (if they exist)
        		if len(Members) > 0:
        		    members = self.createMembers(household)
        		    for eachMember in Members:
            			# need to pull the person record, this can be done via the export record
            			# Reporting Update
            			self.updateReported(eachMember)
            			member = self.createMember(members)
            			#self.customizeMember(member, eachMember, person)
            			self.customizeMember(member, eachMember)
	    
    def createDoc(self):
    	root_element = ET.Element("records")
    	root_element.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    	root_element.attrib["xsi:noNamespaceSchemaLocation"] = "sp.xsd" 
    	root_element.attrib["schema_revision"] = "300_108"
    	root_element.text = "\n"
    	return root_element

    def createClients(self, root_element):
    	clients = ET.SubElement(root_element, "clients")
    	return clients
    
    def createClient(self, clients):
	    client = ET.SubElement(clients, "client")
	    return client
    
    def createEntryExits(self,root_element):
    	entry_exits = ET.SubElement(root_element, "entry_exits")
    	return entry_exits
	     
    def customizeClient(self, client):
    	keyval = 'client'
    	# SBB20071021 changed signature of the generateSysID function.
    	#sysID = self.iDG.generateSysID(keyval)
    	sysID = self.iDG.generateSysID2(keyval, self.sysID)	
    	recID = self.iDG.generateRecID(keyval)
    
    	    
    	client.attrib["record_id"] = recID 
    	#client.attrib["odbid"] = "5"
    	client.attrib["odbid"] = "%s" % self.configurationRec.odbid
    	
    	# SBB20100511 Changing this to be the actual Client ID value
    	#client.attrib["system_id"] = sysID
    	client.attrib["system_id"] = self.person.person_id_unhashed
    	
    	client.attrib["date_added"] = datetime.now().isoformat()
    	client.attrib["date_updated"] = datetime.now().isoformat()
	    
    def customizeClientForEntryExit(self, client):
    	keyval = 'client'
    	# SBB20071021 changed signature of the generateSysID function.
    	#sysID = self.iDG.generateSysID(keyval)
    	sysID = self.iDG.generateSysID2(keyval, self.sysID)	
    	recID = self.iDG.generateRecID(keyval)		
    	client.attrib["record_id"] = recID 
    	#client.attrib["odbid"] = "5"
    	client.attrib["odbid"] = "%s" % self.configurationRec.odbid
    	
    	client.attrib["system_id"] = sysID	
    	client.attrib["date_added"] = datetime.now().isoformat()
    	client.attrib["date_updated"] = datetime.now().isoformat()
    	client.tail = "\n"
	    
	    # SBB20070702 check if self.intakes has none, this is a daily census that is alone
    def customizeClientPersonalIdentifiers(self,client,recordset):
	
    	if recordset.person_legal_first_name_unhashed <> "" and recordset.person_legal_first_name_unhashed <> None:
    	    first_name = ET.SubElement(client, "first_name")
    	    first_name.text = recordset.person_legal_first_name_unhashed
    	
    	if recordset.person_legal_last_name_unhashed <> "" and recordset.person_legal_last_name_unhashed <> None:
    	    last_name = ET.SubElement(client, "last_name")
    	    last_name.text = recordset.person_legal_last_name_unhashed
    	
    	#we don't have the following elements for daily_census only clients, but SvcPt requires them:
    	# I simulated this w/my datasets.  Column names are as in the program
    	if recordset.person_legal_middle_name_unhashed <> "" and recordset.person_legal_middle_name_unhashed <> None:
    	    mi_initial = ET.SubElement(client, "mi_initial")
    	    mi_initial.text = self.fixMiddleInitial(recordset.person_legal_middle_name_unhashed)
    	    
    	# SBB20070831 incoming SSN's are 123456789 and need to be 123-45-6789
    	fixedSSN = self.fixSSN(recordset.person_SSN_unhashed)
    	#ECJ20071111 Omit SSN if it's blank			
    	if fixedSSN <> "" and fixedSSN <> None:	
    	    soc_sec_no = ET.SubElement(client, "soc_sec_no")
    	    soc_sec_no.text = fixedSSN
    	    
    	    #ECJ20071203 We could make the code more complex to determine if partial ssn, but don't know/refused would have to be collected by shelter.
    	    ssn_data_quality = ET.SubElement(client, "ssn_data_quality")
    	    ssn_data_quality.text = "full ssn reported (hud)"
	    

    def customizeClientPersonalIdentifiersForEntryExit(self,client,recordset):
    	#ECJ20100808 I don't think this is used any more, since now we put entry_exit outside the clients tag
        first_name = ET.SubElement(client, "first_name")
    	first_name.text = recordset['First Name']
    	
    	last_name = ET.SubElement(client, "last_name")
    	last_name.text = recordset['Last Name']
    	
    	#we don't have the following elements for daily_census only clients, but SvcPt requires them:
    	# I simulated this w/my datasets.  Column names are as in the program
    	if recordset['MI'] <> "":
    	    mi_initial = ET.SubElement(client, "mi_initial")
    	    mi_initial.text = self.fixMiddleInitial(recordset['MI'])
    	
    	# SBB20070831 incoming SSN's are 123456789 and need to be 123-45-6789
    	fixedSSN = self.fixSSN(recordset['SSN'])	
    	#ECJ20071111 Omit SSN if its blank	
    	if fixedSSN <> "":	
    	    soc_sec_no = ET.SubElement(client, "soc_sec_no")
    	    soc_sec_no.text = fixedSSN
	    

    def createAddress_1(self, dynamiccontent): 
    	address_1 = ET.SubElement(dynamiccontent, "address_1")
    	address_1.attrib["date_added"] = datetime.now().isoformat()
    	return address_1
    
    def createEmergencyContacts(self, dynamiccontent):
    	emergencycontacts = ET.SubElement(dynamiccontent, "emergencycontacts")
    	emergencycontacts.attrib["date_added"] = datetime.now().isoformat()
    	return emergencycontacts
	    
    def customizeEmergencyContacts(self, emergencycontacts):
    	contactsaddress = ET.SubElement(emergencycontacts, "contactsaddress")
    	contactsaddress.attrib["date_added"] = datetime.now().isoformat()
    	contactsaddress.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])		
    	contactsaddress.text = self.intakes['Emergency Address']
    	
    	    
    	contactscity = ET.SubElement(emergencycontacts, "contactscity")
    	contactscity.attrib["date_added"] = datetime.now().isoformat()
    	contactscity.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])									
    	contactscity.text = self.intakes['Emergency City']
    	
    	
    	contactsname = ET.SubElement(emergencycontacts, "contactsname")
    	contactsname.attrib["date_added"] = datetime.now().isoformat()
    	contactsname.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])							
    	contactsname.text = self.intakes['Emergency Contact Name']
    	
    	
    	contactsstate = ET.SubElement(emergencycontacts, "contactsstate")
    	contactsstate.attrib["date_added"] = datetime.now().isoformat()
    	contactsstate.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])									
    	contactsstate.text = self.intakes['Emergency State']
	
	    
    def customizeAddress_1(self, address_1, dbo_address):
    	clientscity = ET.SubElement(address_1, "clientscity")
    	clientscity.attrib["date_added"] = datetime.now().isoformat()
    	clientscity.attrib["date_effective"] = dateutils.fixDate(dbo_address.city_date_collected)
    	clientscity.text = dbo_address.city
    	
    	clientsstate = ET.SubElement(address_1, "clientsstate")
    	clientsstate.attrib["date_added"] = datetime.now().isoformat()
    	clientsstate.attrib["date_effective"] = dateutils.fixDate(dbo_address.state_date_collected)
    	clientsstate.text = dbo_address.state
    	
    	clientszip_1 = ET.SubElement(address_1, "clientszip_1")
    	clientszip_1.attrib["date_added"] = datetime.now().isoformat()
    	clientszip_1.attrib["date_effective"] = dateutils.fixDate(dbo_address.zipcode_date_collected)									
    	clientszip_1.text = dbo_address.zipcode
    
    def createGroupedNeeds(self, base):
    	return ET.SubElement(base, "grouped_needs")
	
    def createNeeds(self, client):
    	needs = ET.SubElement(client, "needs")
    	return needs
    
    def createNeed(self, needs, needData):
    	keyval = 'need'
    	sysID = self.iDG.generateSysID(keyval)
    	
    	#append the need start date to the client's need_id so the need system_ids are unique for each need
    	#since we don't store needs in the database
    	date_for_need_id = needData.need_idid_num
    	#We should have the shelter switch to a 4 digit year, then change the %y to %Y
    	date_object_format = dateutils.fixDate(needData.need_idid_num_date_collected)
    	sysID = sysID + str(date_object_format)
    	recID = self.iDG.generateRecID(keyval)
    	# fixme (need odbid) / is this OK as fixed value or needs to be calculated.
    	#odbid = self.iDG.generateRecID(keyval)
    	
    	
    	need = ET.SubElement(needs, "need")
    	need.attrib["record_id"] = recID 
    	need.attrib["system_id"] = sysID
    	#need.attrib["odbid"] = "5"
    	# SBB20100907 removed from Need.  Not needed.
    	#need.attrib["odbid"] = "%s" % self.configurationRec.odbid
    	
    	need.attrib["date_added"] = datetime.now().isoformat()
    	need.attrib["date_updated"] = datetime.now().isoformat()
    	return need
    
    def customizeNeed(self, need, needData):
  	
    	# Hardwired, don't have this in our Table.
    	provider_id = ET.SubElement(need, "provider_id")
    	provider_id.text = '%s' % self.configurationRec.providerid
    	status = ET.SubElement(need, "status")
        
    	#ECJ20100908 convert HUD_HMIS need status codes to Svcpt4.06 need codes 
        #mapping to Svcpt4.06 from HUD HMIS 2.8: "closed" (2 lapsed and 3 met), "identified" (1 logged), or "in progress"(never mapped to) instead of 1 (logged), 2 (lapsed), 3 (met)
        
        #if settings.DEBUG:    
            #print "needData is: ", needData
            #if needData is not None:
                #print "needData.need_status is: ", needData.need_status
            #else:
                #print "there is no needData"
                #pass
                
        global converted_status
        converted_status = None
        
        if needData.need_status is not None:
            if needData.need_status == "1":
                #if settings.DEBUG:
                    #print "1 converted to identified"
                converted_status = "identified"
            elif needData.need_status == "2":
                #if settings.DEBUG:
                    #print "2 converted to closed"
                converted_status = "closed"
            elif needData.need_status == "3":
                #if settings.DEBUG:
                    #print "3 converted to closed"
                converted_status = "closed"
            else:
                converted_status = None
        if converted_status is not None:
            status.text = converted_status
            
    	code = ET.SubElement(need, "code")
    	code.attrib["type"] = "airs taxonomy"
    	code.text = needData.taxonomy
    	
    	date_set = ET.SubElement(need, "date_set")
    	date_set.text = dateutils.fixDate(needData.need_status_date_collected)
    	
    	# Create these but we don't have data for them (validation)
    	amount = ET.SubElement(need, "amount")
    	amount.text = '0.00'
        
    	outcome = ET.SubElement(need, "outcome")
        #These outcomes can be inferred from need_status: (3 met = "fully met") (2 lapsed = "not met") (1 logged = "service pending")  -->
        converted_outcome = None
        #ECJ20100908 maybe switch this to being an InterpretPicklist 
        if needData.need_status is not None:
            if needData.need_status == "1":
                #if settings.DEBUG:
                    #print "1 converted to service pending"
                converted_outcome = "service pending"
            elif needData.need_status == "2":
                #if settings.DEBUG:
                    #print "2 converted to not met"
                converted_outcome = "not met"
            elif needData.need_status == "3":
                #if settings.DEBUG:
                    #print "3 converted to fully met"
                converted_outcome = "fully met"
            else:
                converted_outcome = None
        if converted_status is not None:
            outcome.text = converted_outcome
        
        #ECJ2010 Comment these out until they are populated
    	#subelement = ET.SubElement(need, "reason_unmet")
    	#subelement = ET.SubElement(need, "family_id")
    	#subelement = ET.SubElement(need, "need_notes")
        
    	# SBB20100520 Modifying this to link the need back to the client.
    	#subelement = ET.SubElement(need, "need_clients")
    	#need_clients = ET.SubElement(need, "need_clients")
    	#self.customizeNeedClients(need_clients)
	
    def customizeNeedClients(self, need_clients):
    	need_client = ET.SubElement(need_clients, "need_client")
    	# SBB20100720 This needs to be a string, not an integer. Converting and formatting the string.
    	need_client.attrib["system_id"] = '%s' % self.person_need.person_id_unhashed
    	#need_client.text = self.person_need.id
    
    #Services in SP406 are like HUD ServiceEvents	
    def createServices(self, need):
    	# services Section
    	services = ET.SubElement(need, "services")
    	return services
 
    #Services in SP408 are like HUD ServiceEvents    
    def createService(self, serviceRecord, services):       
        keyval = 'service'
        #sysID = self.iDG.generateSysID(keyval)
        #sysID = self.iDG.generateSysID2(keyval, self.sysID)    
        recID = self.iDG.generateRecID(keyval)
        service = ET.SubElement(services, "service")
    	service.attrib["record_id"] = recID
    	service.attrib["system_id"] = serviceRecord.service_event_idid_num
    	service.attrib["date_added"] = datetime.now().isoformat()
    	service.attrib["date_updated"] = datetime.now().isoformat()
    	return service
    
    def customizeService(self, serviceRecord, serviceElement):
    	code = ET.SubElement(serviceElement,"code")
    	code.attrib["type"] = "airs taxonomy"
        #Since the needs are always shelter stays, but the codes aren't stated explicity in the csv, these will default to BH-180 
    	#code.text = "BH-180" #token250 type in the schema, not nillable, minOccurs=1
    	code.text = serviceRecord.service_airs_code
        #removed since minOccurs=0 
        #referto_provider_id = ET.SubElement(service, "referto_provider_id")
        #referto_provider_id.text = "provider1"
        #removed since minOccurs=0 and not in CSV
        #refer_date = ET.SubElement(service, "refer_date")
        service_provided = ET.SubElement(serviceElement, "service_provided")
    	service_provided.text = "true"
    	provide_provider_id = ET.SubElement(serviceElement, "provide_provider_id")
    	provide_provider_id.text = "14" 
        #This needs to be populated with  daily census.csv data using the date field from that file 
    	provide_start_date = ET.SubElement(serviceElement, "provide_start_date")
        service_period_start_date = dateutils.fixDate(serviceRecord.service_period_start_date)
        provide_start_date.text = service_period_start_date
    	provide_end_date = ET.SubElement(serviceElement, "provide_end_date")
        service_period_end_date = dateutils.fixDate(serviceRecord.service_period_end_date)
        provide_end_date.text = service_period_end_date
        provider_specific_service_code = ET.SubElement(serviceElement, "provider_specific_service_code")
        provider_specific_service_code.text = serviceRecord.type_of_service
        #add one day to the provide start date to arrive at the end date
        #one_day_difference = timedelta(days=1)
        #start_date_datetime_object_format = dateutils.getDateTimeObj(orig_format)
        #end_date_datetime_object_format = start_date_datetime_object_format + one_day_difference
        #provide_end_date.text = end_date_datetime_object_format.isoformat()
        
    def createGoals(self, client):
    	# goals Section
    	goals = ET.SubElement(client, "goals")
    	
    	return goals
        
    def createGoal(self, goals):
    	keyval = 'goal'
    	sysID = self.iDG.generateSysID(keyval)
    	recID = self.iDG.generateRecID(keyval)		
    	goal = ET.SubElement(goals, "goal")
    	
    	goal.attrib["record_id"] = recID
    	goal.attrib["system_id"] = sysID		
    	goal.attrib["date_added"] = datetime.now().isoformat()
    	goal.attrib["date_updated"] = datetime.now().isoformat()	
    	return goal
        
    def customizeGoal(self, goal):
    	provider_id = ET.SubElement(goal, "provider_id")
    	date_set = ET.SubElement(goal, "date_set")
    	classification = ET.SubElement(goal, "classification")
    	Type = ET.SubElement(goal, "type")
    	Type.text = "goaltypePickOption"
    	status = ET.SubElement(goal, "status")
    	target_date = ET.SubElement(goal, "target_date")
    	outcome = ET.SubElement(goal, "outcome")
    	outcome_date = ET.SubElement(goal, "outcome_date")
    	projected_followup_date = ET.SubElement(goal, "projected_followup_date")
    	followup_made = ET.SubElement(goal, "followup_made")
    	actual_followup_date = ET.SubElement(goal, "actual_followup_date")
    	followup_outcome = ET.SubElement(goal, "followup_outcome")
    	    
    def createAction_steps(self, goal):
    	action_steps = ET.SubElement(goal, "action_steps")
    	return action_steps
    
    def createAction_step(self, action_steps):
    	keyval = 'action_step'
    	sysID = self.iDG.generateSysID(keyval)
    	recID = self.iDG.generateRecID(keyval)		
    	action_step = ET.SubElement(action_steps, "action_step")
    	action_step.attrib["record_id"] = recID
    	action_step.attrib["system_id"] = sysID
    	action_step.attrib["date_added"] = datetime.now().isoformat()
    	action_step.attrib["date_updated"] = datetime.now().isoformat()
    	return action_step
	    
    def customizeAction_step(self, action_step):
    	provider_id = ET.SubElement(action_step, "provider_id")
    	provider_id.text = '%s' % self.configurationRec.providerid
    	date_set = ET.SubElement(action_step, "date_set")
    	description = ET.SubElement(action_step, "description")
    	description.text = "Will take 4k of text (4096 chars). Formatting is preserved."
    	status = ET.SubElement(action_step, "status")
    	target_date = ET.SubElement(action_step, "target_date")
    	outcome = ET.SubElement(action_step, "outcome")
    	outcome_date = ET.SubElement(action_step, "outcome_date")
    	projected_followup_date = ET.SubElement(action_step, "projected_followup_date")
    	followup_made = ET.SubElement(action_step, "followup_made")
    	followup_made.text = "true"
    	actual_followup_date = ET.SubElement(action_step, "actual_followup_date")
    	followup_outcome = ET.SubElement(action_step, "followup_outcome")
    	
    def customizeHousehold(self, household):
    	# SBB20100407 Filling with other for now, since we can't ascertain this value from the data that we currently have
    	Type = ET.SubElement(household, "type")
    	Type.text = "other" #this needs to be made dynamic
    	
    #	            <xsd:enumeration value="couple with no children"/>
    #                    <xsd:enumeration value="female single parent"/>
    #                    <xsd:enumeration value="foster parent(s)"/>
    #                    <xsd:enumeration value="grandparent(s) and child"/>
    #                    <xsd:enumeration value="male single parent"/>
    #                    <xsd:enumeration value="non-custodial caregiver(s)"/>
    #                    <xsd:enumeration value="other"/>
    #                    <xsd:enumeration value="two parent family"/>
    
    	name = ET.SubElement(household, "name")
    	name.text = "tok100Type"
    
        
    def createEntryExit(self, entry_exits, EE):
    	keyval = 'entry_exit'
    	sysID = self.iDG.generateSysID(keyval)
    	#append the entry_exit start date to the client's entry_exit_id so the entry_exit system_ids are unique for each entry_exit
    	#since we don't store entry_exits in the database
    	date_for_entry_exit_id = EE.participation_dates_start_date
    	#We should have the shelter switch to a 4 digit year, then change the %y to %Y
    	entry_exit_date_object_format = dateutils.fixDate(date_for_entry_exit_id)
    	sysID = sysID + str(entry_exit_date_object_format)
    	recID = self.iDG.generateRecID(keyval)
    	entry_exit = ET.SubElement(entry_exits, "entry_exit")
    	
    	# SBB20100225 Removing this, not allowed for Service Point (SP) validation
    	#entry_exit.attrib["odbid"] = "5"
    	entry_exit.attrib["record_id"] = recID
    	entry_exit.attrib["system_id"] = sysID
    	# SBB20100311 EE needs this, it's required.
    	#entry_exit.attrib["odbid"] = "5"
    	entry_exit.attrib["odbid"] = "%s" % self.configurationRec.odbid
    	
    	entry_exit.attrib["date_added"] = datetime.now().isoformat()
    	entry_exit.attrib["date_updated"] = datetime.now().isoformat()
    	
    	self.customizeEntryExit(entry_exit, EE)
    	#self.createEntryExitMember(entry_exit)
    	return entry_exit
    
    def createEntryExitMember(self,entry_exit):
    	keyval = 'member'
    	sysID = self.iDG.generateSysID2(keyval,self.sysID)
    	recID = self.iDG.generateRecID(keyval)
    	members = ET.SubElement(entry_exit, "members")
    	
    	member = ET.SubElement(members, "member")
    	member.attrib["record_id"] = recID
    	member.attrib["system_id"] = sysID	
    	member.attrib["date_added"] = datetime.now().isoformat()
    	member.attrib["date_updated"] = datetime.now().isoformat()
    	
    	# ECJ20071114: Here we have to use the exact system ID for this client from the database, 
    	#and has to match the same one used in any client records above for this person, 
    	#0r else this entry_exit won't show up under the correct client record.
    	client_id = ET.SubElement(member,"client_id")
    	keyval = "client"
    	client_id.text = self.iDG.generateSysID2(keyval,self.sysID)
    
    	if dateutils.fixDate(self.outcom['Exit Date']) is not None:
    		exit_date = ET.SubElement(member, "exit_date")
    		exit_date.text = dateutils.fixDate(self.outcom['Exit Date'])
    		#reason_leaving = ET.SubElement(member, "reason_leaving")
    		#reason_leaving.text = self.pickList.getValue("EereasonLeavingPick", self.outcom['Code'])
    		#reason_leaving_other = ET.SubElement(entry_exit, "reason_leaving_other")
    	if self.pickList.getValue("EeDestinationPick", str.rstrip(self.outcom['Service Point Destnation Parse'])) <> "":
    		destination = ET.SubElement(member, "destination")
    		destination.text = self.pickList.getValue("EeDestinationPick", str.rstrip(self.outcom['Service Point Destnation Parse']))
    	
    	if self.outcom['Address'] <> "" and\
    	    self.outcom['Client ID'] <> "" and\
    	    self.outcom['Education'] <> "" and\
    	    self.outcom['Partner'] <> "":
    	    notes = ET.SubElement(member, "notes")
    	    notes.text = self.formatNotesField(notes.text, 'Address', self.outcom['Address'])
    	    # SBB20070702 Add debugging  to the notes field.  NOTICE: for Production run, Make sure the debug switch is off or notes will be populated with junk data.
    	    if settings.DEBUG:
    		notes.text = self.formatNotesField(notes.text, 'Client ID:', self.outcom['Client ID'])	
    	    # adding education and partner to the notes field
    	    notes.text = self.formatNotesField(notes.text, 'Education', self.outcom['Education'])
    	    notes.text = self.formatNotesField(notes.text, 'Partner', self.outcom['Partner'])
    	
    	# destination_other = ET.SubElement(member, "destination_other")

    def customizeEntryExit(self, entry_exit, EE):
    	type = ET.SubElement(entry_exit, "type")
    	type.text = "hud-40118"
    	
    	provider_id = ET.SubElement(entry_exit, "provider_id")
    	provider_id.text = '%s' % self.configurationRec.providerid
    	
    	if EE.participation_dates_start_date <> "" and EE.participation_dates_start_date <> None:
    	    entry_date = ET.SubElement(entry_exit, "entry_date")
    	    entry_date.text = dateutils.fixDate(EE.participation_dates_start_date)
    	    
    	# SBB20100518 moved from section below (apparently bowman doesn't like this.  Although it validates)
    	# SBB20100520 removed this, not validating
    	#if EE.participation_dates_end_date <> "" and EE.participation_dates_end_date <> None:
    	#    exit_date = ET.SubElement(entry_exit, "exit_date")
    	#    exit_date.text = dateutils.fixDate(EE.participation_dates_end_date)
    	    
    	    # now grab the PersonID from Participation
    	    EEperson = EE.fk_site_svc_part_to_person
    	    
    	    # This creates the subelement for members under Entry Exits.
    	    mbrs = self.createMembers(entry_exit)
    	    
    	    # SBB20100315 From there grab the PersonIDunhashed and try to use that to pull the members,
    	    # DEBUG this to figure out why we are failing to make mbr 
    	    if EEperson.person_id_unhashed <> None:				# and EEperson.person_id_hashed <> None:
    		mbr = self.createMemberEE(mbrs)
    		# SBB20100407 FIXME - Person is not a member, how do I correct this?
    		self.customizeMemberEE(mbr, EE, EEperson)
    		
    	    # Hold off on this for the moment.  Just use Members.
    	    # from there grab the HouseHoldID and try to pull the Household record
    	    # These get stuffed into the EntryExit Record
	    
    def createInfo_releases(self, client):
    	# info_releases Section
    	info_releases = ET.SubElement(client, "info_releases")
    
    	return info_releases
        
    def createInfo_release(self, info_releases):
    	keyval = 'info_release'
    	sysID = self.iDG.generateSysID(keyval)
    	recID = self.iDG.generateRecID(keyval)
    	
    	info_release = ET.SubElement(info_releases, "info_release")
    	
    	#info_release.attrib["record_id"] = "ROI1"
    	info_release.attrib["record_id"] = recID
    	#info_release.attrib["system_id"] = "roi1243a"
    	info_release.attrib["system_id"] = sysID
    	
    	info_release.attrib["date_added"] = datetime.now().isoformat()
    	info_release.attrib["date_updated"] = datetime.now().isoformat()
    	return info_release
    	    
    def customizeInfo_release(self, info_release):
    	# self.IR
    	provider_id = ET.SubElement(info_release, "provider_id")
    	provider_id.text = '%s' % self.configurationRec.providerid
    	date_started = ET.SubElement(info_release, "date_started")
    	date_started.text = self.IR.start_date
    	date_ended = ET.SubElement(info_release, "date_ended")
    	date_ended.text = self.IR.end_date
    	permission = ET.SubElement(info_release, "permission")
    	permission.text = self.IR.release_granted
    	documentation = ET.SubElement(info_release, "documentation")
    	documentation.text = self.pickList.getValue("ROIDocumentationPickOption", str(self.IR.documentation))
    	witness = ET.SubElement(info_release, "witness")
    	witness.text = "tok50Type"
    	    
    def createDynamicContent(self, client):
    	# dynamic content section (installation-specific fields)
    	dynamic_content = ET.SubElement(client, "dynamic_content")
    	return dynamic_content

    def customizeDynamicContent(self, dynamiccontent):
    
    	for ph in self.ph:
    	    
    	    # Reporting Update
    	    self.updateReported(ph)
    	    
    	    dbo_address = ph.fk_person_historical_to_person_address
    	    dbo_veteran = ph.fk_person_historical_to_veteran
    	    
    	    # Is client homeless?
    	    if ph.hud_homeless <> "" and ph.hud_homeless <> None:
    		isclienthomeless = ET.SubElement(dynamiccontent, "isclienthomeless")
    		isclienthomeless.attrib["date_added"] = datetime.now().isoformat()
    		isclienthomeless.attrib["date_effective"] = dateutils.fixDate(ph.hud_homeless_date_collected)
    		if ph.hud_homeless == '1':
    			isclienthomeless.text = 'true'
    		if ph.hud_homeless == '' or ph.hud_homeless == None:
    			isclienthomeless.text = 'false'
    	
    	    if ph.physical_disability <> "" and ph.physical_disability <> None:
    		hud_disablingcondition = ET.SubElement(dynamiccontent, "hud_disablingcondition")
    		hud_disablingcondition.attrib["date_added"] = datetime.now().isoformat()
    		hud_disablingcondition.attrib["date_effective"] = dateutils.fixDate(ph.physical_disability_date_collected)
    		hud_disablingcondition.text = self.pickList.getValue("ENHANCEDYESNOPickOption",str.strip(ph.physical_disability.upper()))
    	
    	    if ph.hours_worked_last_week <> "" and ph.hours_worked_last_week <> None:
    		hud_hrsworkedlastweek = ET.SubElement(dynamiccontent, 'hud_hrsworkedlastweek')
    		hud_hrsworkedlastweek.attrib["date_added"] = datetime.now().isoformat()
    		hud_hrsworkedlastweek.attrib["date_effective"] = dateutils.fixDate(ph.hours_worked_last_week_date_collected)
    		hud_hrsworkedlastweek.text = str.strip(ph.hours_worked_last_week)
    	
    	# FIXME (when provided solution)
    	#    # Are you prescribed any medications?		
    	#    if self.intakes['PrescriptionMeds'] <> "":
    	#	areyouprescribedanyme = ET.SubElement(dynamiccontent,"areyouprescribedanyme")
    	#	areyouprescribedanyme.text = self.intakes['PrescriptionMeds'].lower()
    	#	areyouprescribedanyme.attrib["date_added"] = datetime.now().isoformat()
    	#	areyouprescribedanyme.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])
    	
    	#    # Is your illness life threatening?
    	#    # hivaids_status
    	#    if self.intakes['LifeThreatening'].lower() <> "":
    	#	isyourillnesslifethre = ET.SubElement(dynamiccontent,"isyourillnesslifethre")
    	#	isyourillnesslifethre.text = self.intakes['LifeThreatening'].lower()
    	#	isyourillnesslifethre.attrib["date_added"] = datetime.now().isoformat()
    	#	isyourillnesslifethre.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])   
    	    
    	    # Zip Code
    	    zipcode = ""
            if len(dbo_address) > 0:			# we have addresses
                if dbo_address[0].zip_quality_code == 1:
                    zipcode = dbo_address[0].zipcode
                    if zipcode <> "" and zipcode <> None:
                        hud_zipcodelastpermaddr = ET.SubElement(dynamiccontent, "hud_zipcodelastpermaddr")
                        hud_zipcodelastpermaddr.attrib["date_added"] = datetime.now().isoformat()
                        hud_zipcodelastpermaddr.attrib["date_effective"] = dateutils.fixDate(dbo_address[0].zipcode_date_collected)
                        hud_zipcodelastpermaddr.text = zipcode
    		
    	    if len(dbo_address) > 0:
        		if dbo_address[0].line1 <> "":
        		    
        		    # Reporting Update
        		    self.updateReported(dbo_address[0])
        		    
        		    address_2 = ET.SubElement(dynamiccontent,"address_2")
        		    address_2.attrib["date_added"] = datetime.now().isoformat()
        		    address_2.attrib["date_effective"] = dateutils.fixDate(dbo_address[0].line1_date_collected)
        		    address_2.text = dbo_address[0].line1
        	
            #if self.intakes['USCitizen'].lower() <> "":
            	#uscitizen = ET.SubElement(dynamiccontent,"uscitizen")
            	#uscitizen.text = self.intakes['USCitizen'].lower()
            	#uscitizen.attrib["date_added"] = datetime.now().isoformat()
            	#uscitizen.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])
    	
    	    # already a True and False just lower the value to make it compliant
    	    if str(ph.substance_abuse_problem) <> "" and ph.substance_abuse_problem <> None:
        		usealcoholordrugs = ET.SubElement(dynamiccontent,"usealcoholordrugs")
        		usealcoholordrugs.attrib["date_added"] = datetime.now().isoformat()
        		usealcoholordrugs.attrib["date_effective"] = dateutils.fixDate(ph.substance_abuse_problem_date_collected)
        		usealcoholordrugs.text = 'true'
        	
    	    # Multiple occurences of Site Service Particpation, Only need to flag vet status once?
    	    if len(self.site_service_part) > 0:
        		for ssp in self.site_service_part:
        		    
        		    # Reporting Update
        		    self.updateReported(ssp)
        		    
        		    vet = ssp.veteran_status
        		    
        		    if vet <> "" and vet <> None:
            			veteran = ET.SubElement(dynamiccontent,"veteran")
            			veteran.text = self.pickList.getValue("ENHANCEDYESNOPickOption", str(vet))
            			veteran.attrib["date_added"] = datetime.now().isoformat()
            			veteran.attrib["date_effective"] = dateutils.fixDate(ssp.veteran_status_date_collected)
            			break
    		
    	    if len(dbo_veteran) > 0:
        		hud_militarybranchinfo = None
        		for dbv in dbo_veteran:
    		    
    		    # Reporting Update
        		    self.updateReported(dbv)
        		    branch = dbv.military_branch
        		    if str(branch) <> "" and dbv.military_branch <> None:
    			
            			if hud_militarybranchinfo == None:
            			    hud_militarybranchinfo = ET.SubElement(dynamiccontent,"hud_militarybranchinfo")
            			    hud_militarybranchinfo.attrib["date_added"] = datetime.now().isoformat()
                            militarybranch = ET.SubElement(hud_militarybranchinfo,"militarybranch")
                            militarybranch.attrib["date_added"] = datetime.now().isoformat()
                            militarybranch.attrib["date_effective"] = dateutils.fixDate(dbv.military_branch_date_collected)						
                            militarybranch.text = self.pickList.getValue("MILITARYBRANCHPickOption",str(branch))
    			
    			#if self.convertIntegerToDate(self.intakes['EntranceDate']) <> None:
    			#    hud_militarybranchins = ET.SubElement(hud_militarybranchinfo,"hud_militarybranchins")
    			#    hud_militarybranchins.attrib["date_added"] = datetime.now().isoformat()
    			#    hud_militarybranchins.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])			
    			#    hud_militarybranchins.text = self.convertIntegerToDateTime(self.intakes['EntranceDate'])
    			#
    			#if self.convertIntegerToDate(self.intakes['DischargeDate']) <> None:
    			#    hud_militarybranchinend = ET.SubElement(hud_militarybranchinfo,"hud_militarybranchinend")
    			#    hud_militarybranchinend.attrib["date_added"] = datetime.now().isoformat()
    			#    hud_militarybranchinend.attrib["date_effective"] = dateutils.fixDate(self.intakes['IntakeDate'])			
    			#    hud_militarybranchinend.text = self.convertIntegerToDateTime(self.intakes['DischargeDate'])
    	
    	    #	casecounselor = ET.SubElement(dynamiccontent,"casecounselor")
    	    #	casecounselor.text = self.outcom['Staff']
        
    		
    	    
    	    # primary reason homeless: define/populate it if you have values
        
    	    
    	    # build a list of the values that need to be populated ( space separated list of values )
    	    # then at the end eval the length of the list, if > 0 then join the values into a string
    	    # and assign it to the value [primaryreasonforhomle.text]
    	    
    	    homelessPickOption = []
    	    lookups = [
    	    'Addiction',
    	    'Divorce',
    	    'Domestic Violence',
    	    'Evicted within past week',
    	    'Family-Personal Illness',
    	    'Jail/Prison',
    	    'Moved to seek work',
    	    'Physical-Mental Disability',
    	    'Unable to pay rent-mortgage',
    	    'Other'
    	    ]
    	    
    	    # ECJ20071121 There can only be one primary reason for homelessness, so if they records show more than one set as true, discard all but one.
    	    # I'd rather they just populated "PrimeReason"
        
    	    if str(ph.hud_homeless) <> '' and ph.hud_homeless <> None:
        		primaryreasonforhomle = ET.SubElement(dynamiccontent,"primaryreasonforhomle")
        		primaryreasonforhomle.attrib["date_added"] = datetime.now().isoformat()
        		primaryreasonforhomle.attrib["date_effective"] = dateutils.fixDate(ph.hud_homeless_date_collected)
        		#ECJ20071121 We can only have one primary reason, so discard all but the first
        		#primaryreasonforhomle.text = ' ' + ' '.join(homelessPickOption) + ' '
        		primaryreasonforhomle.text = 'Other'
    	    
    	    #ECJ 20071111 nothing is populated here for incomesource
    	    #incomesource = ET.SubElement(dynamiccontent,"incomesource")
    	    # would need a .text entry here
    	    #incomesource.tail = '\n'
    	    
    	    if len(dbo_address) > 0:
    		if dbo_address[0].line1 <> "":
    		#if self.intakes['ResidentialCity'] <> "" and self.intakes['ResidentialState'] <> "":
    		    address_1 = self.createAddress_1(dynamiccontent)
    		    self.customizeAddress_1(address_1, dbo_address[0])
    		    
    		if str(dbo_address[0].zipcode) <> "" and not dbo_address[0].zipcode == None:
    		    address_1 = self.createAddress_1(dynamiccontent)
    		    self.customizeAddress_1(address_1, dbo_address[0])	
    	
    	#    if self.intakes['Emergency Address'] <> "":
    	#	emergencycontacts = self.createEmergencyContacts(dynamiccontent)
    	#	self.customizeEmergencyContacts(emergencycontacts)
    	    
        if str(ph.currently_employed) <> "" and not ph.currently_employed == None:
            unemployed = ET.SubElement(dynamiccontent, 'unemployed')
            unemployed.attrib["date_added"] = datetime.now().isoformat()
            unemployed.attrib["date_effective"] = dateutils.fixDate(ph.currently_employed_date_collected)						

            if ph.currently_employed == 1:
                unemployed.text = "true"
            else:
                unemployed.text = "false"
        	
    	    #This is an assumption that monthly wage = one employer's wage
	    if str(ph.total_income) <> "" and not ph.total_income == None:
    		monthlyincome = ET.SubElement(dynamiccontent, 'hud_totalmonthlyincome')
    		monthlyincome.attrib["date_added"] = datetime.now().isoformat()
    		monthlyincome.attrib["date_effective"] = dateutils.fixDate(ph.total_income_date_collected)
    		monthlyincome.text = ph.total_income
    	#	workhistory = self.createWorkhistory(dynamiccontent)
    	#	self.customizeWorkhistory(workhistory)

	    if str(ph.physical_disability) <> "" and not ph.physical_disability == None:
    		disabilities_1 = ET.SubElement(dynamiccontent,"disabilities_1")
    		disabilities_1.attrib["date_added"] = datetime.now().isoformat()			
    		self.customizeDisabilities_1(disabilities_1, ph)
    		
    	# Moved these outside the PH Loop, so they don't repeat.  This info comes from person and not personhistorical
    	if self.person.person_gender_unhashed <> "" and self.person.person_gender_unhashed <> None:
    	    svpprofgender = ET.SubElement(dynamiccontent, "svpprofgender")            
    	    svpprofgender.attrib["date_added"] = datetime.now().isoformat()
    	    svpprofgender.attrib["date_effective"] = dateutils.fixDate(self.person.person_gender_date_collected)
    	    svpprofgender.text = self.pickList.getValue("SexPick",self.person.person_gender_unhashed)
    
    	# dob (Date of Birth)        
    	if self.person.person_date_of_birth_unhashed <> "" and self.person.person_date_of_birth_unhashed <> None:
    	    svpprofdob = ET.SubElement(dynamiccontent, "svpprofdob")
    	    svpprofdob.attrib["date_added"] = datetime.now().isoformat()
            #print "self.person.person_date_of_birth_date_collected", self.person.person_date_of_birth_date_collected
    	    svpprofdob.attrib["date_effective"] = dateutils.fixDate(self.person.person_date_of_birth_date_collected)
    	    svpprofdob.text = dateutils.fixDate(self.person.person_date_of_birth_unhashed)

    	if len(self.race) > 0:
    	    race = self.race[0].race_unhashed
    	
    	    # Reporting Update
    	    self.updateReported(self.race[0])
    		    
    	    if race <> "" and race <> None:
    		if self.pickList.getValue("RacePick",str(race)) <> "":
    		    svpprofrace = ET.SubElement(dynamiccontent, "svpprofrace")
    		    svpprofrace.attrib["date_added"] = datetime.now().isoformat()
    		    svpprofrace.attrib["date_effective"] = dateutils.fixDate(self.race[0].race_date_collected)						
    		    svpprofrace.text = self.pickList.getValue("RacePick",str(race))
    		    
        #Ethnicity Handling
    	ethnicity = self.person.person_ethnicity_unhashed
    	if ethnicity <> "" and ethnicity <> None:
    	    svpprofeth = ET.SubElement(dynamiccontent, "svpprofeth")
    	    svpprofeth.attrib["date_added"] = datetime.now().isoformat()
    	    svpprofeth.attrib["date_effective"] = dateutils.fixDate(self.person.person_ethnicity_date_collected)
    	    svpprofeth.text = self.pickList.getValue("EthnicityPick", str(ethnicity))

        #Prior Living Situation Handling
        
        #print "ph has:", ph
        priorresidence = ph.prior_residence
        #print "ph.prior_residence", ph.prior_residence
        if priorresidence <> "" and priorresidence <> None:
            typeoflivingsituation = ET.SubElement(dynamiccontent, "typeoflivingsituation")
            typeoflivingsituation.attrib["date_added"] = datetime.now().isoformat()
            typeoflivingsituation.attrib["date_effective"] = dateutils.fixDate(ph.prior_residence_date_collected)
            typeoflivingsituation.text = self.pickList.getValue("LIVINGSITTYPESPickOption", str(priorresidence))
            #print "typeoflivingsituation.text:", typeoflivingsituation.text
        #	def create6monthtrackinginforma(self, dynamiccontent):
        #		# SBB20070626 Converting name from 6month to sixmonth this XML is not validating..
        #		#Sixmonthtrackinginforma = ET.SubElement(dynamiccontent,"6monthtrackinginforma")
        #		Sixmonthtrackinginforma = ET.SubElement(dynamiccontent,"Sixmonthtrackinginforma")
        #		Sixmonthtrackinginforma.text = "\n"
        #		return Sixmonthtrackinginforma
    	
    	#def customize6monthtrackinginforma(self, Sixmonthtrackinginforma):
        
    def customizeDisabilities_1(self, disabilities_1, ph):
    	#if self.intakes['DisabilityDiscription'] <> "":
    	noteondisability = ET.SubElement(disabilities_1,'noteondisability')
    	noteondisability.attrib["date_added"] = datetime.now().isoformat()
    	noteondisability.attrib["date_effective"] = dateutils.fixDate(ph.physical_disability_date_collected)
    	noteondisability.text = ph.physical_disability
        
    def createWorkhistory(self, dynamiccontent):
    	workhistory = ET.SubElement(dynamiccontent, "workhistory")
    	workhistory.attrib["date_added"] = datetime.now().isoformat()
    	return workhistory
    	    
    def customizeWorkhistory(self, workhistory):	
    	if self.intakes['EmployerName'] <> "":
    	    employername = ET.SubElement(workhistory, 'employername')
    	    buildWorkhistoryAttributes(employername)
    	    employername.text = self.intakes['EmployerName']
    
    #		employersaddress = ET.SubElement(workhistory, 'employersaddress')
    #		buildWorkhistoryAttributes(employersaddress)
    #		employerscity = ET.SubElement(workhistory, 'employerscity')
    #		buildWorkhistoryAttributes(employerscity) 
    #		employersstate = ET.SubElement(workhistory, 'employersstate')
    #		buildWorkhistoryAttributes(employersstate)
    #		employerszip = ET.SubElement(workhistory, 'employerszip')
    #		buildWorkhistoryAttributes(employerszip)
    #		employersphonenumber = ET.SubElement(workhistory, 'employersphonenumber')
    #		buildWorkhistoryAttributes(employersphonenumber)
    	    
    def createHouseholds(self, records):
    	# households section
    	households = ET.SubElement(records, "households")
    
    	return households
        
    def createHousehold(self, households):
    	keyval = 'household'
    	sysID = self.iDG.generateSysID(keyval)
    	recID = self.iDG.generateRecID(keyval)
    	
    	household = ET.SubElement(households, "household")
    
    	# assign household attributes
    	#household.attrib["record_id"] = "ROI1"
    	household.attrib["record_id"] = recID
    	#household.attrib["system_id"] = "roi1243a"
    	household.attrib["system_id"] = sysID
    	
    	household.attrib["date_added"] = datetime.now().isoformat()
    	household.attrib["date_updated"] = datetime.now().isoformat()
    	return household
    	    
    def createMembers(self, household):
    	members = ET.SubElement(household, "members")

    	return members
    
    def createMember(self, members):
    	keyval = 'member'
    	#sysID = self.iDG.generateSysID(keyval)
    	recID = self.iDG.generateRecID(keyval)
    	
    	member = ET.SubElement(members, "member")
    
    	# assign household attributes
    	#member.attrib["record_id"] = "ROI1"
    	member.attrib["record_id"] = recID
    	member.attrib["date_added"] = datetime.now().isoformat()
    	member.attrib["date_updated"] = datetime.now().isoformat()
    	member.attrib["system_id"] = self.iDG.generateSysID2('service', self.sysID)
    	
    	return member
        
    def createMemberEE(self, members):
    	member = ET.SubElement(members, "member")
    	
    	keyval = 'member'
    	#sysID = self.iDG.generateSysID(keyval)
    	recID = self.iDG.generateRecID(keyval)
    	
    	# assign household attributes
    	member.attrib["record_id"] = recID
    	member.attrib["date_added"] = datetime.now().isoformat()
    	member.attrib["date_updated"] = datetime.now().isoformat()
    	member.attrib["system_id"] = self.iDG.generateSysID2('service', self.sysID)
    	
    	return member
        
    def customizeMember(self, member_element, member):
    	client_id = ET.SubElement(member_element, "client_id")
    	# or Hashed?
    	
    	if member.person_id_unhashed != "":
    	    client_id.text = member.person_id_unhashed
    	
    	    date_entered = ET.SubElement(member_element, "date_entered")
    	    date_entered.text = dateutils.fixDate(member.person_id_unhashed_date_collected)
    	else:
    	    client_id.text = member.person_id_hashed
    	
    	    date_entered = ET.SubElement(member_element, "date_entered")
    	    date_entered.text = dateutils.fixDate(member.person_id_hashed_date_collected)
    	
    	# This field is nillable
    	#date_ended = ET.SubElement(member_element, "date_ended")
    	#date_ended.text = ""
    	
    	if member.relationship_to_head_of_household == "":
    	    head_of_household = ET.SubElement(member_element, "head_of_household")
    	    head_of_household.text = "true"
    	else:
    	    # This uses the picklist option to translate from HMIS to SvcPoint.		
    	    relationship = ET.SubElement(member_element, "relationship")
    	    relationship.text = self.pickList.getValue("RelationshipToHeadOfHousehold", str(member.relationship_to_head_of_household))
            
    #    def customizeMember(self, member, EEActivity, memberID):
    #	client_id = ET.SubElement(member, "client_id")
    #	# or Hashed?
    #	client_id.text = memberID 							# eachMember.person_id_unhashed
    #
    #	#date_entered = ET.SubElement(member, "date_entered")
    #	#date_entered.text = dateutils.fixDate(eachMember.person_id_unhashed_date_collected)
    #	
    #	# SBB20100315 Fixing EE to include member information
    #	entry_date = ET.SubElement(member, "entry_date")
    #	entry_date.text = dateutils.fixDate(EEActivity.participation_dates_start_date)
    #	
    #	# exit_date
    #	exit_date = ET.SubElement(member, "exit_date")
    #	exit_date.text = dateutils.fixDate(EEActivity.participation_dates_end_date)
    #	
    #	#reason_leaving= ET.SubElement(member, "reason_leaving")
    #	#reason_leaving.text = "reason_leaving"
    #	
    #	#reason_leaving_other= ET.SubElement(member, "reason_leaving_other")
    #	#reason_leaving_other.text = "reason_leaving_other"
    #	
    #	destination= ET.SubElement(member, "destination")
    #	destination.text = EEActivity.destination
    #	
    #	destination_other= ET.SubElement(member, "destination_other")
    #	destination_other.text = EEActivity.destination_other
    #	
    #	#notes= ET.SubElement(member, "notes")
    #	#notes.text = "notes"
    #	
    #	tenure= ET.SubElement(member, "tenure")
    #	tenure.text = EEActivity.destination_tenure
    #	
    #	#subsidy= ET.SubElement(member, "subsidy")
    #	#subsidy.text = "subsidy"
    #	
    #	# We don't have this?
    #	#date_ended = ET.SubElement(member, "date_ended")
    #	    
    #	    # wrap it in an ElementTree instance, and save as XML

    def customizeMemberEE(self, EEMember_element, site_service_participation, member):
    	client_id = ET.SubElement(EEMember_element, "client_id")
    	
    	if member.person_id_unhashed != "":
    	    client_id.text = member.person_id_unhashed
    	else:
    	    client_id.text = member.person_id_hashed
    	
    	# SBB20100518 Removing this apparently BIS doesn't like this (even though it validates)
    	# SBB20100520 Adding this back in.
    	entry_date = ET.SubElement(EEMember_element, "entry_date")
    	entry_date.text = dateutils.fixDate(site_service_participation.participation_dates_start_date)
    	exit_date = ET.SubElement(EEMember_element, "exit_date")
    	exit_date.text = dateutils.fixDate(site_service_participation.participation_dates_end_date)
    	
    	reason_leaving = ET.SubElement(EEMember_element, "reason_leaving")
    	reason_leaving.text = ''
    	
    	reason_leaving_other = ET.SubElement(EEMember_element, "reason_leaving_other")
    	reason_leaving_other.text = ''
    	
    	destination = ET.SubElement(EEMember_element, "destination")
    	destination.text = site_service_participation.destination
    	
    	destination_other = ET.SubElement(EEMember_element, "destination_other")
    	destination_other.text = site_service_participation.destination_other
    	
    	notes = ET.SubElement(EEMember_element, "notes")
    	notes.text = ''
    	
    	tenure = ET.SubElement(EEMember_element, "tenure")
    	tenure.text = site_service_participation.destination_tenure
    	
    	subsidy = ET.SubElement(EEMember_element, "subsidy")
    	subsidy.text = ''
    	
    	
    	# qs_(name goes here) is a naming convention that designates that the 
    	# result of the lookup is a queryset object.  Python List/Dictionary object)
    	
    	#qs_Sourcedatabase = self.select_SourceDatabase(keyval)
    	# first the Sourcedatabase object
    	    
	def current_picture(node):
	    ''' Internal function.  Debugging aid for the export module.'''
	    if settings.DEBUG:
		print "Current XML Picture is"
		print "======================\n" * 2
		dump(node)
		print "======================\n" * 2
 
    def formatNotesField(self, existingNotesData, formatName, newNotesData):
    	if existingNotesData == None:
    	    existingNotesData = ""
    	    formatData = ""
    	else:
    	    formatData = "\r\n"
    	if newNotesData != 'None':
    	    newData = "%s %s [%s] %s" % (existingNotesData, formatData, formatName, newNotesData)
    	else:
    	    newData = existingNotesData
    	#print newData
    	return newData
         
    def calcHourlyWage(self, monthlyWage):
    	if monthlyWage <> "":
    	    if monthlyWage.strip().isdigit():
    		if float(monthlyWage) > 5000.00:
    		    hourlyWage = float(monthlyWage) / 160.00
    		else:
    		    hourlyWage = float(monthlyWage)
    	    else:
    		hourlyWage = 0.00
    	else:
    	    hourlyWage = 0.00
    		
    	if settings.DEBUG:
    	    print str(round(hourlyWage,2))
    		
    	return str(round(hourlyWage,2))
        
    def fixMiddleInitial(self, middle_initial):
    	fixed_middle_initial = str.lstrip(str.upper(middle_initial))[0]
    #		if fixed_middle_initial <> middle_initial:
    #			print "fixed middle_initial"
    #			print middle_initial
    #			print "initial middle_initial"
    #			print fixed_middle_initial
    	return fixed_middle_initial
        
        # SBB20070920 Ported from Manatee County code base
        # SBB20070831 New function to test and return a correctly formatted SSN
    def fixSSN(self, incomingSSN):
    	originalSSN = incomingSSN
    	
    	# ECJ20071111 Added to make it so blank SSNs don't return "--", and instead return ""
    	if incomingSSN == "" or incomingSSN == None:
    	    return incomingSSN
    	
    	dashCount = incomingSSN.count('-') 
    	if dashCount > 0:
    	    if dashCount == 2:
    		# already has the dashes, return the string
    		if settings.DEBUG:
    		    self.debugMessages.log("incoming SSN is correctly formatted: %s\n" % (incomingSSN))
    			
    		return incomingSSN
    	    else:					# incoming SSN has 1 dash but not 2.  This is an error
    		# fix this data
    		incomingSSN = string.replace(incomingSSN, '-', '')
            if len(incomingSSN) < 9:
                # reformat the string and return
                theError = (1020, 'Data format error discovered in trying to cleanup incoming SSN: %s, original SSN: %s' % (incomingSSN, originalSSN))
                if settings.DEBUG:
                    self.debugMessages.log(">>>> Incoming SSN is INcorrectly formatted.  Original SSN from input file is: %s and Attempted cleaned up SSN is: %s\n" % (originalSSN, incomingSSN))
                raise dataFormatError, theError
    			
    	# If we are here, we can simply reformat the string into dashes
    	if settings.DEBUG:
    	    self.debugMessages.log("incoming SSN is INcorrectly formatted: %s.  Reformatting to: %s\n" % (incomingSSN, '%s-%s-%s' % (incomingSSN[0:3], incomingSSN[3:5], incomingSSN[5:10])))
    	return '%s-%s-%s' % (incomingSSN[0:3], incomingSSN[3:5], incomingSSN[5:10])
    			
if __name__ == "__main__":
    vld = SVCPOINTXMLWriter(".")
    vld.write()
