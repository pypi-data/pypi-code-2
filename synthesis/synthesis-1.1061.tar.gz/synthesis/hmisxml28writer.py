import os.path
from interpretpicklist import Interpretpicklist
from datetime import timedelta, date, datetime
from time import strptime, time
import xmlutilities
from xmlutilities import IDGeneration
#from mx.DateTime import ISO
# SBB20070920 Adding exceptions class
#from clsexceptions import dataFormatError, ethnicityPickNotFound

# Alchemy Libraries
from sqlalchemy import create_engine, Table, Column, Numeric, Integer, String, Boolean, MetaData, ForeignKey, Sequence
from sqlalchemy.orm import sessionmaker, mapper, backref, relation, clear_mappers, eagerload
from sqlalchemy.types import DateTime, Date

from sys import version
from conf import settings
import clsexceptions
import dbobjects
from writer import Writer
from zope.interface import implements

# py 2.5 support
# dynamic import of modules
thisVersion = version[0:3]

#if thisVersion  == '2.5':
#    try:
#    import xml.etree.cElementTree as ET
#    from xml.etree.ElementTree import Element, SubElement, dump
#    except ImportError:
#    import xml.etree.ElementTree as ET
#    from xml.etree.ElementTree import Element, SubElement
#elif thisVersion == '2.4':
#    try:
#    # Try to use the much faster C-based ET.
#    import cElementTree as ET
#    from elementtree.ElementTree import Element, SubElement, dump
#    except ImportError:
#    # Fall back on the pure python one.
#    import elementtree.ElementTree as ET
#    from elementtree.ElementTree import Element, SubElement
#else:
#    print 'Sorry, please see the minimum requirements to run this Application'
#    theError = (1100, 'This application requires Python 2.4 or higher.  You are current using version: %s' % (thisVersion), 'import Error XMLDumper.py')
#    raise SoftwareCompatibilityError, theError

def buildWorkhistoryAttributes(element):
    element.attrib['date_added'] = datetime.now().isoformat()
    element.attrib['date_effective'] = datetime.now().isoformat() #@IndentOk


