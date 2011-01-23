'''reads an Operation PARS Extented HMIS XML Document into memory and parses its contents
storing them into a postgresql database.  This is a log database, so it holds 
everything and doesn't worry about deduplication.  The only thing it enforces 
are exportids, which must be unique.'''

'''Operation PARS extended the HMIS schema adding the ext namespace
   Person/PersonHistorical is where most additions were made
'''

'''
Additions:

personHistorical
	DrugHistory
		DrugHistoryID 
			hmis:IDStr (date)
		DrugCode (date)
		DrugUseFrequency (date)
	EmergencyContacts
		emergencyContact
			EmergencyContactID
				hmis:IDStr (date)
			EmergencyContactName (date)
			* EmergencyContactPhoneNumber (phoneNumberType, date)
			EmergencyContactAddress (date)
				hmis:AddressPeriod 
					hmis:StartDate (date)
					hmis:EndDate (date)
				hmis: Line1 (date)
				hmis: City (date)
				hmis: State (date)
			EmergencyContactRelationToClient (date)
	AnnualPersonalIncome (date)
	EmploymentStatus (date)
	FamilySize (date)
	HearingImpaired (date)
	MaritalStatus (date)
	Non-ambulatory (date)
	ResidentialStatus (date)
	VisuallyImpaired (date)

serviceEvent
	TypeOfServicePAR

siteServiceParticipation
	DischargeType (date)	
	HealthStatusAtDischarge (date)
	VAEligibility (date)

'''

import sys, os
from reader import Reader
from zope.interface import implements
from lxml import etree
#from sqlalchemy import create_engine, Table, Column, Numeric, Integer, String, Boolean, MetaData, ForeignKey, Sequence
#from sqlalchemy.orm import sessionmaker, mapper, backref, relation, clear_mappers
#from sqlalchemy.types import DateTime, Date
from sqlalchemy.exceptions import IntegrityError
import dateutil.parser
#import logging
from conf import settings
import clsexceptions
import dbobjects as dbobjects
import fileutils
from errcatalog import catalog

