''' 
    Reads a HUD HMIS XML 3.0 Document into memory and parses its contents storing them into a postgresql database.
    This is a log database, so it holds everything and doesn't worry about deduplication.
    The only thing it enforces are exportids, which must be unique.
'''

import sys, os
from reader import Reader
from zope.interface import implements
from lxml import etree
from sqlalchemy.exceptions import IntegrityError
import dateutil.parser
from conf import settings
import clsexceptions
import dbobjects as dbobjects
import fileutils
from errcatalog import catalog

#SBB08212010 checked in by ECJ on behalf of SBB
#class HMISXML30Reader(dbobjects.DatabaseObjects):
class HMISXML30Reader(dbobjects.DatabaseObjects): 
    ''' Implements reader interface '''
    implements (Reader) 

    ''' Define XML namespaces '''
    hmis_namespace = "http://www.hmis.info/schema/3_0/HUD_HMIS.xsd" 
    airs_namespace = "http://www.hmis.info/schema/3_0/AIRS_3_0_mod.xsd"
    nsmap = {"hmis" : hmis_namespace, "airs" : airs_namespace}


    def __init__(self, xml_file):
        ''' Put XML file into local object '''
        self.xml_file = xml_file

        ''' Instantiate database object '''
        dbo = dbobjects.DatabaseObjects()
        self.session = dbo.Session()

    def read(self):
        ''' Takes an XML instance file and reads it into memory as a node tree '''
        #print '** Raw XML:', self.xml_file
        tree = etree.parse(self.xml_file)
        #print '** Node tree:', tree
        #self.xml_file.close()
        return tree

    def process_data(self, tree):
        ''' Shreds the XML document into the database '''
        root_element = tree.getroot()
        self.parse_source(root_element)
        return
        
    ''' Parse each table '''
    def parse_source(self, root_element):
        ''' Loop through all sources and then traverse the tree for each export '''
        ''' There can be multiple sources with multiple exports inside each source '''
        
        xpSources = '/hmis:Sources/hmis:Source'
        source_list = root_element.xpath(xpSources, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if source_list is not None:
            for item in source_list:
                self.parse_dict = {}
                ''' Element paths '''
                xpSourceVersion = '../../@hmis:version'                
                xpSourceIDIDNum = 'hmis:SourceID/hmis:IDNum'
                xpSourceIDIDStr = 'hmis:SourceID/hmis:IDStr'
                xpSourceDelete = 'hmis:SourceID/@hmis:Delete'
                xpSourceDeleteOccurredDate = 'hmis:SourceID/@hmis:DeleteOccurredDate'
                xpSourceDeleteEffective = 'hmis:SourceID/@hmis:DeleteEffective'
                xpSourceSoftwareVendor = 'hmis:SoftwareVendor'
                xpSourceSoftwareVersion = 'hmis:SoftwareVersion'
                xpSourceContactEmail = 'hmis:SourceContactEmail'
                xpSourceContactExtension = 'hmis:SourceContactExtension'
                xpSourceContactFirst = 'hmis:SourceContactFirst'        
                xpSourceContactLast = 'hmis:SourceContactLast'        
                xpSourceContactPhone = 'hmis:SourceContactPhone'
                xpSourceName = 'hmis:SourceName'

                ''' Map elements to database columns '''
                self.existence_test_and_add('attr_version', item.xpath(xpSourceVersion, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('source_id_id_id_num_2010', item.xpath(xpSourceIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_id_id_id_str_2010', item.xpath(xpSourceIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_id_id_delete_2010', item.xpath(xpSourceDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('source_id_id_delete_occurred_date_2010', item.xpath(xpSourceDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('source_id_id_delete_effective_2010', item.xpath(xpSourceDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('software_vendor_2010', item.xpath(xpSourceSoftwareVendor, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('software_version_2010', item.xpath(xpSourceSoftwareVersion, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_contact_email_2010', item.xpath(xpSourceContactEmail, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_contact_extension', item.xpath(xpSourceContactExtension, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_contact_first', item.xpath(xpSourceContactFirst, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_contact_last', item.xpath(xpSourceContactLast, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_contact_phone', item.xpath(xpSourceContactPhone, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_name', item.xpath(xpSourceName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Source)

                ''' Parse all exports for this specific source '''
                self.parse_export(item)
        return                

    def parse_export(self, element):
        ''' loop through all exports and traverse the tree '''
        
        ''' Element paths '''
        xpExport = 'hmis:Export'
        xpExportIDIDNum = 'hmis:ExportID/hmis:IDNum'
        xpExportIDIDStr = 'hmis:ExportID/hmis:IDStr'
        xpExportDelete = 'hmis:ExportID/@hmis:Delete'
        xpExportDeleteOccurredDate = 'hmis:ExportID/@hmis:DeleteOccurredDate'
        xpExportDeleteEffective = 'hmis:ExportID/@hmis:DeleteEffective'
        xpExportExportDate = 'hmis:ExportDate'
        xpExportPeriodStartDate = 'hmis:ExportPeriod/hmis:StartDate'
        xpExportPeriodEndDate = 'hmis:ExportPeriod/hmis:EndDate'
        
        itemElements = element.xpath(xpExport, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}

                ''' Map elements to database columns '''
                test = item.xpath(xpExportIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}) 
                if len(test) is 0:
                    test = item.xpath(xpExportIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
                    self.export_id = test
                    value = self.existence_test_and_add('export_id', test, 'text')
                else:
                    self.export_id = test
                    self.existence_test_and_add('export_id', test, 'text')
                self.existence_test_and_add('export_id_id_id_num_2010', item.xpath(xpExportIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('export_id_id_id_str_2010', item.xpath(xpExportIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('export_id_id_delete_2010', item.xpath(xpExportDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('export_id_id_delete_occurred_date_2010', item.xpath(xpExportDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('export_id_id_delete_effective_2010', item.xpath(xpExportDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('export_date', item.xpath(xpExportExportDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date') 
                self.existence_test_and_add('export_period_start_date', item.xpath(xpExportPeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')
                self.existence_test_and_add('export_period_end_date', item.xpath(xpExportPeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')

                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Export)
                
                ''' Create source to export link '''
                self.record_source_export_link()

                ''' Parse sub-tables '''
                self.parse_household(item)
                self.parse_region(item)
                self.parse_agency(item)
                
                
                
                self.parse_person(item)
                self.parse_service(item)
                self.parse_site(item)
                self.parse_site_service(item)
        return

    def parse_household(self, element):
        ''' Element paths '''
        xpHousehold = 'hmis:Household'
        xpHouseholdIDIDNum = 'hmis:HouseholdID/hmis:IDNum'
        xpHouseholdIDIDStr = 'hmis:HouseholdID/hmis:IDStr'
        xpHeadOfHouseholdIDUnhashed = 'hmis:HeadOfHouseholdID/hmis:Unhashed'
        xpHeadOfHouseholdIDHashed = 'hmis:HeadOfHouseholdID/hmis:Hashed'

        itemElements = element.xpath(xpHousehold, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}

                ''' Map elements to database columns '''
                self.existence_test_and_add('household_id_num', item.xpath(xpHouseholdIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('household_id_str', item.xpath(xpHouseholdIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('head_of_household_id_unhashed', item.xpath(xpHeadOfHouseholdIDUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('head_of_household_id_hashed', item.xpath(xpHeadOfHouseholdIDHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('export_id', self.export_id, 'text')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Household)
    
                ''' Parse sub-tables '''
                self.parse_members(item)
    
    def parse_members(self, element):
        ''' Element paths '''
        xpMembers = 'hmis:Members'
        xpMember = 'hmis:Member'
        xpPersonIDUnhashed = 'hmis:PersonID/hmis:Unhashed'
        xpPersonIDHashed = 'hmis:PersonID/hmis:Hashed'
        xpRelationshipToHeadOfHousehold = 'hmis:RelationshipToHeadOfHousehold'
        
        test = element.xpath(xpMembers, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if len(test) > 0:
            itemElements = test[0].xpath(xpMember, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
            if itemElements is not None:
                for item in itemElements:
                    self.parse_dict = {}

                    ''' Map elements to database columns '''
                    self.existence_test_and_add('person_id_unhashed', item.xpath(xpPersonIDUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                    self.existence_test_and_add('person_id_hashed', item.xpath(xpPersonIDHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                    self.existence_test_and_add('relationship_to_head_of_household', item.xpath(xpRelationshipToHeadOfHousehold, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
        
                    ''' Foreign Keys '''
                    self.existence_test_and_add('household_index_id', self.household_index_id, 'no_handling')
        
                    ''' Shred to database '''
                    self.shred(self.parse_dict, dbobjects.Members)

    def parse_region(self, element):
        ''' Element paths '''
        xpRegion = 'hmis:Region'
        xpRegionIDIDNum = 'hmis:RegionID/hmis:IDNum'
        xpRegionIDIDStr = 'hmis:RegionID/hmis:IDStr'
        xpSiteServiceID = 'hmis:SiteServiceID'
        xpRegionType = 'hmis:RegionType'
        xpRegionTypeDateCollected = 'hmis:RegionType/@hmis:dateCollected'
        xpRegionTypeDateEffective = 'hmis:RegionType/@hmis:dateEffective'
        xpRegionTypeDataCollectionStage = 'hmis:RegionType/@hmis:dataCollectionStage'
        xpRegionDescription = 'hmis:RegionDescription'
        xpRegionDescriptionDateCollected = 'hmis:RegionDescription/@hmis:dateCollected'
        xpRegionDescriptionDateEffective = 'hmis:RegionDescription/@hmis:dateEffective'
        xpRegionDescriptionDataCollectionStage = 'hmis:RegionDescription/@hmis:dataCollectionStage'
        
        itemElements = element.xpath(xpRegion, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('region_id_id_num', item.xpath(xpRegionIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('region_id_id_str', item.xpath(xpRegionIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_service_id', item.xpath(xpSiteServiceID, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('region_type', item.xpath(xpRegionType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('region_type_date_collected', item.xpath(xpRegionTypeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('region_type_date_effective', item.xpath(xpRegionTypeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('region_type_data_collection_stage', item.xpath(xpRegionTypeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('region_description', item.xpath(xpRegionDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('region_description_date_collected', item.xpath(xpRegionDescriptionDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('region_description_date_effective', item.xpath(xpRegionDescriptionDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('region_description_data_collection_stage', item.xpath(xpRegionDescriptionDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('export_id', self.export_id, 'text')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Region)
    
    def parse_agency(self, element):
        ''' Element paths '''
        xpAgency = 'hmis:Agency'
        xpAgencyDelete = '../hmis:Agency/@Delete'
        xpAgencyDeleteOccurredDate = '../hmis:Agency/@DeleteOccurredDate'
        xpAgencyDeleteEffective = '../hmis:Agency/@DeleteEffective'
        xpAirsKey = 'airs:Key'
        xpAirsName = 'airs:Name'
        xpAgencyDescription = 'airs:AgencyDescription'
        xpIRSStatus = 'airs:IRSStatus'
        xpSourceOfFunds = 'airs:SourceOfFunds'
        #xpRecordOwner = '@hmis:RecordOwner'
        xpRecordOwner = '../hmis:Agency/@RecordOwner'
        #xpFEIN = '@hmis:FEIN'
        xpFEIN = '../hmis:Agency/@FEIN'
        xpYearInc = '../hmis:Agency/@YearInc'
        xpAnnualBudgetTotal = '../hmis:Agency/@AnnualBudgetTotal'
        xpLegalStatus = '../hmis:Agency/@LegalStatus'
        xpExcludeFromWebsite = '../hmis:Agency/@ExcludeFromWebsite'
        xpExcludeFromDirectory = '../hmis:Agency/@ExcludeFromDirectory'
        
        itemElements = element.xpath(xpAgency, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('attr_delete', item.xpath(xpAgencyDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('attr_delete_occurred_date', item.xpath(xpAgencyDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_effective', item.xpath(xpAgencyDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('airs_key', item.xpath(xpAirsKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('airs_name', item.xpath(xpAirsName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('agency_description', item.xpath(xpAgencyDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('irs_status', item.xpath(xpIRSStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('source_of_funds', item.xpath(xpSourceOfFunds, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('fein', item.xpath(xpFEIN, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('record_owner', item.xpath(xpRecordOwner, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('year_inc', item.xpath(xpYearInc, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('annual_budget_total', item.xpath(xpAnnualBudgetTotal, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('legal_status', item.xpath(xpLegalStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('exclude_from_website', item.xpath(xpExcludeFromWebsite, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('exclude_from_directory', item.xpath(xpExcludeFromDirectory, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                # SBB20100901 Agency foreign key field is export_index_id
                #self.existence_test_and_add('export_id', self.export_id, 'text')
                self.existence_test_and_add('export_index_id', self.export_id, 'text')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Agency)
    
                ''' Parse sub-tables '''
                
                
                self.parse_agency_service(item)
                
                self.parse_aka(item)
                # SBB20100907 Missing, adding back in.
                self.parse_agency_location(item)
                
                # remove this once done with routine, shouldn't pollute keys for other values being parsed
                self.agency_location_index_id = None
                
                self.parse_phone(item)      
                self.parse_url(item)
                self.parse_email(item)      
                self.parse_contact(item)
                self.parse_license_accreditation(item)
                
                self.parse_service_group(item)
                
                # need to reset the contact index once we start processing a site element (because site can have their own contacts)
                self.contact_index_id = None
                
                self.parse_site(item)
                # SBB20100907 clear out the agency primary key - fouling up other parsers
                self.site_index_id = None
                
                self.parse_resource_info(item)
                
                # SBB20100907 clear out the agency primary key - fouling up other parsers
                # done with Agency, clear out the agency primary key, don't want it floating down to other elements.
                self.agency_index_id = None
                
                
    def parse_person(self, element):
        ''' Element paths '''
        xpPerson = 'hmis:Person'
        xpPersonIDNum = 'hmis:PersonID/hmis:IDNum'
        xpPersonIDStr = 'hmis:PersonID/hmis:IDStr'
        xpPersonDeleteOccurredDate = 'hmis:PersonID/@hmis:DeleteOccurredDate'
        xpPersonDeleteEffective = 'hmis:PersonID/@hmis:DeleteEffective'
        xpPersonDelete = 'hmis:PersonID/@hmis:Delete'
        xpPersonDateOfBirthHashed = 'hmis:DateOfBirth/hmis:Hashed'
        xpPersonDateOfBirthHashedDeleteOccurredDate = 'hmis:DateOfBirth/hmis:Hashed/@hmis:DeleteOccurredDate'
        xpPersonDateOfBirthHashedDeleteEffective = 'hmis:DateOfBirth/hmis:Hashed/@hmis:DeleteEffective'
        xpPersonDateOfBirthHashedDelete = 'hmis:DateOfBirth/hmis:Hashed/@hmis:Delete'
        xpPersonDateOfBirthUnhashed = 'hmis:DateOfBirth/hmis:Unhashed'
        xpPersonDateOfBirthUnhashedDeleteOccurredDate = 'hmis:DateOfBirth/hmis:Unhashed/@hmis:DeleteOccurredDate'
        xpPersonDateOfBirthUnhashedDeleteEffective = 'hmis:DateOfBirth/hmis:Unhashed/@hmis:DeleteEffective'
        xpPersonDateOfBirthUnhashedDelete = 'hmis:DateOfBirth/hmis:Unhashed/@hmis:Delete'
        xpPersonEthnicityHashed = 'hmis:Ethnicity/hmis:Hashed'
        xpPersonEthnicityHashedDeleteOccurredDate = 'hmis:Ethnicity/hmis:Hashed/@hmis:DeleteOccurredDate'
        xpPersonEthnicityHashedDeleteEffective = 'hmis:Ethnicity/hmis:Hashed/@hmis:DeleteEffective'
        xpPersonEthnicityHashedDelete = 'hmis:Ethnicity/hmis:Hashed/@hmis:Delete'
        xpPersonEthnicityUnhashed = 'hmis:Ethnicity/hmis:Unhashed'
        xpPersonEthnicityUnhashedDeleteOccurredDate = 'hmis:Ethnicity/hmis:Unhashed/@hmis:DeleteOccurredDate'
        xpPersonEthnicityUnhashedDeleteEffective = 'hmis:Ethnicity/hmis:Unhashed/@hmis:DeleteEffective'
        xpPersonEthnicityUnhashedDelete = 'hmis:Ethnicity/hmis:Unhashed/@hmis:Delete'
        xpPersonGenderHashed = 'hmis:Gender/hmis:Hashed'
        xpPersonGenderHashedDeleteOccurredDate = 'hmis:Gender/hmis:Hashed/@hmis:DeleteOccurredDate'
        xpPersonGenderHashedDeleteEffective = 'hmis:Gender/hmis:Hashed/@hmis:DeleteEffective'
        xpPersonGenderHashedDelete = 'hmis:Gender/hmis:Hashed/@hmis:Delete'
        xpPersonGenderUnhashed = 'hmis:Gender/hmis:Unhashed'
        xpPersonGenderUnhashedDeleteOccurredDate = 'hmis:Gender/hmis:Unhashed/@hmis:DeleteOccurredDate'
        xpPersonGenderUnhashedDeleteEffective = 'hmis:Gender/hmis:Unhashed/@hmis:DeleteEffective'
        xpPersonGenderUnhashedDelete = 'hmis:Gender/hmis:Unhashed/@hmis:Delete'
        xpPersonLegalFirstNameHashed = 'hmis:LegalFirstName/hmis:Hashed'
        xpPersonLegalFirstNameHashedDeleteOccurredDate = 'hmis:LegalFirstName/hmis:Hashed/@hmis:DeleteOccurredDate'
        xpPersonLegalFirstNameHashedDeleteEffective = 'hmis:LegalFirstName/hmis:Hashed/@hmis:DeleteEffective'
        xpPersonLegalFirstNameHashedDelete = 'hmis:LegalFirstName/hmis:Hashed/@hmis:Delete'
        xpPersonLegalFirstNameUnhashed = 'hmis:LegalFirstName/hmis:Unhashed'
        xpPersonLegalFirstNameUnhashedDeleteOccurredDate = 'hmis:LegalFirstName/hmis:Unhashed/@hmis:DeleteOccurredDate'
        xpPersonLegalFirstNameUnhashedDeleteEffective = 'hmis:LegalFirstName/hmis:Unhashed/@hmis:DeleteEffective'
        xpPersonLegalFirstNameUnhashedDelete = 'hmis:LegalFirstName/hmis:Unhashed/@hmis:Delete'
        xpPersonLegalLastNameHashed = 'hmis:LegalLastName/hmis:Hashed'
        xpPersonLegalLastNameHashedDeleteOccurredDate = 'hmis:LegalLastName/hmis:Hashed/@hmis:DeleteOccurredDate'
        xpPersonLegalLastNameHashedDeleteEffective = 'hmis:LegalLastName/hmis:Hashed/@hmis:DeleteEffective'
        xpPersonLegalLastNameHashedDelete = 'hmis:LegalLastName/hmis:Hashed/@hmis:Delete'
        xpPersonLegalLastNameUnhashed = 'hmis:LegalLastName/hmis:Unhashed'
        xpPersonLegalLastNameUnhashedDeleteOccurredDate = 'hmis:LegalLastName/hmis:Unhashed/@hmis:DeleteOccurredDate'
        xpPersonLegalLastNameUnhashedDeleteEffective = 'hmis:LegalLastName/hmis:Unhashed/@hmis:DeleteEffective'
        xpPersonLegalLastNameUnhashedDelete = 'hmis:LegalLastName/hmis:Unhashed/@hmis:Delete'
        xpPersonLegalMiddleNameHashed = 'hmis:LegalMiddleName/hmis:Hashed'
        xpPersonLegalMiddleNameHashedDeleteOccurredDate = 'hmis:LegalMiddleName/hmis:Hashed/@hmis:DeleteOccurredDate'
        xpPersonLegalMiddleNameHashedDeleteEffective = 'hmis:LegalMiddleName/hmis:Hashed/@hmis:DeleteEffective'
        xpPersonLegalMiddleNameHashedDelete = 'hmis:LegalMiddleName/hmis:Hashed/@hmis:Delete'
        xpPersonLegalMiddleNameUnhashed = 'hmis:LegalMiddleName/hmis:Unhashed'
        xpPersonLegalMiddleNameUnhashedDeleteOccurredDate = 'hmis:LegalMiddleName/hmis:Unhashed/@hmis:DeleteOccurredDate'
        xpPersonLegalMiddleNameUnhashedDeleteEffective = 'hmis:LegalMiddleName/hmis:Unhashed/@hmis:DeleteEffective'
        xpPersonLegalMiddleNameUnhashedDelete = 'hmis:LegalMiddleName/hmis:Unhashed/@hmis:Delete'
        xpPersonLegalSuffixHashed = 'hmis:LegalSuffix/hmis:Hashed'
        xpPersonLegalSuffixHashedDeleteOccurredDate = 'hmis:LegalSuffix/hmis:Hashed/@hmis:DeleteOccurredDate'
        xpPersonLegalSuffixHashedDeleteEffective = 'hmis:LegalSuffix/hmis:Hashed/@hmis:DeleteEffective'
        xpPersonLegalSuffixHashedDelete = 'hmis:LegalSuffix/hmis:Hashed/@hmis:Delete'
        xpPersonLegalSuffixUnhashed = 'hmis:LegalSuffix/hmis:Unhashed'
        xpPersonLegalSuffixUnhashedDeleteOccurredDate = 'hmis:LegalSuffix/hmis:Unhashed/@hmis:DeleteOccurredDate'
        xpPersonLegalSuffixUnhashedDeleteEffective = 'hmis:LegalSuffix/hmis:Unhashed/@hmis:DeleteEffective'
        xpPersonLegalSuffixUnhashedDelete = 'hmis:LegalSuffix/hmis:Unhashed/@hmis:Delete'
        xpPersonSocialSecurityNumberHashed = 'hmis:SocialSecurityNumber/hmis:Hashed'
        xpPersonSocialSecurityNumberHashedDeleteOccurredDate = 'hmis:SocialSecurityNumber/hmis:Hashed/@hmis:DeleteOccurredDate'
        xpPersonSocialSecurityNumberHashedDeleteEffective = 'hmis:SocialSecurityNumber/hmis:Hashed/@hmis:DeleteEffective'
        xpPersonSocialSecurityNumberHashedDelete = 'hmis:SocialSecurityNumber/hmis:Hashed/@hmis:Delete'
        xpPersonSocialSecurityNumberUnhashed = 'hmis:SocialSecurityNumber/hmis:Unhashed'
        xpPersonSocialSecurityNumberUnhashedDeleteOccurredDate = 'hmis:SocialSecurityNumber/hmis:Unhashed/@hmis:DeleteOccurredDate'
        xpPersonSocialSecurityNumberUnhashedDeleteEffective = 'hmis:SocialSecurityNumber/hmis:Unhashed/@hmis:DeleteEffective'
        xpPersonSocialSecurityNumberUnhashedDelete = 'hmis:SocialSecurityNumber/hmis:Unhashed/@hmis:Delete'
        xpPersonSocialSecNumberQualityCode = 'hmis:SocialSecurityNumber/hmis:SocialSecNumberQualityCode'
        xpPersonSocialSecNumberQualityCodeDeleteOccurredDate = 'hmis:SocialSecurityNumber/hmis:SocialSecNumberQualityCode/@hmis:DeleteOccurredDate'
        xpPersonSocialSecNumberQualityCodeDeleteEffective = 'hmis:SocialSecurityNumber/hmis:SocialSecNumberQualityCode/@hmis:DeleteEffective'
        xpPersonSocialSecNumberQualityCodeDelete = 'hmis:SocialSecurityNumber/hmis:SocialSecNumberQualityCode/@hmis:Delete'

        itemElements = element.xpath(xpPerson, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('person_id_id_num_2010', item.xpath(xpPersonIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_id_id_str_2010', item.xpath(xpPersonIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_id_delete_occurred_date_2010', item.xpath(xpPersonDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_id_delete_effective_2010', item.xpath(xpPersonDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_id_delete_2010', item.xpath(xpPersonDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_date_of_birth_hashed', item.xpath(xpPersonDateOfBirthHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_date_of_birth_hashed_delete_occurred_date_2010', item.xpath(xpPersonDateOfBirthHashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_date_of_birth_hashed_delete_effective_2010', item.xpath(xpPersonDateOfBirthHashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_date_of_birth_hashed_delete_2010', item.xpath(xpPersonDateOfBirthHashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_date_of_birth_unhashed', item.xpath(xpPersonDateOfBirthUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_date_of_birth_unhashed_delete_occurred_date_2010', item.xpath(xpPersonDateOfBirthUnhashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_date_of_birth_unhashed_delete_effective_2010', item.xpath(xpPersonDateOfBirthUnhashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_date_of_birth_unhashed_delete_2010', item.xpath(xpPersonDateOfBirthUnhashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_ethnicity_hashed', item.xpath(xpPersonEthnicityHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_ethnicity_hashed_delete_occurred_date_2010', item.xpath(xpPersonEthnicityHashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_ethnicity_hashed_delete_effective_2010', item.xpath(xpPersonEthnicityHashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_ethnicity_hashed_delete_2010', item.xpath(xpPersonEthnicityHashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_ethnicity_unhashed', item.xpath(xpPersonEthnicityUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_ethnicity_unhashed_delete_occurred_date_2010', item.xpath(xpPersonEthnicityUnhashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_ethnicity_unhashed_delete_effective_2010', item.xpath(xpPersonEthnicityUnhashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_ethnicity_unhashed_delete_2010', item.xpath(xpPersonEthnicityUnhashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_gender_hashed', item.xpath(xpPersonGenderHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_gender_hashed_delete_occurred_date_2010', item.xpath(xpPersonGenderHashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_gender_hashed_delete_effective_2010', item.xpath(xpPersonGenderHashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_gender_hashed_delete_2010', item.xpath(xpPersonGenderHashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_gender_unhashed', item.xpath(xpPersonGenderUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_gender_unhashed_delete_occurred_date_2010', item.xpath(xpPersonGenderUnhashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_gender_unhashed_delete_effective_2010', item.xpath(xpPersonGenderUnhashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_gender_unhashed_delete_2010', item.xpath(xpPersonGenderUnhashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_first_name_hashed', item.xpath(xpPersonLegalFirstNameHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_first_name_hashed_delete_occurred_date_2010', item.xpath(xpPersonLegalFirstNameHashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_first_name_hashed_delete_effective_2010', item.xpath(xpPersonLegalFirstNameHashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_first_name_hashed_delete_2010', item.xpath(xpPersonLegalFirstNameHashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_first_name_unhashed', item.xpath(xpPersonLegalFirstNameUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_first_name_unhashed_delete_occurred_date_2010', item.xpath(xpPersonLegalFirstNameUnhashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_first_name_unhashed_delete_effective_2010', item.xpath(xpPersonLegalFirstNameUnhashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_first_name_unhashed_delete_2010', item.xpath(xpPersonLegalFirstNameUnhashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_last_name_hashed', item.xpath(xpPersonLegalLastNameHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_last_name_unhashed_delete_occurred_date_2010', item.xpath(xpPersonLegalLastNameHashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_last_name_unhashed_delete_effective_2010', item.xpath(xpPersonLegalLastNameHashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_last_name_unhashed_delete_2010', item.xpath(xpPersonLegalLastNameHashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_last_name_unhashed', item.xpath(xpPersonLegalLastNameUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_last_name_hashed_delete_occurred_date_2010', item.xpath(xpPersonLegalLastNameUnhashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_last_name_hashed_delete_effective_2010', item.xpath(xpPersonLegalLastNameUnhashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_last_name_hashed_delete_2010', item.xpath(xpPersonLegalLastNameUnhashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_middle_name_hashed', item.xpath(xpPersonLegalMiddleNameHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_middle_name_hashed_delete_occurred_date_2010', item.xpath(xpPersonLegalMiddleNameHashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_middle_name_hashed_delete_effective_2010', item.xpath(xpPersonLegalMiddleNameHashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_middle_name_hashed_delete_2010', item.xpath(xpPersonLegalMiddleNameHashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_middle_name_unhashed', item.xpath(xpPersonLegalMiddleNameUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_middle_name_unhashed_delete_occurred_date_2010', item.xpath(xpPersonLegalMiddleNameUnhashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_middle_name_unhashed_delete_effective_2010', item.xpath(xpPersonLegalMiddleNameUnhashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_middle_name_unhashed_delete_2010', item.xpath(xpPersonLegalMiddleNameUnhashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_suffix_hashed', item.xpath(xpPersonLegalSuffixHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_suffix_hashed_delete_occurred_date_2010', item.xpath(xpPersonLegalSuffixHashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_suffix_hashed_delete_effective_2010', item.xpath(xpPersonLegalSuffixHashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_suffix_hashed_delete_2010', item.xpath(xpPersonLegalSuffixHashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_suffix_unhashed', item.xpath(xpPersonLegalSuffixUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_legal_suffix_unhashed_delete_occurred_date_2010', item.xpath(xpPersonLegalSuffixUnhashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_suffix_unhashed_delete_effective_2010', item.xpath(xpPersonLegalSuffixUnhashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_legal_suffix_unhashed_delete_2010', item.xpath(xpPersonLegalSuffixUnhashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_social_security_number_hashed', item.xpath(xpPersonSocialSecurityNumberHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_social_security_number_hashed_delete_occurred_date_2010', item.xpath(xpPersonSocialSecurityNumberHashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_social_security_number_hashed_delete_effective_2010', item.xpath(xpPersonSocialSecurityNumberHashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_social_security_number_hashed_delete_2010', item.xpath(xpPersonSocialSecurityNumberHashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_social_security_number_unhashed', item.xpath(xpPersonSocialSecurityNumberUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_social_security_number_unhashed_delete_occurred_date_2010', item.xpath(xpPersonSocialSecurityNumberUnhashedDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_social_security_number_unhashed_delete_effective_2010', item.xpath(xpPersonSocialSecurityNumberUnhashedDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_social_security_number_unhashed_delete_2010', item.xpath(xpPersonSocialSecurityNumberUnhashedDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_social_sec_number_quality_code', item.xpath(xpPersonSocialSecNumberQualityCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_social_security_number_quality_code_delete_occurred_date_2010', item.xpath(xpPersonSocialSecNumberQualityCodeDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_social_security_number_quality_code_delete_effective_2010', item.xpath(xpPersonSocialSecNumberQualityCodeDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_social_security_number_quality_code_delete_2010', item.xpath(xpPersonSocialSecNumberQualityCodeDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('export_id', self.export_id, 'text')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Person)
    
                ''' Parse sub-tables '''
                self.parse_site_service_participation(item)
                self.parse_need(item)          
                self.parse_service_event(item)
                self.parse_person_historical(item)
                self.parse_release_of_information(item)
                self.parse_other_names(item)
                self.parse_races(item)

    def parse_service(self, element):
        ''' Element paths '''
        xpService = 'hmis:Service'
        xpServiceDeleteOccurredDate = '@hmis:DeleteOccurredDate'
        xpServiceDeleteEffective = '@hmis:DeleteEffective'
        xpServiceDelete = '@hmis:Delete'
        xpAirsKey = 'airs:Key'
        xpAirsAgencyKey = 'airs:AgencyKey'
        xpAirsName = 'airs:Name'
        xpCOCCode = 'hmis:COCCode'
        xpConfiguration = 'hmis:Configuration'
        xpDirectServiceCode = 'hmis:DirectServiceCode'
        xpGranteeIdentifier = 'hmis:GranteeIdentifier'
        xpIndividualFamilyCode = 'hmis:IndividualFamilyCode'
        xpResidentialTrackingMethod = 'hmis:ResidentialTrackingMethod'
        xpServiceType = 'hmis:ServiceType'
        xpServiceEffectivePeriodStartDate = 'hmis:ServiceEffectivePeriod/hmis:StartDate'
        xpServiceEffectivePeriodEndDate = 'hmis:ServiceEffectivePeriod/hmis:EndDate'
        xpServiceRecordedDate = 'hmis:ServiceRecordedDate'
        xpTargetPopulationA = 'hmis:TargetPopulationA'
        xpTargetPopulationB = 'hmis:TargetPopulationB'

        itemElements = element.xpath(xpService, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('attr_delete_occurred_date', item.xpath(xpServiceDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_effective', item.xpath(xpServiceDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_delete', item.xpath(xpServiceDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('airs_key', item.xpath(xpAirsKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('residential_tracking_method', item.xpath(xpAirsAgencyKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('airs_name', item.xpath(xpAirsName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('coc_code', item.xpath(xpCOCCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('configuration', item.xpath(xpConfiguration, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('direct_service_code', item.xpath(xpDirectServiceCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('grantee_identifier', item.xpath(xpGranteeIdentifier, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('individual_family_code', item.xpath(xpIndividualFamilyCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('residential_tracking_method', item.xpath(xpResidentialTrackingMethod, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_type', item.xpath(xpServiceType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_effective_period_start_date', item.xpath(xpServiceEffectivePeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_effective_period_end_date', item.xpath(xpServiceEffectivePeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_recorded_date', item.xpath(xpServiceRecordedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('target_population_a', item.xpath(xpTargetPopulationA, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('target_population_b', item.xpath(xpTargetPopulationB, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                
                ''' Foreign Keys '''
                self.existence_test_and_add('export_id', self.export_id, 'text')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Service)
    
                ''' Parse sub-tables '''
                self.parse_funding_source(item)
                self.parse_inventory(item)      

    def parse_site(self, element):
        ''' Element paths '''
        xpSite = 'airs:Site'
        xpSiteDeleteOccurredDate = '@airs:DeleteOccurredDate'
        xpSiteDeleteEffective = '@airs:DeleteEffective'
        xpSiteDelete = '@airs:Delete'
        xpKey = 'airs:Key'
        xpName = 'airs:Name'
        xpSiteDescription = 'airs:SiteDescription'
        xpPhysicalAddressPreAddressLine = 'airs:PhysicalAddress/airs:PreAddressLine'
        xpPhysicalAddressLine1 = 'airs:PhysicalAddress/airs:Line1'
        xpPhysicalAddressLine2 = 'airs:PhysicalAddress/airs:Line2'
        xpPhysicalAddressCity = 'airs:PhysicalAddress/airs:City'
        xpPhysicalAddressCounty = 'airs:PhysicalAddress/airs:County'
        xpPhysicalAddressState = 'airs:PhysicalAddress/airs:State'
        xpPhysicalAddressZipCode = 'airs:PhysicalAddress/airs:ZipCode'
        xpPhysicalAddressCountry = 'airs:PhysicalAddress/airs:Country'
        xpPhysicalAddressReasonWithheld = 'airs:PhysicalAddress/airs:ReasonWithheld'
        xpPhysicalAddressConfidential = 'airs:PhysicalAddress/@airs:Confidential'
        xpPhysicalAddressDescription = 'airs:PhysicalAddress/@airs:Description' 
        xpMailingAddressPreAddressLine = 'airs:MailingAddress/airs:PreAddressLine'
        xpMailingAddressLine1 = 'airs:MailingAddress/airs:Line1'
        xpMailingAddressLine2 = 'airs:MailingAddress/airs:Line2'
        xpMailingAddressCity = 'airs:MailingAddress/airs:City'
        xpMailingAddressCounty = 'airs:MailingAddress/airs:County'
        xpMailingAddressState = 'airs:MailingAddress/airs:State'
        xpMailingAddressZipCode = 'airs:MailingAddress/airs:ZipCode'
        xpMailingAddressCountry = 'airs:MailingAddress/airs:Country'
        xpMailingAddressReasonWithheld = 'airs:MailingAddress/airs:ReasonWithheld'
        xpMailingAddressConfidential = 'airs:MailingAddress/@airs:Confidential'
        xpMailingAddressDescription = 'airs:MailingAddress/@airs:Description'       
        xpNoPhysicalAddressDescription = 'airs:NoPhysicalAddress/airs:Description'        
        xpNoPhysicalAddressExplanation = 'airs:NoPhysicalAddress/airs:Explanation'        
        xpDisabilitiesAccess = 'airs:DisabilitiesAccess'
        xpPhysicalLocationDescription = 'airs:PhysicalLocationDescription'
        xpBusServiceAccess = 'airs:BusServiceAccess'
        xpPublicAccessToTransportation = "../%s/%s" % (xpSite, '@PublicAccessToTransportation')
        xpYearInc = "../%s/%s" % (xpSite, '@YearInc')
        xpAnnualBudgetTotal = "../%s/%s" % (xpSite, '@AnnualBudgetTotal')
        xpLegalStatus = "../%s/%s" % (xpSite, '@LegalStatus')
        xpExcludeFromWebsite = "../%s/%s" % (xpSite, '@ExcludeFromWebsite')
        xpExcludeFromDirectory = "../%s/%s" % (xpSite, '@ExcludeFromDirectory')
        xpAgencyKey = 'airs:AgencyKey'

        itemElements = element.xpath(xpSite, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('attr_delete_occurred_date', item.xpath(xpSiteDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_effective', item.xpath(xpSiteDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_delete', item.xpath(xpSiteDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('airs_key', item.xpath(xpKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('airs_name', item.xpath(xpName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_description', item.xpath(xpSiteDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_pre_address_line', item.xpath(xpPhysicalAddressPreAddressLine, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_line_1', item.xpath(xpPhysicalAddressLine1, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_line_2', item.xpath(xpPhysicalAddressLine2, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_city', item.xpath(xpPhysicalAddressCity, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_state', item.xpath(xpPhysicalAddressState, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_zip_code', item.xpath(xpPhysicalAddressZipCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_country', item.xpath(xpPhysicalAddressCountry, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_reason_withheld', item.xpath(xpPhysicalAddressReasonWithheld, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_confidential', item.xpath(xpPhysicalAddressConfidential, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_description', item.xpath(xpPhysicalAddressDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_pre_address_line', item.xpath(xpMailingAddressPreAddressLine, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_line_1', item.xpath(xpMailingAddressLine1, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_line_2', item.xpath(xpMailingAddressLine2, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_city', item.xpath(xpMailingAddressCity, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_state', item.xpath(xpMailingAddressState, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_zip_code', item.xpath(xpMailingAddressZipCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_country', item.xpath(xpMailingAddressCountry, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_reason_withheld', item.xpath(xpMailingAddressReasonWithheld, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_confidential', item.xpath(xpMailingAddressConfidential, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_description', item.xpath(xpMailingAddressDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')    
                self.existence_test_and_add('no_physical_address_description', item.xpath(xpNoPhysicalAddressDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')      
                self.existence_test_and_add('no_physical_address_explanation', item.xpath(xpNoPhysicalAddressExplanation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text') 
                self.existence_test_and_add('disabilities_access', item.xpath(xpDisabilitiesAccess, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_location_description', item.xpath(xpPhysicalLocationDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('bus_service_access', item.xpath(xpBusServiceAccess, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('public_access_to_transportation', item.xpath(xpPublicAccessToTransportation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('year_inc', item.xpath(xpYearInc, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('annual_budget_total', item.xpath(xpAnnualBudgetTotal, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('legal_status', item.xpath(xpLegalStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('exclude_from_website', item.xpath(xpExcludeFromWebsite, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('exclude_from_directory', item.xpath(xpExcludeFromDirectory, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('agency_key', item.xpath(xpAgencyKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('export_id', self.export_id, 'text')
                except: pass
                try: self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                except: pass
                    
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Site)
    
                ''' Parse sub-tables '''
                self.parse_url(item)
                self.parse_spatial_location(item)
                self.parse_other_address(item)
                self.parse_cross_street(item)
                self.parse_aka(item)
                self.parse_site_service(item)
                self.parse_languages(item)
                self.parse_time_open(item)            
                self.parse_inventory(item)
                #self.parse_contact(item)            
                self.parse_email(item)      
                self.parse_phone(item)
                # SBB20100907 moved till after email and phone (which are part of the site record, contact will drive it's own searches for email and phone (of the contact))
                self.parse_contact(item) 
    
    # SBB20100916 Adding namespace, site_service can be in both hmis and airs namespaces, needs to be passed by calling context defaulting to hmis, overridden from calling function as airs
    def parse_site_service(self, element, namespace='hmis'):
        ''' Element paths '''
        xpSiteService = '%s:SiteService' % namespace
        xpSiteServiceDeleteOccurredDate = '@airs:DeleteOccurredDate'
        xpSiteServiceDeleteEffective = '@airs:DeleteEffective'
        xpSiteServiceDelete = '@airs:Delete'
        xpName = 'airs:Name'
        xpKey = 'airs:Key'
        xpDescription = 'airs:Description'
        xpFeeStructure = 'airs:FeeStructure'
        xpGenderRequirements = 'airs:GenderRequirements'
        
        xpAreaFlexibility = "../%s/@%s" % (xpSiteService, 'AreaFlexibility')
        xpServiceNotAlwaysAvailable = "../%s/@%s" % (xpSiteService, 'ServiceNotAlwaysAvailable')
        xpServiceGroupKey = "../%s/@%s" % (xpSiteService, 'ServiceGroupKey')
        
        xpServiceID = 'airs:ServiceID'
        xpSiteID = 'airs:SiteID'
        xpGeographicCode = 'airs:GeographicCode'
        xpGeographicCodeDateCollected = 'hmis:GeographicCode/@hmis:dateCollected'
        xpGeographicCodeDateEffective = 'hmis:GeographicCode/@hmis:dateEffective'
        xpGeographicCodeDataCollectionStage = 'hmis:GeographicCode/@hmis:dataCollectionStage'
        xpHousingType = 'airs:HousingType'
        xpHousingTypeDateCollected = 'hmis:HousingType/@hmis:dateCollected'
        xpHousingTypeDateEffective = 'hmis:HousingType/@hmis:dateEffective'
        xpHousingTypeDataCollectionStage = 'hmis:HousingType/@hmis:dataCollectionStage'
        xpPrincipal = 'airs:Principal'
        xpSiteServiceEffectivePeriodStartDate = 'airs:SiteServiceEffectivePeriod/hmis:StartDate'
        xpSiteServiceEffectivePeriodEndDate = 'airs:SiteServiceEffectivePeriod/hmis:EndDate'
        xpSiteServiceRecordedDate = 'airs:SiteServiceRecordedDate'
        xpSiteServiceType = 'airs:SiteServiceType'

        itemElements = element.xpath(xpSiteService, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('attr_delete_occurred_date', item.xpath(xpSiteServiceDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_effective', item.xpath(xpSiteServiceDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_delete', item.xpath(xpSiteServiceDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('name', item.xpath(xpName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('key', item.xpath(xpKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('fee_structure', item.xpath(xpFeeStructure, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('gender_requirements', item.xpath(xpGenderRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                
                self.existence_test_and_add('area_flexibility', item.xpath(xpAreaFlexibility, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('service_not_always_available', item.xpath(xpServiceNotAlwaysAvailable, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('service_group_key', item.xpath(xpServiceGroupKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                
                self.existence_test_and_add('service_id', item.xpath(xpServiceID, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_id', item.xpath(xpSiteID, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('geographic_code', item.xpath(xpGeographicCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('geographic_code_date_collected', item.xpath(xpGeographicCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('geographic_code_date_effective', item.xpath(xpGeographicCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('geographic_code_data_collection_stage', item.xpath(xpGeographicCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('housing_type', item.xpath(xpHousingType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('housing_type_date_collected', item.xpath(xpHousingTypeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('housing_type_date_effective', item.xpath(xpHousingTypeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('housing_type_data_collection_stage', item.xpath(xpHousingTypeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('principal', item.xpath(xpPrincipal, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_service_effective_period_start_date', item.xpath(xpSiteServiceEffectivePeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')
                self.existence_test_and_add('site_service_effective_period_end_date', item.xpath(xpSiteServiceEffectivePeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')
                self.existence_test_and_add('site_service_recorded_date', item.xpath(xpSiteServiceRecordedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_service_type', item.xpath(xpSiteServiceType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('export_id', self.export_id, 'text')
                except: pass
                try: self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                except: pass
                # SBB20100916 missing
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.SiteService)
    
                ''' Parse sub-tables '''
                self.parse_seasonal(item)
                self.parse_residency_requirements(item)
                self.parse_pit_count_set(item)
                self.parse_other_requirements(item)
                self.parse_languages(item)
                self.parse_time_open(item)            
                self.parse_inventory(item)
                self.parse_income_requirements(item)
                self.parse_hmis_asset(item)
                self.parse_geographic_area_served(item)
                self.parse_documents_required(item)
                self.parse_aid_requirements(item)
                self.parse_age_requirements(item)
                self.parse_application_process(item)
                self.parse_taxonomy(item)
                self.parse_family_requirements(item)
                self.parse_resource_info(item)
                
    def parse_service_group(self, element):
        ''' Element paths '''
        xpServiceGroup = 'airs:ServiceGroup'
        xpAirsKey = 'airs:Key'
        xpAirsName = 'airs:Name'
        xpAirsAgencyKey = 'airs:ProgramName'

        itemElements = element.xpath(xpServiceGroup, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('key', item.xpath(xpAirsKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('name', item.xpath(xpAirsName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('program_name', item.xpath(xpAirsAgencyKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ServiceGroup)
    
                ''' Parse sub-tables '''

    def parse_license_accreditation(self, element):
        ''' Element paths '''
        xpLicenseAccreditation = 'airs:LicenseAccreditation'
        xpLicense = 'airs:License'
        xpLicensedBy = 'airs:LicensedBy'

        itemElements = element.xpath(xpLicenseAccreditation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('license', item.xpath(xpLicense, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('licensed_by', item.xpath(xpLicensedBy, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.LicenseAccreditation)
    
                ''' Parse sub-tables '''
                            

    def parse_agency_service(self, element):
        ''' Element paths '''
        xpAgencyService = 'airs:AgencyService'
        xpAirsKey = 'airs:Key'
        xpAgencyKey = 'airs:AgencyKey'
        xpAgencyName = 'airs:Name'

        itemElements = element.xpath(xpAgencyService, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('key', item.xpath(xpAirsKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('agency_key', item.xpath(xpAgencyKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('name', item.xpath(xpAgencyName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.AgencyService)
    
                ''' Parse sub-tables '''
                            

    def parse_url(self, element):
        ''' Element paths '''
        xpUrl = 'airs:URL'
        xpAddress = 'airs:Address'
        xpNote = 'airs:Note'

        itemElements = element.xpath(xpUrl, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('address', item.xpath(xpAddress, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('note', item.xpath(xpNote, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Url)
    
                ''' Parse sub-tables '''
                            

    def parse_spatial_location(self, element):
        ''' Element paths '''
        xpSpatialLocation = 'airs:SpatialLocation'
        xpDescription = 'airs:Description'
        xpDatum = 'airs:Datum'
        xpLatitude = 'airs:Latitude'
        xpLongitude = 'airs:Longitude'

        itemElements = element.xpath(xpSpatialLocation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('datum', item.xpath(xpDatum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('latitude', item.xpath(xpLatitude, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('longitude', item.xpath(xpLongitude, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try:self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.SpatialLocation)
    
                ''' Parse sub-tables '''
                            

    def parse_other_address(self, element):
        ''' Element paths '''
        xpOtherAddress = 'airs:OtherAddress'
        xpPreAddressLine = 'airs:PreAddressLine'
        xpLine1 = 'airs:Line1'
        xpLine2 = 'airs:Line2'
        xpCity = 'airs:City'
        xpCounty = 'airs:County'
        xpState = 'airs:State'
        xpZipCode = 'airs:ZipCode'
        xpCountry = 'airs:Country'
        xpReasonWithheld = 'airs:ReasonWithheld'
        xpConfidential = "../%s/%s" % (xpOtherAddress, '@Confidential')
        xpDescription = "../%s/%s" % (xpOtherAddress, '@Description')

        itemElements = element.xpath(xpOtherAddress, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('pre_address_line', item.xpath(xpPreAddressLine, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('line_1', item.xpath(xpLine1, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('line_2', item.xpath(xpLine2, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('city', item.xpath(xpCity, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('county', item.xpath(xpCounty, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('state', item.xpath(xpState, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('zip_code', item.xpath(xpZipCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('country', item.xpath(xpCountry, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('reason_withheld', item.xpath(xpReasonWithheld, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('confidential', item.xpath(xpConfidential, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                # SBB20100916 missing
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.OtherAddress)
    
                ''' Parse sub-tables '''
                            

    def parse_cross_street(self, element):
        ''' Element paths '''
        xpCrossStreet = 'airs:CrossStreet'

        itemElements = element.xpath(xpCrossStreet, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                # SBB20100916 No need to xpath this.  These are the elements, just stuff in the DB
                #self.existence_test_and_add('cross_street', item.xpath(xpCrossStreet, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('cross_street', item, 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                # SBB20100916 missing..
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.CrossStreet)
    
                ''' Parse sub-tables '''
                            

    # SBB20100914 adding in..missing
    def parse_agency_location(self, element):
        ''' Element paths '''
        # base tag
        xpAgencyLocation = 'airs:AgencyLocation'
        xpKey = 'airs:Key'
        xpName = 'airs:Name'
        xpSiteDescription = 'airs:SiteDescription'
        xpPhysicalAddressPreAddressLine = 'airs:PhysicalAddress/airs:PreAddressLine'
        xpPhysicalAddressLine1 = 'airs:PhysicalAddress/airs:Line1'
        xpPhysicalAddressLine2 = 'airs:PhysicalAddress/airs:Line2'
        xpPhysicalAddressCity = 'airs:PhysicalAddress/airs:City'
        xpPhysicalAddressCounty = 'airs:PhysicalAddress/airs:County'
        xpPhysicalAddressState = 'airs:PhysicalAddress/airs:State'
        xpPhysicalAddressZipCode = 'airs:PhysicalAddress/airs:ZipCode'
        xpPhysicalAddressCountry = 'airs:PhysicalAddress/airs:Country'
        xpPhysicalAddressReasonWithheld = 'airs:PhysicalAddress/airs:ReasonWithheld'
        xpPhysicalAddressConfidential = "../%s/@%s" % ('airs:PhysicalAddress', 'Confidential') 
        xpPhysicalAddressDescription = "../%s/@%s" % ('airs:PhysicalAddress', 'Description') 
        xpMailingAddressPreAddressLine = 'airs:MailingAddress/airs:PreAddressLine'
        xpMailingAddressLine1 = 'airs:MailingAddress/airs:Line1'
        xpMailingAddressLine2 = 'airs:MailingAddress/airs:Line2'
        xpMailingAddressCity = 'airs:MailingAddress/airs:City'
        xpMailingAddressCounty = 'airs:MailingAddress/airs:County'
        xpMailingAddressState = 'airs:MailingAddress/airs:State'
        xpMailingAddressZipCode = 'airs:MailingAddress/airs:ZipCode'
        xpMailingAddressCountry = 'airs:MailingAddress/airs:Country'
        xpMailingAddressReasonWithheld = 'airs:MailingAddress/airs:ReasonWithheld'
        
        xpMailingAddressConfidential = "%s/@%s" % ('airs:MailingAddress', 'Confidential')
        xpMailingAddressDescription = "%s/@%s" % ('airs:MailingAddress', 'Description')
        
        xpNoPhysicalAddressDescription = 'airs:NoPhysicalAddress/airs:Description'        
        xpNoPhysicalAddressExplanation = 'airs:NoPhysicalAddress/airs:Explanation'        
        xpDisabilitiesAccess = 'airs:DisabilitiesAccess'
        xpPhysicalLocationDescription = 'airs:PhysicalLocationDescription'
        xpBusServiceAccess = 'airs:BusServiceAccess'
        
        # attributes
        xpPublicAccessToTransportation = "../%s/@%s" % (xpAgencyLocation, 'PublicAccessToTransportation')
        xpYearInc = "../%s/@%s" % (xpAgencyLocation, 'YearInc')
        xpAnnualBudgetTotal = "../%s/@%s" % (xpAgencyLocation, 'AnnualBudgetTotal')
        xpLegalStatus = "../%s/@%s" % (xpAgencyLocation, 'LegalStatus')
        xpExcludeFromWebsite = "../%s/@%s" % (xpAgencyLocation, 'ExcludeFromWebsite')
        xpExcludeFromDirectory = "../%s/@%s" % (xpAgencyLocation, 'ExcludeFromDirectory')
        
        xpName = 'airs:Name'
        xpConfidential = 'airs:Confidential'
        xpDescription = 'airs:Description'

        itemElements = element.xpath(xpAgencyLocation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('key', item.xpath(xpKey, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('name', item.xpath(xpName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_description', item.xpath(xpSiteDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_pre_address_line', item.xpath(xpPhysicalAddressPreAddressLine, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_line_1', item.xpath(xpPhysicalAddressLine1, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_line_2', item.xpath(xpPhysicalAddressLine2, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_city', item.xpath(xpPhysicalAddressCity, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_state', item.xpath(xpPhysicalAddressState, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_zip_code', item.xpath(xpPhysicalAddressZipCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_country', item.xpath(xpPhysicalAddressCountry, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_reason_withheld', item.xpath(xpPhysicalAddressReasonWithheld, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_confidential', item.xpath(xpPhysicalAddressConfidential, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_address_description', item.xpath(xpPhysicalAddressDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_pre_address_line', item.xpath(xpMailingAddressPreAddressLine, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_line_1', item.xpath(xpMailingAddressLine1, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_line_2', item.xpath(xpMailingAddressLine2, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_city', item.xpath(xpMailingAddressCity, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_state', item.xpath(xpMailingAddressState, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_zip_code', item.xpath(xpMailingAddressZipCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_country', item.xpath(xpMailingAddressCountry, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_reason_withheld', item.xpath(xpMailingAddressReasonWithheld, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mailing_address_confidential', item.xpath(xpMailingAddressConfidential, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('mailing_address_description', item.xpath(xpMailingAddressDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')    
                self.existence_test_and_add('no_physical_address_description', item.xpath(xpNoPhysicalAddressDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')      
                self.existence_test_and_add('no_physical_address_explanation', item.xpath(xpNoPhysicalAddressExplanation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text') 
                self.existence_test_and_add('disabilities_access', item.xpath(xpDisabilitiesAccess, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('physical_location_description', item.xpath(xpPhysicalLocationDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('bus_service_access', item.xpath(xpBusServiceAccess, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                
                # attriubtes
                self.existence_test_and_add('public_access_to_transportation', item.xpath(xpPublicAccessToTransportation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('year_inc', item.xpath(xpYearInc, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('annual_budget_total', item.xpath(xpAnnualBudgetTotal, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('legal_status', item.xpath(xpLegalStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('exclude_from_website', item.xpath(xpExcludeFromWebsite, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('exclude_from_directory', item.xpath(xpExcludeFromDirectory, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.AgencyLocation)
    
                ''' Parse sub-tables '''
                self.parse_aka(item)
                
                # need to set this up, off agency_location this doesn't exist yet but is needed to parse other_address
                self.site_index_id = None
                
                self.parse_other_address(item)
                self.parse_cross_street(item)
                self.parse_phone(item)
                self.parse_url(item)
                self.parse_email(item)      
                self.parse_contact(item)
                self.parse_time_open(item)
                self.parse_languages(item)
                
                self.parse_site_service(item, 'airs')
                self.parse_spatial_location(item)
                
                # reset the contacts index (used inside agency location but should not flow back up to Agency)
                self.contact_index_id = None
                
                
        
    def parse_aka(self, element):
        ''' Element paths '''
        xpAka = 'airs:AKA'
        xpName = 'airs:Name'
        xpConfidential = 'airs:Confidential'
        xpDescription = 'airs:Description'

        itemElements = element.xpath(xpAka, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('name', item.xpath(xpName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('confidential', item.xpath(xpConfidential, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                except: pass
                # SBB20100914 new...
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Aka)
    
                ''' Parse sub-tables '''
                            

    def parse_seasonal(self, element):
        ''' Element paths '''
        xpSeasonal = 'airs:Seasonal'
        xpDescription = 'airs:Description'
        xpStartDate = 'airs:StartDate'
        xpEndDate = 'airs:EndDate'

        itemElements = element.xpath(xpSeasonal, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('start_date', item.xpath(xpStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('end_date', item.xpath(xpEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Seasonal)
    
                ''' Parse sub-tables '''
                            

    def parse_residency_requirements(self, element):
        ''' Element paths '''
        xpResidencyRequirements = 'airs:ResidencyRequirements'

        itemElements = element.xpath(xpResidencyRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('residency_requirements', item.xpath(xpResidencyRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ResidencyRequirements)
    
                ''' Parse sub-tables '''
                            

    def parse_pit_count_set(self, element):
        ''' Element paths '''
        xpPitCountSet = 'hmis:PITCountSet'
        xpPitCountSetIDNum = 'hmis:PitCountSetID/hmis:IDNum'
        xpPitCountSetIDStr = 'hmis:PitCountSetID/hmis:IDStr'
        xpPitCountSetIDDeleteOccurredDate = 'hmis:PitCountSetID/@hmis:deleteOccurredDate'
        xpPitCountSetIDDeleteEffective = 'hmis:PitCountSetID/@hmis:deleteEffective'
        xpPitCountSetIDDelete = 'hmis:PitCountSetID/@hmis:delete'
        xpHUDWaiverReceived = 'hmis:HUDWaiverReceived'
        xpHUDWaiverDate = 'hmis:HUDWaiverDate'
        xpHUDWaiverEffectivePeriodStartDate = 'hmis:HUDWaiverEffectivePeriod/hmis:StartDate'
        xpHUDWaiverEffectivePeriodEndDate = 'hmis:HUDWaiverEffectivePeriod/hmis:EndDate'
        xpLastPITShelteredCountDate = 'hmis:LastPITShelteredCountDate'
        xpLastPITUnshelteredCountDate = 'hmis:LastPITUnshelteredCountDate'
        
        itemElements = element.xpath(xpPitCountSet, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('pit_count_set_id_id_num', item.xpath(xpPitCountSetIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pit_count_set_id_id_str', item.xpath(xpPitCountSetIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pit_count_set_id_delete_occurred_date', item.xpath(xpPitCountSetIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('pit_count_set_id_delete_effective', item.xpath(xpPitCountSetIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('pit_count_set_id_delete', item.xpath(xpPitCountSetIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('hud_waiver_received', item.xpath(xpHUDWaiverReceived, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hud_waiver_date', item.xpath(xpHUDWaiverDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hud_waiver_effective_period_start_date', item.xpath(xpHUDWaiverEffectivePeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hud_waiver_effective_period_end_date', item.xpath(xpHUDWaiverEffectivePeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('last_pit_sheltered_count_date', item.xpath(xpLastPITShelteredCountDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('last_pit_unsheltered_count_date', item.xpath(xpLastPITUnshelteredCountDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.PitCountSet)
    
                ''' Parse sub-tables '''
                self.parse_pit_counts(item)            

    def parse_pit_counts(self, element):
        ''' Element paths '''
        xpPITCountValue = 'hmis:PITCountValue'
        XpPITCountEffectivePeriodStartDate = 'hmis:PITCountEffectivePeriod/hmis:StartDate'
        XpPITCountEffectivePeriodEndDate = 'hmis:PITCountEffectivePeriod/hmis:EndDate'
        xpPITCountRecordedDate = 'hmis:PITCountRecordedDate'
        xpPITHouseholdType = 'hmis:pITHouseholdType'
        
        itemElements = element.xpath(xpPITCountValue, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('pit_count_value', item.xpath(xpPITCountValue, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pit_count_effective_period_start_date', item.xpath(XpPITCountEffectivePeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pit_count_effective_period_end_date', item.xpath(XpPITCountEffectivePeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pit_count_recorded_date', item.xpath(xpPITCountRecordedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pit_count_household_type', item.xpath(xpPITHouseholdType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('pit_count_set_index_id', self.pit_count_set_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.PitCounts)
    
                ''' Parse sub-tables '''
                            

    def parse_other_requirements(self, element):
        ''' Element paths '''
        xpOtherRequirements = 'airs:OtherRequirements'

        itemElements = element.xpath(xpOtherRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('other_requirements', item.xpath(xpOtherRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.OtherRequirements)
    
                ''' Parse sub-tables '''
                            

    def parse_languages(self, element):
        ''' Element paths '''
        xpLanguages = 'airs:Languages'
        xpName = 'airs:Name'
        xpNotes = 'airs:Notes'

        itemElements = element.xpath(xpLanguages, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                # SBB20100915 Don't use xpath to retreive values, since there are many languages under the languages element.  Need all so using getchildren()
                # These are Lists of values, need to iterate over them to stuff into the DB
                valsName = item.xpath(xpName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
                valsNotes = item.xpath(xpNotes, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
                
                # map over them together
                for name, note in map(None, valsName, valsNotes):

                    self.existence_test_and_add('name', name,'text')
                    # test for missing
                    if not note is None:
                        self.existence_test_and_add('notes', note, 'text')

                    ''' Foreign Keys '''
                    try: self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                    except: pass
                    try: self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                    except: pass
                    try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                    except: pass
                    
                    ''' Shred to database '''
                    self.shred(self.parse_dict, dbobjects.Languages)
        
                    ''' Parse sub-tables '''
                    self.parse_time_open(item)            

    def parse_time_open(self, element):
        ''' Unique method that has 2nd loop for each day of week '''

        ''' Element paths '''
        xpTimeOpen = 'airs:TimeOpen'
        xpNotes = 'airs:Notes'
        
        itemElements = element.xpath(xpTimeOpen, namespaces={'airs': self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}

                self.existence_test_and_add('notes', item.xpath(xpNotes, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('languages_index_id', self.languages_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.TimeOpen)

                ''' parse each specific day of week '''
                weekDays = ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday')
                for day in weekDays:
                    self.parse_time_open_day(item, day)

    def parse_time_open_day(self, element, day):
        ''' Unique method -- Loop each day of the week '''

        ''' Element Paths '''
        xpFrom = 'airs:From'
        xpTo = 'airs:To'
        xpDay = 'airs:%s' % (day)
        
        itemElements = element.xpath(xpDay, namespaces={'airs': self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}

                ''' Map elements to database columns '''
                self.existence_test_and_add('from', item.xpath(xpFrom, namespaces={'airs': self.airs_namespace}), 'text')
                self.existence_test_and_add('to', item.xpath(xpTo, namespaces={'airs': self.airs_namespace}), 'text')
                self.existence_test_and_add('day_of_week', day, 'no_handling')

                ''' Foreign Keys '''
                self.existence_test_and_add('time_open_index_id', self.time_open_index_id, 'no_handling')

                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.TimeOpenDays)

    def parse_inventory(self, element):
        ''' Element paths '''
        xpInventory = 'hmis:Inventory'
        xpInventoryDeleteOccurredDate = '@hmis:deleteOccurredDate'
        xpInventoryDeleteEffective = '@hmis:deleteEffective'
        xpInventoryDelete = '@hmis:delete'
        xpHMISParticipationPeriodStartDate = 'hmis:HMISParticipationPeriod/hmis:StartDate'
        xpHMISParticipationPeriodEndDate = 'hmis:HMISParticipationPeriod/hmis:EndDate'
        xpInventoryIDIDNum = 'hmis:InventoryID/hmis:IDNum'
        xpInventoryIDIDStr = 'hmis:InventoryID/hmis:IDStr'
        xpBedInventory = 'hmis:BedInventory'
        xpBedAvailability = '@hmis:BedAvailability'
        xpBedType = '@hmis:BedType'
        xpBedIndividualFamilyType = '@hmis:BedIndividualFamilyType'
        xpChronicHomelessBed = '@hmis:ChronicHomelessBed'
        xpDomesticViolenceShelterBed = '@hmis:DomesticViolenceShelterBed'
        xpHouseholdType = '@hmis:HouseholdType'
        xpHMISParticipatingBeds = 'hmis:HMISParticipatingBeds'
        xpInventoryEffectivePeriodStartDate = 'hmis:InventoryEffectivePeriod/hmis:StartDate'
        xpInventoryEffectivePeriodEndDate = 'hmis:InventoryEffectivePeriod/hmis:EndDate'
        xpInventoryRecordedDate = 'hmis:InventoryRecordedDate'
        xpUnitInventory = 'hmis:UnitInventory'

        itemElements = element.xpath(xpInventory, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('attr_delete_occurred_date', item.xpath(xpInventoryDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_effective', item.xpath(xpInventoryDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('attr_delete', item.xpath(xpInventoryDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hmis_participation_period_start_date', item.xpath(xpHMISParticipationPeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hmis_participation_period_end_date', item.xpath(xpHMISParticipationPeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('inventory_id_id_num', item.xpath(xpInventoryIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('inventory_id_id_str', item.xpath(xpInventoryIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('bed_inventory', item.xpath(xpBedInventory, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('bed_availability', item.xpath(xpBedAvailability, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('bed_type', item.xpath(xpBedType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('bed_individual_family_type', item.xpath(xpBedIndividualFamilyType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('chronic_homeless_bed', item.xpath(xpChronicHomelessBed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('domestic_violence_shelter_bed', item.xpath(xpDomesticViolenceShelterBed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('household_type', item.xpath(xpHouseholdType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hmis_participating_beds', item.xpath(xpHMISParticipatingBeds, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('inventory_effective_period_start_date', item.xpath(xpInventoryEffectivePeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('inventory_effective_period_end_date', item.xpath(xpInventoryEffectivePeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('inventory_recorded_date', item.xpath(xpInventoryRecordedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('unit_inventory', item.xpath(xpUnitInventory, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('service_index_id', self.service_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Inventory)
    
                ''' Parse sub-tables '''
                            

    def parse_income_requirements(self, element):
        ''' Element paths '''
        xpIncomeRequirements = 'airs:IncomeRequirements'

        itemElements = element.xpath(xpIncomeRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('income_requirements', item.xpath(xpIncomeRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.IncomeRequirements)
    
                ''' Parse sub-tables '''
                            

    def parse_hmis_asset(self, element):
        ''' Element paths '''
        xpHMISAsset = 'hmis:HMISAsset'
        xpAssetIDIDNum = 'hmis:AssetID/hmis:IDNum'
        xpAssetIDIDStr = 'hmis:AssetID/hmis:IDStr'
        xpAssetIDDelete = 'hmis:AssetID/@hmis:delete'
        xpAssetIDDeleteOccurredDate = 'hmis:AssetID/@hmis:deleteOccurredDate'
        xpAssetIDDeleteEffective = 'hmis:AssetID/@hmis:deleteEffective'
        xpAssetCount = 'hmis:AssetCount'
        xpAssetCountBedAvailability = 'hmis:AssetCount/@hmis:bedAvailability'
        xpAssetCountBedType = 'hmis:AssetCount/@hmis:bedType'
        xpAssetCountBedIndividualFamilyType = 'hmis:AssetCount/@hmis:bedIndividualFamilyType'
        xpAssetCountChronicHomelessBed = 'hmis:AssetCount/@hmis:chronicHomelessBed'
        xpAssetCountDomesticViolenceShelterBed = 'hmis:AssetCount/@hmis:domesticViolenceShelterBed'
        xpAssetCountHouseholdType = 'hmis:AssetCount/@hmis:householdType'
        xpAssetType = 'hmis:AssetType'
        xpAssetEffectivePeriodStartDate = 'hmis:AssetEffectivePeriod/hmis:StartDate'
        xpAssetEffectivePeriodEndDate = 'hmis:AssetEffectivePeriod/hmis:EndDate'
        xpAssetRecordedDate = 'hmis:RecordedDate'

        itemElements = element.xpath(xpHMISAsset, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('asset_id_id_num', item.xpath(xpAssetIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_id_id_str', item.xpath(xpAssetIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_id_delete', item.xpath(xpAssetIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('asset_id_delete_occurred_date', item.xpath(xpAssetIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('asset_id_delete_effective', item.xpath(xpAssetIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('asset_count', item.xpath(xpAssetCount, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_count_bed_availability', item.xpath(xpAssetCountBedAvailability, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_count_bed_type', item.xpath(xpAssetCountBedType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_count_bed_individual_family_type', item.xpath(xpAssetCountBedIndividualFamilyType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_count_chronic_homeless_bed', item.xpath(xpAssetCountChronicHomelessBed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_count_domestic_violence_shelter_bed', item.xpath(xpAssetCountDomesticViolenceShelterBed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_count_household_type', item.xpath(xpAssetCountHouseholdType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_type', item.xpath(xpAssetType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_effective_period_start_date', item.xpath(xpAssetEffectivePeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_effective_period_end_date', item.xpath(xpAssetEffectivePeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('asset_recorded_date', item.xpath(xpAssetRecordedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.HmisAsset)
    
                ''' Parse sub-tables '''
                self.parse_assignment(item)            

    def parse_assignment(self, element):
        ''' Element paths '''
        xpAssignment = 'hmis:Assignment'
        xpAssignmentIDIDNum = 'hmis:AssignmentID/hmis:IDNum'
        xpAssignmentIDIDStr = 'hmis:AssignmentID/hmis:IDStr'
        xpAssignmentIDDelete = 'hmis:AssignmentID/@hmis:delete'
        xpAssignmentIDDeleteOccurredDate = 'hmis:AssignmentID/@hmis:deleteOccurredDate'
        xpAssignmentIDDeleteEffective = 'hmis:AssignmentID/@hmis:deleteEffective'
        xpPersonIDIDNum = 'hmis:PersonID/hmis:IDNum'
        xpPersonIDIDStr = 'hmis:PersonID/hmis:IDStr'
        xpHouseholdIDIDNum = 'hmis:HouseholdID/hmis:IDNum'
        xpHouseholdIDIDStr = 'hmis:HouseholdID/hmis:IDStr'

        itemElements = element.xpath(xpAssignment, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('assignment_id_id_num', item.xpath(xpAssignmentIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('assignment_id_id_str', item.xpath(xpAssignmentIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('assignment_id_delete', item.xpath(xpAssignmentIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('assignment_id_delete_occurred_date', item.xpath(xpAssignmentIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('assignment_id_delete_effective', item.xpath(xpAssignmentIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_id_id_num', item.xpath(xpPersonIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_id_id_str', item.xpath(xpPersonIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('household_id_id_num', item.xpath(xpHouseholdIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('household_id_id_str', item.xpath(xpHouseholdIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('hmis_asset_index_id', self.hmis_asset_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Assignment)
    
                ''' Parse sub-tables '''
                self.parse_assignment_period(item)            

    def parse_assignment_period(self, element):
        ''' Element paths '''
        xpAssignmentPeriod = 'hmis:AssignmentPeriod'
        xpAssignmentPeriodStartDate = 'hmis:StartDate'
        xpAssignmentPeriodEndDate = 'hmis:EndDate'
        
        itemElements = element.xpath(xpAssignmentPeriod, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('assignment_period_start_date', item.xpath(xpAssignmentPeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('assignment_period_end_date', item.xpath(xpAssignmentPeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('assignment_index_id', self.assignment_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.AssignmentPeriod)
    
                ''' Parse sub-tables '''
                            

    def parse_geographic_area_served(self, element):
        ''' Element paths '''
        xpGeographicAreaServed = 'airs:GeographicAreaServed'
        xpZipCode = 'airs:ZipCode'
        xpCensusTrack = 'airs:CensusTrack'
        xpCity = 'airs:City'
        xpCounty = 'airs:County'
        xpState = 'airs:State'
        xpCountry = 'airs:Country'
        xpDescription = 'airs:Description'

        itemElements = element.xpath(xpGeographicAreaServed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('zipcode', item.xpath(xpZipCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('census_track', item.xpath(xpCensusTrack, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('city', item.xpath(xpCity, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('county', item.xpath(xpCounty, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('state', item.xpath(xpState, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('country', item.xpath(xpCountry, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.GeographicAreaServed)
    
                ''' Parse sub-tables '''
                            

    def parse_documents_required(self, element):
        ''' Element paths '''
        xpDocumentsRequired = 'airs:DocumentsRequired'
        xpDescription = 'airs:Description'

        itemElements = element.xpath(xpDocumentsRequired, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('documents_required', item.xpath(xpDocumentsRequired, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.DocumentsRequired)
    
                ''' Parse sub-tables '''
                            

    def parse_aid_requirements(self, element):
        ''' Element paths '''
        xpAidRequirements = 'airs:AidRequirements'

        itemElements = element.xpath(xpAidRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('aid_requirements', item.xpath(xpAidRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.AidRequirements)
    
                ''' Parse sub-tables '''
                            

    def parse_age_requirements(self, element):
        ''' Element paths '''
        xpAgeRequirements = 'airs:AgeRequirements'
        xpGender = '@airs:Gender'
        xpMinimumAge = '@airs:MinimumAge'
        xpMaximumAge = '@airs:MaximumAge'

        itemElements = element.xpath(xpAgeRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('gender', item.xpath(xpGender, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('minimum_age', item.xpath(xpMinimumAge, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('maximum_age', item.xpath(xpMaximumAge, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.AgeRequirements)
    
                ''' Parse sub-tables '''
                            

    def parse_site_service_participation(self, element):
        ''' Element paths '''
        xpSiteServiceParticipation = 'hmis:SiteServiceParticipation'
        xpSiteServiceParticipationIDIDNum = 'hmis:SiteServiceParticipationID/hmis:IDNum'
        xpSiteServiceParticipationIDIDStr = 'hmis:SiteServiceParticipationID/hmis:IDStr'
        xpSiteServiceParticipationIDDeleteOccurredDate = 'hmis:SiteServiceParticipationID/@hmis:deleteOccurredDate'
        xpSiteServiceParticipationIDDeleteEffective = 'hmis:SiteServiceParticipationID/@hmis:deleteEffective'
        xpSiteServiceParticipationIDDelete = 'hmis:SiteServiceParticipationID/@hmis:delete'            
        xpSiteServiceID = 'hmis:SiteServiceID'
        xpHouseholdIDIDNum = 'hmis:HouseholdID/hmis:IDNum'
        xpHouseholdIDIDStr = 'hmis:HouseholdID/hmis:IDStr'
        xpStartDate = 'hmis:ParticipationDates/hmis:StartDate'
        xpEndDate = 'hmis:ParticipationDates/hmis:EndDate'

        itemElements = element.xpath(xpSiteServiceParticipation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('site_service_participation_idid_num', item.xpath(    xpSiteServiceParticipationIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_service_participation_idid_str', item.xpath(xpSiteServiceParticipationIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_service_participation_id_delete_occurred_date_2010', item.xpath(xpSiteServiceParticipationIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('site_service_participation_id_delete_effective_2010', item.xpath(xpSiteServiceParticipationIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('site_service_participation_id_delete_2010', item.xpath(xpSiteServiceParticipationIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')           
                self.existence_test_and_add('site_service_idid_num', item.xpath(xpSiteServiceID, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('household_idid_num', item.xpath(xpHouseholdIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('household_idid_str', item.xpath(xpHouseholdIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('participation_dates_start_date', item.xpath(xpStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')
                self.existence_test_and_add('participation_dates_end_date', item.xpath(xpEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.SiteServiceParticipation)
    
                ''' Parse sub-tables '''
                self.parse_reasons_for_leaving(item)  
                self.parse_need(item)          
                self.parse_service_event(item)
                self.parse_person_historical(item)

    def parse_reasons_for_leaving(self, element):
        ''' Element paths '''
        xpReasonsForLeaving = 'hmis:ReasonsForLeaving'
        xpReasonsForLeavingIDIDNum = 'hmis:ReasonsForLeavingID/hmis:IDNum'
        xpReasonsForLeavingIDIDStr = 'hmis:ReasonsForLeavingID/hmis:IDStr'
        xpReasonsForLeavingIDDelete = 'hmis:ReasonsForLeavingID/@hmis:delete'
        xpReasonsForLeavingIDDeleteOccurredDate = 'hmis:ReasonsForLeavingID/@hmis:deleteOccurredDate'
        xpReasonsForLeavingIDDeleteEffective = 'hmis:ReasonsForLeavingID/@hmis:deleteEffective'
        xpReasonsForLeaving = 'hmis:ReasonsForLeaving'
        xpReasonsForLeavingDateCollected = 'hmis:ReasonsForLeaving/@hmis:dateCollected'
        xpReasonsForLeavingDateEffective = 'hmis:ReasonsForLeaving/@hmis:dateEffective'
        xpReasonsForLeavingDataCollectionStage = 'hmis:ReasonsForLeaving/@hmis:dataCollectionStage'
        xpReasonsForLeavingOther = 'hmis:ReasonsForLeavingOther'
        xpReasonsForLeavingOtherDateCollected = 'hmis:ReasonsForLeavingOther/@hmis:dateCollected'
        xpReasonsForLeavingOtherDateEffective = 'hmis:ReasonsForLeavingOther/@hmis:dateEffective'
        xpReasonsForLeavingOtherDataCollectionStage = 'hmis:ReasonsForLeavingOther/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpReasonsForLeaving, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('reason_for_leaving_id_id_num', item.xpath(xpReasonsForLeavingIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('reason_for_leaving_id_id_str', item.xpath(xpReasonsForLeavingIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('reason_for_leaving_id_delete', item.xpath(xpReasonsForLeavingIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('reason_for_leaving_id_delete_occurred_date', item.xpath(xpReasonsForLeavingIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('reason_for_leaving_id_delete_effective', item.xpath(xpReasonsForLeavingIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('reason_for_leaving', item.xpath(xpReasonsForLeaving, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('reason_for_leaving_date_collected', item.xpath(xpReasonsForLeavingDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('reason_for_leaving_date_effective', item.xpath(xpReasonsForLeavingDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('reason_for_leaving_data_collection_stage', item.xpath(xpReasonsForLeavingDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('reason_for_leaving_other', item.xpath(xpReasonsForLeavingOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('reason_for_leaving_other_date_collected', item.xpath(xpReasonsForLeavingOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('reason_for_leaving_other_date_effective', item.xpath(xpReasonsForLeavingOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('reason_for_leaving_other_data_collection_stage', item.xpath(xpReasonsForLeavingOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ReasonsForLeaving)
    
                ''' Parse sub-tables '''
                            

    def parse_application_process(self, element):
        ''' Element paths '''
        xpApplicationProcess = 'airs:ApplicationProcess'
        xpStep = 'airs:Step'
        xpDescription = 'airs:Description'

        itemElements = element.xpath(xpApplicationProcess, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('step', item.xpath(xpStep, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ApplicationProcess)
    
                ''' Parse sub-tables '''
                            

    def parse_need(self, element):
        ''' Element paths '''
        xpNeed = 'hmis:Need'
        xpNeedIDIDNum = 'hmis:NeedID/hmis:IDNum'
        xpNeedIDIDStr = 'hmis:NeedID/hmis:IDStr'
        xpNeedIDDeleteOccurredDate = 'hmis:NeedID/@hmis:deleteOccurredDate'
        xpNeedIDDeleteEffective = 'hmis:NeedID/@hmis:deleteEffective'
        xpNeedIDDelete = 'hmis:NeedID/@hmis:delete'
        xpSiteServiceID = 'hmis:SiteServiceID'
        xpNeedEffectivePeriodStartDate = 'hmis:NeedEffectivePeriod/hmis:StartDate'
        xpNeedEffectivePeriodEndDate = 'hmis:NeedEffectivePeriod/hmis:EndDate'
        xpNeedRecordedDate = 'hmis:NeedRecordedDate'
        xpNeedStatus = 'hmis:NeedStatus'

        itemElements = element.xpath(xpNeed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('need_idid_num', item.xpath(xpNeedIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('need_idid_str', item.xpath(xpNeedIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('need_id_delete_occurred_date_2010', item.xpath(xpNeedIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('need_id_delete_delete_effective_2010', item.xpath(xpNeedIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('need_id_delete_2010', item.xpath(xpNeedIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('site_service_idid_num', item.xpath(xpSiteServiceID, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('need_effective_period_start_date_2010', item.xpath(xpNeedEffectivePeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')
                self.existence_test_and_add('need_effective_period_end_date_2010', item.xpath(xpNeedEffectivePeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')
                self.existence_test_and_add('need_recorded_date_2010', item.xpath(xpNeedRecordedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'element_date')
                self.existence_test_and_add('need_status', item.xpath(xpNeedStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Need)
    
                ''' Parse sub-tables '''
                self.parse_taxonomy(item)
                self.parse_service_event(item)

    def parse_taxonomy(self, element):
        ''' Element paths '''
        xpTaxonomy = 'airs:Taxonomy'
        xpCode = 'airs:Code'

        itemElements = element.xpath(xpTaxonomy, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                # SBB20100916 Again, this returns  a list of items which must be processed into the DB as rows
                #self.existence_test_and_add('code', item.xpath(xpCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                
                # These are Lists of values, need to iterate over them to stuff into the DB
                valsName = item.xpath(xpCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
                
                # map over them together
                for code in valsName:
                    self.existence_test_and_add('code', code, 'text')

                    ''' Foreign Keys '''
                    try: self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                    except: pass
                    try: self.existence_test_and_add('need_index_id', self.need_index_id, 'no_handling')
                    except: pass
                
                    ''' Shred to database '''
                    self.shred(self.parse_dict, dbobjects.Taxonomy)
    
                    ''' Parse sub-tables '''
                            

    def parse_service_event(self, element):
        ''' Element paths '''
        xpServiceEvent = 'hmis:ServiceEvent'
        xpServiceEventIDIDNum = 'hmis:ServiceEventID/hmis:IDNum'
        xpServiceEventIDIDStr = 'hmis:ServiceEventID/hmis:IDStr'
        xpServiceEventIDDeleteOccurredDate = 'hmis:ServiceEventID/@hmis:deleteOccurredDate'
        xpServiceEventIDDeleteEffective = 'hmis:ServiceEventID/@hmis:deleteEffective'
        xpServiceEventIDDelete = 'hmis:ServiceEventID/@hmis:delete'        
        xpSiteServiceID = 'hmis:SiteServiceID'
        xpHouseholdIDIDNum = 'hmis:HouseholdID/hmis:IDNum'
        xpHouseholdIDIDStr = 'hmis:HouseholdID/hmis:IDStr'
        xpIsReferral = 'hmis:IsReferral'
        xpQuantityOfServiceEvent = 'hmis:QuantityOfServiceEvent'
        xpQuantityOfServiceEventUnit = 'hmis:QuantityOfServiceEventUnit'
        xpServiceEventAIRSCode = 'hmis:ServiceEventAIRSCode'
        xpServiceEventEffectivePeriodStartDate = 'hmis:ServiceEventEffectivePeriod/hmis:StartDate'
        xpServiceEventEffectivePeriodEndDate = 'hmis:ServiceEventEffectivePeriod/hmis:EndDate'
        xpServiceEventProvisionDate = 'hmis:ServiceEventProvisionDate'
        xpServiceEventRecordedDate = 'hmis:ServiceEventRecordedDate'
        xpServiceEventIndFam = 'hmis:ServiceEventIndFam'
        xpHMISServiceEventCodeTypeOfService = 'hmis:HMISServiceEventCode/hmis:TypeOfService'
        xpHMISServiceEventCodeTypeOfServiceOther = 'hmis:HMISServiceEventCode/hmis:TypeOfServiceOther'
        xpHPRPFinancialAssistanceServiceEventCode = 'hmis:HPRPFinancialAssistanceService'
        xpHPRPRelocationStabilizationServiceEventCode = 'hmis:HPRPRelocationStabilizationServiceEventCode'
        
        itemElements = element.xpath(xpServiceEvent, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('service_event_idid_num', item.xpath(xpServiceEventIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_event_idid_str', item.xpath(xpServiceEventIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_event_id_delete_occurred_date_2010', item.xpath(xpServiceEventIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('service_event_id_delete_effective_2010', item.xpath(xpServiceEventIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('service_event_id_delete_2010', item.xpath(xpServiceEventIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')      
                self.existence_test_and_add('site_service_id_2010', item.xpath(xpSiteServiceID, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('household_idid_num', item.xpath(xpHouseholdIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('household_idid_str', item.xpath(xpHouseholdIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('is_referral', item.xpath(xpIsReferral, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('quantity_of_service', item.xpath(xpQuantityOfServiceEvent, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('quantity_of_service_measure', item.xpath(xpQuantityOfServiceEventUnit, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_airs_code', item.xpath(xpServiceEventAIRSCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_period_start_date', item.xpath(xpServiceEventEffectivePeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_period_end_date', item.xpath(xpServiceEventEffectivePeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_event_provision_date_2010', item.xpath(xpServiceEventProvisionDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_event_recorded_date_2010', item.xpath(xpServiceEventRecordedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_event_ind_fam_2010', item.xpath(xpServiceEventIndFam, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hmis_service_event_code_type_of_service_2010', item.xpath(xpHMISServiceEventCodeTypeOfService, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hmis_service_event_code_type_of_service_other_2010', item.xpath(xpHMISServiceEventCodeTypeOfServiceOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hprp_financial_assistance_service_event_code_2010', item.xpath(xpHPRPFinancialAssistanceServiceEventCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hprp_relocation_stabilization_service_event_code_2010', item.xpath(xpHPRPRelocationStabilizationServiceEventCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('need_index_id', self.need_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ServiceEvent)
    
                ''' Parse sub-tables '''
                self.parse_service_event_notes(item)     
                self.parse_funding_source(item)       

    def parse_service_event_notes(self, element):
        ''' Element paths '''
        xpServiceEventNotes = 'hmis:ServiceEventNotes/hmis:note'
        xpNoteIDIDNum = 'hmis:NoteID/hmis:IDNum'
        xpNoteIDIDStr = 'hmis:NoteID/hmis:IDStr'
        xpNoteIDDeleteOccurredDate = 'hmis:NoteID/@hmis:deleteOccurredDate'
        xpNoteIDDeleteEffective = 'hmis:NoteID/@hmis:deleteEffective'
        xpNoteIDDelete = 'hmis:NoteID/@hmis:delete'             
        xpNoteText = 'hmis:NoteText'
        xpNoteTextDateCollected = 'hmis:NoteText/@hmis:dateCollected'
        xpNoteTextDateEffective = 'hmis:NoteText/@hmis:dateEffective'
        xpNoteTextDataCollectionStage = 'hmis:NoteText/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpServiceEventNotes, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('note_id_id_num', item.xpath(xpNoteIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('note_id_id_str', item.xpath(xpNoteIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('note_delete_occurred_date', item.xpath(xpNoteIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('note_delete_effective', item.xpath(xpNoteIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('note_delete', item.xpath(xpNoteIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')          
                self.existence_test_and_add('note_text', item.xpath(xpNoteText, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('note_text_date_collected', item.xpath(xpNoteTextDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('note_text_date_effective', item.xpath(xpNoteTextDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('note_text_data_collection_stage', item.xpath(xpNoteTextDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('service_event_index_id', self.service_event_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ServiceEventNotes)
    
                ''' Parse sub-tables '''
                            

    def parse_family_requirements(self, element):
        ''' Element paths '''
        xpFamilyRequirements = 'airs:FamilyRequirements'

        itemElements = element.xpath(xpFamilyRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('family_requirements', item.xpath(xpFamilyRequirements, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.FamilyRequirements)
    
                ''' Parse sub-tables '''
                            

    def parse_person_historical(self, element):
        ''' Element paths '''
        xpPersonHistorical = 'hmis:PersonHistorical'        
        xpPersonHistoricalIDIDNum = 'hmis:PersonHistoricalID/hmis:IDNum'
        xpPersonHistoricalIDIDStr = 'hmis:PersonHistoricalID/hmis:IDStr'
        xpSiteServiceID = 'hmis:SiteServiceID'

        itemElements = element.xpath(xpPersonHistorical, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('person_historical_idid_num', item.xpath(xpPersonHistoricalIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_historical_idid_str', item.xpath(xpPersonHistoricalIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('site_service_id_2010', item.xpath(xpSiteServiceID, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.PersonHistorical)
    
                ''' Parse sub-tables '''
                self.parse_housing_status(item)   
                self.parse_veteran(item)
                self.parse_vocational_training(item)         
                self.parse_substance_abuse_problem(item)         
                self.parse_pregnancy(item)         
                self.parse_prior_residence(item)         
                self.parse_physical_disability(item)         
                self.parse_non_cash_benefits(item)         
                self.parse_non_cash_benefits_last_30_days(item)         
                self.parse_mental_health_problem(item)         
                self.parse_length_of_stay_at_prior_residence(item)         
                self.parse_income_total_monthly(item)         
                self.parse_hud_chronic_homeless(item)         
                self.parse_income_last_30_days(item)         
                self.parse_highest_school_level(item)         
                self.parse_hiv_aids_status(item)         
                self.parse_health_status(item)         
                self.parse_engaged_date(item)         
                self.parse_employment(item)         
                self.parse_domestic_violence(item)         
                self.parse_disabling_condition(item)         
                self.parse_developmental_disability(item)         
                self.parse_destinations(item)         
                self.parse_degree(item)         
                self.parse_currently_in_school(item)         
                self.parse_contact_made(item)         
                self.parse_child_enrollment_status(item)         
                self.parse_chronic_health_condition(item) 
                self.parse_income_and_sources(item)
                self.parse_hud_homeless_episodes(item)
                self.parse_person_address(item)
                self.parse_email(item)                              
                self.parse_phone(item)      

    def parse_housing_status(self, element):
        ''' Element paths '''
        xpHousingStatus = 'hmis:HousingStatus'
        xpHousingStatusDateCollected = 'hmis:HousingStatus/@hmis:dateCollected'
        xpHousingStatusDateEffective = 'hmis:HousingStatus/@hmis:dateEffective'
        xpHousingStatusDataCollectionStage = 'hmis:HousingStatus/@hmis:dataCollectionStage'        

        itemElements = element.xpath(xpHousingStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('housing_status', item.xpath(xpHousingStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('housing_status_date_collected', item.xpath(xpHousingStatusDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('housing_status_date_effective', item.xpath(xpHousingStatusDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('housing_status_data_collection_stage', item.xpath(xpHousingStatusDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')      

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.HousingStatus)
    
                ''' Parse sub-tables '''

    def parse_veteran(self, element):
        ''' Unique method -- loops all veteran elements and launches sub parsers '''

        ''' Element paths '''
        xpVeteran = 'hmis:Veteran'
        itemElements = element.xpath(xpVeteran, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}

                self.parse_veteran_military_branches(item)
                self.parse_veteran_military_service_duration(item)  
                self.parse_veteran_served_in_war_zone(item)         
                self.parse_veteran_service_era(item)         
                self.parse_veteran_veteran_status(item)         
                self.parse_veteran_warzones_served(item)                         
        
    def parse_veteran_military_branches(self, element):
        ''' Element paths '''
        xpMilitaryBranches = 'hmis:MilitaryBranches'
        xpMilitaryBranchIDIDNum = 'hmis:MilitaryBranchID/hmis:IDNum'
        xpMilitaryBranchIDIDStr = 'hmis:MilitaryBranchID/hmis:IDStr'
        xpMilitaryBranchIDDeleteOccurredDate = 'hmis:MilitaryBranchID/@hmis:deleteOccurredDate'
        xpMilitaryBranchIDDeleteEffective = 'hmis:MilitaryBranchID/@hmis:deleteEffective'
        xpMilitaryBranchIDDelete = 'hmis:MilitaryBranchID/@hmis:delete'
        xpDischargeStatus = 'hmis:DischargeStatus'
        xpDischargeStatusDateCollected = 'hmis:DischargeStatus/@hmis:dateCollected'
        xpDischargeStatusDateEffective = 'hmis:DischargeStatus/@hmis:dateEffective'
        xpDischargeStatusDataCollectionStage = 'hmis:DischargeStatus/@hmis:dataCollectionStage'
        xpDischargeStatusOther = 'hmis:DischargeStatusOther'
        xpDischargeStatusOtherDateCollected = 'hmis:DischargeStatusOther/@hmis:dateCollected'
        xpDischargeStatusOtherDateEffective = 'hmis:DischargeStatusOther/@hmis:dateEffective'
        xpDischargeStatusOtherDataCollectionStage = 'hmis:DischargeStatusOther/@hmis:dataCollectionStage'
        xpMilitaryBranch = 'hmis:MilitaryBranch'
        xpMilitaryBranchDateCollected = 'hmis:MilitaryBranch/@hmis:dateCollected'
        xpMilitaryBranchDateEffective = 'hmis:MilitaryBranch/@hmis:dateEffective'
        xpMilitaryBranchDataCollectionStage = 'hmis:MilitaryBranch/@hmis:dataCollectionStage'
        xpMilitaryBranchOther = 'hmis:MilitaryBranch'
        xpMilitaryBranchOtherDateCollected = 'hmis:MilitaryBranchOther/@hmis:dateCollected'
        xpMilitaryBranchOtherDateEffective = 'hmis:MilitaryBranchOther/@hmis:dateEffective'
        xpMilitaryBranchOtherDataCollectionStage = 'hmis:MilitaryBranchOther/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpMilitaryBranches, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('military_branch_id_id_id_num', item.xpath(xpMilitaryBranchIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('military_branch_id_id_id_str', item.xpath(xpMilitaryBranchIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('military_branch_id_id_delete_occurred_date', item.xpath(xpMilitaryBranchIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('military_branch_id_id_delete_effective', item.xpath(xpMilitaryBranchIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('military_branch_id_id_delete', item.xpath(xpMilitaryBranchIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('discharge_status', item.xpath(xpDischargeStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('discharge_status_date_collected', item.xpath(xpDischargeStatusDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('discharge_status_date_effective', item.xpath(xpDischargeStatusDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('discharge_status_data_collection_stage', item.xpath(xpDischargeStatusDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('discharge_status_other', item.xpath(xpDischargeStatusOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('discharge_status_other_date_collected', item.xpath(xpDischargeStatusOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('discharge_status_other_date_effective', item.xpath(xpDischargeStatusOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('discharge_status_other_data_collection_stage', item.xpath(xpDischargeStatusOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('military_branch', item.xpath(xpMilitaryBranch, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('military_branch_date_collected', item.xpath(xpMilitaryBranchDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('military_branch_date_effective', item.xpath(xpMilitaryBranchDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('military_branch_data_collection_stage', item.xpath(xpMilitaryBranchDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('military_branch_other', item.xpath(xpMilitaryBranchOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('military_branch_other_date_collected', item.xpath(xpMilitaryBranchOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('military_branch_other_date_effective', item.xpath(xpMilitaryBranchOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('military_branch_other_data_collection_stage', item.xpath(xpMilitaryBranchOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.VeteranMilitaryBranches)
    
                ''' Parse sub-tables '''
                            

    def parse_veteran_military_service_duration(self, element):
        ''' Element paths '''
        xpMilitaryServiceDuration = 'hmis:MilitaryServiceDuration'
        xpMilitaryServiceDurationDateCollected = 'hmis:MilitaryServiceDuration/@hmis:dateCollected'
        xpMilitaryServiceDurationDateEffective = 'hmis:MilitaryServiceDuration/@hmis:dateEffective'
        xpMilitaryServiceDurationDataCollectionStage = 'hmis:MilitaryServiceDuration/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpMilitaryServiceDuration, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('military_service_duration', item.xpath(xpMilitaryServiceDuration, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('military_service_duration_date_collected', item.xpath(xpMilitaryServiceDurationDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('military_service_duration_date_effective', item.xpath(xpMilitaryServiceDurationDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('military_service_duration_data_collection_stage', item.xpath(xpMilitaryServiceDurationDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.VeteranMilitaryServiceDuration)
    
                ''' Parse sub-tables '''
                            

    def parse_veteran_served_in_war_zone(self, element):
        ''' Element paths '''
        xpVeteranServedInWarZone = 'hmis:MilitaryServiceDuration'
        xpVeteranServedInWarZoneDurationDateCollected = 'hmis:VeteranServedInWarZone/@hmis:dateCollected'
        xpVeteranServedInWarZoneDurationDateEffective = 'hmis:VeteranServedInWarZone/@hmis:dateEffective'
        xpVeteranServedInWarZoneDurationDataCollectionStage = 'hmis:VeteranServedInWarZone/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpVeteranServedInWarZone, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('served_in_war_zone', item.xpath(xpVeteranServedInWarZone, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('served_in_war_zone_date_collected', item.xpath(xpVeteranServedInWarZoneDurationDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('served_in_war_zone_date_effective', item.xpath(xpVeteranServedInWarZoneDurationDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('served_in_war_zone_data_collection_stage', item.xpath(xpVeteranServedInWarZoneDurationDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.VeteranServedInWarZone)
    
                ''' Parse sub-tables '''
                            

    def parse_veteran_service_era(self, element):
        ''' Element paths '''
        xpServiceEra = 'hmis:ServiceEra'
        xpServiceEraDurationDateCollected = 'hmis:ServiceEra/@hmis:dateCollected'
        xpServiceEraDurationDateEffective = 'hmis:ServiceEra/@hmis:dateEffective'
        xpServiceEraDurationDataCollectionStage = 'hmis:ServiceEra/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpServiceEra, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('service_era', item.xpath(xpServiceEra, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('service_era_date_collected', item.xpath(xpServiceEraDurationDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('service_era_date_effective', item.xpath(xpServiceEraDurationDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('service_era_data_collection_stage', item.xpath(xpServiceEraDurationDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.VeteranServiceEra)
    
                ''' Parse sub-tables '''
                            

    def parse_veteran_veteran_status(self, element):
        ''' Element paths '''
        xpVeteranStatus = 'hmis:VeteranStatus'
        xpVeteranStatusDurationDateCollected = 'hmis:VeteranStatus/@hmis:dateCollected'
        xpVeteranStatusDurationDateEffective = 'hmis:VeteranStatus/@hmis:dateEffective'
        xpVeteranStatusDurationDataCollectionStage = 'hmis:VeteranStatus/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpVeteranStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('veteran_status', item.xpath(xpVeteranStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('veteran_status_date_collected', item.xpath(xpVeteranStatusDurationDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('veteran_status_date_effective', item.xpath(xpVeteranStatusDurationDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('veteran_status_data_collection_stage', item.xpath(xpVeteranStatusDurationDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.VeteranVeteranStatus)
    
                ''' Parse sub-tables '''
                            

    def parse_veteran_warzones_served(self, element):
        ''' Element paths '''
        xpVeteranWarZonesServed = 'hmis:WarZonesServed'
        xpWarZoneIDIDNum = 'hmis:WarZoneID/hmis:IDNum'
        xpWarZoneIDIDStr = 'hmis:WarZoneID/hmis:IDStr'
        xpWarZoneIDDeleteOccurredDate = 'hmis:MilitaryBranchID/@hmis:deleteOccurredDate'
        xpWarZoneIDDeleteEffective = 'hmis:MilitaryBranchID/@hmis:deleteEffective'
        xpWarZoneIDDelete = 'hmis:MilitaryBranchID/@hmis:delete'
        xpMonthsInWarZone = 'hmis:MonthsInWarZone'
        xpMonthsInWarZoneDateCollected = 'hmis:MonthsInWarZone/@hmis:dateCollected'
        xpMonthsInWarZoneDateEffective = 'hmis:MonthsInWarZone/@hmis:dateEffective'
        xpMonthsInWarZoneDataCollectionStage = 'hmis:MonthsInWarZone/@hmis:dataCollectionStage'
        xpReceivedFire = 'hmis:ReceivedFire'
        xpReceivedFireDateCollected = 'hmis:ReceivedFire/@hmis:dateCollected'
        xpReceivedFireDateEffective = 'hmis:ReceivedFire/@hmis:dateEffective'
        xpReceivedFireDataCollectionStage = 'hmis:ReceivedFire/@hmis:dataCollectionStage'
        xpWarZone = 'hmis:WarZone'
        xpWarZoneDateCollected = 'hmis:WarZone/@hmis:dateCollected'
        xpWarZoneDateEffective = 'hmis:WarZone/@hmis:dateEffective'
        xpWarZoneDataCollectionStage = 'hmis:WarZone/@hmis:dataCollectionStage'
        xpWarZoneOther = 'hmis:WarZoneOther'
        xpWarZoneOtherDateCollected = 'hmis:WarZoneOther/@hmis:dateCollected'
        xpWarZoneOtherDateEffective = 'hmis:WarZoneOther/@hmis:dateEffective'
        xpWarZoneOtherDataCollectionStage = 'hmis:WarZoneOther/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpVeteranWarZonesServed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('war_zone_id_id_id_num', item.xpath(xpWarZoneIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('war_zone_id_id_id_str', item.xpath(xpWarZoneIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('war_zone_id_id_delete_occurred_date', item.xpath(xpWarZoneIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('war_zone_id_id_delete_effective', item.xpath(xpWarZoneIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('war_zone_id_id_delete', item.xpath(xpWarZoneIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('months_in_war_zone', item.xpath(xpMonthsInWarZone, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('months_in_war_zone_date_collected', item.xpath(xpMonthsInWarZoneDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('months_in_war_zone_date_effective', item.xpath(xpMonthsInWarZoneDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('months_in_war_zone_data_collection_stage', item.xpath(xpMonthsInWarZoneDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('received_fire', item.xpath(xpReceivedFire, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('received_fire_date_collected', item.xpath(xpReceivedFireDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('received_fire_date_effective', item.xpath(xpReceivedFireDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('received_fire_data_collection_stage', item.xpath(xpReceivedFireDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('war_zone', item.xpath(xpWarZone, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('war_zone_date_collected', item.xpath(xpWarZoneDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('war_zone_date_effective', item.xpath(xpWarZoneDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('war_zone_data_collection_stage', item.xpath(xpWarZoneDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('war_zone_other', item.xpath(xpWarZoneOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('war_zone_other_date_collected', item.xpath(xpWarZoneOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('war_zone_other_date_effective', item.xpath(xpWarZoneOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('war_zone_other_data_collection_stage', item.xpath(xpWarZoneOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.VeteranWarzonesServed)
    
                ''' Parse sub-tables '''
                            

    def parse_vocational_training(self, element):
        ''' Element paths '''
        xpVocationalTraining = 'hmis:VocationalTraining'
        xpVocationalTrainingDateCollected = 'hmis:VocationalTraining/@hmis:dateCollected'
        xpVocationalTrainingDateEffective = 'hmis:VocationalTraining/@hmis:dateEffective'
        xpVocationalTrainingDataCollectionStage = 'hmis:VocationalTraining/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpVocationalTraining, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('vocational_training', item.xpath(xpVocationalTraining, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('vocational_training_date_collected', item.xpath(xpVocationalTrainingDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('vocational_training_date_effective', item.xpath(xpVocationalTrainingDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('vocational_training_data_collection_stage', item.xpath(xpVocationalTrainingDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.VocationalTraining)
    
                ''' Parse sub-tables '''
                            

    def parse_substance_abuse_problem(self, element):
        ''' Element paths '''
        xpSubstanceAbuseProblem = 'hmis:SubstanceAbuseProblem'
        xpHasSubstanceAbuseProblem = 'hmis:HasSubstanceAbuseProblem'
        xpHasSubstanceAbuseProblemDateCollected = 'hmis:HasSubstanceAbuseProblem/@hmis:dateCollected'
        xpHasSubstanceAbuseProblemDateEffective = 'hmis:HasSubstanceAbuseProblem/@hmis:dateEffective'
        xpHasSubstanceAbuseProblemDataCollectionStage = 'hmis:HasSubstanceAbuseProblem/@hmis:dataCollectionStage'
        xpSubstanceAbuseIndefinite = 'hmis:SubstanceAbuseIndefinite'
        xpSubstanceAbuseIndefiniteDateCollected = 'hmis:SubstanceAbuseIndefinite/@hmis:dateCollected'
        xpSubstanceAbuseIndefiniteDateEffective = 'hmis:SubstanceAbuseIndefinite/@hmis:dateEffective'
        xpSubstanceAbuseIndefiniteDataCollectionStage = 'hmis:SubstanceAbuseIndefinite/@hmis:dataCollectionStage'
        xpReceiveSubstanceAbuseServices = 'hmis:ReceiveSubstanceAbuseServices'
        xpReceiveSubstanceAbuseServicesDateCollected = 'hmis:ReceiveSubstanceAbuseServices/@hmis:dateCollected'
        xpReceiveSubstanceAbuseServicesDateEffective = 'hmis:ReceiveSubstanceAbuseServices/@hmis:dateEffective'
        xpReceiveSubstanceAbuseServicesDataCollectionStage = 'hmis:ReceiveSubstanceAbuseServices/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpSubstanceAbuseProblem, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('has_substance_abuse_problem', item.xpath(xpHasSubstanceAbuseProblem, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('has_substance_abuse_problem_date_collected', item.xpath(xpHasSubstanceAbuseProblemDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_substance_abuse_problem_date_effective', item.xpath(xpHasSubstanceAbuseProblemDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_substance_abuse_problem_data_collection_stage', item.xpath(xpHasSubstanceAbuseProblemDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('substance_abuse_indefinite', item.xpath(xpSubstanceAbuseIndefinite, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('substance_abuse_indefinite_date_collected', item.xpath(xpSubstanceAbuseIndefiniteDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('substance_abuse_indefinite_date_effective', item.xpath(xpSubstanceAbuseIndefiniteDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('substance_abuse_indefinite_data_collection_stage', item.xpath(xpSubstanceAbuseIndefiniteDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('receive_substance_abuse_services', item.xpath(xpReceiveSubstanceAbuseServices, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receive_substance_abuse_services_date_collected', item.xpath(xpReceiveSubstanceAbuseServicesDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_substance_abuse_services_date_effective', item.xpath(xpReceiveSubstanceAbuseServicesDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_substance_abuse_services_data_collection_stage', item.xpath(xpReceiveSubstanceAbuseServicesDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.SubstanceAbuseProblem)
    
                ''' Parse sub-tables '''
                            

    def parse_pregnancy(self, element):
        ''' Element paths '''
        xpPregnancy = 'hmis:Pregnancy'
        xpPregnancyIDIDNum = 'hmis:PregnancyID/hmis:IDNum'
        xpPregnancyIDIDStr = 'hmis:PregnancyID/hmis:IDStr'
        xpPregnancyIDDeleteOccurredDate = 'hmis:PregnancyID/@hmis:deleteOccurredDate'
        xpPregnancyIDDeleteEffective = 'hmis:PregnancyID/@hmis:deleteEffective'
        xpPregnancyIDDelete = 'hmis:PregnancyID/@hmis:delete'
        xpPregnancyStatus = 'hmis:PregnancyStatus'
        xpPregnancyStatusDateCollected = 'hmis:PregnancyStatus/@hmis:dateCollected'
        xpPregnancyStatusDateEffective = 'hmis:PregnancyStatus/@hmis:dateEffective'
        xpPregnancyStatusDataCollectionStage = 'hmis:PregnancyStatus/@hmis:dataCollectionStage'
        xpDueDate = 'hmis:DueDate'
        xpDueDateDateCollected = 'hmis:DueDate/@hmis:dateCollected'
        xpDueDateDateEffective = 'hmis:DueDate/@hmis:dateEffective'
        xpDueDateDataCollectionStage = 'hmis:DueDate/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpPregnancy, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('pregnancy_id_id_id_num', item.xpath(xpPregnancyIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pregnancy_id_id_id_str', item.xpath(xpPregnancyIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pregnancy_id_id_delete_occurred_date', item.xpath(xpPregnancyIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('pregnancy_id_id_delete_effective', item.xpath(xpPregnancyIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('pregnancy_id_id_delete', item.xpath(xpPregnancyIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('pregnancy_status', item.xpath(xpPregnancyStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pregnancy_status_date_collected', item.xpath(xpPregnancyStatusDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('pregnancy_status_date_effective', item.xpath(xpPregnancyStatusDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('pregnancy_status_data_collection_stage', item.xpath(xpPregnancyStatusDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('due_date', item.xpath(xpDueDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'date')
                self.existence_test_and_add('due_date_date_collected', item.xpath(xpDueDateDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('due_date_data_collection_stage', item.xpath(xpDueDateDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Pregnancy)
    
                ''' Parse sub-tables '''
                            

    def parse_prior_residence(self, element):
        ''' Element paths '''
        xpPriorResidence = 'hmis:PriorResidence'
        xpPriorResidenceIDIDNum = 'hmis:PriorResidenceID/hmis:IDNum'
        xpPriorResidenceIDIDStr = 'hmis:PriorResidenceID/hmis:IDStr'
        xpPriorResidenceIDDeleteOccurredDate = 'hmis:PriorResidenceID/@hmis:deleteOccurredDate'
        xpPriorResidenceIDDeleteEffective = 'hmis:PriorResidenceID/@hmis:deleteEffective'
        xpPriorResidenceIDDelete = 'hmis:PriorResidenceID/@hmis:delete'
        xpPriorResidenceCode = 'hmis:PriorResidenceCode'
        xpPriorResidenceCodeDateCollected = 'hmis:PriorResidenceCode/@hmis:dateCollected'
        xpPriorResidenceCodeDateEffective = 'hmis:PriorResidenceCode/@hmis:dateEffective'
        xpPriorResidenceCodeDataCollectionStage = 'hmis:PriorResidenceCode/@hmis:dataCollectionStage'
        xpPriorResidenceOther = 'hmis:PriorResidenceOther'
        xpPriorResidenceOtherDateCollected = 'hmis:PriorResidenceOther/@hmis:dateCollected'
        xpPriorResidenceOtherDateEffective = 'hmis:PriorResidenceOther/@hmis:dateEffective'
        xpPriorResidenceOtherDataCollectionStage = 'hmis:PriorResidenceOther/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpPriorResidence, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('prior_residence_id_id_id_num', item.xpath(xpPriorResidenceIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('prior_residence_id_id_id_str', item.xpath(xpPriorResidenceIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('prior_residence_id_id_delete_occurred_date', item.xpath(xpPriorResidenceIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('prior_residence_id_id_delete_effective', item.xpath(xpPriorResidenceIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('prior_residence_id_id_delete', item.xpath(xpPriorResidenceIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('prior_residence_code', item.xpath(xpPriorResidenceCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('prior_residence_code_date_collected', item.xpath(xpPriorResidenceCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('prior_residence_code_date_effective', item.xpath(xpPriorResidenceCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('prior_residence_code_data_collection_stage', item.xpath(xpPriorResidenceCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('prior_residence_other', item.xpath(xpPriorResidenceOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('prior_residence_other_date_collected', item.xpath(xpPriorResidenceOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('prior_residence_other_date_effective', item.xpath(xpPriorResidenceOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('prior_residence_other_data_collection_stage', item.xpath(xpPriorResidenceOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.PriorResidence)
    
                ''' Parse sub-tables '''
                            

    def parse_physical_disability(self, element):
        ''' Element paths '''
        xpPhysicalDisability = 'hmis:PhysicalDisability'
        xpHasPhysicalDisability = 'hmis:HasPhysicalDisability'
        xpHasPhysicalDisabilityDateCollected = 'hmis:HasPhysicalDisability/@hmis:dateCollected'
        xpHasPhysicalDisabilityDateEffective = 'hmis:HasPhysicalDisability/@hmis:dateEffective'
        xpHasPhysicalDisabilityDataCollectionStage = 'hmis:HasPhysicalDisability/@hmis:dataCollectionStage'
        xpReceivePhysicalDisabilityServices = 'hmis:ReceivePhysicalDisabilityServices'
        xpReceivePhysicalDisabilityServicesDateCollected = 'hmis:ReceivePhysicalDisabilityServices/@hmis:dateCollected'
        xpReceivePhysicalDisabilityServicesDateEffective = 'hmis:ReceivePhysicalDisabilityServices/@hmis:dateEffective'
        xpReceivePhysicalDisabilityServicesDataCollectionStage = 'hmis:ReceivePhysicalDisabilityServices/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpPhysicalDisability, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('has_physical_disability', item.xpath(xpHasPhysicalDisability, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('has_physical_disability_date_collected', item.xpath(xpHasPhysicalDisabilityDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_physical_disability_date_effective', item.xpath(xpHasPhysicalDisabilityDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_physical_disability_data_collection_stage', item.xpath(xpHasPhysicalDisabilityDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('receive_physical_disability_services', item.xpath(xpReceivePhysicalDisabilityServices, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receive_physical_disability_services_date_collected', item.xpath(xpReceivePhysicalDisabilityServicesDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_physical_disability_services_date_effective', item.xpath(xpReceivePhysicalDisabilityServicesDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_physical_disability_services_data_collection_stage', item.xpath(xpReceivePhysicalDisabilityServicesDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.PhysicalDisability)
    
                ''' Parse sub-tables '''
                            

    def parse_non_cash_benefits(self, element):
        ''' Element paths '''
        xpNonCashBenefit = 'hmis:NonCashBenefits/hmis:NonCashBenefit'
        xpNonCashBenefitIDIDNum = 'hmis:NonCashBenefitID/hmis:IDNum'
        xpNonCashBenefitIDIDStr = 'hmis:NonCashBenefitID/hmis:IDStr'
        xpNonCashBenefitIDDeleteOccurredDate = 'hmis:NonCashBenefitID/@hmis:deleteOccurredDate'
        xpNonCashBenefitIDDeleteEffective = 'hmis:NonCashBenefitID/@hmis:deleteEffective'
        xpNonCashBenefitIDDelete = 'hmis:NonCashBenefitID/@hmis:delete'
        xpNonCashSourceCode = 'hmis:NonCashSourceCode'
        xpNonCashSourceCodeDateCollected = 'hmis:NonCashSourceCode/@hmis:dateCollected'
        xpNonCashSourceCodeDateEffective = 'hmis:NonCashSourceCode/@hmis:dateEffective'
        xpNonCashSourceCodeDataCollectionStage = 'hmis:NonCashSourceCode/@hmis:dataCollectionStage'
        xpNonCashSourceOther = 'hmis:NonCashSourceOther'
        xpNonCashSourceOtherDateCollected = 'hmis:NonCashSourceOther/@hmis:dateCollected'
        xpNonCashSourceOtherDateEffective = 'hmis:NonCashSourceOther/@hmis:dateEffective'
        xpNonCashSourceOtherDataCollectionStage = 'hmis:NonCashSourceOther/@hmis:dataCollectionStage'
        xpReceivingNonCashSource = 'hmis:ReceivingNonCashSource'
        xpReceivingNonCashSourceDateCollected = 'hmis:ReceivingNonCashSource/@hmis:dateCollected'
        xpReceivingNonCashSourceDateEffective = 'hmis:ReceivingNonCashSource/@hmis:dateEffective'
        xpReceivingNonCashSourceDataCollectionStage = 'hmis:ReceivingNonCashSource/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpNonCashBenefit, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('non_cash_benefit_id_id_id_num', item.xpath(xpNonCashBenefitIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('non_cash_benefit_id_id_id_str', item.xpath(xpNonCashBenefitIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('non_cash_benefit_id_id_delete_occurred_date', item.xpath(xpNonCashBenefitIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('non_cash_benefit_id_id_delete_effective', item.xpath(xpNonCashBenefitIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('non_cash_benefit_id_id_delete', item.xpath(xpNonCashBenefitIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('non_cash_source_code', item.xpath(xpNonCashSourceCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('non_cash_source_code_date_collected', item.xpath(xpNonCashSourceCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('non_cash_source_code_date_effective', item.xpath(xpNonCashSourceCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('non_cash_source_code_data_collection_stage', item.xpath(xpNonCashSourceCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('non_cash_source_other', item.xpath(xpNonCashSourceOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('non_cash_source_other_date_collected', item.xpath(xpNonCashSourceOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('non_cash_source_other_date_effective', item.xpath(xpNonCashSourceOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('non_cash_source_other_data_collection_stage', item.xpath(xpNonCashSourceOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('receiving_non_cash_source', item.xpath(xpReceivingNonCashSource, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receiving_non_cash_source_date_collected', item.xpath(xpReceivingNonCashSourceDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receiving_non_cash_source_date_effective', item.xpath(xpReceivingNonCashSourceDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receiving_non_cash_source_data_collection_stage', item.xpath(xpReceivingNonCashSourceDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.NonCashBenefits)
    
                ''' Parse sub-tables '''

    def parse_non_cash_benefits_last_30_days(self, element):
        ''' Element paths '''
        xpNonCashBenefitsLast30Days = 'hmis:NonCashBenefitsLast30Days'
        xpNonCashBenefitsLast30DaysDateCollected = 'hmis:NonCashBenefitsLast30Days/@hmis:dateCollected'
        xpNonCashBenefitsLast30DaysDateEffective = 'hmis:NonCashBenefitsLast30Days/@hmis:dateEffective'
        xpNonCashBenefitsLast30DaysDataCollectionStage = 'hmis:NonCashBenefitsLast30Days/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpNonCashBenefitsLast30Days, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('income_last_30_days', item.xpath(xpNonCashBenefitsLast30Days, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('income_last_30_days_date_collected', item.xpath(xpNonCashBenefitsLast30DaysDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_last_30_days_date_effective', item.xpath(xpNonCashBenefitsLast30DaysDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_last_30_days_data_collection_stage', item.xpath(xpNonCashBenefitsLast30DaysDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.NonCashBenefitsLast30Days)
    
                ''' Parse sub-tables '''
                            

    def parse_mental_health_problem(self, element):
        ''' Element paths '''
        xpMentalHealthProblem = 'hmis:MentalHealthProblem'
        xpHasMentalHealthProblem = 'hmis:HasMentalHealthProblem'
        xpHasMentalHealthProblemDateCollected = 'hmis:HasMentalHealthProblem/@hmis:dateCollected'
        xpHasMentalHealthProblemDateEffective = 'hmis:HasMentalHealthProblem/@hmis:dateEffective'
        xpHasMentalHealthProblemDataCollectionStage = 'hmis:HasMentalHealthProblem/@hmis:dataCollectionStage'
        xpMentalHealthIndefinite = 'hmis:MentalHealthIndefinite'
        xpMentalHealthIndefiniteDateCollected = 'hmis:MentalHealthIndefinite/@hmis:dateCollected'
        xpMentalHealthIndefiniteDateEffective = 'hmis:MentalHealthIndefinite/@hmis:dateEffective'
        xpMentalHealthIndefiniteDataCollectionStage = 'hmis:MentalHealthIndefinite/@hmis:dataCollectionStage'
        xpReceiveMentalHealthServices = 'hmis:ReceiveMentalHealthServices'
        xpReceiveMentalHealthServicesDateCollected = 'hmis:ReceiveMentalHealthServices/@hmis:dateCollected'
        xpReceiveMentalHealthServicesDateEffective = 'hmis:ReceiveMentalHealthServices/@hmis:dateEffective'
        xpReceiveMentalHealthServicesDataCollectionStage = 'hmis:ReceiveMentalHealthServices/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpMentalHealthProblem, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('has_mental_health_problem', item.xpath(xpHasMentalHealthProblem, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('has_mental_health_problem_date_collected', item.xpath(xpHasMentalHealthProblemDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_mental_health_problem_date_effective', item.xpath(xpHasMentalHealthProblemDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_mental_health_problem_data_collection_stage', item.xpath(xpHasMentalHealthProblemDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('mental_health_indefinite', item.xpath(xpMentalHealthIndefinite, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('mental_health_indefinite_date_collected', item.xpath(xpMentalHealthIndefiniteDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('mental_health_indefinite_date_effective', item.xpath(xpMentalHealthIndefiniteDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('mental_health_indefinite_data_collection_stage', item.xpath(xpMentalHealthIndefiniteDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('receive_mental_health_services', item.xpath(xpReceiveMentalHealthServices, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receive_mental_health_services_date_collected', item.xpath(xpReceiveMentalHealthServicesDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_mental_health_services_date_effective', item.xpath(xpReceiveMentalHealthServicesDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_mental_health_services_data_collection_stage', item.xpath(xpReceiveMentalHealthServicesDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.MentalHealthProblem)
    
                ''' Parse sub-tables '''
                            

    def parse_length_of_stay_at_prior_residence(self, element):
        ''' Element paths '''
        xpLengthOfStaAtPriorResidence = 'hmis:LengthOfStaAtPriorResidence'
        xpLengthOfStaAtPriorResidenceDateCollected = 'hmis:LengthOfStaAtPriorResidence/@hmis:dateCollected'
        xpLengthOfStaAtPriorResidenceDateEffective = 'hmis:LengthOfStaAtPriorResidence/@hmis:dateEffective'
        xpLengthOfStaAtPriorResidenceDataCollectionStage = 'hmis:LengthOfStaAtPriorResidence/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpLengthOfStaAtPriorResidence, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('length_of_stay_at_prior_residence', item.xpath(xpLengthOfStaAtPriorResidence, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('length_of_stay_at_prior_residence_date_collected', item.xpath(xpLengthOfStaAtPriorResidenceDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('length_of_stay_at_prior_residence_date_effective', item.xpath(xpLengthOfStaAtPriorResidenceDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('length_of_stay_at_prior_residence_data_collection_stage', item.xpath(xpLengthOfStaAtPriorResidenceDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.LengthOfStayAtPriorResidence)
    
                ''' Parse sub-tables '''
                            

    def parse_income_total_monthly(self, element):
        ''' Element paths '''
        xpIncomeTotalMonthly = 'hmis:IncomeTotalMonthly'
        xpIncomeTotalMonthlyDateCollected = 'hmis:IncomeTotalMonthly/@hmis:dateCollected'
        xpIncomeTotalMonthlyDateEffective = 'hmis:IncomeTotalMonthly/@hmis:dateEffective'
        xpIncomeTotalMonthlyDataCollectionStage = 'hmis:IncomeTotalMonthly/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpIncomeTotalMonthly, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('income_total_monthly', item.xpath(xpIncomeTotalMonthly, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('income_total_monthly_date_collected', item.xpath(xpIncomeTotalMonthlyDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_total_monthly_date_effective', item.xpath(xpIncomeTotalMonthlyDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_total_monthly_data_collection_stage', item.xpath(xpIncomeTotalMonthlyDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.IncomeTotalMonthly)
    
                ''' Parse sub-tables '''
                            

    def parse_hud_chronic_homeless(self, element):
        ''' Element paths '''
        xpHUDChronicHomeless = 'hmis:HUDChronicHomeless'
        xpHUDChronicHomelessDateCollected = 'hmis:HUDChronicHomeless/@hmis:dateCollected'
        xpHUDChronicHomelessDateEffective = 'hmis:HUDChronicHomeless/@hmis:dateEffective'
        xpHUDChronicHomelessDataCollectionStage = 'hmis:HUDChronicHomeless/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpHUDChronicHomeless, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('hud_chronic_homeless', item.xpath(xpHUDChronicHomeless, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hud_chronic_homeless_date_collected', item.xpath(xpHUDChronicHomelessDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('hud_chronic_homeless_date_effective', item.xpath(xpHUDChronicHomelessDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('hud_chronic_homeless_data_collection_stage', item.xpath(xpHUDChronicHomelessDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.HudChronicHomeless)
    
                ''' Parse sub-tables '''
                            

    def parse_income_last_30_days(self, element):
        ''' Element paths '''
        xpIncomeLast30Days = 'hmis:IncomeLast30Days'
        xpIncomeLast30DaysDateCollected = 'hmis:IncomeLast30Days/@hmis:dateCollected'
        xpIncomeLast30DaysDateEffective = 'hmis:IncomeLast30Days/@hmis:dateEffective'
        xpIncomeLast30DaysDataCollectionStage = 'hmis:IncomeLast30Days/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpIncomeLast30Days, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('income_last_30_days', item.xpath(xpIncomeLast30Days, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('income_last_30_days_date_collected', item.xpath(xpIncomeLast30DaysDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_last_30_days_date_effective', item.xpath(xpIncomeLast30DaysDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_last_30_days_data_collection_stage', item.xpath(xpIncomeLast30DaysDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.IncomeLast30Days)
    
                ''' Parse sub-tables '''
                            

    def parse_highest_school_level(self, element):
        ''' Element paths '''
        xpHighestSchoolLevel = 'hmis:HighestSchoolLevel'
        xpHighestSchoolLevelDateCollected = 'hmis:HighestSchoolLevel/@hmis:dateCollected'
        xpHighestSchoolLevelDateEffective = 'hmis:HighestSchoolLevel/@hmis:dateEffective'
        xpHighestSchoolLevelDataCollectionStage = 'hmis:HighestSchoolLevel/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpHighestSchoolLevel, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('highest_school_level', item.xpath(xpHighestSchoolLevel, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('highest_school_level_date_collected', item.xpath(xpHighestSchoolLevelDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('highest_school_level_date_effective', item.xpath(xpHighestSchoolLevelDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('highest_school_level_data_collection_stage', item.xpath(xpHighestSchoolLevelDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.HighestSchoolLevel)
    
                ''' Parse sub-tables '''
                            

    def parse_hiv_aids_status(self, element):
        ''' Element paths '''
        xpHIVAIDSStatus = 'hmis:HIVAIDSStatus'
        xpHasHIVAIDS = 'hmis:HasHIVAIDS'
        xpHasHIVAIDSDateCollected = 'hmis:HasHIVAIDS/@hmis:dateCollected'
        xpHasHIVAIDSDateEffective = 'hmis:HasHIVAIDS/@hmis:dateEffective'
        xpHasHIVAIDSDataCollectionStage = 'hmis:HasHIVAIDS/@hmis:dataCollectionStage'
        xpReceiveHIVAIDSServices = 'hmis:ReceiveHIVAIDSServices'
        xpReceiveHIVAIDSServicesDateCollected = 'hmis:ReceiveHIVAIDSServices/@hmis:dateCollected'
        xpReceiveHIVAIDSServicesDateEffective = 'hmis:ReceiveHIVAIDSServices/@hmis:dateEffective'
        xpReceiveHIVAIDSServicesDataCollectionStage = 'hmis:ReceiveHIVAIDSServices/@hmis:dataCollectionStage'        

        itemElements = element.xpath(xpHIVAIDSStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('has_hiv_aids', item.xpath(xpHasHIVAIDS, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('has_hiv_aids_date_collected', item.xpath(xpHasHIVAIDSDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_hiv_aids_date_effective', item.xpath(xpHasHIVAIDSDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_hiv_aids_data_collection_stage', item.xpath(xpHasHIVAIDSDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('receive_hiv_aids_services', item.xpath(xpReceiveHIVAIDSServices, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receive_hiv_aids_services_date_collected', item.xpath(xpReceiveHIVAIDSServicesDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_hiv_aids_services_date_effective', item.xpath(xpReceiveHIVAIDSServicesDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_hiv_aids_services_data_collection_stage', item.xpath(xpReceiveHIVAIDSServicesDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.HivAidsStatus)
    
                ''' Parse sub-tables '''
                            

    def parse_health_status(self, element):
        ''' Element paths '''
        xpHealthStatus = 'hmis:HealthStatus'
        xpHealthStatusDateCollected = 'hmis:HealthStatus/@hmis:dateCollected'
        xpHealthStatusDateEffective = 'hmis:HealthStatus/@hmis:dateEffective'
        xpHealthStatusDataCollectionStage = 'hmis:HealthStatus/@hmis:dataCollectionStage'     

        itemElements = element.xpath(xpHealthStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('health_status', item.xpath(xpHealthStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('health_status_date_collected', item.xpath(xpHealthStatusDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('health_status_date_effective', item.xpath(xpHealthStatusDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('health_status_data_collection_stage', item.xpath(xpHealthStatusDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')   

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.HealthStatus)
    
                ''' Parse sub-tables '''
                            

    def parse_engaged_date(self, element):
        ''' Element paths '''
        xpEngagedDate = 'hmis:EngagedDate'
        xpEngagedDateDateCollected = 'hmis:EngagedDate/@hmis:dateCollected'
        xpEngagedDateDateEffective = 'hmis:EngagedDate/@hmis:dateEffective'
        xpEngagedDateDataCollectionStage = 'hmis:EngagedDate/@hmis:dataCollectionStage'  

        itemElements = element.xpath(xpEngagedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('engaged_date', item.xpath(xpEngagedDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('engaged_date_date_collected', item.xpath(xpEngagedDateDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('engaged_date_data_collection_stage', item.xpath(xpEngagedDateDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.EngagedDate)
    
                ''' Parse sub-tables '''
                            

    def parse_employment(self, element):
        ''' Element paths '''
        xpEmployment = 'hmis:Employment'
        xpEmploymentIDIDNum = 'hmis:PriorResidenceID/hmis:IDNum'
        xpEmploymentIDIDStr = 'hmis:PriorResidenceID/hmis:IDStr'
        xpEmploymentIDDeleteOccurredDate = 'hmis:PriorResidenceID/@hmis:deleteOccurredDate'
        xpEmploymentIDDeleteEffective = 'hmis:PriorResidenceID/@hmis:deleteEffective'
        xpEmploymentIDDelete = 'hmis:PriorResidenceID/@hmis:delete'
        xpCurrentlyEmployed = 'hmis:CurrentlyEmployed'
        xpCurrentlyEmployedDateCollected = 'hmis:CurrentlyEmployed/@hmis:dateCollected'
        xpCurrentlyEmployedDateEffective = 'hmis:CurrentlyEmployed/@hmis:dateEffective'
        xpCurrentlyEmployedDataCollectionStage = 'hmis:CurrentlyEmployed/@hmis:dataCollectionStage'
        xpHoursWorkedLastWeek = 'hmis:HoursWorkedLastWeek'
        xpHoursWorkedLastWeekDateCollected = 'hmis:HoursWorkedLastWeek/@hmis:dateCollected'
        xpHoursWorkedLastWeekDateEffective = 'hmis:HoursWorkedLastWeek/@hmis:dateEffective'
        xpHoursWorkedLastWeekDataCollectionStage = 'hmis:HoursWorkedLastWeek/@hmis:dataCollectionStage'
        xpEmploymentTenure = 'hmis:EmploymentTenure'
        xpEmploymentTenureDateCollected = 'hmis:EmploymentTenure/@hmis:dateCollected'
        xpEmploymentTenureDateEffective = 'hmis:EmploymentTenure/@hmis:dateEffective'
        xpEmploymentTenureDataCollectionStage = 'hmis:EmploymentTenure/@hmis:dataCollectionStage'
        xpLookingForWork = 'hmis:LookingForWork'
        xpLookingForWorkDateCollected = 'hmis:LookingForWork/@hmis:dateCollected'
        xpLookingForWorkDateEffective = 'hmis:LookingForWork/@hmis:dateEffective'
        xpLookingForWorkDataCollectionStage = 'hmis:LookingForWork/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpEmployment, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('employment_id_id_id_num', item.xpath(xpEmploymentIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('employment_id_id_id_str', item.xpath(xpEmploymentIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('employment_id_id_delete_occurred_date', item.xpath(xpEmploymentIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('employment_id_id_delete_effective', item.xpath(xpEmploymentIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('employment_id_id_delete', item.xpath(xpEmploymentIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('currently_employed', item.xpath(xpCurrentlyEmployed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('currently_employed_date_collected', item.xpath(xpCurrentlyEmployedDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('currently_employed_date_effective', item.xpath(xpCurrentlyEmployedDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('currently_employed_data_collection_stage', item.xpath(xpCurrentlyEmployedDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('hours_worked_last_week', item.xpath(xpHoursWorkedLastWeek, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('hours_worked_last_week_date_collected', item.xpath(xpHoursWorkedLastWeekDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('hours_worked_last_week_date_effective', item.xpath(xpHoursWorkedLastWeekDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('hours_worked_last_week_data_collection_stage', item.xpath(xpHoursWorkedLastWeekDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('employment_tenure', item.xpath(xpEmploymentTenure, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('employment_tenure_date_collected', item.xpath(xpEmploymentTenureDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('employment_tenure_date_effective', item.xpath(xpEmploymentTenureDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('employment_tenure_data_collection_stage', item.xpath(xpEmploymentTenureDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('looking_for_work', item.xpath(xpLookingForWork, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('looking_for_work_date_collected', item.xpath(xpLookingForWorkDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('looking_for_work_date_effective', item.xpath(xpLookingForWorkDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('looking_for_work_data_collection_stage', item.xpath(xpLookingForWorkDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Employment)
    
                ''' Parse sub-tables '''
                            

    def parse_domestic_violence(self, element):
        ''' Element paths '''
        xpDomesticViolence = 'hmis:DomesticViolence'
        xpDomesticViolenceSurvivor = 'hmis:DomesticViolenceSurvivor'
        xpDomesticViolenceSurvivorDateCollected = 'hmis:DomesticViolenceSurvivor/@hmis:dateCollected'
        xpDomesticViolenceSurvivorDateEffective = 'hmis:DomesticViolenceSurvivor/@hmis:dateEffective'
        xpDomesticViolenceSurvivorDataCollectionStage = 'hmis:DomesticViolenceSurvivor/@hmis:dataCollectionStage'
        xpDVOccurred = 'hmis:DVOccurred'
        xpDVOccurredDateCollected = 'hmis:DVOccurred/@hmis:dateCollected'
        xpDVOccurredDateEffective = 'hmis:DVOccurred/@hmis:dateEffective'
        xpDVOccurredDataCollectionStage = 'hmis:DVOccurred/@hmis:dataCollectionStage'        

        itemElements = element.xpath(xpDomesticViolence, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('domestic_violence_survivor', item.xpath(xpDomesticViolenceSurvivor, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('domestic_violence_survivor_date_collected', item.xpath(xpDomesticViolenceSurvivorDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('domestic_violence_survivor_date_effective', item.xpath(xpDomesticViolenceSurvivorDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('domestic_violence_survivor_data_collection_stage', item.xpath(xpDomesticViolenceSurvivorDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('dv_occurred', item.xpath(xpDVOccurred, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('dv_occurred_date_collected', item.xpath(xpDVOccurredDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('dv_occurred_date_effective', item.xpath(xpDVOccurredDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('dv_occurred_data_collection_stage', item.xpath(xpDVOccurredDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')     

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.DomesticViolence)
    
                ''' Parse sub-tables '''
                            

    def parse_disabling_condition(self, element):
        ''' Element paths '''
        xpDisablingCondition = 'hmis:DisablingCondition'
        xpDisablingConditionDateCollected = 'hmis:DisablingCondition/@hmis:dateCollected'
        xpDisablingConditionDateEffective = 'hmis:DisablingCondition/@hmis:dateEffective'
        xpDisablingConditionDataCollectionStage = 'hmis:DisablingCondition/@hmis:dataCollectionStage'    

        itemElements = element.xpath(xpDisablingCondition, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('disabling_condition', item.xpath(xpDisablingCondition, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('disabling_condition_date_collected', item.xpath(xpDisablingConditionDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('disabling_condition_date_effective', item.xpath(xpDisablingConditionDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('disabling_condition_data_collection_stage', item.xpath(xpDisablingConditionDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.DisablingCondition)
    
                ''' Parse sub-tables '''
                            

    def parse_developmental_disability(self, element):
        ''' Element paths '''
        xpDevelopmentalDisability = 'hmis:DevelopmentalDisability'
        xpHasDevelopmentalDisability = 'hmis:HasDevelopmentalDisability'
        xpHasDevelopmentalDisabilityDateCollected = 'hmis:HasDevelopmentalDisability/@hmis:dateCollected'
        xpHasDevelopmentalDisabilityDateEffective = 'hmis:HasDevelopmentalDisability/@hmis:dateEffective'
        xpHasDevelopmentalDisabilityDataCollectionStage = 'hmis:HasDevelopmentalDisability/@hmis:dataCollectionStage'    
        xpReceiveDevelopmentalDisability = 'hmis:ReceiveDevelopmentalDisability'
        xpReceiveDevelopmentalDisabilityDateCollected = 'hmis:ReceiveDevelopmentalDisability/@hmis:dateCollected'
        xpReceiveDevelopmentalDisabilityDateEffective = 'hmis:ReceiveDevelopmentalDisability/@hmis:dateEffective'
        xpReceiveDevelopmentalDisabilityDataCollectionStage = 'hmis:ReceiveDevelopmentalDisability/@hmis:dataCollectionStage'    

        itemElements = element.xpath(xpDevelopmentalDisability, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('has_developmental_disability', item.xpath(xpHasDevelopmentalDisability, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('has_developmental_disability_date_collected', item.xpath(xpHasDevelopmentalDisabilityDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_developmental_disability_date_effective', item.xpath(xpHasDevelopmentalDisabilityDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_developmental_disability_data_collection_stage', item.xpath(xpHasDevelopmentalDisabilityDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('receive_developmental_disability', item.xpath(xpReceiveDevelopmentalDisability, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receive_developmental_disability_date_collected', item.xpath(xpReceiveDevelopmentalDisabilityDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_developmental_disability_date_effective', item.xpath(xpReceiveDevelopmentalDisabilityDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_developmental_disability_data_collection_stage', item.xpath(xpReceiveDevelopmentalDisabilityDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.DevelopmentalDisability)
    
                ''' Parse sub-tables '''
                            

    def parse_destinations(self, element):
        ''' Element paths '''
        xpDestinations = 'hmis:Destinations/hmis:Destination'
        xpDestinationIDIDNum = 'hmis:DestinationID/hmis:IDNum'
        xpDestinationIDIDStr = 'hmis:DestinationID/hmis:IDStr'
        xpDestinationIDDeleteOccurredDate = 'hmis:DestinationID/@hmis:deleteOccurredDate'
        xpDestinationIDDeleteEffective = 'hmis:DestinationID/@hmis:deleteEffective'
        xpDestinationIDDelete = 'hmis:DestinationID/@hmis:delete'
        xpDestinationCode = 'hmis:DestinationCode'
        xpDestinationCodeDateCollected = 'hmis:DestinationCode/@hmis:dateCollected'
        xpDestinationCodeDateEffective = 'hmis:DestinationCode/@hmis:dateEffective'
        xpDestinationCodeDataCollectionStage = 'hmis:DestinationCode/@hmis:dataCollectionStage'
        xpDestinationOther = 'hmis:DestinationOther'
        xpDestinationOtherDateCollected = 'hmis:DestinationOther/@hmis:dateCollected'
        xpDestinationOtherDateEffective = 'hmis:DestinationOther/@hmis:dateEffective'
        xpDestinationOtherDataCollectionStage = 'hmis:DestinationOther/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpDestinations, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('destination_id_id_num', item.xpath(xpDestinationIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('destination_id_id_str', item.xpath(xpDestinationIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('destination_id_delete_occurred_date', item.xpath(xpDestinationIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('destination_id_delete_effective', item.xpath(xpDestinationIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('destination_id_delete', item.xpath(xpDestinationIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('destination_code', item.xpath(xpDestinationCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('destination_code_date_collected', item.xpath(xpDestinationCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('destination_code_date_effective', item.xpath(xpDestinationCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('destination_code_data_collection_stage', item.xpath(xpDestinationCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('destination_other', item.xpath(xpDestinationOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('destination_other_date_collected', item.xpath(xpDestinationOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('destination_other_date_effective', item.xpath(xpDestinationOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('destination_other_data_collection_stage', item.xpath(xpDestinationOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Destinations)
    
                ''' Parse sub-tables '''
                            

    def parse_degree(self, element):
        ''' Element paths '''
        xpDegree = 'hmis:Degree'
        xpDegreeIDIDNum = 'hmis:Degree/hmis:IDNum'
        xpDegreeIDIDStr = 'hmis:Degree/hmis:IDStr'
        xpDegreeIDDeleteOccurredDate = 'hmis:Degree/@hmis:deleteOccurredDate'
        xpDegreeIDDeleteEffective = 'hmis:Degree/@hmis:deleteEffective'
        xpDegreeIDDelete = 'hmis:Degree/@hmis:delete'
        xpDegreeOther = 'hmis:DegreeOther'
        xpDegreeOtherDateCollected = 'hmis:DegreeOther/@hmis:dateCollected'
        xpDegreeOtherDateEffective = 'hmis:DegreeOther/@hmis:dateEffective'
        xpDegreeOtherDataCollectionStage = 'hmis:DegreeOther/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpDegree, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('degree_id_id_num', item.xpath(xpDegreeIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('degree_id_id_str', item.xpath(xpDegreeIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('degree_id_delete_occurred_date', item.xpath(xpDegreeIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('degree_id_delete_effective', item.xpath(xpDegreeIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('degree_id_delete', item.xpath(xpDegreeIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('degree_other', item.xpath(xpDegreeOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('degree_other_date_collected', item.xpath(xpDegreeOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('degree_other_date_effective', item.xpath(xpDegreeOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('degree_other_data_collection_stage', item.xpath(xpDegreeOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Degree)
    
                ''' Parse sub-tables '''
                self.parse_degree_code(item)            

    def parse_degree_code(self, element):
        ''' Element paths '''
        xpDegreeCode = 'hmis:DegreeCode'
        xpDegreeCodeDateCollected = 'hmis:DegreeCode/@hmis:dateCollected'
        xpDegreeCodeDateEffective = 'hmis:DegreeCode/@hmis:dateEffective'
        xpDegreeCodeDataCollectionStage = 'hmis:DegreeCode/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpDegreeCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('degree_code', item.xpath(xpDegreeCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('degree_date_collected', item.xpath(xpDegreeCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('degree_date_effective', item.xpath(xpDegreeCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('degree_data_collection_stage', item.xpath(xpDegreeCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('degree_index_id', self.degree_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.DegreeCode)
    
                ''' Parse sub-tables '''
                            

    def parse_currently_in_school(self, element):
        ''' Element paths '''
        xpCurrentlyInSchool = 'hmis:CurrentlyInSchool'
        xpCurrentlyInSchoolDateCollected = 'hmis:CurrentlyInSchool/@hmis:dateCollected'
        xpCurrentlyInSchoolDateEffective = 'hmis:CurrentlyInSchool/@hmis:dateEffective'
        xpCurrentlyInSchoolDataCollectionStage = 'hmis:CurrentlyInSchool/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpCurrentlyInSchool, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('currently_in_school', item.xpath(xpCurrentlyInSchool, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('currently_in_school_date_collected', item.xpath(xpCurrentlyInSchoolDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('currently_in_school_date_effective', item.xpath(xpCurrentlyInSchoolDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('currently_in_school_data_collection_stage', item.xpath(xpCurrentlyInSchoolDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.CurrentlyInSchool)
    
                ''' Parse sub-tables '''
                            

    def parse_contact_made(self, element):
        ''' Element paths '''
        xpContactsMade = 'hmis:ContactsMade/hmis:ContactMade'
        xpContactIDIDNum = 'hmis:ContactID/hmis:IDNum'
        xpContactIDIDStr = 'hmis:ContactID/hmis:IDStr'
        xpContactIDDeleteOccurredDate = 'hmis:ContactID/@hmis:deleteOccurredDate'
        xpContactIDDeleteEffective = 'hmis:ContactID/@hmis:deleteEffective'
        xpContactIDDelete = 'hmis:ContactID/@hmis:delete'
        xpContactDate = 'hmis:ContactDate'
        xpContactDateDataCollectionStage = 'hmis:ContactDate/@hmis:dataCollectionStage'
        xpContactLocation = 'hmis:ContactLocation'
        xpContactLocationDataCollectionStage = 'hmis:ContactLocation/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpContactsMade, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('contact_id_id_num', item.xpath(xpContactIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('contact_id_id_str', item.xpath(xpContactIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('contact_id_delete_occurred_date', item.xpath(xpContactIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('contact_id_delete_effective', item.xpath(xpContactIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('contact_id_delete', item.xpath(xpContactIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('contact_date', item.xpath(xpContactDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('contact_date_data_collection_stage', item.xpath(xpContactDateDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('contact_location', item.xpath(xpContactLocation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('contact_location_data_collection_stage', item.xpath(xpContactLocationDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ContactMade)
    
                ''' Parse sub-tables '''
                            

    def parse_child_enrollment_status(self, element):
        ''' Element paths '''
        xpChildEnrollmentStatus = 'hmis:ChildEnrollmentStatus'
        xpChildEnrollmentStatusIDIDNum = 'hmis:ChildEnrollmentStatusID/hmis:IDNum'
        xpChildEnrollmentStatusIDIDStr = 'hmis:ChildEnrollmentStatusID/hmis:IDStr'
        xpChildEnrollmentStatusIDDeleteOccurredDate = 'hmis:ChildEnrollmentStatusID/@hmis:deleteOccurredDate'
        xpChildEnrollmentStatusIDDeleteEffective = 'hmis:ChildEnrollmentStatusID/@hmis:deleteEffective'
        xpChildEnrollmentStatusIDDelete = 'hmis:ChildEnrollmentStatusID/@hmis:delete'
        xpChildCurrentlyEnrolledInSchool = 'hmis:ChildCurrentlyEnrolledInSchool'
        xpChildCurrentlyEnrolledInSchoolDateCollected = 'hmis:ChildCurrentlyEnrolledInSchool/@hmis:dateCollected'
        xpChildCurrentlyEnrolledInSchoolDateEffective = 'hmis:ChildCurrentlyEnrolledInSchool/@hmis:dateEffective'
        xpChildCurrentlyEnrolledInSchoolDataCollectionStage = 'hmis:ChildCurrentlyEnrolledInSchool/@hmis:dataCollectionStage'
        xpChildSchoolName = 'hmis:ChildSchoolName'
        xpChildSchoolNameDateCollected = 'hmis:ChildSchoolName/@hmis:dateCollected'
        xpChildSchoolNameDateEffective = 'hmis:ChildSchoolName/@hmis:dateEffective'
        xpChildSchoolNameDataCollectionStage = 'hmis:ChildSchoolName/@hmis:dataCollectionStage'
        xpChildMcKinneyVentoLiaison = 'hmis:ChildMcKinneyVentoLiaison'
        xpChildMcKinneyVentoLiaisonDateCollected = 'hmis:ChildMcKinneyVentoLiaison/@hmis:dateCollected'
        xpChildMcKinneyVentoLiaisonDateEffective = 'hmis:ChildMcKinneyVentoLiaison/@hmis:dateEffective'
        xpChildMcKinneyVentoLiaisonDataCollectionStage = 'hmis:ChildMcKinneyVentoLiaison/@hmis:dataCollectionStage'
        xpChildSchoolType = 'hmis:ChildSchoolType'
        xpChildSchoolTypeDateCollected = 'hmis:ChildSchoolType/@hmis:dateCollected'
        xpChildSchoolTypeDateEffective = 'hmis:ChildSchoolType/@hmis:dateEffective'
        xpChildSchoolTypeDataCollectionStage = 'hmis:ChildSchoolType/@hmis:dataCollectionStage'
        xpChildSchoolLastEnrolledDate = 'hmis:ChildSchoolLastEnrolledDate'
        xpChildSchoolLastEnrolledDateDateCollected = 'hmis:ChildSchoolLastEnrolledDate/@hmis:dateCollected'
        xpChildSchoolLastEnrolledDateDateEffective = 'hmis:ChildSchoolLastEnrolledDate/@hmis:dateEffective'
        xpChildSchoolLastEnrolledDateDataCollectionStage = 'hmis:ChildSchoolLastEnrolledDate/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpChildEnrollmentStatus, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('child_enrollment_status_id_id_num', item.xpath(xpChildEnrollmentStatusIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('child_enrollment_status_id_id_str', item.xpath(xpChildEnrollmentStatusIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('child_enrollment_status_id_delete_occurred_date', item.xpath(xpChildEnrollmentStatusIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_enrollment_status_id_delete_effective', item.xpath(xpChildEnrollmentStatusIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_enrollment_status_id_delete', item.xpath(xpChildEnrollmentStatusIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('child_currently_enrolled_in_school', item.xpath(xpChildCurrentlyEnrolledInSchool, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('child_currently_enrolled_in_school_date_collected', item.xpath(xpChildCurrentlyEnrolledInSchoolDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_currently_enrolled_in_school_date_effective', item.xpath(xpChildCurrentlyEnrolledInSchoolDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_currently_enrolled_in_school_data_collection_stage', item.xpath(xpChildCurrentlyEnrolledInSchoolDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('child_school_name', item.xpath(xpChildSchoolName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('child_school_name_date_collected', item.xpath(xpChildSchoolNameDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_school_name_date_effective', item.xpath(xpChildSchoolNameDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_school_name_data_collection_stage', item.xpath(xpChildSchoolNameDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('child_mckinney_vento_liaison', item.xpath(xpChildMcKinneyVentoLiaison, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('child_mckinney_vento_liaison_date_collected', item.xpath(xpChildMcKinneyVentoLiaisonDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_mckinney_vento_liaison_date_effective', item.xpath(xpChildMcKinneyVentoLiaisonDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_mckinney_vento_liaison_data_collection_stage', item.xpath(xpChildMcKinneyVentoLiaisonDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('child_school_type', item.xpath(xpChildSchoolType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('child_school_type_date_collected', item.xpath(xpChildSchoolTypeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_school_type_date_effective', item.xpath(xpChildSchoolTypeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_school_type_data_collection_stage', item.xpath(xpChildSchoolTypeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('child_school_last_enrolled_date', item.xpath(xpChildSchoolLastEnrolledDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('child_school_last_enrolled_date_date_collected', item.xpath(xpChildSchoolLastEnrolledDateDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('child_school_last_enrolled_date_data_collection_stage', item.xpath(xpChildSchoolLastEnrolledDateDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ChildEnrollmentStatus)
    
                ''' Parse sub-tables '''
                self.parse_child_enrollment_status_barrier(item)            

    def parse_child_enrollment_status_barrier(self, element):
        ''' Element paths '''
        xpChildEnrollmentBarrier = 'hmis:ChildEnrollmentBarrier'
        xpBarrierIDIDNum = 'hmis:BarrierID/hmis:IDNum'
        xpBarrierIDIDStr = 'hmis:BarrierID/hmis:IDStr'
        xpBarrierIDDeleteOccurredDate = 'hmis:BarrierID/@hmis:deleteOccurredDate'
        xpBarrierIDDeleteEffective = 'hmis:BarrierID/@hmis:deleteEffective'
        xpBarrierIDDelete = 'hmis:BarrierID/@hmis:delete'
        xpBarrierCode = 'hmis:BarrierCode'
        xpBarrierCodeDateCollected = 'hmis:BarrierCode/@hmis:dateCollected'
        xpBarrierCodeDateEffective = 'hmis:BarrierCode/@hmis:dateEffective'
        xpBarrierCodeDataCollectionStage = 'hmis:BarrierCode/@hmis:dataCollectionStage'
        xpBarrierOther = 'hmis:BarrierOther'
        xpBarrierOtherDateCollected = 'hmis:BarrierOther/@hmis:dateCollected'
        xpBarrierOtherDateEffective = 'hmis:BarrierOther/@hmis:dateEffective'
        xpBarrierOtherDataCollectionStage = 'hmis:BarrierOther/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpChildEnrollmentBarrier, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('barrier_id_id_num', item.xpath(xpBarrierIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('barrier_id_id_str', item.xpath(xpBarrierIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('barrier_id_delete_occurred_date', item.xpath(xpBarrierIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('barrier_id_delete_effective', item.xpath(xpBarrierIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('barrier_id_delete', item.xpath(xpBarrierIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('barrier_code', item.xpath(xpBarrierCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('barrier_code_date_collected', item.xpath(xpBarrierCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('barrier_code_date_effective', item.xpath(xpBarrierCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('barrier_code_data_collection_stage', item.xpath(xpBarrierCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('barrier_other', item.xpath(xpBarrierOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('barrier_other_date_collected', item.xpath(xpBarrierOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('barrier_other_date_effective', item.xpath(xpBarrierOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('barrier_other_data_collection_stage', item.xpath(xpBarrierOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('child_enrollment_status_index_id', self.child_enrollment_status_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ChildEnrollmentStatusBarrier)
    
                ''' Parse sub-tables '''
                            

    def parse_chronic_health_condition(self, element):
        ''' Element paths '''
        xpChronicHealthCondition = 'hmis:ChronicHealthCondition'
        xpHasChronicHealthCondition = 'hmis:HasChronicHealthCondition'
        xpHasChronicHealthConditionDateCollected = 'hmis:HasChronicHealthCondition/@hmis:dateCollected'
        xpHasChronicHealthConditionDateEffective = 'hmis:HasChronicHealthCondition/@hmis:dateEffective'
        xpHasChronicHealthConditionDataCollectionStage = 'hmis:HasChronicHealthCondition/@hmis:dataCollectionStage'
        xpReceiveChronicHealthServices = 'hmis:ReceiveChronicHealthServices'
        xpReceiveChronicHealthServicesDateCollected = 'hmis:ReceiveChronicHealthServices/@hmis:dateCollected'
        xpReceiveChronicHealthServicesDateEffective = 'hmis:ReceiveChronicHealthServices/@hmis:dateEffective'
        xpReceiveChronicHealthServicesDataCollectionStage = 'hmis:ReceiveChronicHealthServices/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpChronicHealthCondition, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('has_chronic_health_condition', item.xpath(xpHasChronicHealthCondition, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('has_chronic_health_condition_date_collected', item.xpath(xpHasChronicHealthConditionDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_chronic_health_condition_date_effective', item.xpath(xpHasChronicHealthConditionDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('has_chronic_health_condition_data_collection_stage', item.xpath(xpHasChronicHealthConditionDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('receive_chronic_health_services', item.xpath(xpReceiveChronicHealthServices, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receive_chronic_health_services_date_collected', item.xpath(xpReceiveChronicHealthServicesDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_chronic_health_services_date_effective', item.xpath(xpReceiveChronicHealthServicesDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receive_chronic_health_services_data_collection_stage', item.xpath(xpReceiveChronicHealthServicesDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ChronicHealthCondition)
    
                ''' Parse sub-tables '''
                            

    def parse_release_of_information(self, element):
        ''' Element paths '''
        xpReleaseOfInformation = 'hmis:ReleaseOfInformation'
        xpReleaseOfInformationIDIDNum = 'hmis:ReleaseOfInformationID/hmis:IDNum'
        xpReleaseOfInformationIDIDStr = 'hmis:ReleaseOfInformationID/hmis:IDStr'
        xpReleaseOfInformationIDDateCollected = 'hmis:ReleaseOfInformationID/@hmis:dateCollected'
        xpReleaseOfInformationIDDateEffective = 'hmis:ReleaseOfInformationID/@hmis:dateEffective'
        xpReleaseOfInformationIDDataCollectionStage = 'hmis:ReleaseOfInformationID/@hmis:dataCollectionStage'
        xpSiteServiceID = 'hmis:SiteServiceID'
        xpDocumentation = 'hmis:Documentation'
        xpDocumentationDateCollected = 'hmis:Documentation/@hmis:dateCollected'
        xpDocumentationDateEffective = 'hmis:Documentation/@hmis:dateEffective'
        xpDocumentationDataCollectionStage = 'hmis:Documentation/@hmis:dataCollectionStage'
        xpStartDate = 'hmis:EffectivePeriod/hmis:StartDate'
        xpEndDate = 'hmis:EffectivePeriod/hmis:EndDate'
        xpReleaseGranted = 'hmis:ReleaseGranted'
        xpReleaseGrantedDateCollected = 'hmis:ReleaseGranted/@hmis:dateCollected'
        xpReleaseGrantedDateEffective = 'hmis:ReleaseGranted/@hmis:dateEffective'
        xpReleaseGrantedDataCollectionStage = 'hmis:ReleaseGranted/@hmis:dataCollectionStage'
        
        itemElements = element.xpath(xpReleaseOfInformation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('release_of_information_idid_num', item.xpath(xpReleaseOfInformationIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('release_of_information_idid_str', item.xpath(xpReleaseOfInformationIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('release_of_information_idid_str_date_collected', item.xpath(xpReleaseOfInformationIDDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('release_of_information_id_date_effective_2010', item.xpath(xpReleaseOfInformationIDDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('release_of_information_id_data_collection_stage_2010', item.xpath(xpReleaseOfInformationIDDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('site_service_idid_str', item.xpath(xpSiteServiceID, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('documentation', item.xpath(xpDocumentation, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('documentation_date_collected', item.xpath(xpDocumentationDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('documentation_date_effective_2010', item.xpath(xpDocumentationDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('documentation_data_collection_stage_2010', item.xpath(xpDocumentationDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('start_date', item.xpath(xpStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('end_date', item.xpath(xpEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('release_granted', item.xpath(xpReleaseGranted, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('release_granted_date_collected', item.xpath(xpReleaseGrantedDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('release_granted_date_effective_2010', item.xpath(xpReleaseGrantedDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('release_granted_data_collection_stage_2010', item.xpath(xpReleaseGrantedDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ReleaseOfInformation)
    
                ''' Parse sub-tables '''
                            

    def parse_income_and_sources(self, element):
        ''' Element paths '''
        xpIncomeAndSources = 'hmis:IncomeAndSources/IncomeAndSource'
        xpIncomeAndSourceIDIDNum = 'hmis:IncomeAndSourceID/hmis:IDNum'
        xpIncomeAndSourceIDIDStr = 'hmis:IncomeAndSourceID/hmis:IDStr'
        xpIncomeAndSourceIDDeleteOccurredDate = 'hmis:IncomeAndSourceID/@hmis:deleteOccurredDate'
        xpIncomeAndSourceIDDeleteEffective = 'hmis:IncomeAndSourceID/@hmis:deleteEffective'
        xpIncomeAndSourceIDDelete = 'hmis:IncomeAndSourceID/@hmis:delete'
        xpIncomeSourceCode = 'hmis:IncomeSourceCode'
        xpIncomeSourceCodeDateCollected = 'hmis:IncomeSourceCode/@hmis:dateCollected'
        xpIncomeSourceCodeDateEffective = 'hmis:IncomeSourceCode/@hmis:dateEffective'
        xpIncomeSourceCodeDataCollectionStage = 'hmis:IncomeSourceCode/@hmis:dataCollectionStage'
        xpIncomeSourceOther = 'hmis:IncomeSourceOther'
        xpIncomeSourceOtherDateCollected = 'hmis:IncomeSourceOther/@hmis:dateCollected'
        xpIncomeSourceOtherDateEffective = 'hmis:IncomeSourceOther/@hmis:dateEffective'
        xpIncomeSourceOtherDataCollectionStage = 'hmis:IncomeSourceOther/@hmis:dataCollectionStage'
        xpReceivingIncomingSource = 'hmis:ReceivingIncomingSource'
        xpReceivingIncomingSourceDateCollected = 'hmis:ReceivingIncomingSource/@hmis:dateCollected'
        xpReceivingIncomingSourceDateEffective = 'hmis:ReceivingIncomingSource/@hmis:dateEffective'
        xpReceivingIncomingSourceDataCollectionStage = 'hmis:ReceivingIncomingSource/@hmis:dataCollectionStage'
        xpIncomeSourceAmount = 'hmis:IncomeSourceAmount'
        xpIncomeSourceAmountDateCollected = 'hmis:IncomeSourceAmount/@hmis:dateCollected'
        xpIncomeSourceAmountDateEffective = 'hmis:IncomeSourceAmount/@hmis:dateEffective'
        xpIncomeSourceAmountDataCollectionStage = 'hmis:IncomeSourceAmount/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpIncomeAndSources, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('income_and_source_id_id_id_num_2010', item.xpath(xpIncomeAndSourceIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('income_and_source_id_id_id_str_2010', item.xpath(xpIncomeAndSourceIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('income_and_source_id_id_delete_occurred_date_2010', item.xpath(xpIncomeAndSourceIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_and_source_id_id_delete_effective_2010', item.xpath(xpIncomeAndSourceIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_and_source_id_id_delete_2010', item.xpath(xpIncomeAndSourceIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('income_source_code', item.xpath(xpIncomeSourceCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('income_source_code_date_collected', item.xpath(xpIncomeSourceCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_source_code_date_effective_2010', item.xpath(xpIncomeSourceCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_source_code_data_collection_stage_2010', item.xpath(xpIncomeSourceCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('income_source_other', item.xpath(xpIncomeSourceOther, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('income_source_other_date_collected', item.xpath(xpIncomeSourceOtherDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_source_other_date_effective_2010', item.xpath(xpIncomeSourceOtherDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_source_other_data_collection_stage_2010', item.xpath(xpIncomeSourceOtherDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('receiving_income_source_2010', item.xpath(xpReceivingIncomingSource, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receiving_income_source_date_collected_2010', item.xpath(xpReceivingIncomingSourceDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receiving_income_source_date_effective_2010', item.xpath(xpReceivingIncomingSourceDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('receiving_income_source_data_collection_stage_2010', item.xpath(xpReceivingIncomingSourceDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('income_source_amount_2010', item.xpath(xpIncomeSourceAmount, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('income_source_amount_date_collected_2010', item.xpath(xpIncomeSourceAmountDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_source_amount_date_effective_2010', item.xpath(xpIncomeSourceAmountDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('income_source_amount_data_collection_stage_2010', item.xpath(xpIncomeSourceAmountDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.IncomeAndSources)
    
                ''' Parse sub-tables '''
                            

    def parse_hud_homeless_episodes(self, element):
        ''' Element paths '''
        xpHudHomelessEpisodes = 'hmis:HUDHomelessEpisodes'
        xpStartDate = 'hmis:StartDate'
        xpEndDate = 'hmis:EndDate'

        itemElements = element.xpath(xpHudHomelessEpisodes, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('start_date', item.xpath(xpStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('end_date', item.xpath(xpEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.HUDHomelessEpisodes)
    
                ''' Parse sub-tables '''
                            
    def parse_person_address(self, element):
        ''' Element paths '''
        xpPersonAddress = 'hmis:PersonAddress'
        xpPersonAddressDateCollected = 'hmis:PersonAddress/@hmis:dateCollected'
        xpPersonAddressDateEffective = 'hmis:PersonAddress/@hmis:dateEffective'
        xpPersonAddressDataCollectionStage = 'hmis:PersonAddress/@hmis:dataCollectionStage'          
        xpAddressPeriodStartDate = 'hmis:AddressPeriod/hmis:StartDate'
        xpAddressPeriodEndDate = 'hmis:AddressPeriod/hmis:EndDate'
        xpPreAddressLine = 'hmis:PreAddressLine'
        xpPreAddressLineDateCollected = 'hmis:PreAddressLine/@hmis:dateCollected'
        xpPreAddressLineDateEffective = 'hmis:PreAddressLine/@hmis:dateEffective'
        xpPreAddressLineDataCollectionStage = 'hmis:PreAddressLine/@hmis:dataCollectionStage'
        xpLine1 = 'hmis:Line1'
        xpLine1DateCollected = 'hmis:Line1/@hmis:dateCollected'
        xpLine1DateEffective = 'hmis:Line1/@hmis:dateEffective'
        xpLine1DataCollectionStage = 'hmis:Line1/@hmis:dataCollectionStage'
        xpLine2 = 'hmis:Line2'
        xpLine2DateCollected = 'hmis:Line2/@hmis:dateCollected'
        xpLine2DateEffective = 'hmis:Line2/@hmis:dateEffective'
        xpLine2DataCollectionStage = 'hmis:Line2/@hmis:dataCollectionStage'
        xpCity = 'hmis:City'
        xpCityDateCollected = 'hmis:City/@hmis:dateCollected'
        xpCityDateEffective = 'hmis:City/@hmis:dateEffective'
        xpCityDataCollectionStage = 'hmis:City/@hmis:dataCollectionStage'
        xpCounty = 'hmis:County'
        xpCountyDateCollected = 'hmis:County/@hmis:dateCollected'
        xpCountyDateEffective = 'hmis:County/@hmis:dateEffective'
        xpCountyDataCollectionStage = 'hmis:County/@hmis:dataCollectionStage'
        xpState = 'hmis:State'
        xpStateDateCollected = 'hmis:State/@hmis:dateCollected'
        xpStateDateEffective = 'hmis:State/@hmis:dateEffective'
        xpStateDataCollectionStage = 'hmis:State/@hmis:dataCollectionStage'
        xpZIPCode = 'hmis:ZIPCode'
        xpZIPCodeDateCollected = 'hmis:ZIPCode/@hmis:dateCollected'
        xpZIPCodeDateEffective = 'hmis:ZIPCode/@hmis:dateEffective'
        xpZIPCodeDataCollectionStage = 'hmis:ZIPCode/@hmis:dataCollectionStage'
        xpCountry = 'hmis:Country'
        xpCountryDateCollected = 'hmis:Country/@hmis:dateCollected'
        xpCountryDateEffective = 'hmis:Country/@hmis:dateEffective'
        xpCountryDataCollectionStage = 'hmis:Country/@hmis:dataCollectionStage'
        xpIsLastPermanentZip = 'hmis:IsLastPermanentZIP'
        xpIsLastPermanentZIPDateCollected = 'hmis:IsLastPermanentZIP/@hmis:dateCollected'
        xpIsLastPermanentZIPDateEffective = 'hmis:IsLastPermanentZIP/@hmis:dateEffective'
        xpIsLastPermanentZIPDataCollectionStage = 'hmis:IsLastPermanentZIP/@hmis:dataCollectionStage'
        xpZipQualityCode = 'hmis:ZIPQualityCode'
        xpZIPQualityCodeDateCollected = 'hmis:ZIPQualityCode/@hmis:dateCollected'
        xpZIPQualityCodeDateEffective = 'hmis:ZIPQualityCode/@hmis:dateEffective'
        xpZIPQualityCodeDataCollectionStage = 'hmis:ZIPQualityCode/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpPersonAddress, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('address_period_start_date', item.xpath(xpAddressPeriodStartDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('address_period_end_date', item.xpath(xpAddressPeriodEndDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pre_address_line', item.xpath(xpPreAddressLine, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('pre_address_line_date_collected', item.xpath(xpPreAddressLineDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('pre_address_line_date_effective_2010', item.xpath(xpPreAddressLineDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('pre_address_line', item.xpath(xpPreAddressLineDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('line1', item.xpath(xpLine1, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('line1_date_collected', item.xpath(xpLine1DateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('line1_date_effective_2010', item.xpath(xpLine1DateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('line1_data_collection_stage_2010', item.xpath(xpLine1DataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('line2', item.xpath(xpLine2, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('line2_date_collected', item.xpath(xpLine2DateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('line2_date_effective_2010', item.xpath(xpLine2DateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('line2_data_collection_stage_2010', item.xpath(xpLine2DataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('city', item.xpath(xpCity, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('city_date_collected', item.xpath(xpCityDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('city_date_effective_2010', item.xpath(xpCityDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('city_data_collection_stage_2010', item.xpath(xpCityDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('county', item.xpath(xpCounty, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('county_date_collected', item.xpath(xpCountyDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('county_date_effective_2010', item.xpath(xpCountyDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('county_data_collection_stage_2010', item.xpath(xpCountyDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('state', item.xpath(xpState, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('state_date_collected', item.xpath(xpStateDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('state_date_effective_2010', item.xpath(xpStateDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('state_data_collection_stage_2010', item.xpath(xpStateDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('zipcode', item.xpath(xpZIPCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('zipcode_date_collected', item.xpath(xpZIPCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('zipcod_date_effective_2010e', item.xpath(xpZIPCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('zipcode_data_collection_stage_2010', item.xpath(xpZIPCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('country', item.xpath(xpCountry, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('country_date_collected', item.xpath(xpCountryDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('country_date_effective_2010', item.xpath(xpCountryDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('country_data_collection_stage_2010', item.xpath(xpCountryDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('is_last_permanent_zip', item.xpath(xpIsLastPermanentZip, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('is_last_permanent_zip_date_collected', item.xpath(xpIsLastPermanentZIPDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('is_last_permanent_zip_date_effective_2010', item.xpath(xpIsLastPermanentZIPDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('is_last_permanent_zip_data_collection_stage_2010', item.xpath(xpIsLastPermanentZIPDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('zip_quality_code', item.xpath(xpZipQualityCode, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('zip_quality_code_date_collected', item.xpath(xpZIPQualityCodeDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('zip_quality_code_date_effective_2010', item.xpath(xpZIPQualityCodeDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('zip_quality_code_data_collection_stage_2010', item.xpath(xpZIPQualityCodeDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.PersonAddress)
    
                ''' Parse sub-tables '''
                            
    def parse_other_names(self, element):
        ''' Element paths '''
        xpOtherNames = 'hmis:OtherNames'
        xpOtherFirstNameUnhashed = 'hmis:OtherFirstName/hmis:Unhashed'
        xpOtherFirstNameUnhashedDateCollected = 'hmis:OtherFirstName/hmis:Unhashed/@hmis:dateCollected'
        xpOtherFirstNameUnhashedDateEffective = 'hmis:OtherFirstName/hmis:Unhashed/@hmis:dateEffective'
        xpOtherFirstNameUnhashedDataCollectionStage = 'hmis:OtherFirstName/hmis:Unhashed/@hmis:dataCollectionStage'
        xpOtherFirstNameHashed = 'hmis:OtherFirstName/hmis:Hashed'
        xpOtherFirstNameHashedDateCollected = 'hmis:OtherFirstName/hmis:Hashed/@hmis:dateCollected'
        xpOtherFirstNameHashedDateEffective = 'hmis:OtherFirstName/hmis:Hashed/@hmis:dateEffective'
        xpOtherFirstNameHashedDataCollectionStage = 'hmis:OtherFirstName/hmis:Hashed/@hmis:dataCollectionStage'
        xpOtherLastNameUnhashed = 'hmis:OtherLastName/hmis:Unhashed'
        xpOtherLastNameUnhashedDateCollected = 'hmis:OtherLastName/hmis:Unhashed/@hmis:dateCollected'
        xpOtherLastNameUnhashedDateEffective = 'hmis:OtherLastName/hmis:Unhashed/@hmis:dateEffective'
        xpOtherLastNameUnhashedDataCollectionStage = 'hmis:OtherLastName/hmis:Unhashed/@hmis:dataCollectionStage'
        xpOtherLastNameHashed = 'hmis:OtherLastName/hmis:Hashed'
        xpOtherLastNameHashedDateCollected = 'hmis:OtherLastName/hmis:Hashed/@hmis:dateCollected'
        xpOtherLastNameHashedDateEffective = 'hmis:OtherLastName/hmis:Hashed/@hmis:dateEffective'
        xpOtherLastNameHashedDataCollectionStage = 'hmis:OtherLastName/hmis:Hashed/@hmis:dataCollectionStage'
        xpOtherMiddleNameUnhashed = 'hmis:OtherMiddleName/hmis:Unhashed'
        xpOtherMiddleNameUnhashedDateCollected = 'hmis:OtherMiddleName/hmis:Unhashed/@hmis:dateCollected'
        xpOtherMiddleNameUnhashedDateEffective = 'hmis:OtherMiddleName/hmis:Unhashed/@hmis:dateEffective'
        xpOtherMiddleNameUnhashedDataCollectionStage = 'hmis:OtherMiddleName/hmis:Unhashed/@hmis:dataCollectionStage'
        xpOtherMiddleNameHashed = 'hmis:OtherMiddleName/hmis:Hashed'
        xpOtherMiddleNameHashedDateCollected = 'hmis:OtherMiddleName/hmis:Hashed/@hmis:dateCollected'
        xpOtherMiddleNameHashedDateEffective = 'hmis:OtherMiddleName/hmis:Hashed/@hmis:dateEffective'
        xpOtherMiddleNameHashedDataCollectionStage = 'hmis:OtherMiddleName/hmis:Hashed/@hmis:dataCollectionStage'
        xpOtherSuffixUnhashed = 'hmis:OtherSuffix/hmis:Unhashed'
        xpOtherSuffixUnhashedDateCollected = 'hmis:OtherSuffix/hmis:Unhashed/@hmis:dateCollected'
        xpOtherSuffixUnhashedDateEffective = 'hmis:OtherSuffix/hmis:Unhashed/@hmis:dateEffective'
        xpOtherSuffixUnhashedDataCollectionStage = 'hmis:OtherSuffix/hmis:Unhashed/@hmis:dataCollectionStage'
        xpOtherSuffixHashed = 'hmis:OtherSuffix/hmis:Hashed'
        xpOtherSuffixHashedDateCollected = 'hmis:OtherSuffix/hmis:Hashed/@hmis:dateCollected'
        xpOtherSuffixHashedDateEffective = 'hmis:OtherSuffix/hmis:Hashed/@hmis:dateEffective'
        xpOtherSuffixHashedDataCollectionStage = 'hmis:OtherSuffix/hmis:Hashed/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpOtherNames, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('other_first_name_unhashed', item.xpath(xpOtherFirstNameUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('other_first_name_hashed', item.xpath(xpOtherFirstNameHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('other_first_name_date_collected', item.xpath(xpOtherFirstNameHashedDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('other_first_name_date_effective_2010', item.xpath(xpOtherFirstNameHashedDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('other_first_name_data_collection_stage_2010', item.xpath(xpOtherFirstNameHashedDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('other_last_name_unhashed', item.xpath(xpOtherLastNameUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('other_last_name_hashed', item.xpath(xpOtherLastNameHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('other_last_name_date_collected', item.xpath(xpOtherLastNameHashedDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('other_last_name_date_effective_2010', item.xpath(xpOtherLastNameHashedDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('other_last_name_data_collection_stage_2010', item.xpath(xpOtherLastNameHashedDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('other_middle_name_unhashed', item.xpath(xpOtherMiddleNameUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('other_middle_name_hashed', item.xpath(xpOtherMiddleNameHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('other_middle_name_date_collected', item.xpath(xpOtherMiddleNameHashedDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('other_middle_name_date_effective_2010', item.xpath(xpOtherMiddleNameHashedDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('other_middle_name_data_collection_stage_2010', item.xpath(xpOtherMiddleNameHashedDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('other_suffix_unhashed', item.xpath(xpOtherSuffixUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('other_suffix_hashed', item.xpath(xpOtherSuffixHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('other_suffix_date_collected', item.xpath(xpOtherSuffixHashedDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('other_suffix_date_effective_2010', item.xpath(xpOtherSuffixHashedDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('other_suffix_data_collection_stage_2010', item.xpath(xpOtherSuffixHashedDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                
                ''' Foreign Keys '''
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.OtherNames)
    
                ''' Parse sub-tables '''
                            
    def parse_races(self, element):
        ''' Element paths '''
        xpRaces = 'hmis:Race'
        xpRaceUnhashed = 'hmis:Unhashed'
        xpRaceUnhashedDateCollected = 'hmis:Unhashed/@hmis:dateCollected'
        xpRaceUnhashedDataCollectionStage = 'hmis:Unhashed/@hmis:dataCollectionStage'
        xpRaceHashed = 'hmis:Hashed'

        itemElements = element.xpath(xpRaces, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('race_unhashed', item.xpath(xpRaceUnhashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('race_date_collected', item.xpath(xpRaceUnhashedDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('race_data_collection_stage_2010', item.xpath(xpRaceUnhashedDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('race_hashed', item.xpath(xpRaceHashed, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Races)
    
                ''' Parse sub-tables '''
        
    def parse_funding_source(self, element):
        ''' Element paths '''
        xpFundingSource = 'hmis:FundingSources/hmis:FundingSource'
        xpFundingSourceIDIDNum = 'hmis:FundingSourceID/hmis:IDNum'
        xpFundingSourceIDIDStr = 'hmis:FundingSourceID/hmis:IDStr'
        xpFundingSourceIDDeleteOccurredDate = 'hmis:FundingSourceID/@hmis:deleteOccurredDate'
        xpFundingSourceIDDeleteEffective = 'hmis:FundingSourceID/@hmis:deleteEffective'
        xpFundingSourceIDDelete = 'hmis:FundingSourceID/@hmis:delete'
        xpFederalCFDA = 'hmis:FederalCFDA'
        xpReceivesMcKinneyFunding = 'hmis:ReceivesMcKinneyFunding'
        xpAdvanceOrArrears = 'hmis:AdvanceOrArrears'
        xpFinancialAssistanceAmount = 'hmis:FinancialAssistanceAmount'

        itemElements = element.xpath(xpFundingSource, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('funding_source_id_id_num', item.xpath(xpFundingSourceIDIDNum, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('funding_source_id_id_str', item.xpath(xpFundingSourceIDIDStr, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('funding_source_id_delete_occurred_date', item.xpath(xpFundingSourceIDDeleteOccurredDate, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('funding_source_id_delete_effective', item.xpath(xpFundingSourceIDDeleteEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('funding_source_id_delete', item.xpath(xpFundingSourceIDDelete, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('federal_cfda_number', item.xpath(xpFederalCFDA, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('receives_mckinney_funding', item.xpath(xpReceivesMcKinneyFunding, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('advance_or_arrears', item.xpath(xpAdvanceOrArrears, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('financial_assistance_amount', item.xpath(xpFinancialAssistanceAmount, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('service_index_id', self.service_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('service_event_index_id', self.service_event_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.FundingSource)
    
                ''' Parse sub-tables '''
                            

    def parse_resource_info(self, element):
        ''' Element paths '''
        xpResourceInfo = 'airs:ResourceInfo'
        xpResourceSpecialist = 'airs:ResourceSpecialist'
        xpAvailableForDirectory = "../%s/%s" % (xpResourceInfo, '@AvailableForDirectory')
        xpAvailableForReferral = "../%s/%s" % (xpResourceInfo, '@AvailableForReferral')
        xpAvailableForResearch = "../%s/%s" % (xpResourceInfo, '@AvailableForResearch')
        xpDateAdded = "../%s/%s" % (xpResourceInfo, '@DateAdded')
        xpDateLastVerified = "../%s/%s" % (xpResourceInfo, '@DateLastVerified')
        xpDateOfLastAction = "../%s/%s" % (xpResourceInfo, '@DateOfLastAction')
        xpLastActionType = "../%s/%s" % (xpResourceInfo, '@LastActionType')

        itemElements = element.xpath(xpResourceInfo, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('resource_specialist', item.xpath(xpResourceSpecialist, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('available_for_directory', item.xpath(xpAvailableForDirectory, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('available_for_referral', item.xpath(xpAvailableForReferral, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('available_for_research', item.xpath(xpAvailableForResearch, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('date_added', item.xpath(xpDateAdded, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('date_last_verified', item.xpath(xpDateLastVerified, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('date_of_last_action', item.xpath(xpDateOfLastAction, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('last_action_type', item.xpath(xpLastActionType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.ResourceInfo)
    
                ''' Parse sub-tables '''
                self.parse_contact(item)            
                self.parse_email(item)      
                self.parse_phone(item)      
            
    def parse_contact(self, element):
        ''' Element paths '''
        xpContact = 'airs:Contact'
        xpTitle = 'airs:Title'
        xpName = 'airs:Name'
        xpType = "../%s/%s" % (xpContact, '@Type')

        itemElements = element.xpath(xpContact, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('title', item.xpath(xpTitle, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('name', item.xpath(xpName, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                # SBB20100909 wrong type element (attribute)
                self.existence_test_and_add('type', item.xpath(xpType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                except: pass
                # SBB20100908 Need to test this.  A site doesn't have resource Info but contacts do under other elements
                try: self.existence_test_and_add('resource_info_index_id', self.resource_info_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Contact)
    
                ''' Parse sub-tables '''
                self.parse_email(item)      
                self.parse_phone(item)      

    def parse_email(self, element):
        ''' Element paths '''
        xpEmail = 'airs:Email'
        xpAddress = 'airs:Address'
        xpNote = 'airs:Note'
        xpPersonEmail = 'airs:PersonEmail'
        xpPersonEmailDateCollected = 'hmis:PersonEmail/@hmis:dateCollected'
        xpPersonEmailDateEffective = 'hmis:PersonEmail/@hmis:dateEffective'
        xpPersonEmailDataCollectionStage = 'hmis:PersonEmail/@hmis:dataCollectionStage'

        itemElements = element.xpath(xpEmail, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('address', item.xpath(xpAddress, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('note', item.xpath(xpNote, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_email', item.xpath(xpPersonEmail, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('person_email_date_collected', item.xpath(xpPersonEmailDateCollected, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_email_date_effective', item.xpath(xpPersonEmailDateEffective, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_date')
                self.existence_test_and_add('person_email_data_collection_stage', item.xpath(xpPersonEmailDataCollectionStage, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('contact_index_id', self.contact_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('resource_info_index_id', self.resource_info_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Email)
    
                ''' Parse sub-tables '''
                            

    def parse_phone(self, element):
        ''' Element paths '''
        xpPhone = 'airs:Phone'
        xpPhoneNumber = 'airs:PhoneNumber'
        xpReasonWithheld = 'airs:ReasonWithheld'
        xpExtension = 'airs:Extension'
        xpDescription = 'airs:Description'
        xpType = 'airs:Type'
        xpFunction = 'airs:Function'
        xpTollFree = "../%s/%s" % (xpPhone, '@TollFree')
        xpConfidential = "../%s/%s" % (xpPhone, '@Confidential')

        itemElements = element.xpath(xpPhone, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace})
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                self.existence_test_and_add('phone_number', item.xpath(xpPhoneNumber, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('reason_withheld', item.xpath(xpReasonWithheld, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('extension', item.xpath(xpExtension, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('description', item.xpath(xpDescription, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('type', item.xpath(xpType, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('function', item.xpath(xpFunction, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'text')
                self.existence_test_and_add('toll_free', item.xpath(xpTollFree, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')
                self.existence_test_and_add('confidential', item.xpath(xpConfidential, namespaces={'hmis':self.hmis_namespace,'airs':self.airs_namespace}), 'attribute_text')

                ''' Foreign Keys '''
                try: self.existence_test_and_add('agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('contact_index_id', self.contact_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('resource_info_index_id', self.resource_info_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('site_index_id', self.site_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('service_index_id', self.service_index_id, 'no_handling')
                except: pass
                try: self.existence_test_and_add('person_historical_index_id', self.person_historical_index_id, 'no_handling')
                except: pass
                                
                ''' Shred to database '''
                self.shred(self.parse_dict, dbobjects.Phone)
    
                ''' Parse sub-tables '''
                            

    ''' Build link/bridge tables '''
            
    def record_source_export_link(self):
        ''' record the link between source and export '''
        self.existence_test_and_add('source_index_id', self.source_index_id, 'no_handling')
        self.existence_test_and_add('export_index_id', self.export_index_id, 'no_handling')
        self.shred(self.parse_dict, dbobjects.SourceExportLink)
        return            

    def record_agency_child_link(self):
        ''' record the link between agency and any children '''
        self.existence_test_and_add('agency_index_id', self.agency_index_id, 'no_handling')
        self.existence_test_and_add('export_index_id', self.export_index_id, 'no_handling')
        self.shred(self.parse_dict, dbobjects.AgencyChild)
        return            

    ''' Utility methods '''
            
    def shred(self, parse_dict, mapping):
        ''' commits the record set to the database '''
        mapped = mapping(parse_dict)
        #self.session.merge(mapped)
        #self.session.flush()
        
        ''' store foreign keys '''
        if mapping.__name__ == "Source":
            self.source_index_id = mapped.id
            print "Source:",self.source_index_id

        if mapping.__name__ == "Export":
            self.export_index_id = mapped.export_id
            print "Export:",self.export_index_id
            
        if mapping.__name__ == "Household":
            self.household_index_id = mapped.id
            print "Household:",self.household_index_id

        if mapping.__name__ == "Agency":
            self.agency_index_id = mapped.id
            print "Agency:",self.agency_index_id
            
        # SBB20100914 adding new
        if mapping.__name__ == "AgencyLocation":
            self.agency_location_index_id = mapped.id
            print "Agency Location:",self.agency_location_index_id

        if mapping.__name__ == "Site":
            self.site_index_id = mapped.id
            print "Site:",self.site_index_id

        if mapping.__name__ == "SiteService":
            self.site_service_index_id = mapped.id
            print "SiteService:",self.site_service_index_id

        if mapping.__name__ == "PitCountSet":
            self.pit_count_set_index_id = mapped.id
            print "PitCountSet:",self.pit_count_set_index_id

        if mapping.__name__ == "Languages":
            self.languages_index_id = mapped.id
            print "Languages:",self.languages_index_id

        if mapping.__name__ == "Service":
            self.service_index_id = mapped.id
            print "Service:",self.service_index_id

        if mapping.__name__ == "HmisAsset":
            self.hmis_asset_index_id = mapped.id
            print "HmisAsset:",self.hmis_asset_index_id

        if mapping.__name__ == "Assignment":
            self.assignment_index_id = mapped.id
            print "Assignment:",self.assignment_index_id

        if mapping.__name__ == "Person":
            self.person_index_id = mapped.id
            print "Person:",self.person_index_id

        if mapping.__name__ == "SiteServiceParticipation":
            self.site_service_participation_index_id = mapped.id
            print "SiteServiceParticipation:",self.site_service_participation_index_id

        if mapping.__name__ == "Need":
            self.need_index_id = mapped.id
            print "Need:",self.need_index_id

        if mapping.__name__ == "ServiceEvent":
            self.service_event_index_id = mapped.id
            print "ServiceEvent:",self.service_event_index_id            
            
        if mapping.__name__ == "PersonHistorical":
            self.person_historical_index_id = mapped.id
            print "PersonHistorical:",self.person_historical_index_id                              
            
        if mapping.__name__ == "Degree":
            self.degree_index_id = mapped.id
            print "Degree:",self.degree_index_id                
            
        if mapping.__name__ == "ChildEnrollmentStatus":
            self.child_enrollment_status_index_id = mapped.id
            print "ChildEnrollmentStatus:",self.child_enrollment_status_index_id     
            
        if mapping.__name__ == "ResourceInfo":
            self.resource_info_index_id = mapped.id
            print "ResourceInfo:",self.resource_info_index_id               

        if mapping.__name__ == "Contact":
            self.contact_index_id = mapped.id
            print "Contact:",self.contact_index_id                                   
            
        if mapping.__name__ == "TimeOpen":
            self.time_open_index_id = mapped.id
            print "TimeOpen:",self.time_open_index_id   
                        
        self.session.commit()
        return
        
    def existence_test_and_add(self, db_column, query_string, handling):
        ''' Checks that the query actually has a result and adds to dictionary '''
        if handling == 'no_handling':
                self.persist(db_column, query_string = query_string)
                #print query_string
                return True
        elif len(query_string) is not 0 or None:
            if handling == 'attribute_text':
                self.persist(db_column, query_string = str(query_string[0]))
                #print query_string
                return True
            if handling == 'text':
                self.persist(db_column, query_string = query_string[0].text)
                #print query_string
                return True
            elif handling == 'attribute_date':
                self.persist(db_column, query_string = dateutil.parser.parse(query_string[0]))
                #print query_string
                return True
            elif handling == 'element_date':
                self.persist(db_column, query_string = dateutil.parser.parse(query_string[0].text))
                #print query_string
                return True
            else:
                print "Need to specify the handling"
                return False
        else:
            # SBB20100915 added to handle non-list element values
            if type(query_string) == type(list()):
                return False
            # not empty list now evaluate it
            else:
                if handling == 'attribute_text':
                    self.persist(db_column, query_string = str(query_string))
                    #print query_string
                    return True
                if handling == 'text':
                    self.persist(db_column, query_string = query_string.text)
                    #print query_string
                    return True
                elif handling == 'attribute_date':
                    self.persist(db_column, query_string = dateutil.parser.parse(query_string))
                    #print query_string
                    return True
                elif handling == 'element_date':
                    self.persist(db_column, query_string = dateutil.parser.parse(query_string.text))
                    #print query_string
                    return True
            
    def persist(self, db_column, query_string):
        ''' Adds dictionary item with database column and associated data element '''
        self.parse_dict.__setitem__(db_column, query_string)
        return
        
def main(argv=None):  
    ''' Manually test this Reader class '''
    if argv is None:
        argv = sys.argv

    ## clear db tables (may have to run twice to get objects linked properly)
    import postgresutils
    UTILS = postgresutils.Utils()
    UTILS.blank_database()

    #inputFile = os.path.join("%s" % settings.BASE_PATH, "%s" % settings.INPUTFILES_PATH, "HUD_HMIS_3_0_Instance.xml")
    inputFile = "/mnt/mariah/HUD_HMIS_XML/HUD_HMIS_Instance-modified-3.0.xml"
    
    if settings.DB_PASSWD == "":
        settings.DB_PASSWD = raw_input("Please enter your password: ")
    
    if os.path.isfile(inputFile) is True:#_adapted_further
        try:
            xml_file = open(inputFile,'r') 
        except:
            print "Error opening import file"
            
        reader = HMISXML30Reader(xml_file)
        tree = reader.read()
        reader.process_data(tree)
        xml_file.close()

if __name__ == "__main__":
    sys.exit(main())