class HMISXML28Writer(dbobjects.DatabaseObjects):
    
    # Writer Interface
    implements (Writer)
    
    hmis_namespace = "http://www.hmis.info/schema/2_8/HUD_HMIS_2_8.xsd" 
    airs_namespace = "http://www.hmis.info/schema/2_8/AIRS_3_0_draft5_mod.xsd"
    nsmap = {"hmis" : hmis_namespace, "airs" : airs_namespace}    
    
    def __init__(self, poutDirectory, debug=False, debugMessages=None):
        #print "%s Class Initialized" % self.__name__
        if settings.DEBUG:
            print "XML File to be dumped to: %s" % poutDirectory
            
        self.outDirectory = poutDirectory
        self.pickList = Interpretpicklist()
        # SBB20070626 Adding the declaration for outcomes list
        self.intakes = {}
        self.outcomes = None
        self.daily_census = []
        
        # SBB20070628 adding a buffer for errors to be displayed at the end of the process.
        self.errorMsgs = []
        
        self.xmlU = IDGeneration()
        # adding a debug switch that is managed in the INI
        self.debug = debug
        # SBB20071023 Adding Debugging Messages class to XMLDumper
        #if debug == True:
        #    print "Debug switch is: %s" % debug
    
        if debug == True:
            print "Debug switch is: %s" % debug
            self.debugMessages = debugMessages
            
        #SBB20070626 Breaking this function into 2 parts one for the intakes and a second (one) for the outcomes (many) Relationship is 1 to many
        #def push_data(self, intakes, outcomes):
        #push_data takes a matched set of information (intakes and outcomes) to generate the XML

    def prettify(self):
        self.xmlU.indent(self.root_element)

    def dumpErrors(self):
        print "Error Reporting"
        print "-" * 80
        for row in range(len(self.errorMsgs)):
            print "%s %s" % (row, self.errorMsgs[row])
        
    def push_data_intakes(self, intakes):
        if self.debug == True:
            print "XMLModule Intakes Pushed" 
        self.intakes = intakes

    def push_data_outcomes(self, outcomes):
    # this is a list of dictionaries.  When formatting the output, need to iterate through the list and then take the dictionary keys to insert the values where needed
        if self.debug == True:
            print "XMLModule Outcomes Pushed" 
        #print self.intakes
        self.outcomes = outcomes
        
    def push_data_daily_census(self, daily_census):
    # this is a list of dictionaries.  When formatting the output, need to iterate through the list and then take the dictionary keys to insert the values where needed
        if self.debug == True:
            print "XMLModule daily_census Pushed" 
        self.daily_census = daily_census
    
    # SBB20071021 Set the systemID value from the DB.
    def setSysID(self, pSysID):
        self.sysID = pSysID
        # SBB20071021



    def processXML(self): # records represents whatever element you're tacking more onto, like entry_exits or clients
        if self.debug == True:
            print "Appending XML to Base Record"
    
        # generate the SystemID Number based on the Current Users Data, You must pass in the word 'system' in order to create the current users key.
        self.SystemID = self.xmlU.generateSystemID('system')
    
        
        
        # start the clients
        
        self.root_element = self.createDoc() #makes root element with XML header attributes
        
        records = self.createClients(self.root_element)
        
        # Clear the session
        #session.clear()
    
        mappedObjects = dbobjects.DatabaseObjects()
        # first get the export object then get it's related objects
        Persons = mappedObjects.queryDB(dbobjects.Person)
        for self.person in Persons:
            
            self.ph = self.person.fk_person_to_person_historical
            
            # Instead of generating a number (above), use the client number that is already provided in the legacy system
            # or
            self.xmlU.initializeSystemID(self.person.id)
            self.sysID = self.person.id
    
            if not self.person == None and self.outcomes == None:
            client = self.createClient(records)
            self.customizeClient(client)
            self.customizeClientPersonalIdentifiers(client, self.person)
            dynamiccontent = self.createDynamic_content(client)
            self.customizeDynamiccontent(dynamiccontent)
            
            continue    # FIXME (Remove when done)
        
            if not self.intakes == None and not self.outcomes == None:
            for self.intake in self.intakes:
                client = self.createClient(records)
                self.customizeClientForEntryExit(client)
                self.customizeClientPersonalIdentifiersForEntryExit(client,self.intake)
        
        # SBB20070627 we are only going to create needs/services records for daily census entries.  
        #If there aren't any, we'll skip this portion of the code
        if not self.daily_census == None:
            for self.dsRec in self.daily_census:
            client = self.createClient(records)
            self.customizeClient(client)
            self.customizeClientPersonalIdentifiers(client,self.dsRec)
            needs = self.createNeeds(client) 
            need = self.createNeed(needs)
            self.customizeNeed(need)
            services = self.createServices(need)
            service = self.createService(services)
            self.customizeService(service)
    
        if not self.outcomes == None and self.intakes == None:            
            for self.outcom in self.outcomes:
            entry_exit = self.createEntryExit(records)
            
    #        Removed all household elements, since the csv data does not convey household data
    #        households = self.createHouseholds(records)
    #        household = self.createHousehold(households)
    #        self.customizeHousehold(household)
    #        members = self.createMembers(household)
    #        member = self.createMember(members)
    #        self.customizeMember(member)
        
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
    #sysID = self.xmlU.generateSysID(keyval)
    sysID = self.xmlU.generateSysID2(keyval, self.sysID)    
    recID = self.xmlU.generateRecID(keyval)
    client.attrib["record_id"] = recID 
    client.attrib["odbid"] = "5" 
    client.attrib["system_id"] = sysID    
    client.attrib["date_added"] = datetime.now().isoformat()
    client.attrib["date_updated"] = datetime.now().isoformat()
        
    def customizeClientForEntryExit(self, client):
    keyval = 'client'
    # SBB20071021 changed signature of the generateSysID function.
    #sysID = self.xmlU.generateSysID(keyval)
    sysID = self.xmlU.generateSysID2(keyval, self.sysID)    
    recID = self.xmlU.generateRecID(keyval)        
    client.attrib["record_id"] = recID 
    client.attrib["odbid"] = "5" 
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
        

    # SBB20070920 Fix SSN's to make sure that they have the right format
    # SBB20070831 incoming SSN's are 123456789 and need to be 123-45-6789
    fixedSSN = self.fixSSN(recordset.person_social_security_number_unhashed)
    #ECJ20071111 Omit SSN if it's blank            
    if fixedSSN <> "" and fixedSSN <> None:    
        soc_sec_no = ET.SubElement(client, "soc_sec_no")
        soc_sec_no.text = fixedSSN
        
        #ECJ20071203 We could make the code more complex to determine if partial ssn, but don't know/refused would have to be collected by shelter.
        ssn_data_quality = ET.SubElement(client, "ssn_data_quality")
        ssn_data_quality.text = "full ssn reported (hud)"
        

    def customizeClientPersonalIdentifiersForEntryExit(self,client,recordset):
    first_name = ET.SubElement(client, "first_name")
    first_name.text = recordset['First Name']
    
    last_name = ET.SubElement(client, "last_name")
    last_name.text = recordset['Last Name']
    
    #we don't have the following elements for daily_census only clients, but SvcPt requires them:
    # I simulated this w/my datasets.  Column names are as in the program
    if recordset['MI'] <> "":
        mi_initial = ET.SubElement(client, "mi_initial")
        mi_initial.text = self.fixMiddleInitial(recordset['MI'])
    

    # SBB20070920 Fix SSN's to make sure that they have the right format
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
    contactsaddress.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])        
    contactsaddress.text = self.intakes['Emergency Address']
    
        
    contactscity = ET.SubElement(emergencycontacts, "contactscity")
    contactscity.attrib["date_added"] = datetime.now().isoformat()
    contactscity.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                    
    contactscity.text = self.intakes['Emergency City']
    
    
    contactsname = ET.SubElement(emergencycontacts, "contactsname")
    contactsname.attrib["date_added"] = datetime.now().isoformat()
    contactsname.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                            
    contactsname.text = self.intakes['Emergency Contact Name']
    
    
    contactsstate = ET.SubElement(emergencycontacts, "contactsstate")
    contactsstate.attrib["date_added"] = datetime.now().isoformat()
    contactsstate.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                    
    contactsstate.text = self.intakes['Emergency State']
    
        
    def customizeAddress_1(self, address_1):
    clientscity = ET.SubElement(address_1, "clientscity")
    clientscity.text = self.intakes['ResidentialCity']
    clientscity.attrib["date_added"] = datetime.now().isoformat()
    clientscity.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                    
    
    clientsstate = ET.SubElement(address_1, "clientsstate")
    clientsstate.text = self.intakes['ResidentialState']
    clientsstate.attrib["date_added"] = datetime.now().isoformat()
    clientsstate.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                            
    
    clientszip_1 = ET.SubElement(address_1, "clientszip_1")
    clientszip_1.attrib["date_added"] = datetime.now().isoformat()
    clientszip_1.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                    
    clientszip_1.text = self.intakes['ResidentialZip']
    
    
    def createNeeds(self, client):
    needs = ET.SubElement(client, "needs")
    
    return needs
    
    def createNeed(self, needs):
    keyval = 'need'
    sysID = self.xmlU.generateSysID(keyval)
    
    #append the need start date to the client's need_id so the need system_ids are unique for each need
    #since we don't store needs in the database
    date_for_need_id = self.dsRec['Date']
    #We should have the shelter switch to a 4 digit year, then change the %y to %Y
    date_object_format = self.fixDateNoTime(date_for_need_id)
    sysID = sysID + str(date_object_format)
    recID = self.xmlU.generateRecID(keyval)
    
    need = ET.SubElement(needs, "need")
    need.attrib["record_id"] = recID 
    need.attrib["system_id"] = sysID
    
    need.attrib["date_added"] = datetime.now().isoformat()
    need.attrib["date_updated"] = datetime.now().isoformat()
    
    
    return need
    
    def customizeNeed(self, need):    
    provider_id = ET.SubElement(need, "provider_id")
    provider_id.text = "14"
    
    
    status = ET.SubElement(need, "status")
    status.text = "closed"
    
    
    code = ET.SubElement(need, "code")
    code.attrib["type"] = "airs taxonomy"
    code.text = "BH-180"
    
    
    if self.debug == True:
        notes = ET.SubElement(need, "notes")
        notes.text = 'Client ID: %s' % self.dsRec['Client ID']
        notes.tail = '\n'
        
    date_set = ET.SubElement(need, "date_set")
    # ECJ20071114: The Need date_set will be the same day as the service provided date
    orig_format = self.dsRec['Date']
    #We should have the shelter switch to a 4 digit year, then change the %y to %Y
    date_set_datetime_object_format = self.fixDate(orig_format) 
    date_set.text = date_set_datetime_object_format
    
        
    def createServices(self, need):
    # services Section
    services = ET.SubElement(need, "services")
    services.text = "\n"
    services.tail = "\n"
    return services