class PARXMLReader(dbobjects.DatabaseObjects):
    '''Implements reader interface.'''
    implements (Reader) 
    
    # define schema namespaces
    hmis_namespace = "http://www.hmis.info/schema/2_8/HUD_HMIS_2_8.xsd" 
    airs_namespace = "http://www.hmis.info/schema/2_8/AIRS_3_0_draft5_mod.xsd"
    ext_namespace = "http://xsd.alexandriaconsulting.com/cgi-bin/trac.cgi/export/344/trunk/synthesis/xsd/Operation_PAR_Extend_HUD_HMIS_2_8.xsd"
    nsmap = {"hmis" : hmis_namespace, "airs" : airs_namespace, "ext" : ext_namespace}

    def __init__(self, xml_file):
        
        # Validate that we have a valid username & password to access the database
        #if settings.DB_USER == "":
        #    raise clsexceptions.DatabaseAuthenticationError(1001, "Invalid user to access database", self.__init__)
        #if settings.DB_PASSWD == "":
        #    raise clsexceptions.DatabaseAuthenticationError(1002, "Invalid password to access database", self.__init__)
        #    
        #self.pg_db = create_engine('postgres://%s:%s@localhost:%s/%s' % (settings.DB_USER, settings.DB_PASSWD, settings.DB_PORT, settings.DB_DATABASE), echo=settings.DEBUG_ALCHEMY)#, server_side_cursors=True)
        ##self.sqlite_db = create_engine('sqlite:///:memory:', echo=True)
        self.xml_file = xml_file
        #self.db_metadata = MetaData(self.pg_db)
        ##self.db_metadata = MetaData(self.sqlite_db)
        #Session = sessionmaker(bind=self.pg_db, autoflush=True, transactional=True)
        ##Session = sessionmaker(bind=self.sqlite_db, autoflush=True, transactional=True)
        #
        #self.session = Session()
        
        ##logging.basicConfig(filename='./sql.log')
        ##logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
        ##logging.getLogger('sqlalchemy.orm.unitofwork').setLevel(logging.DEBUG) 
        #
        ## good practice to clear the mapper.  Especially when we are running our tests
        #clear_mappers()
        
        # moved all mapping ORM logic to new module/class
        dbo = dbobjects.DatabaseObjects()
        self.session = dbo.session()
        #self.export_map()
        #self.database_map()
        #self.person_map()
        #self.person_historical_map()
        #self.release_of_information_map()
        #self.income_and_sources_map()
        #self.veteran_map()
        #self.hud_homeless_episodes_map()
        #self.person_address_map()
        #self.other_names_map()
        #self.races_map()
        #self.household_map()
        #self.member_map()
        
        #only client information needed for this project
        #self.site_service_map()
        
    def read(self):
        '''Takes an XML instance file and reads it into \n
        memory as a node tree.'''
        #print 'inside read', self.xml_file
        tree = etree.parse(self.xml_file)
        #self.xml_file.close()
        return tree
        
    def process_data(self, tree):
        '''Shreds the XML document into the database.'''
        root_element = tree.getroot()
        try:
            self.parse_export(root_element)
        except IntegrityError:
            fileutils.makeBlock("CAUGHT INTEGRITY ERROR")
            err = catalog.errorCatalog[1002]
            raise clsexceptions.DuplicateXMLDocumentError, (err[0], err[1], 'process_data()'  )
        
        #test join
        #for u,a in self.session.query(Person, Export).filter(Person.export_id==Export.export_id): 
        #    print 'Person', u.export_id, 'Export', a.export_software_version
        return

    def parse_source(self, root_element):
        '''Look for a DatabaseID and related fields in the XML and persists it.'''
        #Now populate the mapping
        #Xpath query strings
        xpSourceID = '/ext:SourceDatabase/ext:DatabaseID'
        xpSourceIDIDNum = 'hmis:IDNum'
        xpSourceIDIDStr = 'hmis:IDStr'
        xpExportIDIDNum = '../ext:Export/hmis:ExportID/hmis:IDNum'
        xpExportIDIDStr = '../ext:Export/hmis:ExportID/hmis:IDStr'
        xpIDNumdateCollected = 'hmis:IDNum/@hmis:dateCollected'
        xpIDStrdateCollected = 'hmis:IDStr/@hmis:dateCollected'
        xpSourceContactEmail = '../ext:DatabaseContactEmail'
        xpSourceContactEmaildateCollected = '../ext:DatabaseContactEmail/@hmis:dateCollected'
        xpSourceContactExtension = '../ext:DatabaseContactExtension'
        xpSourceContactExtensiondateCollected = '../ext:DatabaseContactExtension/@hmis:dateCollected'
        xpSourceContactFirst = '../ext:DatabaseContactFirst'
        xpSourceContactFirstdateCollected = '../ext:DatabaseContactFirst/@hmis:dateCollected'
        xpSourceContactLast = '../ext:DatabaseContactLast'
        xpSourceContactLastdateCollected = '../ext:DatabaseContactLast/@hmis:dateCollected'
        xpSourceContactPhone = '../ext:DatabaseContactPhone'
        xpSourceContactPhonedateCollected = '../ext:DatabaseContactPhone/@hmis:dateCollected'
        xpSourceName = '../ext:DatabaseName'
        xpSourceNamedateCollected = '../ext:DatabaseName/@hmis:dateCollected'
        #find each occurrence of database_id in the XML, make a new table
        #schema allows for multiple database tags, but that's both unlikely and problematic.
        #enforce only one database tag (by only taking the first element in the list in the next line [0])
        database_id_tag = root_element.xpath(xpSourceID, namespaces={'ext': self.ext_namespace})[0]
        #and make a fake list so the code still works
        database_id_tag = [database_id_tag]
        if database_id_tag is not None:
            for item in database_id_tag:
                self.parse_dict = {}
                database_id_val = item.xpath(xpSourceIDIDNum, namespaces={'hmis': self.hmis_namespace})
                
                if len(database_id_val) is 0:
                    database_id_val = item.xpath(xpSourceIDIDStr, namespaces={'hmis': self.hmis_namespace})
                    self.parse_dict.__setitem__('source_id', database_id_val[0].text)
                    self.existence_test_and_add('source_id_date_collected', item.xpath(xpIDStrdateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                else:
                    self.parse_dict.__setitem__('source_id', database_id_val[0].text)
                    self.existence_test_and_add('source_id', item.xpath(xpIDNumdateCollected, namespaces={'hmis': self.hmis_namespace})[0], 'attribute_date')
                    
                test = item.xpath(xpExportIDIDNum, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
                if len(test) is 0:
                    self.existence_test_and_add('export_id', item.xpath(xpExportIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                else:
                    self.existence_test_and_add('export_id', test, 'text')
                self.existence_test_and_add('source_email', item.xpath(xpSourceContactEmail, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                self.existence_test_and_add('source_email_date_collected', item.xpath(xpSourceContactEmaildateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                self.existence_test_and_add('source_contact_extension', item.xpath(xpSourceContactExtension, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                self.existence_test_and_add('source_contact_extension_date_collected', item.xpath(xpSourceContactExtensiondateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                self.existence_test_and_add('source_contact_first', item.xpath(xpSourceContactFirst, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                self.existence_test_and_add('source_contact_first_date_collected', item.xpath(xpSourceContactFirstdateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                self.existence_test_and_add('source_contact_last', item.xpath(xpSourceContactLast, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                self.existence_test_and_add('source_contact_last_date_collected', item.xpath(xpSourceContactLastdateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                self.existence_test_and_add('source_contact_phone', item.xpath(xpSourceContactPhone, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                self.existence_test_and_add('source_contact_phone_date_collected', item.xpath(xpSourceContactPhonedateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                self.existence_test_and_add('source_name', item.xpath(xpSourceName, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                self.existence_test_and_add('source_name_date_collected', item.xpath(xpSourceNamedateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                self.shred(self.parse_dict, dbobjects.Source)
                #had to hard code this to just use root element, since we're not allowing multiple database_ids per XML file
                self.parse_person(root_element)
                self.parse_household(root_element)
            return
    
    def parse_export(self, root_element):
        '''Looks for an ExportID and related fields in the XML and persists it.'''      
        "this code allows for multiple export ids per file, but that's problematic."
        #Xpath query strings
        xpExport = 'ext:Export'
        xpExportIDIDNum = 'hmis:ExportID/hmis:IDNum'
        xpExportIDIDStr = 'hmis:ExportID/hmis:IDStr'
        xpIDNumdateCollected = 'hmis:ExportID/hmis:IDNum/@hmis:dateCollected'
        xpIDStrdateCollected = 'hmis:ExportID/hmis:IDStr/@hmis:dateCollected'
        xpExportExportDate = 'hmis:ExportDate'
        xpExportExportDatedateCollected = 'hmis:ExportDate/@hmis:dateCollected'
        xpExportPeriodStartDate = 'hmis:ExportPeriod/hmis:StartDate'
        xpExportPeriodStartDatedateCollected = 'hmis:ExportPeriod/hmis:StartDate/@hmis:dateCollected'
        xpExportPeriodEndDate = 'hmis:ExportPeriod/hmis:EndDate'
        xpExportPeriodEndDatedateCollected = 'hmis:ExportPeriod/hmis:EndDate/@hmis:dateCollected'
        xpExportSoftwareVendor = 'hmis:SoftwareVendor'
        xpExportSoftwareVendordateCollected = 'hmis:SoftwareVendor/@hmis:dateCollected'
        xpExportSoftwareVendor = 'hmis:SoftwareVendor'
        xpExportSoftwareVendordateCollected = 'hmis:SoftwareVendor/@hmis:dateCollected'
        xpExportSoftwareVersion = 'hmis:SoftwareVersion'
        xpExportSoftwareVersiondateCollected = 'hmis:SoftwareVersion/@hmis:dateCollected'
        
        "enforce only one export tag (by only taking the first element in the list in the next line [0])"
        export = root_element.xpath(xpExport, namespaces={'ext': self.ext_namespace})[0]
        #and make a fake list so the code still works
        export = [export]
        if export is not None:
            for item in export:
                self.parse_dict = {}
                test = item.xpath(xpExportIDIDNum, namespaces={'hmis': self.hmis_namespace}) 
                if len(test) is 0:
                    test = item.xpath(xpExportIDIDStr, namespaces={'hmis': self.hmis_namespace})
                    self.export_id = test
                    value = self.existence_test_and_add('export_id', test, 'text')
                    self.existence_test_and_add('export_id_date_collected', item.xpath(xpIDStrdateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                else:
                    self.export_id = test
                    self.existence_test_and_add('export_id', test, 'text')
                    self.existence_test_and_add('export_id_date_collected', item.xpath(xpIDNumdateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')    
                self.existence_test_and_add('export_date', item.xpath(xpExportExportDate, namespaces={'hmis': self.hmis_namespace}), 'element_date') 
                self.existence_test_and_add('export_date_date_collected', item.xpath(xpExportExportDatedateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                self.existence_test_and_add('export_period_start_date', item.xpath(xpExportPeriodStartDate, namespaces={'hmis': self.hmis_namespace}), 'element_date')
                self.existence_test_and_add('export_period_start_date_date_collected', item.xpath(xpExportPeriodStartDatedateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                self.existence_test_and_add('export_period_end_date', item.xpath(xpExportPeriodEndDate, namespaces={'hmis': self.hmis_namespace}), 'element_date')
                self.existence_test_and_add('export_period_end_date_date_collected', item.xpath(xpExportPeriodEndDatedateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                self.existence_test_and_add('export_software_vendor', item.xpath(xpExportSoftwareVendor, namespaces={'hmis': self.hmis_namespace}), 'text')
                self.existence_test_and_add('export_software_vendor_date_collected', item.xpath(xpExportSoftwareVendordateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                self.existence_test_and_add('export_software_version', item.xpath(xpExportSoftwareVersion, namespaces={'hmis': self.hmis_namespace}), 'text')
                self.existence_test_and_add('export_software_version_date_collected', item.xpath(xpExportSoftwareVersiondateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
#                self.session.flush()
#                print 'export id is', Export.c.id
                self.shred(self.parse_dict, dbobjects.Export)
                self.parse_source(root_element)
                #current projects only using client sections, not resources    
                #self.parse_site_service(database_id_tag)

        #current projects only using client sections, not resources      
        else:
            self.shred(self.parse_dict, dbobjects.Export)
            return

    def parse_other_names(self, person_tag):
        '''Looks for an OtherNames tag and related fields in the XML and persists it.'''      
        '''This code allows for multiple OtherNames per Person'''
        #Xpath query strings
        xpOtherNames = 'ext:OtherNames'
        #I don't want the PersonID from the XML, as there could be two of the 
        #same PersonID within the same export.  Need the Person Table Index
        #So that's what is used.  See where this index is retrieved after the 
        #session flush.
        xpOtherFirstNameUnhashed = 'hmis:OtherFirstName/hmis:Unhashed'
        xpOtherFirstNameHashed = 'hmis:OtherFirstName/hmis:Hashed'
        xpOtherFirstNameDateCollectedUnhashed = 'hmis:OtherFirstName/hmis:Unhashed/@hmis:dateCollected'
        xpOtherFirstNameDateCollectedHashed = 'hmis:OtherFirstName/hmis:Hashed/@hmis:dateCollected'
        xpOtherLastNameUnhashed = 'hmis:OtherLastName/hmis:Unhashed'
        xpOtherLastNameHashed = 'hmis:OtherLastName/hmis:Hashed'
        xpOtherLastNameDateCollectedUnhashed = 'hmis:OtherLastName/hmis:Unhashed/@hmis:dateCollected'
        xpOtherLastNameDateCollectedHashed = 'hmis:OtherLastName/hmis:Hashed/@hmis:dateCollected'        
        xpOtherMiddleNameUnhashed = 'hmis:OtherMiddleName/hmis:Unhashed'
        xpOtherMiddleNameHashed = 'hmis:OtherMiddleName/hmis:Hashed'
        xpOtherMiddleNameDateCollectedUnhashed = 'hmis:OtherMiddleName/hmis:Unhashed/@hmis:dateCollected'
        xpOtherMiddleNameDateCollectedHashed = 'hmis:OtherMiddleName/hmis:Hashed/@hmis:dateCollected'
        xpOtherSuffixUnhashed = 'hmis:OtherSuffix/hmis:Unhashed'
        xpOtherSuffixHashed = 'hmis:OtherSuffix/hmis:Hashed'
        xpOtherSuffixDateCollectedUnhashed = 'hmis:OtherSuffix/hmis:Unhashed/@hmis:dateCollected'
        xpOtherSuffixDateCollectedHashed = 'hmis:OtherSuffix/hmis:Hashed/@hmis:dateCollected'
        
        other_names = person_tag.xpath(xpOtherNames, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
        if other_names is not None:
            for item in other_names:
                self.parse_dict = {}
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                test = self.existence_test_and_add('other_first_name_unhashed', item.xpath(xpOtherFirstNameUnhashed, namespaces={'hmis': self.hmis_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('other_first_name_date_collected', item.xpath(xpOtherFirstNameDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace}),'attribute_date')
                if test is False:
                    test = self.existence_test_and_add('other_first_name_hashed', item.xpath(xpOtherFirstNameHashed, namespaces={'hmis': self.hmis_namespace}), 'text')
                    self.existence_test_and_add('other_first_name_date_collected', item.xpath(xpOtherFirstNameDateCollectedHashed, namespaces={'hmis': self.hmis_namespace}),'attribute_date')
                test = self.existence_test_and_add('other_last_name_unhashed', item.xpath(xpOtherLastNameUnhashed, namespaces={'hmis': self.hmis_namespace}),'text')
                if test is True:
                    self.existence_test_and_add('other_last_name_date_collected', item.xpath(xpOtherLastNameDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace}),'attribute_date')
                if test is False:
                    self.existence_test_and_add('other_last_name_hashed', item.xpath(xpOtherLastNameHashed, namespaces={'hmis': self.hmis_namespace}),'text')
                    self.existence_test_and_add('other_last_name_date_collected', item.xpath(xpOtherLastNameDateCollectedHashed, namespaces={'hmis': self.hmis_namespace}),'attribute_date')
                test = self.existence_test_and_add('other_middle_name_unhashed', item.xpath(xpOtherMiddleNameUnhashed, namespaces={'hmis': self.hmis_namespace}),'text')
                if test is True:
                    self.existence_test_and_add('other_middle_name_date_collected', item.xpath(xpOtherMiddleNameDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace}),'attribute_date')
                if test is False:
                    self.existence_test_and_add('other_middle_name_hashed', item.xpath(xpOtherMiddleNameHashed, namespaces={'hmis': self.hmis_namespace}),'text')
                    self.existence_test_and_add('other_middle_name_date_collected', item.xpath(xpOtherMiddleNameDateCollectedHashed, namespaces={'hmis': self.hmis_namespace}),'attribute_date')
                test = self.existence_test_and_add('other_suffix_unhashed', item.xpath(xpOtherSuffixUnhashed, namespaces={'hmis': self.hmis_namespace}),'text')
                if test is True:
                    self.existence_test_and_add('other_suffix_date_collected', item.xpath(xpOtherSuffixDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace}),'attribute_date')
                if test is False:
                    self.existence_test_and_add('other_suffix_hashed', item.xpath(xpOtherSuffixHashed, namespaces={'hmis': self.hmis_namespace}),'text')
                    self.existence_test_and_add('other_suffix_date_collected', item.xpath(xpOtherSuffixDateCollectedHashed, namespaces={'hmis': self.hmis_namespace}),'attribute_date')
                self.shred(self.parse_dict, dbobjects.OtherNames)
        else:
            self.shred(self.parse_dict, dbobjects.OtherNames)
            return
        
    
    def parse_hud_homeless_episodes(self, element):
        ### xpPath Definitions
            xpHudHomelessEpisodes = 'hmis:HUDHomelessEpisodes'
        ### StartDate
            xpStartDate = 'hmis:StartDate'
            xpStartDateDateCollected = 'hmis:StartDate/@hmis:dateCollected'
        ### EndDate
            xpEndDate = 'hmis:EndDate'
            xpEndDateDateCollected = 'hmis:EndDate/@hmis:dateCollected'
        
        ### xpPath Parsing
            itemElements = element.xpath(xpHudHomelessEpisodes, namespaces={'hmis': self.hmis_namespace})
            if itemElements is not None:
                for item in itemElements:
                ### StartDate
                    fldName='start_date'
                    self.existence_test_and_add(fldName, item.xpath(xpStartDate, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='start_date_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpStartDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### EndDate
                    fldName='end_date'
                    self.existence_test_and_add(fldName, item.xpath(xpEndDate, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='end_date_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpEndDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                    
                    self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                    
                ### HudHomelessEpisodes (Shred)
                    self.shred(self.parse_dict, dbobjects.HUDHomelessEpisodes)

        ### Parse any subtables
    def parse_veteran(self, element):
    ### xpPath Definitions
        xpVeteran = 'hmis:Veteran'
    ### ServiceEra
        xpServiceEra = 'hmis:ServiceEra'
        xpServiceEraDateCollected = 'hmis:ServiceEra/@hmis:dateCollected'
    ### MilitaryServiceDuration
        xpMilitaryServiceDuration = 'hmis:MilitaryServiceDuration'
        xpMilitaryServiceDurationDateCollected = 'hmis:MilitaryServiceDuration/@hmis:dateCollected'
    ### ServedInWarZone
        xpServedInWarZone = 'hmis:ServedInWarZone'
        xpServedInWarZoneDateCollected = 'hmis:ServedInWarZone/@hmis:dateCollected'
    ### WarZone
        xpWarZone = 'hmis:WarZone'
        xpWarZoneDateCollected = 'hmis:WarZone/@hmis:dateCollected'
    ### WarZoneOther
        xpWarZoneOther = 'hmis:WarZoneOther'
        xpWarZoneOtherDateCollected = 'hmis:WarZoneOther/@hmis:dateCollected'
    ### MonthsInWarZone
        xpMonthsInWarZone = 'hmis:MonthsInWarZone'
        xpMonthsInWarZoneDateCollected = 'hmis:MonthsInWarZone/@hmis:dateCollected'
    ### ReceivedFire
        xpReceivedFire = 'hmis:ReceivedFire'
        xpReceivedFireDateCollected = 'hmis:ReceivedFire/@hmis:dateCollected'
    ### MilitaryBranch
        xpMilitaryBranch = 'hmis:MilitaryBranch'
        xpMilitaryBranchDateCollected = 'hmis:MilitaryBranch/@hmis:dateCollected'
    ### MilitaryBranchOther
        xpMilitaryBranchOther = 'hmis:MilitaryBranchOther'
        xpMilitaryBranchOtherDateCollected = 'hmis:MilitaryBranchOther/@hmis:dateCollected'
    ### DischargeStatus
        xpDischargeStatus = 'hmis:DischargeStatus'
        xpDischargeStatusDateCollected = 'hmis:DischargeStatus/@hmis:dateCollected'
    ### DischargeStatusOther
        xpDischargeStatusOther = 'hmis:DischargeStatusOther'
        xpDischargeStatusOtherDateCollected = 'hmis:DischargeStatusOther/@hmis:dateCollected'
        
    ### xpPath Parsing
        itemElements = element.xpath(xpVeteran, namespaces={'hmis': self.hmis_namespace})
        
        if itemElements is not None:
            for item in itemElements:
            ### ServiceEra
                fldName='service_era'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEra, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_era_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEraDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### MilitaryServiceDuration
                fldName='military_service_duration'
                self.existence_test_and_add(fldName, item.xpath(xpMilitaryServiceDuration, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='military_service_duration_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpMilitaryServiceDurationDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ServedInWarZone
                fldName='served_in_war_zone'
                self.existence_test_and_add(fldName, item.xpath(xpServedInWarZone, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='served_in_war_zone_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServedInWarZoneDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### WarZone
                fldName='war_zone'
                self.existence_test_and_add(fldName, item.xpath(xpWarZone, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='war_zone_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpWarZoneDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### WarZoneOther
                fldName='war_zone_other'
                self.existence_test_and_add(fldName, item.xpath(xpWarZoneOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='war_zone_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpWarZoneOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### MonthsInWarZone
                fldName='months_in_war_zone'
                self.existence_test_and_add(fldName, item.xpath(xpMonthsInWarZone, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='months_in_war_zone_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpMonthsInWarZoneDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ReceivedFire
                fldName='received_fire'
                self.existence_test_and_add(fldName, item.xpath(xpReceivedFire, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='received_fire_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpReceivedFireDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### MilitaryBranch
                fldName='military_branch'
                self.existence_test_and_add(fldName, item.xpath(xpMilitaryBranch, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='military_branch_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpMilitaryBranchDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### MilitaryBranchOther
                fldName='military_branch_other'
                self.existence_test_and_add(fldName, item.xpath(xpMilitaryBranchOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='military_branch_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpMilitaryBranchOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### DischargeStatus
                fldName='discharge_status'
                self.existence_test_and_add(fldName, item.xpath(xpDischargeStatus, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='discharge_status_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDischargeStatusDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### DischargeStatusOther
                fldName='discharge_status_other'
                self.existence_test_and_add(fldName, item.xpath(xpDischargeStatusOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='discharge_status_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDischargeStatusOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
    
            ### Veteran (Shred)
                self.shred(self.parse_dict, dbobjects.Veteran)
    
    def parse_person_address(self, element):
        ### xpPath Definitions
            xpPersonAddress = 'hmis:PersonAddress'
        ### StartDate
            xpAddressPeriodStartDate = 'hmis:AddressPeriod/hmis:StartDate'
            xpAddressPeriodStartDateDateCollected = 'hmis:AddressPeriod/hmis:StartDate/@hmis:dateCollected'
        ### EndDate
            xpAddressPeriodEndDate = 'hmis:AddressPeriod/hmis:EndDate'
            xpAddressPeriodEndDateDateCollected = 'hmis:AddressPeriod/hmis:EndDate/@hmis:dateCollected'
        ### PreAddressLine
            xpPreAddressLine = 'hmis:PreAddressLine'
            xpPreAddressLineDateCollected = 'hmis:PreAddressLine/@hmis:dateCollected'
        ### Line1
            xpLine1 = 'hmis:Line1'
            xpLine1DateCollected = 'hmis:Line1/@hmis:dateCollected'
        ### Line2
            xpLine2 = 'hmis:Line2'
            xpLine2DateCollected = 'hmis:Line2/@hmis:dateCollected'
            ### City
            xpCity = 'hmis:City'
            xpCityDateCollected = 'hmis:City/@hmis:dateCollected'
            ### County
            xpCounty = 'hmis:County'
            xpCountyDateCollected = 'hmis:County/@hmis:dateCollected'
            ### State
            xpState = 'hmis:State'
            xpStateDateCollected = 'hmis:State/@hmis:dateCollected'
            ### ZIPCode
            xpZIPCode = 'hmis:ZIPCode'
            xpZIPCodeDateCollected = 'hmis:ZIPCode/@hmis:dateCollected'
            ### Country
            xpCountry = 'hmis:Country'
            xpCountryDateCollected = 'hmis:Country/@hmis:dateCollected'
            
            #*# is_last_permanent_zip
            xpIsLastPermanentZip = 'hmis:IsLastPermanentZIP'
            xpIsLastPermanentZipDateCollected = 'hmis:IsLastPermanentZIP/@hmis:dateCollected'
            
            #*# zip_quality_code
            xpZipQualityCode = 'hmis:ZIPQualityCode'
            xpZipQualityCodeDateCollected = 'hmis:ZIPQualityCode/@hmis:dateCollected'

            ### xpPath Parsing
            itemElements = element.xpath(xpPersonAddress, namespaces={'hmis': self.hmis_namespace})
            if itemElements is not None:
                for item in itemElements:
                    
                ### StartDate
                    test = item.xpath(xpAddressPeriodStartDate, namespaces={'hmis': self.hmis_namespace})
                    if len(test) > 0:
                        fldName='address_period_start_date'
                        self.existence_test_and_add(fldName, item.xpath(xpAddressPeriodStartDate, namespaces={'hmis': self.hmis_namespace}), 'element_date')
                        fldName='address_period_start_date_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpAddressPeriodStartDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                    
                ### EndDate
                    test = item.xpath(xpAddressPeriodEndDate, namespaces={'hmis': self.hmis_namespace})
                    if len(test) > 0:
                        fldName='address_period_end_date'
                        self.existence_test_and_add(fldName, item.xpath(xpAddressPeriodEndDate, namespaces={'hmis': self.hmis_namespace}), 'element_date')
                        fldName='address_period_end_date_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpAddressPeriodEndDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                    
                ### PreAddressLine
                    fldName='pre_address_line'
                    self.existence_test_and_add(fldName, item.xpath(xpPreAddressLine, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='pre_address_line_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpPreAddressLineDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### Line1
                    fldName='line1'
                    self.existence_test_and_add(fldName, item.xpath(xpLine1, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='line1_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpLine1DateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### Line2
                    fldName='line2'
                    self.existence_test_and_add(fldName, item.xpath(xpLine2, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='line2_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpLine2DateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### City
                    fldName='city'
                    self.existence_test_and_add(fldName, item.xpath(xpCity, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='city_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpCityDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### County
                    fldName='county'
                    self.existence_test_and_add(fldName, item.xpath(xpCounty, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='county_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpCountyDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### State
                    fldName='state'
                    self.existence_test_and_add(fldName, item.xpath(xpState, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='state_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpStateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### ZIPCode
                    fldName='zipcode'
                    self.existence_test_and_add(fldName, item.xpath(xpZIPCode, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='zipcode_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpZIPCodeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### Country
                    fldName='country'
                    self.existence_test_and_add(fldName, item.xpath(xpCountry, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='country_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpCountryDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                    
                ### IsLastPermanentZip
                    fldName='is_last_permanent_zip'
                    self.existence_test_and_add(fldName, item.xpath(xpIsLastPermanentZip, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='is_last_permanent_zip_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpIsLastPermanentZipDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                    
                ### ZipQualityCode
                    fldName='zip_quality_code'
                    self.existence_test_and_add(fldName, item.xpath(xpZipQualityCode, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='zip_quality_code_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpZipQualityCodeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')

                    self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                    ### PersonAddress (Shred)
                    self.shred(self.parse_dict, dbobjects.PersonAddress)
            
    def parse_income_and_sources(self, item):
        ### xpPath Definitions
        ### Amount
            xpIncomeAndSources = 'hmis:IncomeAndSources'
            xpAmount = 'hmis:Amount'
            xpAmountDateCollected = 'hmis:Amount/@hmis:dateCollected'
        ### IncomeSourceCode
            xpIncomeSourceCode = 'hmis:IncomeSourceCode'
            xpIncomeSourceCodeDateCollected = 'hmis:IncomeSourceCode/@hmis:dateCollected'
        ### IncomeSourceOther
            xpIncomeSourceOther = 'hmis:IncomeSourceOther'
            xpIncomeSourceOtherDateCollected = 'hmis:IncomeSourceOther/@hmis:dateCollected'
            
        ### xpPath Parsing
            incomeSources =  item.xpath(xpIncomeAndSources, namespaces={'hmis': self.hmis_namespace})
            
            if incomeSources is not None:
                for income in incomeSources:
                ### Amount
                    fldName='amount'
                    self.existence_test_and_add(fldName, income.xpath(xpAmount, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='amount_date_collected'
                    self.existence_test_and_add(fldName, income.xpath(xpAmountDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### IncomeSourceCode
                    fldName='income_source_code'
                    self.existence_test_and_add(fldName, income.xpath(xpIncomeSourceCode, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='income_source_code_date_collected'
                    self.existence_test_and_add(fldName, income.xpath(xpIncomeSourceCodeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### IncomeSourceOther
                    fldName='income_source_other'
                    self.existence_test_and_add(fldName, income.xpath(xpIncomeSourceOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='income_source_other_date_collected'
                    self.existence_test_and_add(fldName, income.xpath(xpIncomeSourceOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            
                    self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
        
                ### IncomeAndSources (Shred)
                    self.shred(self.parse_dict, dbobjects.IncomeAndSources)

    def parse_emergency_contact(self, element):
        ### xpPath Definitions
            xpEmergencyContacts = 'ext:EmergencyContacts/ext:EmergencyContact'
        ### EmergencyContactID
            xpEmergencyContactID = 'ext:EmergencyContactID/hmis:IDStr'
            xpEmergencyContactIDDateCollected = 'ext:EmergencyContactID/hmis:IDStr/@hmis:dateCollected'        
        ### EmergencyContactName
            xpEmergencyContactName = 'ext:EmergencyContactName'
            xpEmergencyContactNameDateCollected = 'ext:EmergencyContactName/@hmis:dateCollected'

            '''EmergencyContactPhoneNumber is maxOccurs="unbounded" 
               If more than 2 will be entered, this must be separated
               into a seperate table
            '''
            
        ### EmergencyContactPhoneNumber-0
            xpEmergencyContactPhoneNumber0 = 'ext:EmergencyContactPhoneNumber[1]'
            xpEmergencyContactPhoneNumberDateCollected0 = 'ext:EmergencyContactPhoneNumber[1]/@hmis:dateCollected'
            xpEmergencyContactPhoneNumberType0 = 'ext:EmergencyContactPhoneNumber[1]/@phoneNumberType'            

        ### EmergencyContactPhoneNumber-1
            xpEmergencyContactPhoneNumber1 = 'ext:EmergencyContactPhoneNumber[2]'
            xpEmergencyContactPhoneNumberDateCollected1 = 'ext:EmergencyContactPhoneNumber[2]/@hmis:dateCollected'
            xpEmergencyContactPhoneNumberType1 = 'ext:EmergencyContactPhoneNumber[2]/@phoneNumberType' 
                        
        ### StartDate
            xpEmergencyContactAddressPeriodStartDate = 'ext:EmergencyContactAddress/hmis:AddressPeriod/hmis:StartDate'
            xpEmergencyContactAddressPeriodStartDateDateCollected = 'ext:EmergencyContactAddress/hmis:AddressPeriod/hmis:StartDate/@hmis:dateCollected'
        ### EndDate
            xpEmergencyContactAddressPeriodEndDate = 'ext:EmergencyContactAddress/hmis:AddressPeriod/hmis:EndDate'
            xpEmergencyContactAddressPeriodEndDateDateCollected = 'ext:EmergencyContactAddress/hmis:AddressPeriod/hmis:EndDate/@hmis:dateCollected'

        ### Line1
            xpLine1 = 'ext:EmergencyContactAddress/hmis:Line1'
            xpLine1DateCollected = 'ext:EmergencyContactAddress/hmis:Line1/@hmis:dateCollected'
        ### Line2
            xpLine2 = 'ext:EmergencyContactAddress/hmis:Line2'
            xpLine2DateCollected = 'ext:EmergencyContactAddress/hmis:Line2/@hmis:dateCollected'
        ### City
            xpCity = 'ext:EmergencyContactAddress/hmis:City'
            xpCityDateCollected = 'ext:EmergencyContactAddress/hmis:City/@hmis:dateCollected'
        ### State
            xpState = 'ext:EmergencyContactAddress/hmis:State'
            xpStateDateCollected = 'ext:EmergencyContactAddress/hmis:State/@hmis:dateCollected'
            
        ### EmergencyContactRelationToClient
            xpEmergencyContactRelationToClient = 'ext:EmergencyContactRelationToClient'
            xpEmergencyContactRelationToClientDateCollected = 'ext:EmergencyContactRelationToClient/@hmis:dateCollected'

            ### xpPath Parsing
            itemElements = element.xpath(xpEmergencyContacts, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace})
            if itemElements is not None:
                for item in itemElements:
                    
                ### StartDate
                    test = item.xpath(xpEmergencyContactAddressPeriodStartDate, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace})
                    if len(test) > 0:
                        fldName='emergency_contact_address_period_start_date'
                        self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactAddressPeriodStartDate, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'element_date')
                        fldName='emergency_contact_address_period_start_date_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactAddressPeriodStartDateDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')
                    
                ### EndDate
                    test = item.xpath(xpEmergencyContactAddressPeriodEndDate, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace})
                    if len(test) > 0:
                        fldName='emergency_contact_address_period_end_date'
                        self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactAddressPeriodEndDate, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'element_date')
                        fldName='emergency_contact_address_period_end_date_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactAddressPeriodEndDateDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')
                    
                
                ### EmergencyContactID
                    fldName='emergency_contact_id'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactID, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_id_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactIDDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')

                ### EmergencyContactName
                    fldName='emergency_contact_name'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactName, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_name_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactNameDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')
                ### EmergencyContactPhoneNumber-0
                    fldName='emergency_contact_phone_number_0'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactPhoneNumber0, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_phone_number_date_collected_0'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactPhoneNumberDateCollected0, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                    
                    fldName='emergency_contact_phone_number_type_0'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactPhoneNumberType0, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_text')
                ### EmergencyContactPhoneNumber-1
                    fldName='emergency_contact_phone_number_1'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactPhoneNumber1, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_phone_number_date_collected_1'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactPhoneNumberDateCollected1, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                    
                    fldName='emergency_contact_phone_number_type_1'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactPhoneNumberType1, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_text')         
                ### Line1
                    fldName='emergency_contact_address_line1'
                    self.existence_test_and_add(fldName, item.xpath(xpLine1, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_address_line1_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpLine1DateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')
                ### Line2
                    fldName='emergency_contact_address_line2'
                    self.existence_test_and_add(fldName, item.xpath(xpLine2, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_address_line2_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpLine2DateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')
                ### City
                    fldName='emergency_contact_address_city'
                    self.existence_test_and_add(fldName, item.xpath(xpCity, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_address_city_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpCityDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')
                ### State
                    fldName='emergency_contact_address_state'
                    self.existence_test_and_add(fldName, item.xpath(xpState, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_address_state_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpStateDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')
                    

                ### EmergencyContactRelationToClient
                    fldName='emergency_contact_relation_to_client'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactRelationToClient, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                    fldName='emergency_contact_relation_to_client_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpEmergencyContactRelationToClientDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')

                    self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                    ### EmergencyContact (Shred)
                    self.shred(self.parse_dict, dbobjects.EmergencyContact)    
                        
    def parse_drug_history(self, element):
        ### xpPath Definitions
            xpDrugHistory = 'ext:DrugHistory'
        ### ID
            xpDrugHistoryID = 'ext:DrugHistoryID/hmis:IDStr'
            xpDrugHistoryIDDateCollected = 'ext:DrugHistoryID/hmis:IDStr/@hmis:dateCollected'
        ### DrugCode
            xpDrugCode = 'ext:DrugCode'
            xpDrugCodeDateCollected = 'ext:DrugCode/@hmis:dateCollected'
        ### DrugUseFrequency
            xpDrugUseFrequency = 'ext:DrugUseFrequency'
            xpDrugUseFrequencyDateCollected = 'ext:DrugUseFrequency/@hmis:dateCollected'

            ### xpPath Parsing
            itemElements = element.xpath(xpDrugHistory, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace})
            if itemElements is not None:
                for item in itemElements:

                ### DrugHistoryID
                    test = item.xpath(xpDrugHistoryID, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace})
                    if len(test) > 0:
                        fldName='drug_history_id'
                        self.existence_test_and_add(fldName, item.xpath(xpDrugHistoryID, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                        fldName='drug_history_id_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpDrugHistoryIDDateCollected, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')

                ### DrugCode
                    test = item.xpath(xpDrugCode, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace})
                    if len(test) > 0:
                        fldName='drug_code'
                        self.existence_test_and_add(fldName, item.xpath(xpDrugCode, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                        fldName='drug_code_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpDrugCodeDateCollected, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')

                ### DrugUseFrequency
                    test = item.xpath(xpDrugUseFrequency, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace})
                    if len(test) > 0:
                        fldName='drug_use_frequency'
                        self.existence_test_and_add(fldName, item.xpath(xpDrugUseFrequency, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                        fldName='drug_use_frequency_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpDrugUseFrequencyDateCollected, namespaces={'ext':self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')

                    self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')

                    ### PersonAddress (Shred)
                    self.shred(self.parse_dict, dbobjects.DrugHistory)

    def parse_person_historical(self, person_tag):
        '''Looks for an PersonHistorical tag and related fields in the XML and persists it.'''      
        '''This code allows for multiple PersonHistorical per Person'''
        #Xpath query strings
        
    ### xpPath Definitions
        xpSvcParticipationPersonHistorical = 'ext:SiteServiceParticipation/ext:PersonHistorical'
        xpPersonHistorical = 'ext:PersonHistorical'
        #I don't want the PersonID from the XML, as there could be two of the 
        #same PersonID within the same export.  Need the Person Table Index
        #So that's what is used.  See where this index is retrieved after the 
        #session flush.
        
    ### PersonHistoricalIDIDNum
        xpPersonHistoricalIDIDNum = 'hmis:PersonHistoricalID/hmis:IDNum'
        xpPersonHistoricalIDIDNumDateCollected = 'hmis:PersonHistoricalID/hmis:IDNum/@hmis:dateCollected'
    ### PersonHistoricalIDIDStr
        xpPersonHistoricalIDIDStr = 'hmis:PersonHistoricalID/hmis:IDStr'
        xpPersonHistoricalIDIDStrDateCollected = 'hmis:PersonHistoricalID/hmis:IDStr/@hmis:dateCollected'
    ### BarrierCode
        xpBarrierCode = 'hmis:BarrierCode'
        xpBarrierCodeDateCollected = 'hmis:BarrierCode/@hmis:dateCollected'
    ### BarrierOther
        xpBarrierOther = 'hmis:BarrierOther'
        xpBarrierOtherDateCollected = 'hmis:BarrierOther/@hmis:dateCollected'
    ### ChildCurrentlyEnrolledInSchool
        xpChildCurrentlyEnrolledInSchool = 'hmis:ChildCurrentlyEnrolledInSchool'
        xpChildCurrentlyEnrolledInSchoolDateCollected = 'hmis:ChildCurrentlyEnrolledInSchool/@hmis:dateCollected'
    ### CurrentlyEmployed
        xpCurrentlyEmployed = 'hmis:CurrentlyEmployed'
        xpCurrentlyEmployedDateCollected = 'hmis:CurrentlyEmployed/@hmis:dateCollected'
    ### CurrentlyInSchool
        xpCurrentlyInSchool = 'hmis:CurrentlyInSchool'
        xpCurrentlyInSchoolDateCollected = 'hmis:CurrentlyInSchool/@hmis:dateCollected'
    ### DegreeCode
        xpDegreeCode = 'hmis:DegreeCode'
        xpDegreeCodeDateCollected = 'hmis:DegreeCode/@hmis:dateCollected'
    ### DegreeOther
        xpDegreeOther = 'hmis:DegreeOther'
        xpDegreeOtherDateCollected = 'hmis:DegreeOther/@hmis:dateCollected'
    ### DevelopmentalDisability
        xpDevelopmentalDisability = 'hmis:DevelopmentalDisability'
        xpDevelopmentalDisabilityDateCollected = 'hmis:DevelopmentalDisability/@hmis:dateCollected'
    ### DomesticViolence
        xpDomesticViolence = 'hmis:DomesticViolence'
        xpDomesticViolenceDateCollected = 'hmis:DomesticViolence/@hmis:dateCollected'
    ### DomesticViolenceHowLong
        xpDomesticViolenceHowLong = 'hmis:DomesticViolenceHowLong'
        xpDomesticViolenceHowLongDateCollected = 'hmis:DomesticViolenceHowLong/@hmis:dateCollected'
    ### DueDate
        xpDueDate = 'hmis:DueDate'
        xpDueDateDateCollected = 'hmis:DueDate/@hmis:dateCollected'
    ### EmploymentTenure
        xpEmploymentTenure = 'hmis:EmploymentTenure'
        xpEmploymentTenureDateCollected = 'hmis:EmploymentTenure/@hmis:dateCollected'
    ### HealthStatus
        xpHealthStatus = 'hmis:HealthStatus'
        xpHealthStatusDateCollected = 'hmis:HealthStatus/@hmis:dateCollected'
    ### HighestSchoolLevel
        xpHighestSchoolLevel = 'hmis:HighestSchoolLevel'
        xpHighestSchoolLevelDateCollected = 'hmis:HighestSchoolLevel/@hmis:dateCollected'
    ### HIVAIDSStatus
        xpHIVAIDSStatus = 'hmis:HIVAIDSStatus'
        xpHIVAIDSStatusDateCollected = 'hmis:HIVAIDSStatus/@hmis:dateCollected'
    ### HoursWorkedLastWeek
        xpHoursWorkedLastWeek = 'hmis:HoursWorkedLastWeek'
        xpHoursWorkedLastWeekDateCollected = 'hmis:HoursWorkedLastWeek/@hmis:dateCollected'
    ### HUDChronicHomeless
        xpHUDChronicHomeless = 'hmis:HUDChronicHomeless'
        xpHUDChronicHomelessDateCollected = 'hmis:HUDChronicHomeless/@hmis:dateCollected'
    ### HUDHomeless
        xpHUDHomeless = 'hmis:HUDHomeless'
        xpHUDHomelessDateCollected = 'hmis:HUDHomeless/@hmis:dateCollected'
    ### LengthOfStayAtPriorResidence
        xpLengthOfStayAtPriorResidence = 'hmis:LengthOfStayAtPriorResidence'
        xpLengthOfStayAtPriorResidenceDateCollected = 'hmis:LengthOfStayAtPriorResidence/@hmis:dateCollected'
    ### LookingForWork
        xpLookingForWork = 'hmis:LookingForWork'
        xpLookingForWorkDateCollected = 'hmis:LookingForWork/@hmis:dateCollected'
    ### MentalHealthIndefinite
        xpMentalHealthIndefinite = 'hmis:MentalHealthIndefinite'
        xpMentalHealthIndefiniteDateCollected = 'hmis:MentalHealthIndefinite/@hmis:dateCollected'
    ### MentalHealthProblem
        xpMentalHealthProblem = 'hmis:MentalHealthProblem'
        xpMentalHealthProblemDateCollected = 'hmis:MentalHealthProblem/@hmis:dateCollected'
    ### NonCashSourceCode
        xpNonCashSourceCode = 'hmis:NonCashSourceCode'
        xpNonCashSourceCodeDateCollected = 'hmis:NonCashSourceCode/@hmis:dateCollected'
    ### NonCashSourceOther
        xpNonCashSourceOther = 'hmis:NonCashSourceOther'
        xpNonCashSourceOtherDateCollected = 'hmis:NonCashSourceOther/@hmis:dateCollected'
    ### PersonEmail
        xpPersonEmail = 'hmis:PersonEmail'
        xpPersonEmailDateCollected = 'hmis:PersonEmail/@hmis:dateCollected'
    ### PersonPhoneNumber
        xpPersonPhoneNumber = 'hmis:PersonPhoneNumber'
        xpPersonPhoneNumberDateCollected = 'hmis:PersonPhoneNumber/@hmis:dateCollected'
    ### PhysicalDisability
        xpPhysicalDisability = 'hmis:PhysicalDisability'
        xpPhysicalDisabilityDateCollected = 'hmis:PhysicalDisability/@hmis:dateCollected'
    ### PregnancyStatus
        xpPregnancyStatus = 'hmis:PregnancyStatus'
        xpPregnancyStatusDateCollected = 'hmis:PregnancyStatus/@hmis:dateCollected'
    ### PriorResidence
        xpPriorResidence = 'hmis:PriorResidence'
        xpPriorResidenceDateCollected = 'hmis:PriorResidence/@hmis:dateCollected'
    ### PriorResidenceOther
        xpPriorResidenceOther = 'hmis:PriorResidenceOther'
        xpPriorResidenceOtherDateCollected = 'hmis:PriorResidenceOther/@hmis:dateCollected'
    ### ReasonForLeaving
        xpReasonForLeaving = 'hmis:ReasonForLeaving'
        xpReasonForLeavingDateCollected = 'hmis:ReasonForLeaving/@hmis:dateCollected'
    ### ReasonForLeavingOther
        xpReasonForLeavingOther = 'hmis:ReasonForLeavingOther'
        xpReasonForLeavingOtherDateCollected = 'hmis:ReasonForLeavingOther/@hmis:dateCollected'
    ### SchoolLastEnrolledDate
        xpSchoolLastEnrolledDate = 'hmis:SchoolLastEnrolledDate'
        xpSchoolLastEnrolledDateDateCollected = 'hmis:SchoolLastEnrolledDate/@hmis:dateCollected'
    ### SchoolName
        xpSchoolName = 'hmis:SchoolName'
        xpSchoolNameDateCollected = 'hmis:SchoolName/@hmis:dateCollected'
    ### SchoolType
        xpSchoolType = 'hmis:SchoolType'
        xpSchoolTypeDateCollected = 'hmis:SchoolType/@hmis:dateCollected'
    ### SubsidyOther
        xpSubsidyOther = 'hmis:SubsidyOther'
        xpSubsidyOtherDateCollected = 'hmis:SubsidyOther/@hmis:dateCollected'
    ### SubsidyType
        xpSubsidyType = 'hmis:SubsidyType'
        xpSubsidyTypeDateCollected = 'hmis:SubsidyType/@hmis:dateCollected'
    ### SubstanceAbuseIndefinite
        xpSubstanceAbuseIndefinite = 'hmis:SubstanceAbuseIndefinite'
        xpSubstanceAbuseIndefiniteDateCollected = 'hmis:SubstanceAbuseIndefinite/@hmis:dateCollected'
    ### SubstanceAbuseProblem
        xpSubstanceAbuseProblem = 'hmis:SubstanceAbuseProblem'
        xpSubstanceAbuseProblemDateCollected = 'hmis:SubstanceAbuseProblem/@hmis:dateCollected'
    ### TotalIncome
        xpTotalIncome = 'hmis:TotalIncome'
        xpTotalIncomeDateCollected = 'hmis:TotalIncome/@hmis:dateCollected'
    ### VocationalTraining
        xpVocationalTraining = 'hmis:VocationalTraining'
        xpVocationalTrainingDateCollected = 'hmis:VocationalTraining/@hmis:dateCollected'
    ### AnnualPersonalIncome
        xpAnnualPersonalIncome = 'ext:AnnualPersonalIncome'
        xpAnnualPersonalIncomeDateCollected = 'ext:AnnualPersonalIncome/@hmis:dateCollected'
    ### EmploymentStatus
        xpEmploymentStatus = 'ext:EmploymentStatus'
        xpEmploymentStatusDateCollected = 'ext:EmploymentStatus/@hmis:dateCollected'   
    ### FamilySize
        xpFamilySize = 'ext:FamilySize'
        xpFamilySizeDateCollected = 'ext:FamilySize/@hmis:dateCollected'                  
    ### HearingImpaired
        xpHearingImpaired = 'ext:HearingImpaired'
        xpHearingImpairedDateCollected = 'ext:HearingImpaired/@hmis:dateCollected'
    ### MaritalStatus
        xpMaritalStatus = 'ext:MaritalStatus'
        xpMaritalStatusDateCollected = 'ext:MaritalStatus/@hmis:dateCollected'
    ### Non-ambulatory
        xpNonAmbulatory = 'ext:Non-ambulatory'
        xpNonAmbulatoryDateCollected = 'ext:Non-ambulatory/@hmis:dateCollected'
    ### ResidentialStatus
        xpResidentialStatus = 'ext:ResidentialStatus'
        xpResidentialStatusDateCollected = 'ext:ResidentialStatus/@hmis:dateCollected'                
    ### VisuallyImpaired
        xpVisuallyImpaired = 'ext:VisuallyImpaired'
        xpVisuallyImpairedDateCollected = 'ext:VisuallyImpaired/@hmis:dateCollected'

        # First test for the real 'PersonHistorical' subelement of person, if not found, test to see if we can get it from the SiteServiceParticipation
        person_historical = person_tag.xpath(xpPersonHistorical, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
        # test if nothign was found, if so, run against the personHistorical as part of service participation
        if len(person_historical) == 0:
            person_historical = person_tag.xpath(xpSvcParticipationPersonHistorical, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
        
        if (person_historical is not None) and len(person_historical) > 0:
            for item in person_historical:
                self.parse_dict = {}
                
                # Foreign key to Person
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                # Foreign key to SiteServiceParticipation
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                
            ### PersonHistoricalIDIDNum
                fldName='person_historical_idid_num'
                self.existence_test_and_add(fldName, item.xpath(xpPersonHistoricalIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='person_historical_idid_num_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpPersonHistoricalIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### PersonHistoricalIDIDStr
                fldName='person_historical_idid_str'
                self.existence_test_and_add(fldName, item.xpath(xpPersonHistoricalIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='person_historical_idid_str_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpPersonHistoricalIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### BarrierCode
                fldName='barrier_code'
                self.existence_test_and_add(fldName, item.xpath(xpBarrierCode, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='barrier_code_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpBarrierCodeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### BarrierOther
                fldName='barrier_other'
                self.existence_test_and_add(fldName, item.xpath(xpBarrierOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='barrier_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpBarrierOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ChildCurrentlyEnrolledInSchool
                fldName='child_currently_enrolled_in_school'
                self.existence_test_and_add(fldName, item.xpath(xpChildCurrentlyEnrolledInSchool, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='child_currently_enrolled_in_school_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpChildCurrentlyEnrolledInSchoolDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### CurrentlyEmployed
                fldName='currently_employed'
                self.existence_test_and_add(fldName, item.xpath(xpCurrentlyEmployed, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='currently_employed_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpCurrentlyEmployedDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### CurrentlyInSchool
                fldName='currently_in_school'
                self.existence_test_and_add(fldName, item.xpath(xpCurrentlyInSchool, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='currently_in_school_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpCurrentlyInSchoolDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### DegreeCode
                fldName='degree_code'
                self.existence_test_and_add(fldName, item.xpath(xpDegreeCode, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='degree_code_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDegreeCodeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### DegreeOther
                fldName='degree_other'
                self.existence_test_and_add(fldName, item.xpath(xpDegreeOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='degree_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDegreeOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### DevelopmentalDisability
                fldName='developmental_disability'
                self.existence_test_and_add(fldName, item.xpath(xpDevelopmentalDisability, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='developmental_disability_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDevelopmentalDisabilityDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### DomesticViolence
                fldName='domestic_violence'
                self.existence_test_and_add(fldName, item.xpath(xpDomesticViolence, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='domestic_violence_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDomesticViolenceDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### DomesticViolenceHowLong
                fldName='domestic_violence_how_long'
                self.existence_test_and_add(fldName, item.xpath(xpDomesticViolenceHowLong, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='domestic_violence_how_long_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDomesticViolenceHowLongDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### DueDate
                fldName='due_date'
                self.existence_test_and_add(fldName, item.xpath(xpDueDate, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='due_date_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDueDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### EmploymentTenure
                fldName='employment_tenure'
                self.existence_test_and_add(fldName, item.xpath(xpEmploymentTenure, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='employment_tenure_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpEmploymentTenureDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### HealthStatus
                fldName='health_status'
                self.existence_test_and_add(fldName, item.xpath(xpHealthStatus, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='health_status_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHealthStatusDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### HighestSchoolLevel
                fldName='highest_school_level'
                self.existence_test_and_add(fldName, item.xpath(xpHighestSchoolLevel, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='highest_school_level_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHighestSchoolLevelDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### HIVAIDSStatus
                fldName='hivaids_status'
                self.existence_test_and_add(fldName, item.xpath(xpHIVAIDSStatus, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='hivaids_status_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHIVAIDSStatusDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### HoursWorkedLastWeek
                fldName='hours_worked_last_week'
                self.existence_test_and_add(fldName, item.xpath(xpHoursWorkedLastWeek, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='hours_worked_last_week_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHoursWorkedLastWeekDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### HUDChronicHomeless
                fldName='hud_chronic_homeless'
                self.existence_test_and_add(fldName, item.xpath(xpHUDChronicHomeless, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='hud_chronic_homeless_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHUDChronicHomelessDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### HUDHomeless
                fldName='hud_homeless'
                self.existence_test_and_add(fldName, item.xpath(xpHUDHomeless, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='hud_homeless_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHUDHomelessDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### LengthOfStayAtPriorResidence
                fldName='length_of_stay_at_prior_residence'
                self.existence_test_and_add(fldName, item.xpath(xpLengthOfStayAtPriorResidence, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='length_of_stay_at_prior_residence_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpLengthOfStayAtPriorResidenceDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### LookingForWork
                fldName='looking_for_work'
                self.existence_test_and_add(fldName, item.xpath(xpLookingForWork, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='looking_for_work_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpLookingForWorkDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### MentalHealthIndefinite
                fldName='mental_health_indefinite'
                self.existence_test_and_add(fldName, item.xpath(xpMentalHealthIndefinite, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='mental_health_indefinite_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpMentalHealthIndefiniteDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### MentalHealthProblem
                fldName='mental_health_problem'
                self.existence_test_and_add(fldName, item.xpath(xpMentalHealthProblem, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='mental_health_problem_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpMentalHealthProblemDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### NonCashSourceCode
                fldName='non_cash_source_code'
                self.existence_test_and_add(fldName, item.xpath(xpNonCashSourceCode, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='non_cash_source_code_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpNonCashSourceCodeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### NonCashSourceOther
                fldName='non_cash_source_other'
                self.existence_test_and_add(fldName, item.xpath(xpNonCashSourceOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='non_cash_source_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpNonCashSourceOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### PersonEmail
                fldName='person_email'
                self.existence_test_and_add(fldName, item.xpath(xpPersonEmail, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='person_email_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpPersonEmailDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### PersonPhoneNumber
                fldName='person_phone_number'
                self.existence_test_and_add(fldName, item.xpath(xpPersonPhoneNumber, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='person_phone_number_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpPersonPhoneNumberDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### PhysicalDisability
                fldName='physical_disability'
                self.existence_test_and_add(fldName, item.xpath(xpPhysicalDisability, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='physical_disability_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpPhysicalDisabilityDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### PregnancyStatus
                fldName='pregnancy_status'
                self.existence_test_and_add(fldName, item.xpath(xpPregnancyStatus, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='pregnancy_status_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpPregnancyStatusDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### PriorResidence
                fldName='prior_residence'
                self.existence_test_and_add(fldName, item.xpath(xpPriorResidence, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='prior_residence_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpPriorResidenceDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### PriorResidenceOther
                fldName='prior_residence_other'
                self.existence_test_and_add(fldName, item.xpath(xpPriorResidenceOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='prior_residence_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpPriorResidenceOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ReasonForLeaving
                fldName='reason_for_leaving'
                self.existence_test_and_add(fldName, item.xpath(xpReasonForLeaving, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='reason_for_leaving_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpReasonForLeavingDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ReasonForLeavingOther
                fldName='reason_for_leaving_other'
                self.existence_test_and_add(fldName, item.xpath(xpReasonForLeavingOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='reason_for_leaving_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpReasonForLeavingOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SchoolLastEnrolledDate
                fldName='school_last_enrolled_date'
                self.existence_test_and_add(fldName, item.xpath(xpSchoolLastEnrolledDate, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='school_last_enrolled_date_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSchoolLastEnrolledDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SchoolName
                fldName='school_name'
                self.existence_test_and_add(fldName, item.xpath(xpSchoolName, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='school_name_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSchoolNameDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SchoolType
                fldName='school_type'
                self.existence_test_and_add(fldName, item.xpath(xpSchoolType, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='school_type_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSchoolTypeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SubsidyOther
                fldName='subsidy_other'
                self.existence_test_and_add(fldName, item.xpath(xpSubsidyOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='subsidy_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSubsidyOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SubsidyType
                fldName='subsidy_type'
                self.existence_test_and_add(fldName, item.xpath(xpSubsidyType, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='subsidy_type_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSubsidyTypeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SubstanceAbuseIndefinite
                fldName='substance_abuse_indefinite'
                self.existence_test_and_add(fldName, item.xpath(xpSubstanceAbuseIndefinite, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='substance_abuse_indefinite_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSubstanceAbuseIndefiniteDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SubstanceAbuseProblem
                fldName='substance_abuse_problem'
                self.existence_test_and_add(fldName, item.xpath(xpSubstanceAbuseProblem, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='substance_abuse_problem_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSubstanceAbuseProblemDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### TotalIncome
                fldName='total_income'
                self.existence_test_and_add(fldName, item.xpath(xpTotalIncome, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='total_income_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpTotalIncomeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### VocationalTraining
                fldName='vocational_training'
                self.existence_test_and_add(fldName, item.xpath(xpVocationalTraining, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='vocational_training_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpVocationalTrainingDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')

            ### AnnualPersonalIncome
                fldName='annual_personal_income'
                self.existence_test_and_add(fldName, item.xpath(xpAnnualPersonalIncome, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                fldName='annual_personal_income_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpAnnualPersonalIncomeDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')
            ### EmploymentStatus
                fldName='employment_status'
                self.existence_test_and_add(fldName, item.xpath(xpEmploymentStatus, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                fldName='employment_status_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpEmploymentStatusDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                
            ### FamilySize
                fldName='family_size'
                self.existence_test_and_add(fldName, item.xpath(xpFamilySize, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                fldName='family_size_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpFamilySizeDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                
            ### HearingImpaired
                fldName='hearing_impaired'
                self.existence_test_and_add(fldName, item.xpath(xpHearingImpaired, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                fldName='hearing_impaired_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHearingImpairedDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                
            ### MaritalStatus
                fldName='marital_status'
                self.existence_test_and_add(fldName, item.xpath(xpMaritalStatus, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                fldName='marital_status_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpMaritalStatusDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                
            ### Non-ambulatory
                fldName='non_ambulatory'
                self.existence_test_and_add(fldName, item.xpath(xpNonAmbulatory, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                fldName='non_ambulatory_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpNonAmbulatoryDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                
            ### ResidentialStatus
                fldName='residential_status'
                self.existence_test_and_add(fldName, item.xpath(xpResidentialStatus, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                fldName='residential_status_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpResidentialStatusDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                
            ### VisuallyImpaired
                fldName='visually_impaired'
                self.existence_test_and_add(fldName, item.xpath(xpVisuallyImpaired, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'text')
                fldName='visually_impaired_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpVisuallyImpairedDateCollected, namespaces={'ext': self.ext_namespace, 'hmis': self.hmis_namespace}), 'attribute_date')                
                
                self.shred(self.parse_dict, dbobjects.PersonHistorical)
            
            ### Parse any subtables
                self.parse_hud_homeless_episodes(item) 
                self.parse_income_and_sources(item)
                self.parse_person_address(item) 
                self.parse_veteran(item)
                self.parse_drug_history(item)
                self.parse_emergency_contact(item)
                
        else:
            self.shred(self.parse_dict, dbobjects.PersonHistorical)
            return

    def parse_person(self, root_element):
        '''Looks for a Person tag and related fields in the XML and persists \n
        it.  This code allows for multiple persons per file'''
        #Xpath query strings
        xpPerson = 'ext:Person'
        xpExportID = '../hmis:Export/hmis:ExportID/hmis:IDNum'
        xpPersonIDHashed = 'ext:PersonID/hmis:Hashed'
        xpPersonIDUnhashed = 'ext:PersonID/hmis:Unhashed'
        #need to handle IDStr
        xpPersonIDDateCollectedHashed = 'ext:PersonID/hmis:Hashed/@hmis:dateCollected'
        xpPersonIDDateCollectedUnhashed = 'ext:PersonID/hmis:Unhashed/@hmis:dateCollected'
        xpPersonDateOfBirthHashed = 'ext:DateOfBirth/hmis:Hashed'
        xpPersonDateOfBirthUnhashed = 'ext:DateOfBirth/hmis:Unhashed'
        xpPersonDateOfBirthDateCollectedHashed = 'ext:DateOfBirth/hmis:Hashed/@hmis:dateCollected'
        xpPersonDateOfBirthDateCollectedUnhashed = 'ext:DateOfBirth/hmis:Unhashed/@hmis:dateCollected'
        xpPersonEthnicityHashed = 'ext:Ethnicity/hmis:Hashed'
        xpPersonEthnicityUnhashed = 'ext:Ethnicity/hmis:Unhashed'
        xpPersonEthnicityDateCollectedHashed = 'ext:Ethnicity/hmis:Hashed/@hmis:dateCollected'
        xpPersonEthnicityDateCollectedUnhashed = 'ext:Ethnicity/hmis:Unhashed/@hmis:dateCollected'
        xpPersonGenderHashed = 'ext:Gender/hmis:Hashed'
        xpPersonGenderUnhashed = 'ext:Gender/hmis:Unhashed'
        xpPersonGenderDateCollectedHashed = 'ext:Gender/hmis:Hashed/@hmis:dateCollected'
        xpPersonGenderDateCollectedUnhashed = 'ext:Gender/hmis:Unhashed/@hmis:dateCollected'
        xpPersonLegalFirstNameHashed = 'ext:LegalFirstName/hmis:Hashed'
        xpPersonLegalFirstNameUnhashed = 'ext:LegalFirstName/hmis:Unhashed'
        xpPersonLegalFirstNameDateCollectedHashed = 'ext:LegalFirstName/hmis:Hashed/@hmis:dateCollected'
        xpPersonLegalFirstNameDateCollectedUnhashed = 'ext:LegalFirstName/hmis:Unhashed/@hmis:dateCollected'
        xpPersonLegalLastNameHashed = 'ext:LegalLastName/hmis:Hashed'
        xpPersonLegalLastNameUnhashed = 'ext:LegalLastName/hmis:Unhashed'
        xpPersonLegalLastNameDateCollectedHashed = 'ext:LegalLastName/hmis:Hashed/@hmis:dateCollected'
        xpPersonLegalLastNameDateCollectedUnhashed = 'ext:LegalLastName/hmis:Unhashed/@hmis:dateCollected'
        xpPersonLegalMiddleNameHashed = 'ext:LegalMiddleName/hmis:Hashed'
        xpPersonLegalMiddleNameUnhashed = 'ext:LegalMiddleName/hmis:Unhashed'
        xpPersonLegalMiddleNameDateCollectedHashed = 'ext:LegalMiddleName/hmis:Hashed/@hmis:dateCollected'
        xpPersonLegalMiddleNameDateCollectedUnhashed = 'ext:LegalMiddleName/hmis:Unhashed/@hmis:dateCollected'
        xpPersonLegalSuffixHashed = 'ext:LegalSuffix/hmis:Hashed'
        xpPersonLegalSuffixUnhashed = 'ext:LegalSuffix/hmis:Unhashed'
        xpPersonLegalSuffixDateCollectedHashed = 'ext:LegalSuffix/hmis:Hashed/@hmis:dateCollected'
        xpPersonLegalSuffixDateCollectedUnhashed = 'ext:LegalSuffix/hmis:Unhashed/@hmis:dateCollected'
        xpPersonSocialSecurityNumberHashed = 'ext:SocialSecurityNumber/hmis:Hashed'
        xpPersonSocialSecurityNumberUnhashed = 'ext:SocialSecurityNumber/hmis:Unhashed'
        xpPersonSocialSecurityNumberDateCollectedHashed = 'ext:SocialSecurityNumber/hmis:Hashed/@hmis:dateCollected'
        xpPersonSocialSecurityNumberDateCollectedUnhashed = 'ext:SocialSecurityNumber/hmis:Unhashed/@hmis:dateCollected'
        xpPersonSocialSecNumberQualityCode = 'ext:SocialSecurityNumber/hmis:SocialSecNumberQualityCode'
        xpPersonSocialSecNumberQualityCodeDateCollected = 'ext:SocialSecurityNumber/hmis:SocialSecNumberQualityCode/@hmis:dateCollected'
        person = root_element.xpath(xpPerson, namespaces={'hmis': self.hmis_namespace, 'ext':self.ext_namespace})
        if person is not None:
            for item in person:
                self.parse_dict = {}
                test = self.existence_test_and_add('person_id_unhashed', item.xpath(xpPersonIDUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), "text")
                if test is True:
                    self.existence_test_and_add('person_id_date_collected', item.xpath(xpPersonIDDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                if test is False:
                    self.existence_test_and_add('person_id_hashed', item.xpath(xpPersonIDHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    self.existence_test_and_add('person_id_date_collected', item.xpath(xpPersonIDDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date') 
                self.existence_test_and_add('export_id', self.export_id, 'text')
                #self.existence_test_and_add('export_id', item.xpath(xpExportID, namespaces={'hmis': self.hmis_namespace}), 'text')
                test = self.existence_test_and_add('person_date_of_birth_unhashed', item.xpath(xpPersonDateOfBirthUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('person_date_of_birth_date_collected', item.xpath(xpPersonDateOfBirthDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')      
                if test is False:
                    self.existence_test_and_add('person_date_of_birth_hashed', item.xpath(xpPersonDateOfBirthHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    self.existence_test_and_add('person_date_of_birth_date_collected', item.xpath(xpPersonDateOfBirthDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')      
                test = self.existence_test_and_add('person_ethnicity_unhashed', item.xpath(xpPersonEthnicityUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('person_ethnicity_date_collected', item.xpath(xpPersonEthnicityDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')     
                if test is False:
                    self.existence_test_and_add('person_ethnicity_hashed', item.xpath(xpPersonEthnicityHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    self.existence_test_and_add('person_ethnicity_date_collected', item.xpath(xpPersonEthnicityDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')     
                test = self.existence_test_and_add('person_gender_unhashed', item.xpath(xpPersonGenderUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('person_gender_date_collected', item.xpath(xpPersonGenderDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')                    
                if test is False:
                    self.existence_test_and_add('person_gender_hashed', item.xpath(xpPersonGenderHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    self.existence_test_and_add('person_gender_date_collected', item.xpath(xpPersonGenderDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                test = self.existence_test_and_add('person_legal_first_name_unhashed', item.xpath(xpPersonLegalFirstNameUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')         
                if test is True:
                    self.existence_test_and_add('person_legal_first_name_date_collected', item.xpath(xpPersonLegalFirstNameDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                if test is False:
                    self.existence_test_and_add('person_legal_first_name_hashed', item.xpath(xpPersonLegalFirstNameHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')         
                    self.existence_test_and_add('person_legal_first_name_date_collected', item.xpath(xpPersonLegalFirstNameDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                test = self.existence_test_and_add('person_legal_last_name_unhashed', item.xpath(xpPersonLegalLastNameUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('person_legal_last_name_date_collected', item.xpath(xpPersonLegalLastNameDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                if test is False:
                    self.existence_test_and_add('person_legal_last_name_hashed', item.xpath(xpPersonLegalLastNameHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    self.existence_test_and_add('person_legal_last_name_date_collected', item.xpath(xpPersonLegalLastNameDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                test = self.existence_test_and_add('person_legal_middle_name_unhashed', item.xpath(xpPersonLegalMiddleNameUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('person_legal_middle_name_date_collected', item.xpath(xpPersonLegalMiddleNameDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                if test is False:
                    self.existence_test_and_add('person_legal_middle_name_hashed', item.xpath(xpPersonLegalMiddleNameHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    self.existence_test_and_add('person_legal_middle_name_date_collected', item.xpath(xpPersonLegalMiddleNameDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')                        
                test = self.existence_test_and_add('person_legal_suffix_unhashed', item.xpath(xpPersonLegalSuffixUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('person_legal_suffix_date_collected', item.xpath(xpPersonLegalSuffixDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                if test is False:
                    self.existence_test_and_add('person_legal_suffix_hashed', item.xpath(xpPersonLegalSuffixHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    self.existence_test_and_add('person_legal_suffix_date_collected', item.xpath(xpPersonLegalSuffixDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')                        
                test = self.existence_test_and_add('person_social_security_number_unhashed', item.xpath(xpPersonSocialSecurityNumberUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('person_social_security_number_date_collected', item.xpath(xpPersonSocialSecurityNumberDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                if test is False:
                    self.existence_test_and_add('person_social_security_number_hashed', item.xpath(xpPersonSocialSecurityNumberHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    self.existence_test_and_add('person_social_security_number_date_collected', item.xpath(xpPersonSocialSecurityNumberDateCollectedHashed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')                    
                self.existence_test_and_add('person_social_sec_number_quality_code', item.xpath(xpPersonSocialSecNumberQualityCode, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')                
                self.existence_test_and_add('person_social_sec_number_quality_code_date_collected', item.xpath(xpPersonSocialSecNumberQualityCodeDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')                
                self.shred(self.parse_dict, dbobjects.Person)
                self.parse_person_historical(item)
                self.parse_other_names(item)
                self.parse_races(item)
                self.parse_release_of_information(item)
                self.parse_site_service_participation(item)
#                self.session.flush()
#                print 'export id is', Export.c.
            return
        else:
            self.shred(self.parse_dict, dbobjects.Person)
            return
        
    def parse_races(self, person_tag):
        '''Looks for a Race tag and related fields in the XML and persists it.'''      
        '''This code allows for multiple Races per Person'''
        #Xpath query strings
        xpRaces = 'ext:Race'
        xpRaceUnhashed = 'hmis:Unhashed'
        xpRaceHashed = 'hmis:Hashed'
        xpRaceDateCollectedUnhashed = 'hmis:Unhashed/@hmis:dateCollected'
        xpRaceDateCollectedHashed = 'hmis:Hashed/@hmis:dateCollected'

        races = person_tag.xpath(xpRaces, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
        if races is not None:
            for item in races:
                self.parse_dict = {}
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                test = self.existence_test_and_add('race_unhashed', item.xpath(xpRaceUnhashed, namespaces={'hmis': self.hmis_namespace}), 'text')
                if test is True:
                    self.existence_test_and_add('race_date_collected', item.xpath(xpRaceDateCollectedUnhashed, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                if test is False:
                    self.existence_test_and_add('race_hashed', item.xpath(xpRaceHashed, namespaces={'hmis': self.hmis_namespace}), 'text')
                    self.existence_test_and_add('race_date_collected', item.xpath(xpRaceDateCollectedHashed, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                self.shred(self.parse_dict, dbobjects.Races)           
        else:
            self.shred(self.parse_dict, dbobjects.Races)
            return
        
    def parse_household(self, element):
        ### xpPath Definitions
            xpHousehold = 'ext:Household'
        ### HouseholdIDIDNum
            xpHouseholdIDIDNum = 'hmis:HouseholdID/hmis:IDNum'
            xpHouseholdIDIDNumDateCollected = 'hmis:HouseholdID/hmis:IDNum/@hmis:dateCollected'
        ### HouseholdIDIDStr
            xpHouseholdIDIDStr = 'hmis:HouseholdID/hmis:IDStr'
            xpHouseholdIDIDStrDateCollected = 'hmis:HouseholdID/hmis:IDStr/@hmis:dateCollected'
        ### HeadOfHouseholdIDUnhashed
            xpHeadOfHouseholdIDUnhashed = 'hmis:HeadOfHouseholdID/hmis:Unhashed'
            xpHeadOfHouseholdIDUnhashedDateCollected = 'hmis:HeadOfHouseholdID/hmis:Unhashed/@hmis:dateCollected'
        ### HeadOfHouseholdIDHashed
            xpHeadOfHouseholdIDHashed = 'hmis:HeadOfHouseholdID/hmis:Hashed'
            xpHeadOfHouseholdIDHashedDateCollected = 'hmis:HeadOfHouseholdID/hmis:Hashed/@hmis:dateCollected'
        ### xpPath Parsing
            itemElements = element.xpath(xpHousehold, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
            if itemElements is not None:
                for item in itemElements:
                    self.parse_dict = {}
                    # Foreign Key
                    self.existence_test_and_add('export_id', self.export_id, 'text')
                ### HouseholdIDIDNum
                    fldName='household_id_num'
                    self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='household_id_num_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### HouseholdIDIDStr
                    fldName='household_id_str'
                    self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='household_id_str_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### HeadOfHouseholdIDUnhashed
                    fldName='head_of_household_id_unhashed'
                    self.existence_test_and_add(fldName, item.xpath(xpHeadOfHouseholdIDUnhashed, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='head_of_household_id_unhashed_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpHeadOfHouseholdIDUnhashedDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### HeadOfHouseholdIDHashed
                    fldName='head_of_household_id_hashed'
                    self.existence_test_and_add(fldName, item.xpath(xpHeadOfHouseholdIDHashed, namespaces={'hmis': self.hmis_namespace}), 'text')
                    fldName='head_of_household_id_hashed_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpHeadOfHouseholdIDHashedDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                ### Household (Shred)
                    self.shred(self.parse_dict, dbobjects.Household)
        
                ### Parse any subtables
                    self.parse_members(item)
            
    
    def parse_members(self, element):
        ### xpPath Definitions
            xpMembers = 'ext:Members'
            xpMember = 'ext:Member'
        ### PersonIDUnhashed
            xpPersonIDUnhashed = 'hmis:PersonID/hmis:Unhashed'
            xpPersonIDUnhashedDateCollected = 'hmis:PersonID/hmis:Unhashed/@hmis:dateCollected'
        ### PersonIDHashed
            xpPersonIDHashed = 'hmis:PersonID/hmis:Hashed'
            xpPersonIDHashedDateCollected = 'hmis:PersonID/hmis:Hashed/@hmis:dateCollected'
        ### RelationshipToHeadOfHousehold
            xpRelationshipToHeadOfHousehold = 'hmis:RelationshipToHeadOfHousehold'
            xpRelationshipToHeadOfHouseholdDateCollected = 'hmis:RelationshipToHeadOfHousehold/@hmis:dateCollected'
            
            ### xpPath Parsing
            # put a test first
            test = element.xpath(xpMembers, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
            if len(test) > 0:
                # if the tag exists (under household) it will always be 1.  with many 'members' underneath it.
                itemElements = test[0].xpath(xpMember, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
                if itemElements is not None:
                    for item in itemElements:
                        self.parse_dict = {}
                    ### PersonIDUnhashed
                        fldName='person_id_unhashed'
                        self.existence_test_and_add(fldName, item.xpath(xpPersonIDUnhashed, namespaces={'hmis': self.hmis_namespace}), 'text')
                        fldName='person_id_unhashed_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpPersonIDUnhashedDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                    ### PersonIDHashed
                        fldName='person_id_hashed'
                        self.existence_test_and_add(fldName, item.xpath(xpPersonIDHashed, namespaces={'hmis': self.hmis_namespace}), 'text')
                        fldName='person_id_hashed_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpPersonIDHashedDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
                    ### RelationshipToHeadOfHousehold
                        fldName='relationship_to_head_of_household'
                        self.existence_test_and_add(fldName, item.xpath(xpRelationshipToHeadOfHousehold, namespaces={'hmis': self.hmis_namespace}), 'text')
                        fldName='relationship_to_head_of_household_date_collected'
                        self.existence_test_and_add(fldName, item.xpath(xpRelationshipToHeadOfHouseholdDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            
                        # Stuff the forgeign key in 
                        self.existence_test_and_add('household_index_id', self.household_index_id, 'no_handling')
            
                    ### Member (Shred)
                        self.shred(self.parse_dict, dbobjects.Members)
            
                    ### Parse any subtables
    
    def parse_release_of_information(self, element):
    ### xpPath Definitions
        xpReleaseOfInformation = 'ext:ReleaseOfInformation'
    ### ReleaseOfInformationIDIDNum
        xpReleaseOfInformationIDIDNum = 'hmis:ReleaseOfInformationID/hmis:IDNum'
        xpReleaseOfInformationIDIDNumDateCollected = 'hmis:ReleaseOfInformationID/hmis:IDNum/@hmis:dateCollected'
    ### ReleaseOfInformationIDIDStr
        xpReleaseOfInformationIDIDStr = 'hmis:ReleaseOfInformationID/hmis:IDStr'
        xpReleaseOfInformationIDIDStrDateCollected = 'hmis:ReleaseOfInformationID/hmis:IDStr/@hmis:dateCollected'
    ### SiteServiceIDIDNum
        xpSiteServiceIDIDNum = 'hmis:SiteServiceID/hmis:IDNum'
        xpSiteServiceIDIDNumDateCollected = 'hmis:SiteServiceID/hmis:IDNum/@hmis:dateCollected'
    ### SiteServiceIDIDStr
        xpSiteServiceIDIDStr = 'hmis:SiteServiceID/hmis:IDStr'
        xpSiteServiceIDIDStrDateCollected = 'hmis:SiteServiceID/hmis:IDStr/@hmis:dateCollected'
    ### Documentation
        xpDocumentation = 'hmis:Documentation'
        xpDocumentationDateCollected = 'hmis:Documentation/@hmis:dateCollected'
    ### StartDate
        xpStartDate = 'hmis:EffectivePeriod/hmis:StartDate'
        xpStartDateDateCollected = 'hmis:EffectivePeriod/hmis:StartDate/@hmis:dateCollected'
    ### EndDate
        xpEndDate = 'hmis:EffectivePeriod/hmis:EndDate'
        xpEndDateDateCollected = 'hmis:EffectivePeriod/hmis:EndDate/@hmis:dateCollected'
    ### ReleaseGranted
        xpReleaseGranted = 'hmis:ReleaseGranted'
        xpReleaseGrantedDateCollected = 'hmis:ReleaseGranted/@hmis:dateCollected'

    ### xpPath Parsing
        itemElements = element.xpath(xpReleaseOfInformation, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
        if itemElements is not None:
            for item in itemElements:
                
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                
            ### ReleaseOfInformationIDIDNum
                fldName='release_of_information_idid_num'
                self.existence_test_and_add(fldName, item.xpath(xpReleaseOfInformationIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='release_of_information_idid_num_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpReleaseOfInformationIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ReleaseOfInformationIDIDStr
                fldName='release_of_information_idid_str'
                self.existence_test_and_add(fldName, item.xpath(xpReleaseOfInformationIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='release_of_information_idid_str_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpReleaseOfInformationIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SiteServiceIDIDNum
                fldName='site_service_idid_num'
                self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='site_service_idid_num_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SiteServiceIDIDStr
                fldName='site_service_idid_str'
                self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='site_service_idid_str_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### Documentation
                fldName='documentation'
                self.existence_test_and_add(fldName, item.xpath(xpDocumentation, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='documentation_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpDocumentationDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ###* StartDate (DateRange)
                fldName='start_date'
                self.existence_test_and_add(fldName, item.xpath(xpStartDate, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='start_date_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpStartDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ###* EndDate (DateRange)
                fldName='end_date'
                self.existence_test_and_add(fldName, item.xpath(xpEndDate, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='end_date_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpEndDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')                
            ### ReleaseGranted
                fldName='release_granted'
                self.existence_test_and_add(fldName, item.xpath(xpReleaseGranted, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='release_granted_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpReleaseGrantedDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
    
            ### ReleaseOfInformation (Shred)
                self.shred(self.parse_dict, dbobjects.ReleaseOfInformation)
            

    def parse_need(self, element):
    ### xpPath Definitions
        xpNeed = 'ext:Need'
    ### NeedIDIDNum
        xpNeedIDIDNum = 'hmis:NeedID/hmis:IDNum'
        xpNeedIDIDNumDateCollected = 'hmis:NeedID/hmis:IDNum/@hmis:dateCollected'
    ### NeedIDIDStr
        xpNeedIDIDStr = 'hmis:NeedIDIDStr'
        xpNeedIDIDStrDateCollected = 'hmis:NeedID/hmis:IDStr/@hmis:dateCollected'
    ### SiteServiceIDIDNum
        xpSiteServiceIDIDNum = 'hmis:SiteServiceID/hmis:IDNum'
        xpSiteServiceIDIDNumDateCollected = 'hmis:SiteServiceID/hmis:IDNum/@hmis:dateCollected'
    ### SiteServiceIDIDStr
        xpSiteServiceIDIDStr = 'hmis:SiteServiceID/hmis:IDStr'
        xpSiteServiceIDIDStrDateCollected = 'hmis:SiteServiceIDIDStr/@hmis:dateCollected'
    ### ServiceEventIDIDNum
        xpServiceEventIDIDNum = 'hmis:ServiceEventID/hmis:IDNum'
        xpServiceEventIDIDNumDateCollected = 'hmis:ServiceEventIDIDNum/@hmis:dateCollected'
    ### ServiceEventIDIDStr
        xpServiceEventIDIDStr = 'hmis:ServiceEventID/hmis:IDStr'
        xpServiceEventIDIDStrDateCollected = 'hmis:ServiceEventID/hmis:IDStr/@hmis:dateCollected'
    ### NeedStatus
        xpNeedStatus = 'hmis:NeedStatus'
        xpNeedStatusDateCollected = 'hmis:NeedStatus/@hmis:dateCollected'
    ### Taxonomy
        xpTaxonomy = 'hmis:Taxonomy/airs:Code'
        xpTaxonomyDateCollected = 'hmis:Taxonomy/airs:Code/@hmis:dateCollected'

    ### xpPath Parsing
        itemElements = element.xpath(xpNeed, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
        if itemElements is not None:
            for item in itemElements:
            ### foreign key value
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
            ### NeedIDIDNum
                fldName='need_idid_num'
                self.existence_test_and_add(fldName, item.xpath(xpNeedIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='need_idid_num_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpNeedIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### NeedIDIDStr
                fldName='need_idid_str'
                self.existence_test_and_add(fldName, item.xpath(xpNeedIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='need_idid_str_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpNeedIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SiteServiceIDIDNum
                fldName='site_service_idid_num'
                self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='site_service_idid_num_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### SiteServiceIDIDStr
                fldName='site_service_idid_str'
                self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='site_service_idid_str_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ServiceEventIDIDNum
                fldName='service_event_idid_num'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEventIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_event_idid_num_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEventIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ServiceEventIDIDStr
                fldName='service_event_idid_str'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEventIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_event_idid_str_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEventIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### NeedStatus
                fldName='need_status'
                self.existence_test_and_add(fldName, item.xpath(xpNeedStatus, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='need_status_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpNeedStatusDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### Taxonomy
                fldName='taxonomy'
                self.existence_test_and_add(fldName, item.xpath(xpTaxonomy, namespaces=self.nsmap), 'text')
        
            ### Need (Shred)
                self.shred(self.parse_dict, dbobjects.Need)
        
            ### Parse any subtables

    def parse_site_service_participation(self, element):
        ### xpPath Definitions
            xpSiteServiceParticipation = 'ext:SiteServiceParticipation'
        ### SiteServiceParticipationIDIDNum
            xpSiteServiceParticipationIDIDNum = 'ext:SiteServiceParticipationID/hmis:IDNum'
            xpSiteServiceParticipationIDIDNumDateCollected = 'ext:SiteServiceParticipationID/hmis:IDNum/@hmis:dateCollected'
        ### SiteServiceParticipationIDIDStr
            xpSiteServiceParticipationIDIDStr = 'ext:SiteServiceParticipationID/hmis:IDStr'
            xpSiteServiceParticipationIDIDStrDateCollected = 'ext:SiteServiceParticipationID/hmis:IDStr/@hmis:dateCollected'
        ### SiteServiceIDIDNum
            xpSiteServiceIDIDNum = 'ext:SiteServiceID/hmis:IDNum'
            xpSiteServiceIDIDNumDateCollected = 'ext:SiteServiceID/hmis:IDNum/@hmis:dateCollected'
        ### SiteServiceIDIDStr
            xpSiteServiceIDIDStr = 'ext:SiteServiceID/hmis:IDStr'
            xpSiteServiceIDIDStrDateCollected = 'ext:SiteServiceID/hmis:IDStr/@hmis:dateCollected'
        ### HouseholdIDIDNum
            xpHouseholdIDIDNum = 'ext:HouseholdID/hmis:IDNum'
            xpHouseholdIDIDNumDateCollected = 'ext:HouseholdID/hmis:IDNum/@hmis:dateCollected'
        ### HouseholdIDIDStr
            xpHouseholdIDIDStr = 'ext:HouseholdID/hmis:IDStr'
            xpHouseholdIDIDStrDateCollected = 'ext:HouseholdID/hmis:IDStr/@hmis:dateCollected'
        ### Destination
            xpDestination = 'ext:Destination'
            xpDestinationDateCollected = 'ext:Destination/@hmis:dateCollected'
        ### DestinationOther
            xpDestinationOther = 'ext:DestinationOther'
            xpDestinationOtherDateCollected = 'ext:DestinationOther/@hmis:dateCollected'
        ### DestinationTenure
            xpDestinationTenure = 'ext:DestinationTenure'
            xpDestinationTenureDateCollected = 'ext:DestinationTenure/@hmis:dateCollected'
        ### DisablingCondition
            xpDisablingCondition = 'ext:DisablingCondition'
            xpDisablingConditionDateCollected = 'ext:DisablingCondition/@hmis:dateCollected'
        ### Participation Dates (Start Date)
            xpStartDate = 'ext:ParticipationDates/hmis:StartDate'
            xpStartDateDateCollected = 'ext:ParticipationDates/hmis:StartDate/@hmis:dateCollected'
        ### Participation Dates (End Date)
            xpEndDate = 'ext:ParticipationDates/hmis:EndDate'
            xpEndDateDateCollected = 'ext:ParticipationDates/hmis:EndDate/@hmis:dateCollected'
        ### VeteranStatus
            xpVeteranStatus = 'ext:VeteranStatus'
            xpVeteranStatusDateCollected = 'ext:VeteranStatus/@hmis:dateCollected'
            
            '''Operation PARS'''
        ### DischargeType
            xpDischargeType = 'ext:DischargeType'
            xpDischargeTypeDateCollected = 'ext:DischargeType/@hmis:dateCollected'    
        ### HealthStatusAtDischarge
            xpHealthStatusAtDischarge = 'ext:HealthStatusAtDischarge'
            xpHealthStatusAtDischargeDateCollected = 'ext:HealthStatusAtDischarge/@hmis:dateCollected'
        ### VAEligibility
            xpVAEligibility = 'ext:VAEligibility'
            xpVAEligibilityDateCollected = 'ext:VAEligibility/@hmis:dateCollected'

        ### xpPath Parsing
            itemElements = element.xpath(xpSiteServiceParticipation, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
            if itemElements is not None:
                for item in itemElements:
                    # Foreign key to Person
                    self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                ### SiteServiceParticipationIDIDNum
                    fldName='site_service_participation_idid_num'
                    self.existence_test_and_add(fldName, item.xpath(xpSiteServiceParticipationIDIDNum, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='site_service_participation_idid_num_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpSiteServiceParticipationIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### SiteServiceParticipationIDIDStr
                    fldName='site_service_participation_idid_str'
                    self.existence_test_and_add(fldName, item.xpath(xpSiteServiceParticipationIDIDStr, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='site_service_participation_idid_str_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpSiteServiceParticipationIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### SiteServiceIDIDNum
                    fldName='site_service_idid_num'
                    self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDNum, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='site_service_idid_num_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### SiteServiceIDIDStr
                    fldName='site_service_idid_str'
                    self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDStr, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='site_service_idid_str_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpSiteServiceIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### HouseholdIDIDNum
                    fldName='household_idid_num'
                    self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDNum, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='household_idid_num_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### HouseholdIDIDStr
                    fldName='household_idid_str'
                    self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDStr, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='household_idid_str_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### Destination
                    fldName='destination'
                    self.existence_test_and_add(fldName, item.xpath(xpDestination, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='destination_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpDestinationDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### DestinationOther
                    fldName='destination_other'
                    self.existence_test_and_add(fldName, item.xpath(xpDestinationOther, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='destination_other_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpDestinationOtherDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### DestinationTenure
                    fldName='destination_tenure'
                    self.existence_test_and_add(fldName, item.xpath(xpDestinationTenure, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='destination_tenure_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpDestinationTenureDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### DisablingCondition
                    fldName='disabling_condition'
                    self.existence_test_and_add(fldName, item.xpath(xpDisablingCondition, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='disabling_condition_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpDisablingConditionDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### Participation Dates (Start Date)
                    fldName='participation_dates_start_date'
                    self.existence_test_and_add(fldName, item.xpath(xpStartDate, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='participation_dates_start_date_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpStartDateDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### Participation Dates (End Date)
                    fldName='participation_dates_end_date'
                    self.existence_test_and_add(fldName, item.xpath(xpEndDate, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='participation_dates_end_date_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpEndDateDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### VeteranStatus
                    fldName='veteran_status'
                    self.existence_test_and_add(fldName, item.xpath(xpVeteranStatus, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='veteran_status_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpVeteranStatusDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### DischargeType
                    fldName='discharge_type'
                    self.existence_test_and_add(fldName, item.xpath(xpDischargeType, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='discharge_type_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpDischargeTypeDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### HealthStatusAtDischarge
                    fldName='health_status_at_discharge'
                    self.existence_test_and_add(fldName, item.xpath(xpHealthStatusAtDischarge, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='health_status_at_discharge_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpHealthStatusAtDischargeDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                ### VAEligibility
                    fldName='va_eligibility'
                    self.existence_test_and_add(fldName, item.xpath(xpVAEligibility, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'text')
                    fldName='va_eligibility_date_collected'
                    self.existence_test_and_add(fldName, item.xpath(xpVAEligibilityDateCollected, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace}), 'attribute_date')
                        
        
                ### SiteServiceParticipation (Shred)
                    self.shred(self.parse_dict, dbobjects.SiteServiceParticipation)
        
                ### Parse any subtables
                    #self.parse_participation_dates(item)
                    #self.parse_person_historical(item)
                    self.parse_need(item)
                    self.parse_service_event(item)

    def parse_service_event(self, element):
    ### xpPath Definitions
        xpServiceEvent = 'ext:ServiceEvent'
    ### ServiceEventIDIDNum
        xpServiceEventIDIDNum = 'hmis:ServiceEventID/hmis:IDNum'
        xpServiceEventIDIDNumDateCollected = 'hmis:ServiceEventID/hmis:IDNum/@hmis:dateCollected'
    ### ServiceEventIDIDStr
        xpServiceEventIDIDStr = 'hmis:ServiceEventID/hmis:IDStr'
        xpServiceEventIDIDStrDateCollected = 'hmis:ServiceEventID/hmis:IDStr/@hmis:dateCollected'
    ### HouseholdIDIDNum
        xpHouseholdIDIDNum = 'hmis:HouseholdID/hmis:IDNum'
        xpHouseholdIDIDNumDateCollected = 'hmis:HouseholdID/hmis:IDNum/@hmis:dateCollected'
    ### HouseholdIDIDStr
        xpHouseholdIDIDStr = 'hmis:HouseholdID/hmis:IDStr'
        xpHouseholdIDIDStrDateCollected = 'hmis:HouseholdIDIDStr/@hmis:dateCollected'
    ### IsReferral
        xpIsReferral = 'hmis:IsReferral'
        xpIsReferralDateCollected = 'hmis:IsReferral/@hmis:dateCollected'
    ### QuantityOfService
        xpQuantityOfService = 'hmis:QuantityOfService'
        xpQuantityOfServiceDateCollected = 'hmis:QuantityOfService/@hmis:dateCollected'
    ### QuantityOfServiceMeasure
        xpQuantityOfServiceMeasure = 'hmis:QuantityOfServiceMeasure'
        xpQuantityOfServiceMeasureDateCollected = 'hmis:QuantityOfServiceMeasure/@hmis:dateCollected'
    ### ServiceAIRSCode
        xpServiceAIRSCode = 'hmis:ServiceAIRSCode'
        xpServiceAIRSCodeDateCollected = 'hmis:ServiceAIRSCode/@hmis:dateCollected'
    ###
        xpServicePeriodStartDate = 'hmis:ServicePeriod/hmis:StartDate'
        xpServicePeriodStartDateDateCollected = 'hmis:ServicePeriod/hmis:StartDate/@hmis:dateCollected'
    
        xpServicePeriodEndDate = 'hmis:ServicePeriod/hmis:EndDate'
        xpServicePeriodEndDateDateCollected = 'hmis:ServicePeriod/hmis:EndDate/@hmis:dateCollected'
        
    ### ServiceUnit
        xpServiceUnit = 'hmis:ServiceUnit'
        xpServiceUnitDateCollected = 'hmis:ServiceUnit/@hmis:dateCollected'
    ### TypeOfService
        xpTypeOfService = 'hmis:TypeOfService'
        xpTypeOfServiceDateCollected = 'hmis:TypeOfService/@hmis:dateCollected'
    ### TypeOfServiceOther
        xpTypeOfServiceOther = 'hmis:TypeOfServiceOther'
        xpTypeOfServiceOtherDateCollected = 'hmis:TypeOfServiceOther/@hmis:dateCollected'
        
        '''Operation PARS'''
        xpTypeOfServicePAR = 'ext:TypeOfServicePAR'
        
    
    ### xpPath Parsing
        itemElements = element.xpath(xpServiceEvent, namespaces={'hmis': self.hmis_namespace, 'ext': self.ext_namespace})
        if itemElements is not None:
            for item in itemElements:
            ### ServiceEventIDIDNum
                fldName='service_event_idid_num'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEventIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_event_idid_num_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEventIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ServiceEventIDIDStr
                fldName='service_event_idid_str'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEventIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_event_idid_str_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServiceEventIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### HouseholdIDIDNum
                fldName='household_idid_num'
                self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDNum, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='household_idid_num_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDNumDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### HouseholdIDIDStr
                fldName='household_idid_str'
                self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDStr, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='household_idid_str_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpHouseholdIDIDStrDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### IsReferral
                fldName='is_referral'
                self.existence_test_and_add(fldName, item.xpath(xpIsReferral, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='is_referral_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpIsReferralDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### QuantityOfService
                fldName='quantity_of_service'
                self.existence_test_and_add(fldName, item.xpath(xpQuantityOfService, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='quantity_of_service_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpQuantityOfServiceDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### QuantityOfServiceMeasure
                fldName='quantity_of_service_measure'
                self.existence_test_and_add(fldName, item.xpath(xpQuantityOfServiceMeasure, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='quantity_of_service_measure_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpQuantityOfServiceMeasureDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ServiceAIRSCode
                fldName='service_airs_code'
                self.existence_test_and_add(fldName, item.xpath(xpServiceAIRSCode, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_airs_code_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServiceAIRSCodeDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### Service Period (Start Date)
                fldName='service_period_start_date'
                self.existence_test_and_add(fldName, item.xpath(xpServicePeriodStartDate, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_period_start_date_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServicePeriodStartDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### Service Period (End Date)
                fldName='service_period_end_date'
                self.existence_test_and_add(fldName, item.xpath(xpServicePeriodEndDate, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_period_end_date_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServicePeriodEndDateDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### ServiceUnit
                fldName='service_unit'
                self.existence_test_and_add(fldName, item.xpath(xpServiceUnit, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='service_unit_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpServiceUnitDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### TypeOfService
                fldName='type_of_service'
                self.existence_test_and_add(fldName, item.xpath(xpTypeOfService, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='type_of_service_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpTypeOfServiceDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### TypeOfServiceOther
                fldName='type_of_service_other'
                self.existence_test_and_add(fldName, item.xpath(xpTypeOfServiceOther, namespaces={'hmis': self.hmis_namespace}), 'text')
                fldName='type_of_service_other_date_collected'
                self.existence_test_and_add(fldName, item.xpath(xpTypeOfServiceOtherDateCollected, namespaces={'hmis': self.hmis_namespace}), 'attribute_date')
            ### TypeOfServicePAR
                fldName='type_of_service_par'
                self.existence_test_and_add(fldName, item.xpath(xpTypeOfServicePAR, namespaces={'ext': self.ext_namespace}), 'text')
                
            ### ServiceEvent (Shred)
                self.shred(self.parse_dict, dbobjects.ServiceEvent)
            
            ### Parse any subtables
                #self.parse_service_period(item)
                        
#current projects only using client sections, not resources    
#    def parse_site_service(self, database_id_tag):
#        '''Looks for a SiteService and related fields in the XML and persists the data set.'''
#        #Xpath query strings
#        xpSiteService = '/hmis:SourceDatabase/hmis:SiteService'
#        xpSiteServiceName = '/hmis:SourceDatabase/hmis:SiteService/airs:Name'
#       
#        site_service = database_id_tag.xpath(xpSiteService, namespaces={'airs': self.airs_namespace})
#        if site_service is not None:
#            for item in site_service:
#               self.parse_dict = {}
#               self.parse_dict.__setitem__('site_service_name', item.text)
#                #xpIDNumdateCollected = '/hmis:SourceDatabase/hmis:Export/hmis:ExportID/hmis:IDNum/@hmis:dateCollected'
#                #parse_dict.__setitem__('export_id_date_collected', dateutil.parser.parse(root_element.xpath(xpIDNumdateCollected, namespaces={'hmis': self.hmis_namespace})[0]))
#                self.shred(parse_dict, SiteService)
#        return
        
    def convertFloat(self, x):
        if '.' in x:
            try:
                x = int(float(x))
                return str(x)
            except ValueError:
                if len(x) > 32: x = 'OVERLIMIT'     ## use this to remove strings > 32 in testing
                return x
        else:
                if len(x) > 32: x = 'OVERLIMIT'     ## use this to remove strings > 32 in testing
                return x            

    def shred(self, parse_dict, mapping):
        '''Commits the record set to the database'''
        mapped = mapping(parse_dict)
        self.session.save(mapped)
        self.session.flush()
        #Save the indexes generated at run-time so can be used
        #in dependent tables
        if mapping.__name__ == "Household":
            self.household_index_id = mapped.id
        if mapping.__name__ == "PersonHistorical":
            self.person_historical_index_id = mapped.id
        if mapping.__name__ == "Person":
            self.person_index_id = mapped.id
            self.site_service_index_id = None
        if mapping.__name__ == "SiteServiceParticipation":
            self.site_service_index_id = mapped.id
        self.session.commit()
        return
    
    def existence_test_and_add(self, db_column, query_string, handling):
        '''checks that the query actually has a result and adds to dict'''
        #if len(query_string) is not 0:
        if handling == 'no_handling':
                print 'NO HANDLE'
                self.persist(db_column, query_string = query_string)
                return True
        elif len(query_string) is not 0 or None:
            if handling == 'attribute_text':
                self.persist(db_column, str(query_string[0]))
                return True
            if handling == 'text':
                '''convert floats to integers'''
                query_converted = self.convertFloat(query_string[0].text)
                self.persist(db_column, query_string = query_converted)
                #print '#### text - pre',query_string[0].text
                #print '#### text - post',query_converted               
                return True
            elif handling == 'attribute_date':
                self.persist(db_column, query_string = dateutil.parser.parse(query_string[0]))
                return True
            elif handling == 'element_date':
                self.persist(db_column, query_string = dateutil.parser.parse(query_string[0].text))
                return True
            else:
                print "need to specify the handling"
                return False
        else:
            return False
            
    def persist(self, db_column, query_string):
        self.parse_dict.__setitem__(db_column, query_string)
        return
    
def main(argv=None):  
    if argv is None:
        argv = sys.argv
    #import postgresutils
    #UTILS = postgresutils.Utils()
    #UTILS.blank_database()

    inputFile = "/media/psf/Development/Projects/Alexandria/DATA/StagingFiles/Operation_PAR_XML_instance1.xml"
    #inputFile = os.path.join("%s" % settings.BASE_PATH, "%s" % settings.INPUTFILES_PATH, "Example_HUD_HMIS_2_8_Instance.xml")
    #inputFile = "/home/user/Documents/Development/AlexandriaConsulting/repos/trunk/synthesis/Staging/HMIS_2_8_Project_Heart_8-27-2009.xml"
    #inputFile = "/home/user/Documents/Development/AlexandriaConsulting/repos/trunk/synthesis/Staging/HMIS_2_8_Project_Heart_10-07-2009v2.xml"
    #inputFile = "/home/user/Documents/Development/AlexandriaConsulting/repos/trunk/synthesis/Staging/ExampleSBB_HUD_HMIS_2_8_Instance.xml"
    
    if settings.DB_PASSWD == "":
        settings.DB_PASSWD = raw_input("Please enter your password: ")
    
    if os.path.isfile(inputFile) is True:#_adapted_further
        try:
            xml_file = open(inputFile,'r') 
        except:
            print "error"
            
        reader = PARXMLReader(xml_file)
        tree = reader.read()
        reader.process_data(tree)
        xml_file.close()

if __name__ == "__main__":
    sys.exit(main()) 