# These services have to be created whenever there is an associated service in the daily census
#    But ... first we have to get a daily census dictionary populated and available to call

    def createService(self, services):
    keyval = 'service'
    sysID = self.xmlU.generateSysID(keyval)
    #append the service start date to the client's serviceid so the service system_ids are unique for each service
    #since we don't store services in the database
    date_for_service_id = self.dsRec['Date']
    date_object_format = self.fixDateNoTime(date_for_service_id)
    sysID = sysID + str(date_object_format)
    recID = self.xmlU.generateRecID(keyval)
    service = ET.SubElement(services, "service")
    service.attrib["record_id"] = recID
    service.attrib["system_id"] = sysID
    #We should have the shelter switch to a 4 digit year, then change the %y to %Y
    service.attrib["date_added"] = datetime.now().isoformat()
    service.attrib["date_updated"] = datetime.now().isoformat()
    service.text = "\n"
    service.tail = "\n"
    
    return service
    
    def customizeService(self, service):
    code = ET.SubElement(service,"code")
    code.attrib["type"] = "airs taxonomy"
#Since the needs are always shelter stays, but the codes aren't stated explicity in the csv, these will default to BH-180 
    code.text = "BH-180" #token250 type in the schema, not nillable, minOccurs=1
    
    
#        removed since minOccurs=0 and not in CSV        
#        referto_provider_id = ET.SubElement(service, "referto_provider_id")
#        referto_provider_id.text = "provider1"
#        referto_provider_id.tail = "\n"
    
#        removed since minOccurs=0 and not in CSV
#        refer_date = ET.SubElement(service, "refer_date")
#        refer_date.tail = "\n"
    
    service_provided = ET.SubElement(service, "service_provided")
    service_provided.text = "true"
    
    
    provide_provider_id = ET.SubElement(service, "provide_provider_id")
    provide_provider_id.text = "14" 
    
    
#        This needs to be populated with  daily census.csv data using the date field from that file 
    provide_start_date = ET.SubElement(service, "provide_start_date")
#        Need to populate provide_start/end_dates with a date:
    orig_format = self.dsRec['Date']
    #We should have the shelter switch to a 4 digit year, then change the %y to %Y
    start_date_object_format = self.fixDate(orig_format)
#        print "The service key fixed date is:" 
#        print start_date_date_object_format
    #start_date_datetime_object_format = datetime(*strptime(orig_format, "%m/%d/%y")[0:5])
    
    provide_start_date.text = start_date_object_format
    

#        This needs to be populated with  daily census.csv data using the date field + 1 day from that file         
    provide_end_date = ET.SubElement(service, "provide_end_date")
    #add one day to the provide start date to arrive at the end date
    one_day_difference = timedelta(days=1)
    start_date_datetime_object_format = self.getDateTimeObj(orig_format)
    end_date_datetime_object_format = start_date_datetime_object_format + one_day_difference
    provide_end_date.text = end_date_datetime_object_format.isoformat()
    
        
    def createGoals(self, client):
    # goals Section
    goals = ET.SubElement(client, "goals")
    
    return goals
    
    def createGoal(self, goals):
    keyval = 'goal'
    sysID = self.xmlU.generateSysID(keyval)
    recID = self.xmlU.generateRecID(keyval)        
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
    sysID = self.xmlU.generateSysID(keyval)
    recID = self.xmlU.generateRecID(keyval)        
    action_step = ET.SubElement(action_steps, "action_step")
    action_step.attrib["record_id"] = recID
    action_step.attrib["system_id"] = sysID
    action_step.attrib["date_added"] = datetime.now().isoformat()
    action_step.attrib["date_updated"] = datetime.now().isoformat()
    return action_step
        
    def customizeAction_step(self, action_step):
    provider_id = ET.SubElement(action_step, "provider_id")
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
    
    def createEntryExit(self, entry_exits):
    keyval = 'entry_exit'
    sysID = self.xmlU.generateSysID(keyval)
    #append the entry_exit start date to the client's entry_exit_id so the entry_exit system_ids are unique for each entry_exit
    #since we don't store entry_exits in the database
    date_for_entry_exit_id = self.outcom['Entry Date']
    #We should have the shelter switch to a 4 digit year, then change the %y to %Y
    entry_exit_date_object_format = self.fixDateNoTime(date_for_entry_exit_id)
    sysID = sysID + str(entry_exit_date_object_format)
    recID = self.xmlU.generateRecID(keyval)
    entry_exit = ET.SubElement(entry_exits, "entry_exit")
    
    entry_exit.attrib["odbid"] = "5"
    entry_exit.attrib["record_id"] = recID
    entry_exit.attrib["system_id"] = sysID    
    entry_exit.attrib["date_added"] = datetime.now().isoformat()
    entry_exit.attrib["date_updated"] = datetime.now().isoformat()
    self.customizeEntryExit(entry_exit)
    self.createEntryExitMember(entry_exit)
    return entry_exit
    
    def createEntryExitMember(self,entry_exit):
    keyval = 'member'
    sysID = self.xmlU.generateSysID2(keyval,self.sysID)
    recID = self.xmlU.generateRecID(keyval)
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
    client_id.text = self.xmlU.generateSysID2(keyval,self.sysID)

    

    if self.fixDate(self.outcom['Exit Date']) is not None:
        exit_date = ET.SubElement(member, "exit_date")
        exit_date.text = self.fixDate(self.outcom['Exit Date'])
    
        
    #Shelter does not provide a reason leaving in outcom.csv
    #if self.pickList.getValue("EereasonLeavingPick", self.outcom['Code']) <> "":
        #reason_leaving = ET.SubElement(member, "reason_leaving")
        #reason_leaving.text = self.pickList.getValue("EereasonLeavingPick", self.outcom['Code'])
        #reason_leaving.tail = "\n"
        #reason_leaving_other = ET.SubElement(entry_exit, "reason_leaving_other")
        #reason_leaving_other.tail = "\n"
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
        if self.debug == True:
        notes.text = self.formatNotesField(notes.text, 'Client ID:', self.outcom['Client ID'])    
        # adding education and partner to the notes field
        notes.text = self.formatNotesField(notes.text, 'Education', self.outcom['Education'])
        notes.text = self.formatNotesField(notes.text, 'Partner', self.outcom['Partner'])
    
    # destination_other = ET.SubElement(member, "destination_other")
    # destination_other.tail = "\n"

    def customizeEntryExit(self, entry_exit):
    type = ET.SubElement(entry_exit, "type")
    type.text = "hud-40118"
    
    provider_id = ET.SubElement(entry_exit, "provider_id")
    provider_id.text = "14"
    
    if self.fixDate(self.outcom['Entry Date']) <> "":
        entry_date = ET.SubElement(entry_exit, "entry_date")
    
        entry_date.text = self.fixDate(self.outcom['Entry Date'])
        
    def createInfo_releases(self, client):
    # info_releases Section
    info_releases = ET.SubElement(client, "info_releases")
    
    
    return info_releases
    
    def createInfo_release(self, info_releases):
    keyval = 'info_release'
    sysID = self.xmlU.generateSysID(keyval)
    recID = self.xmlU.generateRecID(keyval)
    
    info_release = ET.SubElement(info_releases, "info_release")
    
    #info_release.attrib["record_id"] = "ROI1"
    info_release.attrib["record_id"] = recID
    #info_release.attrib["system_id"] = "roi1243a"
    info_release.attrib["system_id"] = sysID
    
    info_release.attrib["date_added"] = datetime.now().isoformat()
    info_release.attrib["date_updated"] = datetime.now().isoformat()
    return info_release
        
    def customizeInfo_release(self, info_release):
    provider_id = ET.SubElement(info_release, "provider_id")
    date_started = ET.SubElement(info_release, "date_started")
    date_ended = ET.SubElement(info_release, "date_ended")
    permission = ET.SubElement(info_release, "permission")
    documentation = ET.SubElement(info_release, "documentation")
    witness = ET.SubElement(info_release, "witness")
    witness.text = "tok50Type"
        
    def createDynamic_content(self, client):
    # dynamic content section
    dynamic_content = ET.SubElement(client, "dynamic_content")
    #dynamic_content.text = "\n"
    #dynamic_content.tail = "\n"
    return dynamic_content

    def customizeDynamiccontent(self, dynamiccontent):

    for ph in self.ph:
        
        # Is client homeless?
        if ph.hud_homeless <> "" and ph.hud_homeless <> None:
        isclienthomeless = ET.SubElement(dynamiccontent, "isclienthomeless")
        isclienthomeless.attrib["date_added"] = datetime.now().isoformat()
        isclienthomeless.attrib["date_effective"] = self.fixDate(ph.hud_homeless_date_collected)
        if ph.hud_homeless == '1':
            isclienthomeless.text = 'true'
        if ph.hud_homeless == '' or ph.hud_homeless == None:
            isclienthomeless.text = 'false'
    
        if ph.physical_disability <> "" and ph.physical_disability <> None:
        hud_disablingcondition = ET.SubElement(dynamiccontent, "hud_disablingcondition")
        hud_disablingcondition.attrib["date_added"] = datetime.now().isoformat()
        hud_disablingcondition.attrib["date_effective"] = self.fixDate(ph.physical_disability_date_collected)
        hud_disablingcondition.text = self.pickList.getValue("ENHANCEDYESNOPickOption",str.strip(ph.physical_disability.upper()))
    
        if ph.hours_worked_last_week <> "" and ph.hours_worked_last_week <> None:
        hud_hrsworkedlastweek = ET.SubElement(dynamiccontent, 'hud_hrsworkedlastweek')
        hud_hrsworkedlastweek.attrib["date_added"] = datetime.now().isoformat()
        hud_hrsworkedlastweek.attrib["date_effective"] = self.fixDate(ph.hours_worked_last_week_date_collected)
        hud_hrsworkedlastweek.text = str.strip(ph.hours_worked_last_week)
    
    # FIXME (when provided solution by Eric)
    #    # Are you prescribed any medications?        
    #    if self.intakes['PrescriptionMeds'] <> "":
    #    areyouprescribedanyme = ET.SubElement(dynamiccontent,"areyouprescribedanyme")
    #    areyouprescribedanyme.text = self.intakes['PrescriptionMeds'].lower()
    #    areyouprescribedanyme.attrib["date_added"] = datetime.now().isoformat()
    #    areyouprescribedanyme.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
    
    #    # Is your illness life threatening?
    #    # hivaids_status
    #    if self.intakes['LifeThreatening'].lower() <> "":
    #    isyourillnesslifethre = ET.SubElement(dynamiccontent,"isyourillnesslifethre")
    #    isyourillnesslifethre.text = self.intakes['LifeThreatening'].lower()
    #    isyourillnesslifethre.attrib["date_added"] = datetime.now().isoformat()
    #    isyourillnesslifethre.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
        
        
        
    
    
        continue
    
        # race and ethnicity (at Cleveland, one field, "self.intakes['Race']", handles both)
        race = self.intakes['Race'].lower()
        if race <> "":
        if self.pickList.getValue("RacePick",race) <> "":
            svpprofrace = ET.SubElement(dynamiccontent, "svpprofrace")
            svpprofrace.attrib["date_added"] = datetime.now().isoformat()
            svpprofrace.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                        
            svpprofrace.text = self.pickList.getValue("RacePick",race)
            
        #ECJ20071022 We can't just make all people Ethnicity "Other" who are not explicity flagged as "Hispanic"
        #The real solution to the problem is that they need to split Ethnicity/Race into two separate fields.    
        
        ethnicity = self.pickList.getValue("EthnicityPick",race)
        if ethnicity <> "":
            svpprofeth = ET.SubElement(dynamiccontent, "svpprofeth")
            svpprofeth.attrib["date_added"] = datetime.now().isoformat()
            svpprofeth.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
            svpprofeth.text = ethnicity
            
        
        # Zip Code
        if self.intakes['Zip'] <> "":
        hud_zipcodelastpermaddr = ET.SubElement(dynamiccontent, "hud_zipcodelastpermaddr")
        hud_zipcodelastpermaddr.attrib["date_added"] = datetime.now().isoformat()
        hud_zipcodelastpermaddr.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
        hud_zipcodelastpermaddr.text = self.intakes['Zip']
        
    
        # living situation
        if self.pickList.getValue("LIVINGSITTYPESPickOption",self.intakes['ResidentType']):
        typeoflivingsituation =  ET.SubElement(dynamiccontent,"typeoflivingsituation")
        typeoflivingsituation.text = self.pickList.getValue("LIVINGSITTYPESPickOption",self.intakes['ResidentType'])
        typeoflivingsituation.attrib["date_added"] = datetime.now().isoformat()
        typeoflivingsituation.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
        
            
        
        if self.intakes['ResidentialAddress'] <> "":
        address_2 = ET.SubElement(dynamiccontent,"address_2")
        address_2.attrib["date_added"] = datetime.now().isoformat()
        address_2.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
        address_2.text = self.intakes['ResidentialAddress']
        
        
        if self.intakes['USCitizen'].lower() <> "":
        uscitizen = ET.SubElement(dynamiccontent,"uscitizen")
        uscitizen.text = self.intakes['USCitizen'].lower()
        uscitizen.attrib["date_added"] = datetime.now().isoformat()
        uscitizen.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
        
        
        # already a True and False just lower the value to make it compliant
        if     self.intakes['UseDrugsorAlchohol'].lower() <> "":
        usealcoholordrugs = ET.SubElement(dynamiccontent,"usealcoholordrugs")
        usealcoholordrugs.text = self.intakes['UseDrugsorAlchohol'].lower()
        usealcoholordrugs.attrib["date_added"] = datetime.now().isoformat()
        usealcoholordrugs.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
        
        
        if self.pickList.getValue("ENHANCEDYESNOPickOption", self.intakes['Military']) <> "":
        veteran = ET.SubElement(dynamiccontent,"veteran")
        veteran.text = self.pickList.getValue("ENHANCEDYESNOPickOption", self.intakes['Military'])
        veteran.attrib["date_added"] = datetime.now().isoformat()
        veteran.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])
        
        
        if self.intakes['Branch'] <> "" or self.convertIntegerToDate(self.intakes['EntranceDate']) <> None or self.convertIntegerToDate(self.intakes['DischargeDate']) <> None:
        hud_militarybranchinfo = ET.SubElement(dynamiccontent,"hud_militarybranchinfo")
        hud_militarybranchinfo.attrib["date_added"] = datetime.now().isoformat()
        
        if self.intakes['Branch'] <> "":
            militarybranch = ET.SubElement(hud_militarybranchinfo,"militarybranch")
            militarybranch.attrib["date_added"] = datetime.now().isoformat()
            militarybranch.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                        
            militarybranch.text = self.pickList.getValue("MILITARYBRANCHPickOption",self.intakes['Branch'])
        
        if self.convertIntegerToDate(self.intakes['EntranceDate']) <> None:
            hud_militarybranchins = ET.SubElement(hud_militarybranchinfo,"hud_militarybranchins")
            hud_militarybranchins.attrib["date_added"] = datetime.now().isoformat()
            hud_militarybranchins.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])            
            hud_militarybranchins.text = self.convertIntegerToDateTime(self.intakes['EntranceDate'])
        
        if self.convertIntegerToDate(self.intakes['DischargeDate']) <> None:
            hud_militarybranchinend = ET.SubElement(hud_militarybranchinfo,"hud_militarybranchinend")
            hud_militarybranchinend.attrib["date_added"] = datetime.now().isoformat()
            hud_militarybranchinend.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])            
            hud_militarybranchinend.text = self.convertIntegerToDateTime(self.intakes['DischargeDate'])
        
        
        #    casecounselor = ET.SubElement(dynamiccontent,"casecounselor")
        #    casecounselor.text = self.outcom['Staff']
    
        # True False Processing section, subelement is only created if the value is True.
        if self.intakes['Warrant'] == 'TRUE':
        currentwarrantissued = ET.SubElement(dynamiccontent,"currentwarrantissued")
        currentwarrantissued.attrib["date_added"] = datetime.now().isoformat()
        currentwarrantissued.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                    
        currentwarrantissued.text = 'true'
        
            
        if self.intakes['Parole'] == 'TRUE':
        onparole = ET.SubElement(dynamiccontent,"onparole")
        onparole.attrib["date_added"] = datetime.now().isoformat()
        onparole.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                    
        onparole.text = 'true'
        
            
        if self.intakes['Probation'] == 'TRUE':
        onprobation = ET.SubElement(dynamiccontent,"onprobation")
        onprobation.attrib["date_added"] = datetime.now().isoformat()
        onprobation.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                    
        onprobation.text = 'true'
        
        
        if self.intakes['SexOffender'] == 'TRUE':
        convictedsexoffneder = ET.SubElement(dynamiccontent,"convictedsexoffneder")
        convictedsexoffneder.attrib["date_added"] = datetime.now().isoformat()
        convictedsexoffneder.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                                
        convictedsexoffneder.text = 'true'
        
            
        if self.intakes['ArrestedBefore'] == 'TRUE':
        everbeenarrestedbefore = ET.SubElement(dynamiccontent,"everbeenarrestedbefore")
        everbeenarrestedbefore.attrib["date_added"] = datetime.now().isoformat()
        everbeenarrestedbefore.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                                
        everbeenarrestedbefore.text = 'true'
        
                        
        if self.intakes['Jail/Prisontime'] == 'TRUE':
        arrestrecord = ET.SubElement(dynamiccontent,"arrestrecord")
        arrestrecord.attrib["date_added"] = datetime.now().isoformat()
        arrestrecord.text = '\n'
        
        servedtime = ET.SubElement(arrestrecord,"servedtime")
        servedtime.attrib["date_added"] = datetime.now().isoformat()
        servedtime.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                                
        servedtime.text = 'true'
        
        
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
    
        for lookup in lookups:
        if self.intakes[lookup] == 'TRUE':
            homelessPickOption.append(self.pickList.getValue("HOMELESSREASONPickOption",lookup))
        if len(homelessPickOption) > 0:
        primaryreasonforhomle = ET.SubElement(dynamiccontent,"primaryreasonforhomle")
        primaryreasonforhomle.attrib["date_added"] = datetime.now().isoformat()
        primaryreasonforhomle.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                        
        #ECJ20071121 We can only have one primary reason, so discard all but the first
        #primaryreasonforhomle.text = ' ' + ' '.join(homelessPickOption) + ' '
        primaryreasonforhomle.text = homelessPickOption[0]
        primaryreasonforhomle.tail = '\n'
        
        #ECJ 20071111 nothing is populated here for incomesource
        #incomesource = ET.SubElement(dynamiccontent,"incomesource")
        # would need a .text entry here
        #incomesource.tail = '\n'
        
        if self.intakes['ResidentialCity'] <> "" and self.intakes['ResidentialState'] <> "":
        address_1 = self.createAddress_1(dynamiccontent)
        self.customizeAddress_1(address_1)
        
        if self.intakes['ResidentialZip'] <> "":
        address_1 = self.createAddress_1(dynamiccontent)
        self.customizeAddress_1(address_1)    
    
        if self.intakes['Emergency Address'] <> "":
        emergencycontacts = self.createEmergencyContacts(dynamiccontent)
        self.customizeEmergencyContacts(emergencycontacts)
        
        if str.strip(self.intakes['EmploymentStatus']) <> "":
        unemployed = ET.SubElement(dynamiccontent, 'unemployed')
        unemployed.attrib["date_added"] = datetime.now().isoformat()
        unemployed.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                        
        if str.strip(self.intakes['EmploymentStatus'])=="Unemployed":
            unemployed.text = "true"
        else:
            unemployed.text = "false"
        
        
        #This is an assumption that monthly wage = one employer's wage
        if     self.intakes['MonthlyWage-CheckAmount'] <> "":
        monthlyincome = ET.SubElement(dynamiccontent, 'hud_totalmonthlyincome')
        monthlyincome.attrib["date_added"] = datetime.now().isoformat()
        monthlyincome.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                        
        monthlyincome.text = self.intakes['MonthlyWage-CheckAmount']
        
        
        if self.intakes['EmployerName'] <> ""\
        and self.pickList.getValue("EmploymentPick", self.intakes['EmploymentStatus']) <> "" \
        and self.intakes['Hours-Week'] <> "" and self.calcHourlyWage(self.intakes['MonthlyWage-CheckAmount'])<> "":
        workhistory = self.createWorkhistory(dynamiccontent)
        
        self.customizeWorkhistory(workhistory)
            
        if self.intakes['DisabilityDiscription'] <> "":
        disabilities_1 = ET.SubElement(dynamiccontent,"disabilities_1")
        disabilities_1.attrib["date_added"] = datetime.now().isoformat()            
        self.customizeDisabilities_1(disabilities_1)
        
    # Moved these outside the PH Loop, so they don't repeat.  This info comes from person and not personhistorical
    # gender: this is just hard-coded to male for now, since this is a male shelter
    # person_gender_unhashed
    #if self.pickList.getValue("SexPick","male") <> "":
    if self.person.person_gender_unhashed <> "" and self.person.person_gender_unhashed <> None:
        svpprofgender = ET.SubElement(dynamiccontent, "svpprofgender")
        svpprofgender.attrib["date_added"] = datetime.now().isoformat()
        svpprofgender.attrib["date_effective"] = self.fixDate(self.person.person_gender_date_collected)
        svpprofgender.text = self.pickList.getValue("SexPick",self.person.person_gender_unhashed)

    # dob (Date of Birth)
    if self.person.person_date_of_birth_unhashed <> "" and self.person.person_date_of_birth_unhashed <> None:
        svpprofdob = ET.SubElement(dynamiccontent, "svpprofdob")
        svpprofdob.attrib["date_added"] = datetime.now().isoformat()
        svpprofdob.attrib["date_effective"] = self.fixDate(self.person.person_date_of_birth_date_collected)
        #svpprofdob.text = self.convertIntegerToDateTime(self.intakes['DOB'])
        svpprofdob.text = self.fixDate(self.person.person_date_of_birth_unhashed)

    #    def create6monthtrackinginforma(self, dynamiccontent):
    #        # SBB20070626 Converting name from 6month to sixmonth this XML is not validating..
    #        #Sixmonthtrackinginforma = ET.SubElement(dynamiccontent,"6monthtrackinginforma")
    #        Sixmonthtrackinginforma = ET.SubElement(dynamiccontent,"Sixmonthtrackinginforma")
    #        Sixmonthtrackinginforma.text = "\n"
    #        return Sixmonthtrackinginforma
    
    #def customize6monthtrackinginforma(self, Sixmonthtrackinginforma):
    
    def customizeDisabilities_1(self, disabilities_1):
    if self.intakes['DisabilityDiscription'] <> "":
        noteondisability = ET.SubElement(disabilities_1,'noteondisability')
        noteondisability.attrib["date_added"] = datetime.now().isoformat()
        noteondisability.attrib["date_effective"] = self.fixDate(self.intakes['IntakeDate'])                                    
        noteondisability.text = self.intakes['DisabilityDiscription']
        
    
    def createWorkhistory(self, dynamiccontent):
    workhistory = ET.SubElement(dynamiccontent, "workhistory")
    workhistory.attrib["date_added"] = datetime.now().isoformat()
    return workhistory
        
    def customizeWorkhistory(self, workhistory):    
    if self.intakes['EmployerName'] <> "":
        employername = ET.SubElement(workhistory, 'employername')
        buildWorkhistoryAttributes(employername)
        employername.text = self.intakes['EmployerName']

        
#        if self.intakes[''] <> "":    
#            supervisorsname = ET.SubElement(workhistory, 'supervisorsname')
#            supervisorsname.tail = "\n"
#            buildWorkhistoryAttributes(supervisorsname)
#            supervisorsname.text = self.intakes['']
        
#        employersaddress = ET.SubElement(workhistory, 'employersaddress')
#        employersaddress.tail = "\n"
#        buildWorkhistoryAttributes(employersaddress)
#        employerscity = ET.SubElement(workhistory, 'employerscity')
#        employerscity.tail = "\n"
#        buildWorkhistoryAttributes(employerscity) 
#        employersstate = ET.SubElement(workhistory, 'employersstate')
#        employersstate.tail = "\n"
#        buildWorkhistoryAttributes(employersstate)
#        employerszip = ET.SubElement(workhistory, 'employerszip')
#        employerszip.tail = "\n"
#        buildWorkhistoryAttributes(employerszip)
#        employersphonenumber = ET.SubElement(workhistory, 'employersphonenumber')
#        employersphonenumber.tail = "\n"
#        buildWorkhistoryAttributes(employersphonenumber)
    if self.pickList.getValue("EmploymentPick", self.intakes['EmploymentStatus']) <> "":
        employmentstatus_1 = ET.SubElement(workhistory, 'employmentstatus_1')
        buildWorkhistoryAttributes(employmentstatus_1)
        employmentstatus_1.text = self.pickList.getValue("EmploymentPick", self.intakes['EmploymentStatus'])

    if self.intakes['Hours-Week'] <> "":
        hoursofworkperweek = ET.SubElement(workhistory, 'hoursofworkperweek')
        buildWorkhistoryAttributes(hoursofworkperweek)
        hoursofworkperweek.text = self.intakes['Hours-Week']

    if self.calcHourlyWage(self.intakes['MonthlyWage-CheckAmount']) <> "":
        hourlywage = ET.SubElement(workhistory, 'hourlywage')
        buildWorkhistoryAttributes(hourlywage)
        hourlywage.text = self.calcHourlyWage(self.intakes['MonthlyWage-CheckAmount'])

#        receivinghealthinsurancethisemployer = ET.SubElement(workhistory, 'receivinghealthinsurancethisemployer')
#        receivinghealthinsurancethisemployer.tail = "\n"
#        buildWorkhistoryAttributes(receivinghealthinsurancethisemployer)
#        categoryofemployment = ET.SubElement(workhistory, 'categoryofemployment')
#        categoryofemployment.tail = "\n"
#        buildWorkhistoryAttributes(categoryofemployment)
#        employersfax_1 = ET.SubElement(workhistory, 'employersfax_1')
#        employersfax_1.tail = "\n"
#        buildWorkhistoryAttributes(employersfax_1)
#        workhistorystart = ET.SubElement(workhistory, 'workhistorystart')
#        workhistorystart.tail = "\n"
#        buildWorkhistoryAttributes(workhistorystart)
        
    def createHouseholds(self, records):
    # households section
    households = ET.SubElement(records, "households")

    return households
    
    def createHousehold(self, households):
    keyval = 'household'
    sysID = self.xmlU.generateSysID(keyval)
    recID = self.xmlU.generateRecID(keyval)
    
    household = ET.SubElement(households, "household")

    # assign household attributes
    #household.attrib["record_id"] = "ROI1"
    household.attrib["record_id"] = recID
    #household.attrib["system_id"] = "roi1243a"
    household.attrib["system_id"] = sysID
    
    household.attrib["date_added"] = datetime.now().isoformat()
    household.attrib["date_updated"] = datetime.now().isoformat()
    
    Type = ET.SubElement(household, "type")
    Type.text = "familystatusPickOption" #this needs to be made dynamic

    name = ET.SubElement(household, "name")
    name.text = "tok100Type"

    
    return household
        
    def createMembers(self, household):
    members = ET.SubElement(household, "members")

    return members
    
    def createMember(self, members):
    keyval = 'member'
    #sysID = self.xmlU.generateSysID(keyval)
    recID = self.xmlU.generateRecID(keyval)
    
    member = ET.SubElement(members, "member")

    # assign household attributes
    #member.attrib["record_id"] = "ROI1"
    member.attrib["record_id"] = recID
    member.attrib["date_added"] = datetime.now().isoformat()
    member.attrib["date_updated"] = datetime.now().isoformat()
    
    return member
    
    def customizeMember(self, member):
    client_id = ET.SubElement(member, "client_id")

    date_entered = ET.SubElement(member, "date_entered")

    date_ended = ET.SubElement(member, "date_ended")

    head_of_household = ET.SubElement(member, "head_of_household")

    relationship = ET.SubElement(member, "relationship")

        
    #    return provider
        
        # wrap it in an ElementTree instance, and save as XML
#    def writeOutXML(self):
#    tree = ET.ElementTree(self.root_element)
#    if self.debug == True:
#        print "trying to write XML to: %s " % os.path.join(self.outDirectory, "page.xml")
#    tree.write(os.path.join(self.outDirectory, "page.xml"))
    
    # qs_(name goes here) is a naming convention that designates that the 
    # result of the lookup is a queryset object.  Python List/Dictionary object)
    
    #qs_Sourcedatabase = self.select_SourceDatabase(keyval)
    # first the Sourcedatabase object
        
    def current_picture(node):
        ''' Internal function.  Debugging aid for the export module.'''
        if self.debug:
        print "Current XML Picture is"
        print "======================\n" * 2
        dump(node)
        print "======================\n" * 2
    
    def getDateTimeObj(self, inputDate):
    dateParts = inputDate.split('/')
    if len(dateParts[2]) == 4:
        inputDateFmt = "%m/%d/%Y"
    else:
    # can't determine the date format, try to determine from other attributes
        if len(inputDate) == 10 or len(inputDate) == 9:
        inputDateFmt = "%m/%d/%Y"
        else:
        inputDateFmt = "%m/%d/%y"
        
    # format a Datetime Obj so we can do some math on it.
    newDate = datetime(*strptime(inputDate, inputDateFmt)[0:3])
    return newDate
        
    def fixDate(self, inputDate):
    #dateParts = strptime(s, "%m/%d/%Y")[0:3]
    #newDate = datetime(*strptime(inputDate, "%d-%b-%y")[0:3]).isoformat()
    # test the inputDate length, it might be 08/08/2007 or 08/08/07
    # SBB20091007 if the incoming date is already a Datetimeobject simply send back the isoformat
    if isinstance(inputDate, datetime) or isinstance(inputDate, date):
        return inputDate.isoformat()
        
    if inputDate == "" or inputDate == None:
        return None    
    else:
        newDate = self.getDateTimeObj(inputDate).isoformat()
        if self.debug == True:
        self.debugMessages.log("FUNCTION: fixDate() incoming date is: %s and clean date is: %s\n" % (inputDate, newDate))
        return newDate
        
    def fixDateNoTime(self, inputDate):
    #dateParts = strptime(s, "%m/%d/%Y")[0:3]
    #newDate = datetime(*strptime(inputDate, "%d-%b-%y")[0:3]).isoformat()
    # test the inputDate length, it might be 08/08/2007 or 08/08/07
    
        
    if input == "":
        print "empty date encountered!" + self
    
    else:
        newDate = self.getDateTimeObj(inputDate).date()
        if self.debug == True:
        self.debugMessages.log("FUNCTION: fixDate() incoming date is: %s and clean date is: %s\n" % (inputDate, newDate))
        return newDate
    
    def dateStringToDateObject(self, dateString):#Takes MM/DD/YYYY and turns into a standard dateTime object
    #dateString = "16/6/1981"
    date_object = time.strptime(dateString, "%d/%m/%Y")
    return date_object
        
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
    
    def convertIntegerToDate(self, intDate):
    #if intDate == "":
    #    intDate = 0
    # SBB20070628 New test, we might still have Junk in our data, need to clean up and test it.  If junk remove the value
    if not intDate.isdigit():
        if intDate == "":
        #intDate = 0
        #ECJ20071111 Had to change this so blank dates don't result in 1900-01-01
        return
        else:
        self.errorMsgs.append("WARNING: during conversion of an integer to date format this string was passed: %s which is not all numbers" % intDate)
        intDate = 0

    td = timedelta(days=int(intDate))
    # Excel dates are Days since 1900-01-01 = 1
    newDate = date(1900,01,01) + td
    if self.debug == True:
        print 'Incoming Date is: %s and converted Date is: %s' % (intDate, newDate.isoformat())

    return newDate.isoformat()
    
    def convertIntegerToDateTime(self, intDate):
    #if intDate == "":
    #    intDate = 0
    # SBB20070628 New test, we might still have Junk in our data, need to clean up and test it.  If junk remove the value
    if not intDate.isdigit():
        #ECJ20071111 Had to change this so blank dates don't result in 1900-01-01
        if intDate == "":            
        return
        else:
        self.errorMsgs.append("WARNING: during conversion of an integer to date format this string was passed: %s which is not all numbers" % intDate)
        intDate = 0

    td = timedelta(days=int(intDate))
    # Excel dates are Days since 1900-01-01 = 1
    isodate = date(1900,01,01) + td
    isodatetime = str(isodate)+'T00:00:00'
    if self.debug == True:
        print 'Incoming Date is: %s and converted Date is: %s' % (intDate, isodatetime)
    return isodatetime
    
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
        
    if self.debug == True:
        print str(round(hourlyWage,2))
        
    return str(round(hourlyWage,2))
    
    def fixMiddleInitial(self, middle_initial):
    fixed_middle_initial = str.lstrip(str.upper(middle_initial))[0]
#        if fixed_middle_initial <> middle_initial:
#            print "fixed middle_initial"
#            print middle_initial
#            print "initial middle_initial"
#            print fixed_middle_initial
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
        if self.debug == True:
            self.debugMessages.log("incoming SSN is correctly formatted: %s\n" % (incomingSSN))
            
        return incomingSSN
        else:                    # incoming SSN has 1 dash but not 2.  This is an error
        # fix this data
        incomingSSN = string.replace(incomingSSN, '-', '')
        if len(incomingSSN) < 9:
            if self.debug == True:
            self.debugMessages.log(">>>> Incoming SSN is INcorrectly formatted.  Original SSN from input file is: %s and Attempted cleaned up SSN is: %s\n" % (originalSSN, incomingSSN))
            # reformat the string and return
            theError = (1020, 'Data format error discovered in trying to cleanup incoming SSN: %s, original SSN: %s' % (incomingSSN, originalSSN))
            raise dataFormatError, theError
            
    # If we are here, we can simply reformat the string into dashes
    if self.debug == True:
        self.debugMessages.log("incoming SSN is INcorrectly formatted: %s.  Reformatting to: %s\n" % (incomingSSN, '%s-%s-%s' % (incomingSSN[0:3], incomingSSN[3:5], incomingSSN[5:10])))
    return '%s-%s-%s' % (incomingSSN[0:3], incomingSSN[3:5], incomingSSN[5:10])

    def write(self):    
        self.startTransaction()
        self.processXML()
        self.prettify()
        xmlutilities.writeOutXML()
        #self.commitTransaction()
        return True
            
if __name__ == "__main__":
    vld = HMISXML28Writer(".")
    files = vld.processXML()
    vld.prettify()
    xmlutilities.writeOutXML()
