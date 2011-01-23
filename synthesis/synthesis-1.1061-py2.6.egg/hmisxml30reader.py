''' 
    Reads a HUD HMIS XML 3.0 Document into memory and parses its contents storing them into a postgresql database.
    This is a log database, so it holds everything and doesn't worry about deduplication.
'''

import sys, os
from synthesis.reader import Reader
from zope.interface import implements
from lxml import etree
import dateutil.parser
from conf import settings
import dbobjects

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
        #if settings.DEBUG:
        #    print "does self.xml_file exist?", os.path.exists(self.xml_file)
        ''' Instantiate database object '''
        dbo = dbobjects.DatabaseObjects()
        self.session = dbo.Session()

    def read(self):
        ''' Takes an XML instance file and reads it into memory as a node tree '''
        #print '** Raw XML:', self.xml_file
        #if settings.DEBUG:
        #    print "does self.xml_file still exist?", os.path.exists(self.xml_file)
        tree = etree.parse(self.xml_file)
        #print '** Node tree:', tree
        #self.xml_file.close()
        return tree

    def process_data(self, tree):
        ''' Shreds the XML document into the database '''
        root_element = tree.getroot()
        parse_source(self, root_element)
        return
        
''' Parse each table (other readers use these, so they're stand-alone methods)'''
def parse_source(self, root_element):
    ''' Loop through all sources and then traverse the tree for each export '''
    ''' There can be multiple sources with multiple exports inside each source '''
    
    xpSources = '/hmis:Sources/hmis:Source'
    source_list = root_element.xpath(xpSources, namespaces = self.nsmap)
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
            #xp_source_exports = 'hmis:Export'
                           
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'schema_version', item.xpath(xpSourceVersion, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'source_id_id_num', item.xpath(xpSourceIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_id_id_str', item.xpath(xpSourceIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_id_id_delete', item.xpath(xpSourceDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'source_id_id_delete_occurred_date', item.xpath(xpSourceDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'source_id_id_delete_effective_date', item.xpath(xpSourceDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'software_vendor', item.xpath(xpSourceSoftwareVendor, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'software_version', item.xpath(xpSourceSoftwareVersion, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_contact_email', item.xpath(xpSourceContactEmail, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_contact_extension', item.xpath(xpSourceContactExtension, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_contact_first', item.xpath(xpSourceContactFirst, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_contact_last', item.xpath(xpSourceContactLast, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_contact_phone', item.xpath(xpSourceContactPhone, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_name', item.xpath(xpSourceName, namespaces = self.nsmap), 'text')
            source_id_str = item.xpath(xpSourceIDIDStr, namespaces = self.nsmap)
            source_id_num = item.xpath(xpSourceIDIDNum, namespaces = self.nsmap)

            if source_id_str is not None:
                #source_id = source_id_str[0].text 
                existence_test_and_add(self, 'source_id', source_id_str, 'text')

            elif source_id_num is not None:
                #source_id = source_id_num[0].text 
                existence_test_and_add(self, 'source_id', source_id_num, 'text')

            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Source)
            
            
            
            #print "self.source_index_id is: ", self.source_index_id
            

            ''' Parse all exports for this specific source '''
            parse_export(self, item)
    return                

def parse_export(self, element):
    ''' loop through all exports and traverse the tree '''
    
    ''' Element paths '''
    xpExport = 'hmis:Export'
    xpExportIDIDNum = 'hmis:ExportID/hmis:IDNum'
    xpExportIDIDStr = 'hmis:ExportID/hmis:IDStr'
    xpExportDelete = 'hmis:ExportID/@hmis:delete'
    xpExportDeleteOccurredDate = 'hmis:ExportID/@hmis:deleteOccurredDate'
    xpExportDeleteEffective = 'hmis:ExportID/@hmis:deleteEffective'
    xpExportExportDate = 'hmis:ExportDate'
    xpExportPeriodStartDate = 'hmis:ExportPeriod/hmis:StartDate'
    xpExportPeriodEndDate = 'hmis:ExportPeriod/hmis:EndDate'
    
    itemElements = element.xpath(xpExport, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}

            ''' Map elements to database columns '''
            test = item.xpath(xpExportIDIDNum, namespaces = self.nsmap)
            if len(test) is 0:
                test = item.xpath(xpExportIDIDStr, namespaces = self.nsmap)
                self.export_id = test
                existence_test_and_add(self, 'export_id', test, 'text')
            else:
                self.export_id = test
                existence_test_and_add(self, 'export_id', test, 'text')
            existence_test_and_add(self, 'export_id_id_num', item.xpath(xpExportIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'export_id_id_str', item.xpath(xpExportIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'export_id_delete', item.xpath(xpExportDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'export_id_delete_occurred_date', item.xpath(xpExportDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'export_id_delete_effective_date', item.xpath(xpExportDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'export_date', item.xpath(xpExportExportDate, namespaces = self.nsmap), 'element_date') 
            existence_test_and_add(self, 'export_period_start_date', item.xpath(xpExportPeriodStartDate, namespaces = self.nsmap), 'element_date')
            existence_test_and_add(self, 'export_period_end_date', item.xpath(xpExportPeriodEndDate, namespaces = self.nsmap), 'element_date')

            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Export)
            
            ''' Create source to export link '''
            record_source_export_link(self)

            ''' Parse sub-tables '''
            parse_household(self, item)
            parse_region(self, item)
            parse_agency(self, item)
            parse_person(self, item)
            parse_service(self, item)
            parse_site(self, item)
            parse_site_service(self, item)
    return

def parse_household(self, element):
    ''' Element paths '''
    xpHousehold = 'hmis:Household'
    xpHouseholdIDIDNum = 'hmis:HouseholdID/hmis:IDNum'
    xpHouseholdIDIDStr = 'hmis:HouseholdID/hmis:IDStr'
    xpHeadOfHouseholdIDUnhashed = 'hmis:HeadOfHouseholdID/hmis:Unhashed'
    xpHeadOfHouseholdIDHashed = 'hmis:HeadOfHouseholdID/hmis:Hashed'

    itemElements = element.xpath(xpHousehold, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}

            ''' Map elements to database columns '''
            existence_test_and_add(self, 'household_id_num', item.xpath(xpHouseholdIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'household_id_str', item.xpath(xpHouseholdIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'head_of_household_id_unhashed', item.xpath(xpHeadOfHouseholdIDUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'head_of_household_id_hashed', item.xpath(xpHeadOfHouseholdIDHashed, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Household)

            ''' Parse sub-tables '''
            parse_members(self, item)

def parse_members(self, element):
    ''' Element paths '''
    xpMembers = 'hmis:Members'
    xpMember = 'hmis:Member'
    xpPersonIDUnhashed = 'hmis:PersonID/hmis:Unhashed'
    xpPersonIDHashed = 'hmis:PersonID/hmis:Hashed'
    xpRelationshipToHeadOfHousehold = 'hmis:RelationshipToHeadOfHousehold'
    
    test = element.xpath(xpMembers, namespaces = self.nsmap)
    if len(test) > 0:
        itemElements = test[0].xpath(xpMember, namespaces = self.nsmap)
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}

                ''' Map elements to database columns '''
                existence_test_and_add(self, 'person_id_unhashed', item.xpath(xpPersonIDUnhashed, namespaces = self.nsmap), 'text')
                existence_test_and_add(self, 'person_id_hashed', item.xpath(xpPersonIDHashed, namespaces = self.nsmap), 'text')
                existence_test_and_add(self, 'relationship_to_head_of_household', item.xpath(xpRelationshipToHeadOfHousehold, namespaces = self.nsmap), 'text')
    
                ''' Foreign Keys '''
                existence_test_and_add(self, 'household_index_id', self.household_index_id, 'no_handling')
    
                ''' Shred to database '''
                shred(self, self.parse_dict, dbobjects.Members)

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
    
    itemElements = element.xpath(xpRegion, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'region_id_id_num', item.xpath(xpRegionIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'region_id_id_str', item.xpath(xpRegionIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'site_service_id', item.xpath(xpSiteServiceID, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'region_type', item.xpath(xpRegionType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'region_type_date_collected', item.xpath(xpRegionTypeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'region_type_date_effective', item.xpath(xpRegionTypeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'region_type_data_collection_stage', item.xpath(xpRegionTypeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'region_description', item.xpath(xpRegionDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'region_description_date_collected', item.xpath(xpRegionDescriptionDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'region_description_date_effective', item.xpath(xpRegionDescriptionDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'region_description_data_collection_stage', item.xpath(xpRegionDescriptionDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Region)

def parse_agency(self, element):
    ''' Element paths '''
    xpAgency = 'hmis:Agency'
    xpAgencyDelete = './@delete'
    xpAgencyDeleteOccurredDate = './@deleteOccurredDate'
    xpAgencyDeleteEffective = './@deleteEffective'
    xpAirsKey = 'airs:Key'
    xpAirsName = 'airs:Name'
    xpAgencyDescription = 'airs:AgencyDescription'
    xpIRSStatus = 'airs:IRSStatus'
    xpSourceOfFunds = 'airs:SourceOfFunds'
    #xpRecordOwner = '@hmis:RecordOwner'
    xpRecordOwner = './@RecordOwner'
    #xpFEIN = '@hmis:FEIN'
    xpFEIN = './@FEIN'
    xpYearInc = './@YearInc'
    xpAnnualBudgetTotal = './@AnnualBudgetTotal'
    xpLegalStatus = './@LegalStatus'
    xpExcludeFromWebsite = './@ExcludeFromWebsite'
    xpExcludeFromDirectory = './@ExcludeFromDirectory'
    
    itemElements = element.xpath(xpAgency, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'agency_delete', item.xpath(xpAgencyDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'agency_delete_occurred_date', item.xpath(xpAgencyDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'agency_delete_effective_date', item.xpath(xpAgencyDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'airs_key', item.xpath(xpAirsKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'airs_name', item.xpath(xpAirsName, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'agency_description', item.xpath(xpAgencyDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'irs_status', item.xpath(xpIRSStatus, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'source_of_funds', item.xpath(xpSourceOfFunds, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'fein', item.xpath(xpFEIN, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'record_owner', item.xpath(xpRecordOwner, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'year_inc', item.xpath(xpYearInc, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'annual_budget_total', item.xpath(xpAnnualBudgetTotal, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'legal_status', item.xpath(xpLegalStatus, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'exclude_from_website', item.xpath(xpExcludeFromWebsite, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'exclude_from_directory', item.xpath(xpExcludeFromDirectory, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
                            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Agency)

            ''' Parse sub-tables '''
            parse_agency_service(self, item)
            
            parse_aka(self, item)
            # SBB20100907 Missing, adding back in.
            parse_agency_location(self, item)
            
            # remove this once done with routine, shouldn't pollute keys for other values being parsed
            self.agency_location_index_id = None
            
            parse_phone(self, item)      
            parse_url(self, item)
            parse_email(self, item)      
            parse_contact(self, item)
            parse_license_accreditation(self, item)
            
            parse_service_group(self, item)
            
            # need to reset the contact index once we start processing a site element (because site can have their own contacts)
            self.contact_index_id = None
            
            parse_site(self, item)
            # SBB20100907 clear out the agency primary key - fouling up other parsers
            self.site_index_id = None
            
            parse_resource_info(self, item)
            
            # SBB20100907 clear out the agency primary key - fouling up other parsers
            # done with Agency, clear out the agency primary key, don't want it floating down to other elements.
            self.agency_index_id = None
            
            
def parse_person(self, element):
    ''' Element paths '''
    xpPerson = 'hmis:Person'
    xpPersonIDNum = 'hmis:PersonID/hmis:IDNum'
    xpPersonIDStr = 'hmis:PersonID/hmis:IDStr'
    xpPersonIDDeleteOccurredDate = 'hmis:PersonID/@hmis:DeleteOccurredDate'
    xpPersonIDDeleteEffective = 'hmis:PersonID/@hmis:DeleteEffective'
    xpPersonDelete = 'hmis:PersonID/@hmis:Delete'
    xpPersonDateOfBirthHashed = 'hmis:DateOfBirth/hmis:Hashed'
    xpPersonDateOfBirthHashedDateCollected = 'hmis:DateOfBirth/hmis:Hashed/@hmis:dateCollected'
    xpPersonDateOfBirthUnhashed = 'hmis:DateOfBirth/hmis:Unhashed'
    xpPersonDateOfBirthUnhashedDateCollected = 'hmis:DateOfBirth/hmis:Unhashed/@hmis:dateCollected'
    xpPersonDateOfBirthType = 'hmis:DateOfBirth/hmis:DateOfBirthType'
    xpPersonDateOfBirthTypeDateCollected = 'hmis:DateOfBirth/hmis:DateOfBirthType/@hmis:dateCollected'
    xpPersonEthnicityHashedDateCollected = 'hmis:Ethnicity/hmis:Hashed/@hmis:dateCollected'
    xpPersonEthnicityUnhashedDateCollected = 'hmis:Ethnicity/hmis:Unhashed/@hmis:dateCollected'
    xpPersonEthnicityHashed = 'hmis:Ethnicity/hmis:Hashed'
    xpPersonEthnicityUnhashed = 'hmis:Ethnicity/hmis:Unhashed'
    xpPersonGenderHashed = 'hmis:Gender/hmis:Hashed'
    xpPersonGenderUnhashed = 'hmis:Gender/hmis:Unhashed'
    xpPersonGenderHashedDateCollected = 'hmis:Gender/hmis:Hashed/@hmis:dateCollected'
    xpPersonGenderUnhashedDateCollected = 'hmis:Gender/hmis:Unhashed/@hmis:dateCollected'        
    xpPersonGenderHashedDateEffective = 'hmis:Gender/hmis:Hashed/@hmis:dateEffective'
    xpPersonGenderUnhashedDateEffective = 'hmis:Gender/hmis:Unhashed/@hmis:dateEffective'                
    xpPersonLegalFirstNameHashed = 'hmis:LegalFirstName/hmis:Hashed'
    xpPersonLegalFirstNameUnhashed = 'hmis:LegalFirstName/hmis:Unhashed'
    xpPersonLegalFirstNameHashedDateEffective = 'hmis:LegalFirstName/hmis:Hashed/@hmis:dateEffective'
    xpPersonLegalFirstNameUnhashedDateEffective = 'hmis:LegalFirstName/hmis:Unhashed/@hmis:dateEffective'        
    xpPersonLegalFirstNameHashedDateCollected = 'hmis:LegalFirstName/hmis:Hashed/@hmis:dateCollected'
    xpPersonLegalFirstNameUnhashedDateCollected = 'hmis:LegalFirstName/hmis:Unhashed/@hmis:dateCollected'        
    xpPersonLegalLastNameHashed = 'hmis:LegalLastName/hmis:Hashed'
    xpPersonLegalLastNameUnhashed = 'hmis:LegalLastName/hmis:Unhashed'
    xpPersonLegalLastNameHashedDateEffective = 'hmis:LegalLastName/hmis:Hashed/@hmis:dateEffective'
    xpPersonLegalLastNameUnhashedDateEffective = 'hmis:LegalLastName/hmis:Unhashed/@hmis:dateEffective'        
    xpPersonLegalLastNameHashedDateCollected = 'hmis:LegalLastName/hmis:Hashed/@hmis:dateCollected'
    xpPersonLegalLastNameUnhashedDateCollected = 'hmis:LegalLastName/hmis:Unhashed/@hmis:dateCollected'        
    xpPersonLegalMiddleNameHashed = 'hmis:LegalMiddleName/hmis:Hashed'
    xpPersonLegalMiddleNameUnhashed = 'hmis:LegalMiddleName/hmis:Unhashed'
    xpPersonLegalMiddleNameHashedDateEffective = 'hmis:LegalMiddleName/hmis:Hashed/@hmis:dateEffective'
    xpPersonLegalMiddleNameUnhashedDateEffective = 'hmis:LegalMiddleName/hmis:Unhashed/@hmis:dateEffective'        
    xpPersonLegalMiddleNameHashedDateCollected = 'hmis:LegalMiddleName/hmis:Hashed/@hmis:dateCollected'
    xpPersonLegalMiddleNameUnhashedDateCollected = 'hmis:LegalMiddleName/hmis:Unhashed/@hmis:dateCollected'        
    xpPersonLegalSuffixHashed = 'hmis:LegalSuffix/hmis:Hashed'
    xpPersonLegalSuffixUnhashed = 'hmis:LegalSuffix/hmis:Unhashed'
    xpPersonLegalSuffixHashedDateEffective = 'hmis:LegalSuffix/hmis:Hashed/@hmis:dateEffective'
    xpPersonLegalSuffixUnhashedDateEffective = 'hmis:LegalSuffix/hmis:Unhashed/@hmis:dateEffective'        
    xpPersonLegalSuffixHashedDateCollected = 'hmis:LegalSuffix/hmis:Hashed/@hmis:dateCollected'
    xpPersonLegalSuffixUnhashedDateCollected = 'hmis:LegalSuffix/hmis:Unhashed/@hmis:dateCollected'        
    xpPersonSocialSecurityNumberHashed = 'hmis:SocialSecurityNumber/hmis:Hashed'
    xpPersonSocialSecurityNumberUnhashed = 'hmis:SocialSecurityNumber/hmis:Unhashed'
    xpPersonSocialSecurityNumberHashedDateCollected = 'hmis:SocialSecurityNumber/hmis:Hashed/@hmis:dateCollected'
    xpPersonSocialSecurityNumberUnhashedDateCollected = 'hmis:SocialSecurityNumber/hmis:Unhashed/@hmis:dateCollected'
    xpPersonSocialSecurityNumberHashedDateEffective = 'hmis:SocialSecurityNumber/hmis:Hashed/@hmis:dateEffective'
    xpPersonSocialSecurityNumberUnhashedDateEffective = 'hmis:SocialSecurityNumber/hmis:Unhashed/@hmis:dateEffective' 
    xpPersonSocialSecurityNumberQualityCode = 'hmis:SocialSecurityNumber/hmis:SocialSecNumberQualityCode'
    xpPersonSocialSecurityNumberQualityCodeDateEffective = 'hmis:SocialSecurityNumber/hmis:SocialSecNumberQualityCode/@hmis:dateEffective'
    xpPersonSocialSecurityNumberQualityCodeDateCollected = 'hmis:SocialSecurityNumber/hmis:SocialSecNumberQualityCode/@hmis:dateCollected' 

    itemElements = element.xpath(xpPerson, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'person_id_id_num', item.xpath(xpPersonIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_id_id_str', item.xpath(xpPersonIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_id_delete_occurred_date', item.xpath(xpPersonIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_id_delete_effective_date', item.xpath(xpPersonIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_id_delete', item.xpath(xpPersonDelete, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_date_of_birth_hashed', item.xpath(xpPersonDateOfBirthHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_date_of_birth_hashed_date_collected', item.xpath(xpPersonDateOfBirthHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_date_of_birth_unhashed', item.xpath(xpPersonDateOfBirthUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_date_of_birth_unhashed_date_collected', item.xpath(xpPersonDateOfBirthUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_date_of_birth_type', item.xpath(xpPersonDateOfBirthType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_date_of_birth_type_date_collected', item.xpath(xpPersonDateOfBirthTypeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_ethnicity_hashed', item.xpath(xpPersonEthnicityHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_ethnicity_unhashed', item.xpath(xpPersonEthnicityUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_ethnicity_unhashed_date_collected', item.xpath(xpPersonEthnicityUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_ethnicity_hashed_date_collected', item.xpath(xpPersonEthnicityHashedDateCollected, namespaces = self.nsmap), 'attribute_date')                                
            existence_test_and_add(self, 'person_gender_hashed', item.xpath(xpPersonGenderHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_gender_unhashed', item.xpath(xpPersonGenderUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_gender_unhashed_date_collected', item.xpath(xpPersonGenderUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_gender_hashed_date_collected', item.xpath(xpPersonGenderHashedDateCollected, namespaces = self.nsmap), 'attribute_date')                                                
            existence_test_and_add(self, 'person_gender_unhashed_date_effective', item.xpath(xpPersonGenderUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_gender_hashed_date_effective', item.xpath(xpPersonGenderHashedDateEffective, namespaces = self.nsmap), 'attribute_date')                                                                
            existence_test_and_add(self, 'person_legal_first_name_hashed', item.xpath(xpPersonLegalFirstNameHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_legal_first_name_unhashed', item.xpath(xpPersonLegalFirstNameUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_legal_first_name_hashed_date_collected', item.xpath(xpPersonLegalFirstNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_first_name_unhashed_date_collected', item.xpath(xpPersonLegalFirstNameUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_first_name_hashed_date_effective', item.xpath(xpPersonLegalFirstNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_first_name_unhashed_date_effective', item.xpath(xpPersonLegalFirstNameUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_legal_last_name_hashed', item.xpath(xpPersonLegalLastNameHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_legal_last_name_unhashed', item.xpath(xpPersonLegalLastNameUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_legal_last_name_hashed_date_collected', item.xpath(xpPersonLegalLastNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_last_name_unhashed_date_collected', item.xpath(xpPersonLegalLastNameUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_legal_last_name_hashed_date_effective', item.xpath(xpPersonLegalLastNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_last_name_unhashed_date_effective', item.xpath(xpPersonLegalLastNameUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                                
            existence_test_and_add(self, 'person_legal_middle_name_hashed', item.xpath(xpPersonLegalMiddleNameHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_legal_middle_name_unhashed', item.xpath(xpPersonLegalMiddleNameUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_legal_middle_name_hashed_date_collected', item.xpath(xpPersonLegalMiddleNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_middle_name_unhashed_date_collected', item.xpath(xpPersonLegalMiddleNameUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_legal_middle_name_hashed_date_effective', item.xpath(xpPersonLegalMiddleNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_middle_name_unhashed_date_effective', item.xpath(xpPersonLegalMiddleNameUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                                           
            existence_test_and_add(self, 'person_legal_suffix_hashed', item.xpath(xpPersonLegalSuffixHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_legal_suffix_unhashed', item.xpath(xpPersonLegalSuffixUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_legal_suffix_hashed_date_collected', item.xpath(xpPersonLegalSuffixHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_suffix_unhashed_date_collected', item.xpath(xpPersonLegalSuffixUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_legal_suffix_hashed_date_effective', item.xpath(xpPersonLegalSuffixHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_legal_suffix_unhashed_date_effective', item.xpath(xpPersonLegalSuffixUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                                           
            existence_test_and_add(self, 'person_social_security_number_unhashed', item.xpath(xpPersonSocialSecurityNumberUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_social_security_number_hashed', item.xpath(xpPersonSocialSecurityNumberHashed, namespaces = self.nsmap), 'text')                
            existence_test_and_add(self, 'person_social_security_number_hashed_date_collected', item.xpath(xpPersonSocialSecurityNumberHashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_social_security_number_unhashed_date_collected', item.xpath(xpPersonSocialSecurityNumberUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_social_security_number_hashed_date_effective', item.xpath(xpPersonSocialSecurityNumberHashedDateEffective, namespaces = self.nsmap), 'attribute_date')                
            existence_test_and_add(self, 'person_social_security_number_unhashed_date_effective', item.xpath(xpPersonSocialSecurityNumberUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_social_security_number_quality_code', item.xpath(xpPersonSocialSecurityNumberQualityCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_social_security_number_quality_code_date_effective', item.xpath(xpPersonSocialSecurityNumberQualityCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_social_security_number_quality_code_date_collected', item.xpath(xpPersonSocialSecurityNumberQualityCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            
            ''' Foreign Keys '''
            existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Person)

            ''' Parse sub-tables '''
            parse_site_service_participation(self, item)
            parse_need(self, item)          
            parse_service_event(self, item)
            parse_person_historical(self, item)
            parse_release_of_information(self, item)
            parse_other_names(self, item)
            parse_races(self, item)

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

    itemElements = element.xpath(xpService, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'service_delete_occurred_date', item.xpath(xpServiceDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'service_delete_effective_date', item.xpath(xpServiceDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'service_delete', item.xpath(xpServiceDelete, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'airs_key', item.xpath(xpAirsKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'residential_tracking_method', item.xpath(xpAirsAgencyKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'airs_name', item.xpath(xpAirsName, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'coc_code', item.xpath(xpCOCCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'configuration', item.xpath(xpConfiguration, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'direct_service_code', item.xpath(xpDirectServiceCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'grantee_identifier', item.xpath(xpGranteeIdentifier, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'individual_family_code', item.xpath(xpIndividualFamilyCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'residential_tracking_method', item.xpath(xpResidentialTrackingMethod, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_type', item.xpath(xpServiceType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_effective_period_start_date', item.xpath(xpServiceEffectivePeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_effective_period_end_date', item.xpath(xpServiceEffectivePeriodEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_recorded_date', item.xpath(xpServiceRecordedDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'target_population_a', item.xpath(xpTargetPopulationA, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'target_population_b', item.xpath(xpTargetPopulationB, namespaces = self.nsmap), 'text')
            
            ''' Foreign Keys '''
            existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Service)

            ''' Parse sub-tables '''
            parse_funding_source(self, item)
            parse_inventory(self, item)      

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

    itemElements = element.xpath(xpSite, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'site_delete_occurred_date', item.xpath(xpSiteDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'site_delete_effective_date', item.xpath(xpSiteDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'site_delete', item.xpath(xpSiteDelete, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'airs_key', item.xpath(xpKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'airs_name', item.xpath(xpName, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'site_description', item.xpath(xpSiteDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_pre_address_line', item.xpath(xpPhysicalAddressPreAddressLine, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_line_1', item.xpath(xpPhysicalAddressLine1, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_line_2', item.xpath(xpPhysicalAddressLine2, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_city', item.xpath(xpPhysicalAddressCity, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_state', item.xpath(xpPhysicalAddressState, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_zip_code', item.xpath(xpPhysicalAddressZipCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_country', item.xpath(xpPhysicalAddressCountry, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_reason_withheld', item.xpath(xpPhysicalAddressReasonWithheld, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_confidential', item.xpath(xpPhysicalAddressConfidential, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_description', item.xpath(xpPhysicalAddressDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_pre_address_line', item.xpath(xpMailingAddressPreAddressLine, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_line_1', item.xpath(xpMailingAddressLine1, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_line_2', item.xpath(xpMailingAddressLine2, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_city', item.xpath(xpMailingAddressCity, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_state', item.xpath(xpMailingAddressState, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_zip_code', item.xpath(xpMailingAddressZipCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_country', item.xpath(xpMailingAddressCountry, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_reason_withheld', item.xpath(xpMailingAddressReasonWithheld, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_confidential', item.xpath(xpMailingAddressConfidential, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_description', item.xpath(xpMailingAddressDescription, namespaces = self.nsmap), 'text')    
            existence_test_and_add(self, 'no_physical_address_description', item.xpath(xpNoPhysicalAddressDescription, namespaces = self.nsmap), 'text')      
            existence_test_and_add(self, 'no_physical_address_explanation', item.xpath(xpNoPhysicalAddressExplanation, namespaces = self.nsmap), 'text') 
            existence_test_and_add(self, 'disabilities_access', item.xpath(xpDisabilitiesAccess, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_location_description', item.xpath(xpPhysicalLocationDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'bus_service_access', item.xpath(xpBusServiceAccess, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'public_access_to_transportation', item.xpath(xpPublicAccessToTransportation, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'year_inc', item.xpath(xpYearInc, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'annual_budget_total', item.xpath(xpAnnualBudgetTotal, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'legal_status', item.xpath(xpLegalStatus, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'exclude_from_website', item.xpath(xpExcludeFromWebsite, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'exclude_from_directory', item.xpath(xpExcludeFromDirectory, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'agency_key', item.xpath(xpAgencyKey, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            except: pass
                
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Site)

            ''' Parse sub-tables '''
            parse_url(self, item)
            parse_spatial_location(self, item)
            parse_other_address(self, item)
            parse_cross_street(self, item)
            parse_aka(self, item)
            parse_site_service(self, item)
            parse_languages(self, item)
            parse_time_open(self, item)            
            parse_inventory(self, item)
            #parse_contact(self, item)            
            parse_email(self, item)      
            parse_phone(self, item)
            # SBB20100907 moved till after email and phone (which are part of the site record, contact will drive it's own searches for email and phone (of the contact))
            parse_contact(self, item) 

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

    itemElements = element.xpath(xpSiteService, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'site_service_delete_occurred_date', item.xpath(xpSiteServiceDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'site_service_delete_effective_date', item.xpath(xpSiteServiceDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'site_service_delete', item.xpath(xpSiteServiceDelete, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'name', item.xpath(xpName, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'key', item.xpath(xpKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'fee_structure', item.xpath(xpFeeStructure, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'gender_requirements', item.xpath(xpGenderRequirements, namespaces = self.nsmap), 'text')
            
            existence_test_and_add(self, 'area_flexibility', item.xpath(xpAreaFlexibility, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'service_not_always_available', item.xpath(xpServiceNotAlwaysAvailable, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'service_group_key', item.xpath(xpServiceGroupKey, namespaces = self.nsmap), 'attribute_text')
            
            existence_test_and_add(self, 'service_id', item.xpath(xpServiceID, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'site_id', item.xpath(xpSiteID, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'geographic_code', item.xpath(xpGeographicCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'geographic_code_date_collected', item.xpath(xpGeographicCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'geographic_code_date_effective', item.xpath(xpGeographicCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'geographic_code_data_collection_stage', item.xpath(xpGeographicCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'housing_type', item.xpath(xpHousingType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'housing_type_date_collected', item.xpath(xpHousingTypeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'housing_type_date_effective', item.xpath(xpHousingTypeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'housing_type_data_collection_stage', item.xpath(xpHousingTypeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'principal', item.xpath(xpPrincipal, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'site_service_effective_period_start_date', item.xpath(xpSiteServiceEffectivePeriodStartDate, namespaces = self.nsmap), 'element_date')
            existence_test_and_add(self, 'site_service_effective_period_end_date', item.xpath(xpSiteServiceEffectivePeriodEndDate, namespaces = self.nsmap), 'element_date')
            existence_test_and_add(self, 'site_service_recorded_date', item.xpath(xpSiteServiceRecordedDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'site_service_type', item.xpath(xpSiteServiceType, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            except: pass
            # SBB20100916 missing
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.SiteService)

            ''' Parse sub-tables '''
            parse_seasonal(self, item)
            parse_residency_requirements(self, item)
            parse_pit_count_set(self, item)
            parse_other_requirements(self, item)
            parse_languages(self, item)
            parse_time_open(self, item)            
            parse_inventory(self, item)
            parse_income_requirements(self, item)
            parse_hmis_asset(self, item)
            parse_geographic_area_served(self, item)
            parse_documents_required(self, item)
            parse_aid_requirements(self, item)
            parse_age_requirements(self, item)
            parse_application_process(self, item)
            parse_taxonomy(self, item)
            parse_family_requirements(self, item)
            parse_resource_info(self, item)
            
def parse_service_group(self, element):
    ''' Element paths '''
    xpServiceGroup = 'airs:ServiceGroup'
    xpAirsKey = 'airs:Key'
    xpAirsName = 'airs:Name'
    xpAirsAgencyKey = 'airs:ProgramName'

    itemElements = element.xpath(xpServiceGroup, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'key', item.xpath(xpAirsKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'name', item.xpath(xpAirsName, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'program_name', item.xpath(xpAirsAgencyKey, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ServiceGroup)

            ''' Parse sub-tables '''

def parse_license_accreditation(self, element):
    ''' Element paths '''
    xpLicenseAccreditation = 'airs:LicenseAccreditation'
    xpLicense = 'airs:License'
    xpLicensedBy = 'airs:LicensedBy'

    itemElements = element.xpath(xpLicenseAccreditation, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'license', item.xpath(xpLicense, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'licensed_by', item.xpath(xpLicensedBy, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.LicenseAccreditation)

            ''' Parse sub-tables '''
                        

def parse_agency_service(self, element):
    ''' Element paths '''
    xpAgencyService = 'airs:AgencyService'
    xpAirsKey = 'airs:Key'
    xpAgencyKey = 'airs:AgencyKey'
    xpAgencyName = 'airs:Name'

    itemElements = element.xpath(xpAgencyService, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'key', item.xpath(xpAirsKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'agency_key', item.xpath(xpAgencyKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'name', item.xpath(xpAgencyName, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.AgencyService)

            ''' Parse sub-tables '''
                        

def parse_url(self, element):
    ''' Element paths '''
    xpUrl = 'airs:URL'
    xpAddress = 'airs:Address'
    xpNote = 'airs:Note'

    itemElements = element.xpath(xpUrl, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'address', item.xpath(xpAddress, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'note', item.xpath(xpNote, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Url)

            ''' Parse sub-tables '''
                        

def parse_spatial_location(self, element):
    ''' Element paths '''
    xpSpatialLocation = 'airs:SpatialLocation'
    xpDescription = 'airs:Description'
    xpDatum = 'airs:Datum'
    xpLatitude = 'airs:Latitude'
    xpLongitude = 'airs:Longitude'

    itemElements = element.xpath(xpSpatialLocation, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'datum', item.xpath(xpDatum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'latitude', item.xpath(xpLatitude, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'longitude', item.xpath(xpLongitude, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try:existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.SpatialLocation)

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

    itemElements = element.xpath(xpOtherAddress, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'pre_address_line', item.xpath(xpPreAddressLine, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'line_1', item.xpath(xpLine1, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'line_2', item.xpath(xpLine2, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'city', item.xpath(xpCity, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'county', item.xpath(xpCounty, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'state', item.xpath(xpState, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'zip_code', item.xpath(xpZipCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'country', item.xpath(xpCountry, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'reason_withheld', item.xpath(xpReasonWithheld, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'confidential', item.xpath(xpConfidential, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            # SBB20100916 missing
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.OtherAddress)

            ''' Parse sub-tables '''
                        

def parse_cross_street(self, element):
    ''' Element paths '''
    xpCrossStreet = 'airs:CrossStreet'

    itemElements = element.xpath(xpCrossStreet, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'cross_street', item, 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            # SBB20100916 missing..
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.CrossStreet)

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

    itemElements = element.xpath(xpAgencyLocation, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'key', item.xpath(xpKey, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'name', item.xpath(xpName, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'site_description', item.xpath(xpSiteDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_pre_address_line', item.xpath(xpPhysicalAddressPreAddressLine, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_line_1', item.xpath(xpPhysicalAddressLine1, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_line_2', item.xpath(xpPhysicalAddressLine2, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_city', item.xpath(xpPhysicalAddressCity, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_state', item.xpath(xpPhysicalAddressState, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_zip_code', item.xpath(xpPhysicalAddressZipCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_country', item.xpath(xpPhysicalAddressCountry, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_reason_withheld', item.xpath(xpPhysicalAddressReasonWithheld, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_confidential', item.xpath(xpPhysicalAddressConfidential, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_address_description', item.xpath(xpPhysicalAddressDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_pre_address_line', item.xpath(xpMailingAddressPreAddressLine, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_line_1', item.xpath(xpMailingAddressLine1, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_line_2', item.xpath(xpMailingAddressLine2, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_city', item.xpath(xpMailingAddressCity, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_state', item.xpath(xpMailingAddressState, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_zip_code', item.xpath(xpMailingAddressZipCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_country', item.xpath(xpMailingAddressCountry, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_reason_withheld', item.xpath(xpMailingAddressReasonWithheld, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mailing_address_confidential', item.xpath(xpMailingAddressConfidential, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'mailing_address_description', item.xpath(xpMailingAddressDescription, namespaces = self.nsmap), 'attribute_text')    
            existence_test_and_add(self, 'no_physical_address_description', item.xpath(xpNoPhysicalAddressDescription, namespaces = self.nsmap), 'text')      
            existence_test_and_add(self, 'no_physical_address_explanation', item.xpath(xpNoPhysicalAddressExplanation, namespaces = self.nsmap), 'text') 
            existence_test_and_add(self, 'disabilities_access', item.xpath(xpDisabilitiesAccess, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'physical_location_description', item.xpath(xpPhysicalLocationDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'bus_service_access', item.xpath(xpBusServiceAccess, namespaces = self.nsmap), 'text')
            
            # attriubtes
            existence_test_and_add(self, 'public_access_to_transportation', item.xpath(xpPublicAccessToTransportation, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'year_inc', item.xpath(xpYearInc, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'annual_budget_total', item.xpath(xpAnnualBudgetTotal, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'legal_status', item.xpath(xpLegalStatus, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'exclude_from_website', item.xpath(xpExcludeFromWebsite, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'exclude_from_directory', item.xpath(xpExcludeFromDirectory, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.AgencyLocation)

            ''' Parse sub-tables '''
            parse_aka(self, item)
            
            # need to set this up, off agency_location this doesn't exist yet but is needed to parse other_address
            self.site_index_id = None
            
            parse_other_address(self, item)
            parse_cross_street(self, item)
            parse_phone(self, item)
            parse_url(self, item)
            parse_email(self, item)      
            parse_contact(self, item)
            parse_time_open(self, item)
            parse_languages(self, item)
            
            #not working yet
            #parse_site_service(item, 'airs')
            parse_spatial_location(self, item)
            
            # reset the contacts index (used inside agency location but should not flow back up to Agency)
            self.contact_index_id = None
            
            
    
def parse_aka(self, element):
    ''' Element paths '''
    xpAka = 'airs:AKA'
    xpName = 'airs:Name'
    xpConfidential = 'airs:Confidential'
    xpDescription = 'airs:Description'

    itemElements = element.xpath(xpAka, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'name', item.xpath(xpName, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'confidential', item.xpath(xpConfidential, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            except: pass
            # SBB20100914 new...
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Aka)

            ''' Parse sub-tables '''
                        

def parse_seasonal(self, element):
    ''' Element paths '''
    xpSeasonal = 'airs:Seasonal'
    xpDescription = 'airs:Description'
    xpStartDate = 'airs:StartDate'
    xpEndDate = 'airs:EndDate'

    itemElements = element.xpath(xpSeasonal, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'start_date', item.xpath(xpStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'end_date', item.xpath(xpEndDate, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Seasonal)

            ''' Parse sub-tables '''
                        

def parse_residency_requirements(self, element):
    ''' Element paths '''
    xpResidencyRequirements = 'airs:ResidencyRequirements'

    itemElements = element.xpath(xpResidencyRequirements, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'residency_requirements', item.xpath(xpResidencyRequirements, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ResidencyRequirements)

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
    
    itemElements = element.xpath(xpPitCountSet, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'pit_count_set_id_id_num', item.xpath(xpPitCountSetIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pit_count_set_id_id_str', item.xpath(xpPitCountSetIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pit_count_set_id_delete_occurred_date', item.xpath(xpPitCountSetIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'pit_count_set_id_delete_effective_date', item.xpath(xpPitCountSetIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'pit_count_set_id_delete', item.xpath(xpPitCountSetIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'hud_waiver_received', item.xpath(xpHUDWaiverReceived, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hud_waiver_date', item.xpath(xpHUDWaiverDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hud_waiver_effective_period_start_date', item.xpath(xpHUDWaiverEffectivePeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hud_waiver_effective_period_end_date', item.xpath(xpHUDWaiverEffectivePeriodEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'last_pit_sheltered_count_date', item.xpath(xpLastPITShelteredCountDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'last_pit_unsheltered_count_date', item.xpath(xpLastPITUnshelteredCountDate, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.PitCountSet)

            ''' Parse sub-tables '''
            parse_pit_counts(self, item)            

def parse_pit_counts(self, element):
    ''' Element paths '''
    xpPITCountValue = 'hmis:PITCountValue'
    XpPITCountEffectivePeriodStartDate = 'hmis:PITCountEffectivePeriod/hmis:StartDate'
    XpPITCountEffectivePeriodEndDate = 'hmis:PITCountEffectivePeriod/hmis:EndDate'
    xpPITCountRecordedDate = 'hmis:PITCountRecordedDate'
    xpPITHouseholdType = 'hmis:pITHouseholdType'
    
    itemElements = element.xpath(xpPITCountValue, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'pit_count_value', item.xpath(xpPITCountValue, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pit_count_effective_period_start_date', item.xpath(XpPITCountEffectivePeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pit_count_effective_period_end_date', item.xpath(XpPITCountEffectivePeriodEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pit_count_recorded_date', item.xpath(xpPITCountRecordedDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pit_count_household_type', item.xpath(xpPITHouseholdType, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'pit_count_set_index_id', self.pit_count_set_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.PitCounts)

            ''' Parse sub-tables '''
                        

def parse_other_requirements(self, element):
    ''' Element paths '''
    xpOtherRequirements = 'airs:OtherRequirements'

    itemElements = element.xpath(xpOtherRequirements, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'other_requirements', item.xpath(xpOtherRequirements, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.OtherRequirements)

            ''' Parse sub-tables '''
                        

def parse_languages(self, element):
    ''' Element paths '''
    xpLanguages = 'airs:Languages'
    xpName = 'airs:Name'
    xpNotes = 'airs:Notes'

    itemElements = element.xpath(xpLanguages, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            # SBB20100915 Don't use xpath to retreive values, since there are many languages under the languages element.  Need all so using getchildren()
            # These are Lists of values, need to iterate over them to stuff into the DB
            valsName = item.xpath(xpName, namespaces = self.nsmap)
            valsNotes = item.xpath(xpNotes, namespaces = self.nsmap)
            
            # map over them together
            for name, note in map(None, valsName, valsNotes):

                existence_test_and_add(self, 'name', name,'text')
                # test for missing
                if not note is None:
                    existence_test_and_add(self, 'notes', note, 'text')

                ''' Foreign Keys '''
                try: existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
                except: pass
                try: existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
                except: pass
                try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                shred(self, self.parse_dict, dbobjects.Languages)
    
                ''' Parse sub-tables '''
                parse_time_open(self, item)            

def parse_time_open(self, element):
    ''' Unique method that has 2nd loop for each day of week '''

    ''' Element paths '''
    xpTimeOpen = 'airs:TimeOpen'
    xpNotes = 'airs:Notes'
    
    itemElements = element.xpath(xpTimeOpen, namespaces={'airs': self.airs_namespace})
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}

            existence_test_and_add(self, 'notes', item.xpath(xpNotes, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'languages_index_id', self.languages_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.TimeOpen)

            ''' parse each specific day of week '''
            weekDays = ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday')
            for day in weekDays:
                parse_time_open_day(self, item, day)

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
            existence_test_and_add(self, 'from', item.xpath(xpFrom, namespaces={'airs': self.airs_namespace}), 'text')
            existence_test_and_add(self, 'to', item.xpath(xpTo, namespaces={'airs': self.airs_namespace}), 'text')
            existence_test_and_add(self, 'day_of_week', day, 'no_handling')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'time_open_index_id', self.time_open_index_id, 'no_handling')

            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.TimeOpenDays)

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

    itemElements = element.xpath(xpInventory, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'inventory_delete_occurred_date', item.xpath(xpInventoryDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'inventory_delete_effective_date', item.xpath(xpInventoryDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'inventory_delete', item.xpath(xpInventoryDelete, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hmis_participation_period_start_date', item.xpath(xpHMISParticipationPeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hmis_participation_period_end_date', item.xpath(xpHMISParticipationPeriodEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'inventory_id_id_num', item.xpath(xpInventoryIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'inventory_id_id_str', item.xpath(xpInventoryIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'bed_inventory', item.xpath(xpBedInventory, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'bed_availability', item.xpath(xpBedAvailability, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'bed_type', item.xpath(xpBedType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'bed_individual_family_type', item.xpath(xpBedIndividualFamilyType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'chronic_homeless_bed', item.xpath(xpChronicHomelessBed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'domestic_violence_shelter_bed', item.xpath(xpDomesticViolenceShelterBed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'household_type', item.xpath(xpHouseholdType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hmis_participating_beds', item.xpath(xpHMISParticipatingBeds, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'inventory_effective_period_start_date', item.xpath(xpInventoryEffectivePeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'inventory_effective_period_end_date', item.xpath(xpInventoryEffectivePeriodEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'inventory_recorded_date', item.xpath(xpInventoryRecordedDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'unit_inventory', item.xpath(xpUnitInventory, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'service_index_id', self.service_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Inventory)

            ''' Parse sub-tables '''
                        

def parse_income_requirements(self, element):
    ''' Element paths '''
    xpIncomeRequirements = 'airs:IncomeRequirements'

    itemElements = element.xpath(xpIncomeRequirements, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'income_requirements', item.xpath(xpIncomeRequirements, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.IncomeRequirements)

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

    itemElements = element.xpath(xpHMISAsset, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'asset_id_id_num', item.xpath(xpAssetIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_id_id_str', item.xpath(xpAssetIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_id_delete', item.xpath(xpAssetIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'asset_id_delete_occurred_date', item.xpath(xpAssetIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'asset_id_delete_effective_date', item.xpath(xpAssetIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'asset_count', item.xpath(xpAssetCount, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_count_bed_availability', item.xpath(xpAssetCountBedAvailability, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_count_bed_type', item.xpath(xpAssetCountBedType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_count_bed_individual_family_type', item.xpath(xpAssetCountBedIndividualFamilyType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_count_chronic_homeless_bed', item.xpath(xpAssetCountChronicHomelessBed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_count_domestic_violence_shelter_bed', item.xpath(xpAssetCountDomesticViolenceShelterBed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_count_household_type', item.xpath(xpAssetCountHouseholdType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_type', item.xpath(xpAssetType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_effective_period_start_date', item.xpath(xpAssetEffectivePeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_effective_period_end_date', item.xpath(xpAssetEffectivePeriodEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'asset_recorded_date', item.xpath(xpAssetRecordedDate, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.HmisAsset)

            ''' Parse sub-tables '''
            parse_assignment(self, item)            

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

    itemElements = element.xpath(xpAssignment, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'assignment_id_id_num', item.xpath(xpAssignmentIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'assignment_id_id_str', item.xpath(xpAssignmentIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'assignment_id_delete', item.xpath(xpAssignmentIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'assignment_id_delete_occurred_date', item.xpath(xpAssignmentIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'assignment_id_delete_effective_date', item.xpath(xpAssignmentIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_id_id_num', item.xpath(xpPersonIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_id_id_str', item.xpath(xpPersonIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'household_id_id_num', item.xpath(xpHouseholdIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'household_id_id_str', item.xpath(xpHouseholdIDIDStr, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'hmis_asset_index_id', self.hmis_asset_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Assignment)

            ''' Parse sub-tables '''
            parse_assignment_period(self, item)            

def parse_assignment_period(self, element):
    ''' Element paths '''
    xpAssignmentPeriod = 'hmis:AssignmentPeriod'
    xpAssignmentPeriodStartDate = 'hmis:StartDate'
    xpAssignmentPeriodEndDate = 'hmis:EndDate'
    
    itemElements = element.xpath(xpAssignmentPeriod, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'assignment_period_start_date', item.xpath(xpAssignmentPeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'assignment_period_end_date', item.xpath(xpAssignmentPeriodEndDate, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'assignment_index_id', self.assignment_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.AssignmentPeriod)

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

    itemElements = element.xpath(xpGeographicAreaServed, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'zipcode', item.xpath(xpZipCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'census_track', item.xpath(xpCensusTrack, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'city', item.xpath(xpCity, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'county', item.xpath(xpCounty, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'state', item.xpath(xpState, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'country', item.xpath(xpCountry, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.GeographicAreaServed)

            ''' Parse sub-tables '''
                        

def parse_documents_required(self, element):
    ''' Element paths '''
    xpDocumentsRequired = 'airs:DocumentsRequired'
    xpDescription = 'airs:Description'

    itemElements = element.xpath(xpDocumentsRequired, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'documents_required', item.xpath(xpDocumentsRequired, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.DocumentsRequired)

            ''' Parse sub-tables '''
                        

def parse_aid_requirements(self, element):
    ''' Element paths '''
    xpAidRequirements = 'airs:AidRequirements'

    itemElements = element.xpath(xpAidRequirements, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'aid_requirements', item.xpath(xpAidRequirements, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.AidRequirements)

            ''' Parse sub-tables '''
                        

def parse_age_requirements(self, element):
    ''' Element paths '''
    xpAgeRequirements = 'airs:AgeRequirements'
    xpGender = '@airs:Gender'
    xpMinimumAge = '@airs:MinimumAge'
    xpMaximumAge = '@airs:MaximumAge'

    itemElements = element.xpath(xpAgeRequirements, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'gender', item.xpath(xpGender, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'minimum_age', item.xpath(xpMinimumAge, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'maximum_age', item.xpath(xpMaximumAge, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.AgeRequirements)

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

    itemElements = element.xpath(xpSiteServiceParticipation, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'site_service_participation_idid_num', item.xpath(    xpSiteServiceParticipationIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'site_service_participation_idid_str', item.xpath(xpSiteServiceParticipationIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'site_service_participation_id_delete_occurred_date', item.xpath(xpSiteServiceParticipationIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'site_service_participation_id_delete_effective_date', item.xpath(xpSiteServiceParticipationIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'site_service_participation_id_delete', item.xpath(xpSiteServiceParticipationIDDelete, namespaces = self.nsmap), 'attribute_text')           
            existence_test_and_add(self, 'site_service_idid_num', item.xpath(xpSiteServiceID, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'household_idid_num', item.xpath(xpHouseholdIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'household_idid_str', item.xpath(xpHouseholdIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'participation_dates_start_date', item.xpath(xpStartDate, namespaces = self.nsmap), 'element_date')
            existence_test_and_add(self, 'participation_dates_end_date', item.xpath(xpEndDate, namespaces = self.nsmap), 'element_date')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.SiteServiceParticipation)

            ''' Parse sub-tables '''
            parse_reasons_for_leaving(self, item)  
            parse_need(self, item)          
            parse_service_event(self, item)
            parse_person_historical(self, item)

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

    itemElements = element.xpath(xpReasonsForLeaving, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'reason_for_leaving_id_id_num', item.xpath(xpReasonsForLeavingIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'reason_for_leaving_id_id_str', item.xpath(xpReasonsForLeavingIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'reason_for_leaving_id_delete', item.xpath(xpReasonsForLeavingIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'reason_for_leaving_id_delete_occurred_date', item.xpath(xpReasonsForLeavingIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'reason_for_leaving_id_delete_effective_date', item.xpath(xpReasonsForLeavingIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'reason_for_leaving', item.xpath(xpReasonsForLeaving, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'reason_for_leaving_date_collected', item.xpath(xpReasonsForLeavingDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'reason_for_leaving_date_effective', item.xpath(xpReasonsForLeavingDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'reason_for_leaving_data_collection_stage', item.xpath(xpReasonsForLeavingDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'reason_for_leaving_other', item.xpath(xpReasonsForLeavingOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'reason_for_leaving_other_date_collected', item.xpath(xpReasonsForLeavingOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'reason_for_leaving_other_date_effective', item.xpath(xpReasonsForLeavingOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'reason_for_leaving_other_data_collection_stage', item.xpath(xpReasonsForLeavingOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ReasonsForLeaving)

            ''' Parse sub-tables '''
                        

def parse_application_process(self, element):
    ''' Element paths '''
    xpApplicationProcess = 'airs:ApplicationProcess'
    xpStep = 'airs:Step'
    xpDescription = 'airs:Description'

    itemElements = element.xpath(xpApplicationProcess, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'step', item.xpath(xpStep, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ApplicationProcess)

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

    itemElements = element.xpath(xpNeed, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'need_idid_num', item.xpath(xpNeedIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'need_idid_str', item.xpath(xpNeedIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'need_id_delete_occurred_date', item.xpath(xpNeedIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'need_id_delete_delete_effective_date', item.xpath(xpNeedIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'need_id_delete', item.xpath(xpNeedIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'site_service_idid_num', item.xpath(xpSiteServiceID, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'need_effective_period_start_date', item.xpath(xpNeedEffectivePeriodStartDate, namespaces = self.nsmap), 'element_date')
            existence_test_and_add(self, 'need_effective_period_end_date', item.xpath(xpNeedEffectivePeriodEndDate, namespaces = self.nsmap), 'element_date')
            existence_test_and_add(self, 'need_recorded_date', item.xpath(xpNeedRecordedDate, namespaces = self.nsmap), 'element_date')
            existence_test_and_add(self, 'need_status', item.xpath(xpNeedStatus, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Need)

            ''' Parse sub-tables '''
            parse_taxonomy(self, item)
            parse_service_event(self, item)

def parse_taxonomy(self, element):
    ''' Element paths '''
    xpTaxonomy = 'airs:Taxonomy'
    xpCode = 'airs:Code'

    itemElements = element.xpath(xpTaxonomy, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            # SBB20100916 Again, this returns  a list of items which must be processed into the DB as rows
            #existence_test_and_add(self, 'code', item.xpath(xpCode, namespaces = self.nsmap), 'text')
            
            # These are Lists of values, need to iterate over them to stuff into the DB
            valsName = item.xpath(xpCode, namespaces = self.nsmap)
            
            # map over them together
            for code in valsName:
                existence_test_and_add(self, 'code', code, 'text')

                ''' Foreign Keys '''
                try: existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
                except: pass
                try: existence_test_and_add(self, 'need_index_id', self.need_index_id, 'no_handling')
                except: pass
            
                ''' Shred to database '''
                shred(self, self.parse_dict, dbobjects.Taxonomy)

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
    
    itemElements = element.xpath(xpServiceEvent, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'service_event_idid_num', item.xpath(xpServiceEventIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_event_idid_str', item.xpath(xpServiceEventIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_event_id_delete_occurred_date', item.xpath(xpServiceEventIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'service_event_id_delete_effective_date', item.xpath(xpServiceEventIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'service_event_id_delete', item.xpath(xpServiceEventIDDelete, namespaces = self.nsmap), 'attribute_text')      
            existence_test_and_add(self, 'site_service_id', item.xpath(xpSiteServiceID, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'household_idid_num', item.xpath(xpHouseholdIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'household_idid_str', item.xpath(xpHouseholdIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'is_referral', item.xpath(xpIsReferral, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'quantity_of_service', item.xpath(xpQuantityOfServiceEvent, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'quantity_of_service_measure', item.xpath(xpQuantityOfServiceEventUnit, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_airs_code', item.xpath(xpServiceEventAIRSCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_period_start_date', item.xpath(xpServiceEventEffectivePeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_period_end_date', item.xpath(xpServiceEventEffectivePeriodEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_event_provision_date', item.xpath(xpServiceEventProvisionDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_event_recorded_date', item.xpath(xpServiceEventRecordedDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_event_ind_fam', item.xpath(xpServiceEventIndFam, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hmis_service_event_code_type_of_service', item.xpath(xpHMISServiceEventCodeTypeOfService, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hmis_service_event_code_type_of_service_other', item.xpath(xpHMISServiceEventCodeTypeOfServiceOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hprp_financial_assistance_service_event_code', item.xpath(xpHPRPFinancialAssistanceServiceEventCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hprp_relocation_stabilization_service_event_code', item.xpath(xpHPRPRelocationStabilizationServiceEventCode, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'need_index_id', self.need_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ServiceEvent)

            ''' Parse sub-tables '''
            parse_service_event_notes(self, item)     
            parse_funding_source(self, item)       

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

    itemElements = element.xpath(xpServiceEventNotes, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'note_id_id_num', item.xpath(xpNoteIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'note_id_id_str', item.xpath(xpNoteIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'note_delete_occurred_date', item.xpath(xpNoteIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'note_delete_effective_date', item.xpath(xpNoteIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'note_delete', item.xpath(xpNoteIDDelete, namespaces = self.nsmap), 'attribute_text')          
            existence_test_and_add(self, 'note_text', item.xpath(xpNoteText, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'note_text_date_collected', item.xpath(xpNoteTextDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'note_text_date_effective', item.xpath(xpNoteTextDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'note_text_data_collection_stage', item.xpath(xpNoteTextDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'service_event_index_id', self.service_event_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ServiceEventNotes)

            ''' Parse sub-tables '''
                        

def parse_family_requirements(self, element):
    ''' Element paths '''
    xpFamilyRequirements = 'airs:FamilyRequirements'

    itemElements = element.xpath(xpFamilyRequirements, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'family_requirements', item.xpath(xpFamilyRequirements, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.FamilyRequirements)

            ''' Parse sub-tables '''
                        

def parse_person_historical(self, element):
    ''' Element paths '''
    xpPersonHistorical = 'hmis:PersonHistorical'        
    xpPersonHistoricalIDIDNum = 'hmis:PersonHistoricalID/hmis:IDNum'
    xpPersonHistoricalIDIDStr = 'hmis:PersonHistoricalID/hmis:IDStr'
    xpPersonHistoricalIDDelete = 'hmis:PersonHistoricalID/@hmis:delete'
    xpPersonHistoricalIDDeleteEffective = 'hmis:PersonHistoricalID/@hmis:deleteEffective'
    xpPersonHistoricalIDDeleteOccurredDate = 'hmis:PersonHistoricalID/@hmis:deleteOccurredDate'
    xpSiteServiceID = 'hmis:SiteServiceID'

    itemElements = element.xpath(xpPersonHistorical, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'person_historical_id_id_num', item.xpath(xpPersonHistoricalIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_historical_id_id_str', item.xpath(xpPersonHistoricalIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_historical_id_delete', item.xpath(xpPersonHistoricalIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'person_historical_id_delete_effective_date', item.xpath(xpPersonHistoricalIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_historical_id_delete_occurred_date', item.xpath(xpPersonHistoricalIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'site_service_id', item.xpath(xpSiteServiceID, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.PersonHistorical)

            ''' Parse sub-tables '''
            parse_housing_status(self, item)   
            parse_veteran(self, item)
            parse_vocational_training(self, item)         
            parse_substance_abuse_problem(self, item)         
            parse_pregnancy(self, item)         
            parse_prior_residence(self, item)         
            parse_physical_disability(self, item)         
            parse_non_cash_benefits(self, item)         
            parse_non_cash_benefits_last_30_days(self, item)         
            parse_mental_health_problem(self, item)         
            parse_length_of_stay_at_prior_residence(self, item)         
            parse_income_total_monthly(self, item)         
            parse_hud_chronic_homeless(self, item)         
            parse_income_last_30_days(self, item)         
            parse_highest_school_level(self, item)         
            parse_hiv_aids_status(self, item)         
            parse_health_status(self, item)         
            parse_engaged_date(self, item)         
            parse_employment(self, item)         
            parse_domestic_violence(self, item)         
            parse_disabling_condition(self, item)         
            parse_developmental_disability(self, item)         
            parse_destinations(self, item)         
            parse_degree(self, item)         
            parse_currently_in_school(self, item)         
            parse_contact_made(self, item)         
            parse_child_enrollment_status(self, item)         
            parse_chronic_health_condition(self, item) 
            parse_income_and_sources(self, item)
            parse_hud_homeless_episodes(self, item)
            parse_person_address(self, item)
            parse_email(self, item)                              
            parse_phone(self, item)      

def parse_housing_status(self, element):
    ''' Element paths '''
    xpHousingStatus = 'hmis:HousingStatus'
    xpHousingStatusDateCollected = '@hmis:dateCollected'
    xpHousingStatusDateEffective = '@hmis:dateEffective'
    xpHousingStatusDataCollectionStage = '@hmis:dataCollectionStage'        

    itemElements = element.xpath(xpHousingStatus, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'housing_status', item, 'text')
            existence_test_and_add(self, 'housing_status_date_collected', item.xpath(xpHousingStatusDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'housing_status_date_effective', item.xpath(xpHousingStatusDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'housing_status_data_collection_stage', item.xpath(xpHousingStatusDataCollectionStage, namespaces = self.nsmap), 'attribute_text')      

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.HousingStatus)

            ''' Parse sub-tables '''

def parse_veteran(self, element):
    ''' Unique method -- loops all veteran elements and launches sub parsers '''

    ''' Element paths '''
    xpVeteran = 'hmis:Veteran'
    itemElements = element.xpath(xpVeteran, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}

            parse_veteran_military_branches(self, item)
            parse_veteran_served_in_war_zone(self, item)         
            parse_veteran_service_era(self, item)         
            parse_veteran_veteran_status(self, item)         
            parse_veteran_warzones_served(self, item)                         
    
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

    itemElements = element.xpath(xpMilitaryBranches, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'military_branch_id_id_id_num', item.xpath(xpMilitaryBranchIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'military_branch_id_id_id_str', item.xpath(xpMilitaryBranchIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'military_branch_id_id_delete_occurred_date', item.xpath(xpMilitaryBranchIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'military_branch_id_id_delete_effective_date', item.xpath(xpMilitaryBranchIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'military_branch_id_id_delete', item.xpath(xpMilitaryBranchIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'discharge_status', item.xpath(xpDischargeStatus, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'discharge_status_date_collected', item.xpath(xpDischargeStatusDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'discharge_status_date_effective', item.xpath(xpDischargeStatusDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'discharge_status_data_collection_stage', item.xpath(xpDischargeStatusDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'discharge_status_other', item.xpath(xpDischargeStatusOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'discharge_status_other_date_collected', item.xpath(xpDischargeStatusOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'discharge_status_other_date_effective', item.xpath(xpDischargeStatusOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'discharge_status_other_data_collection_stage', item.xpath(xpDischargeStatusOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'military_branch', item.xpath(xpMilitaryBranch, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'military_branch_date_collected', item.xpath(xpMilitaryBranchDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'military_branch_date_effective', item.xpath(xpMilitaryBranchDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'military_branch_data_collection_stage', item.xpath(xpMilitaryBranchDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'military_branch_other', item.xpath(xpMilitaryBranchOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'military_branch_other_date_collected', item.xpath(xpMilitaryBranchOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'military_branch_other_date_effective', item.xpath(xpMilitaryBranchOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'military_branch_other_data_collection_stage', item.xpath(xpMilitaryBranchOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.VeteranMilitaryBranches)

            ''' Parse sub-tables '''
                        

def parse_veteran_military_service_duration(self, element):
    ''' Element paths '''
    xpMilitaryServiceDuration = 'hmis:MilitaryServiceDuration'
    xpMilitaryServiceDurationDateCollected = 'hmis:MilitaryServiceDuration/@hmis:dateCollected'
    xpMilitaryServiceDurationDateEffective = 'hmis:MilitaryServiceDuration/@hmis:dateEffective'
    xpMilitaryServiceDurationDataCollectionStage = 'hmis:MilitaryServiceDuration/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpMilitaryServiceDuration, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'military_service_duration', item.xpath(xpMilitaryServiceDuration, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'military_service_duration_date_collected', item.xpath(xpMilitaryServiceDurationDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'military_service_duration_date_effective', item.xpath(xpMilitaryServiceDurationDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'military_service_duration_data_collection_stage', item.xpath(xpMilitaryServiceDurationDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.VeteranMilitaryServiceDuration)

            ''' Parse sub-tables '''
                        

def parse_veteran_served_in_war_zone(self, element):
    ''' Element paths '''
    xpVeteranServedInWarZone = 'hmis:MilitaryServiceDuration'
    xpVeteranServedInWarZoneDurationDateCollected = 'hmis:VeteranServedInWarZone/@hmis:dateCollected'
    xpVeteranServedInWarZoneDurationDateEffective = 'hmis:VeteranServedInWarZone/@hmis:dateEffective'
    xpVeteranServedInWarZoneDurationDataCollectionStage = 'hmis:VeteranServedInWarZone/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpVeteranServedInWarZone, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'served_in_war_zone', item.xpath(xpVeteranServedInWarZone, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'served_in_war_zone_date_collected', item.xpath(xpVeteranServedInWarZoneDurationDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'served_in_war_zone_date_effective', item.xpath(xpVeteranServedInWarZoneDurationDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'served_in_war_zone_data_collection_stage', item.xpath(xpVeteranServedInWarZoneDurationDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.VeteranServedInWarZone)

            ''' Parse sub-tables '''
                        

def parse_veteran_service_era(self, element):
    ''' Element paths '''
    xpServiceEra = 'hmis:ServiceEra'
    xpServiceEraDurationDateCollected = 'hmis:ServiceEra/@hmis:dateCollected'
    xpServiceEraDurationDateEffective = 'hmis:ServiceEra/@hmis:dateEffective'
    xpServiceEraDurationDataCollectionStage = 'hmis:ServiceEra/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpServiceEra, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'service_era', item.xpath(xpServiceEra, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'service_era_date_collected', item.xpath(xpServiceEraDurationDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'service_era_date_effective', item.xpath(xpServiceEraDurationDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'service_era_data_collection_stage', item.xpath(xpServiceEraDurationDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.VeteranServiceEra)

            ''' Parse sub-tables '''
                        

def parse_veteran_veteran_status(self, element):
    ''' Element paths '''
    xpVeteranStatus = 'hmis:VeteranStatus'
    xpVeteranStatusDurationDateCollected = './@hmis:dateCollected'
    xpVeteranStatusDurationDateEffective = './@hmis:dateEffective'
    xpVeteranStatusDurationDataCollectionStage = './@hmis:dataCollectionStage'

    itemElements = element.xpath(xpVeteranStatus, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'veteran_status', item, 'text')
            existence_test_and_add(self, 'veteran_status_date_collected', item.xpath(xpVeteranStatusDurationDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'veteran_status_date_effective', item.xpath(xpVeteranStatusDurationDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'veteran_status_data_collection_stage', item.xpath(xpVeteranStatusDurationDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.VeteranVeteranStatus)

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

    itemElements = element.xpath(xpVeteranWarZonesServed, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'war_zone_id_id_id_num', item.xpath(xpWarZoneIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'war_zone_id_id_id_str', item.xpath(xpWarZoneIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'war_zone_id_id_delete_occurred_date', item.xpath(xpWarZoneIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'war_zone_id_id_delete_effective_date', item.xpath(xpWarZoneIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'war_zone_id_id_delete', item.xpath(xpWarZoneIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'months_in_war_zone', item.xpath(xpMonthsInWarZone, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'months_in_war_zone_date_collected', item.xpath(xpMonthsInWarZoneDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'months_in_war_zone_date_effective', item.xpath(xpMonthsInWarZoneDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'months_in_war_zone_data_collection_stage', item.xpath(xpMonthsInWarZoneDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'received_fire', item.xpath(xpReceivedFire, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'received_fire_date_collected', item.xpath(xpReceivedFireDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'received_fire_date_effective', item.xpath(xpReceivedFireDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'received_fire_data_collection_stage', item.xpath(xpReceivedFireDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'war_zone', item.xpath(xpWarZone, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'war_zone_date_collected', item.xpath(xpWarZoneDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'war_zone_date_effective', item.xpath(xpWarZoneDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'war_zone_data_collection_stage', item.xpath(xpWarZoneDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'war_zone_other', item.xpath(xpWarZoneOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'war_zone_other_date_collected', item.xpath(xpWarZoneOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'war_zone_other_date_effective', item.xpath(xpWarZoneOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'war_zone_other_data_collection_stage', item.xpath(xpWarZoneOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.VeteranWarzonesServed)

            ''' Parse sub-tables '''
                        

def parse_vocational_training(self, element):
    ''' Element paths '''
    xpVocationalTraining = 'hmis:VocationalTraining'
    xpVocationalTrainingDateCollected = 'hmis:VocationalTraining/@hmis:dateCollected'
    xpVocationalTrainingDateEffective = 'hmis:VocationalTraining/@hmis:dateEffective'
    xpVocationalTrainingDataCollectionStage = 'hmis:VocationalTraining/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpVocationalTraining, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'vocational_training', item.xpath(xpVocationalTraining, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'vocational_training_date_collected', item.xpath(xpVocationalTrainingDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'vocational_training_date_effective', item.xpath(xpVocationalTrainingDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'vocational_training_data_collection_stage', item.xpath(xpVocationalTrainingDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.VocationalTraining)

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

    itemElements = element.xpath(xpSubstanceAbuseProblem, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'has_substance_abuse_problem', item.xpath(xpHasSubstanceAbuseProblem, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'has_substance_abuse_problem_date_collected', item.xpath(xpHasSubstanceAbuseProblemDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_substance_abuse_problem_date_effective', item.xpath(xpHasSubstanceAbuseProblemDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_substance_abuse_problem_data_collection_stage', item.xpath(xpHasSubstanceAbuseProblemDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'substance_abuse_indefinite', item.xpath(xpSubstanceAbuseIndefinite, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'substance_abuse_indefinite_date_collected', item.xpath(xpSubstanceAbuseIndefiniteDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'substance_abuse_indefinite_date_effective', item.xpath(xpSubstanceAbuseIndefiniteDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'substance_abuse_indefinite_data_collection_stage', item.xpath(xpSubstanceAbuseIndefiniteDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'receive_substance_abuse_services', item.xpath(xpReceiveSubstanceAbuseServices, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receive_substance_abuse_services_date_collected', item.xpath(xpReceiveSubstanceAbuseServicesDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_substance_abuse_services_date_effective', item.xpath(xpReceiveSubstanceAbuseServicesDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_substance_abuse_services_data_collection_stage', item.xpath(xpReceiveSubstanceAbuseServicesDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.SubstanceAbuseProblem)

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

    itemElements = element.xpath(xpPregnancy, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'pregnancy_id_id_id_num', item.xpath(xpPregnancyIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pregnancy_id_id_id_str', item.xpath(xpPregnancyIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pregnancy_id_id_delete_occurred_date', item.xpath(xpPregnancyIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'pregnancy_id_id_delete_effective_date', item.xpath(xpPregnancyIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'pregnancy_id_id_delete', item.xpath(xpPregnancyIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'pregnancy_status', item.xpath(xpPregnancyStatus, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pregnancy_status_date_collected', item.xpath(xpPregnancyStatusDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'pregnancy_status_date_effective', item.xpath(xpPregnancyStatusDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'pregnancy_status_data_collection_stage', item.xpath(xpPregnancyStatusDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'due_date', item.xpath(xpDueDate, namespaces = self.nsmap), 'date')
            existence_test_and_add(self, 'due_date_date_collected', item.xpath(xpDueDateDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'due_date_data_collection_stage', item.xpath(xpDueDateDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Pregnancy)

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

    itemElements = element.xpath(xpPriorResidence, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'prior_residence_id_id_num', item.xpath(xpPriorResidenceIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'prior_residence_id_id_str', item.xpath(xpPriorResidenceIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'prior_residence_id_delete_occurred_date', item.xpath(xpPriorResidenceIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'prior_residence_id_delete_effective_date', item.xpath(xpPriorResidenceIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'prior_residence_id_delete', item.xpath(xpPriorResidenceIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'prior_residence_code', item.xpath(xpPriorResidenceCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'prior_residence_code_date_collected', item.xpath(xpPriorResidenceCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'prior_residence_code_date_effective', item.xpath(xpPriorResidenceCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'prior_residence_code_data_collection_stage', item.xpath(xpPriorResidenceCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'prior_residence_other', item.xpath(xpPriorResidenceOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'prior_residence_other_date_collected', item.xpath(xpPriorResidenceOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'prior_residence_other_date_effective', item.xpath(xpPriorResidenceOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'prior_residence_other_data_collection_stage', item.xpath(xpPriorResidenceOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.PriorResidence)

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

    itemElements = element.xpath(xpPhysicalDisability, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'has_physical_disability', item.xpath(xpHasPhysicalDisability, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'has_physical_disability_date_collected', item.xpath(xpHasPhysicalDisabilityDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_physical_disability_date_effective', item.xpath(xpHasPhysicalDisabilityDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_physical_disability_data_collection_stage', item.xpath(xpHasPhysicalDisabilityDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'receive_physical_disability_services', item.xpath(xpReceivePhysicalDisabilityServices, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receive_physical_disability_services_date_collected', item.xpath(xpReceivePhysicalDisabilityServicesDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_physical_disability_services_date_effective', item.xpath(xpReceivePhysicalDisabilityServicesDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_physical_disability_services_data_collection_stage', item.xpath(xpReceivePhysicalDisabilityServicesDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.PhysicalDisability)

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

    itemElements = element.xpath(xpNonCashBenefit, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'non_cash_benefit_id_id_id_num', item.xpath(xpNonCashBenefitIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'non_cash_benefit_id_id_id_str', item.xpath(xpNonCashBenefitIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'non_cash_benefit_id_id_delete_occurred_date', item.xpath(xpNonCashBenefitIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'non_cash_benefit_id_id_delete_effective_date', item.xpath(xpNonCashBenefitIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'non_cash_benefit_id_id_delete', item.xpath(xpNonCashBenefitIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'non_cash_source_code', item.xpath(xpNonCashSourceCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'non_cash_source_code_date_collected', item.xpath(xpNonCashSourceCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'non_cash_source_code_date_effective', item.xpath(xpNonCashSourceCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'non_cash_source_code_data_collection_stage', item.xpath(xpNonCashSourceCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'non_cash_source_other', item.xpath(xpNonCashSourceOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'non_cash_source_other_date_collected', item.xpath(xpNonCashSourceOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'non_cash_source_other_date_effective', item.xpath(xpNonCashSourceOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'non_cash_source_other_data_collection_stage', item.xpath(xpNonCashSourceOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'receiving_non_cash_source', item.xpath(xpReceivingNonCashSource, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receiving_non_cash_source_date_collected', item.xpath(xpReceivingNonCashSourceDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receiving_non_cash_source_date_effective', item.xpath(xpReceivingNonCashSourceDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receiving_non_cash_source_data_collection_stage', item.xpath(xpReceivingNonCashSourceDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.NonCashBenefits)

            ''' Parse sub-tables '''

def parse_non_cash_benefits_last_30_days(self, element):
    ''' Element paths '''
    xpNonCashBenefitsLast30Days = 'hmis:NonCashBenefitsLast30Days'
    xpNonCashBenefitsLast30DaysDateCollected = 'hmis:NonCashBenefitsLast30Days/@hmis:dateCollected'
    xpNonCashBenefitsLast30DaysDateEffective = 'hmis:NonCashBenefitsLast30Days/@hmis:dateEffective'
    xpNonCashBenefitsLast30DaysDataCollectionStage = 'hmis:NonCashBenefitsLast30Days/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpNonCashBenefitsLast30Days, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'income_last_30_days', item.xpath(xpNonCashBenefitsLast30Days, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'income_last_30_days_date_collected', item.xpath(xpNonCashBenefitsLast30DaysDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_last_30_days_date_effective', item.xpath(xpNonCashBenefitsLast30DaysDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_last_30_days_data_collection_stage', item.xpath(xpNonCashBenefitsLast30DaysDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.NonCashBenefitsLast30Days)

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

    itemElements = element.xpath(xpMentalHealthProblem, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'has_mental_health_problem', item.xpath(xpHasMentalHealthProblem, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'has_mental_health_problem_date_collected', item.xpath(xpHasMentalHealthProblemDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_mental_health_problem_date_effective', item.xpath(xpHasMentalHealthProblemDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_mental_health_problem_data_collection_stage', item.xpath(xpHasMentalHealthProblemDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'mental_health_indefinite', item.xpath(xpMentalHealthIndefinite, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'mental_health_indefinite_date_collected', item.xpath(xpMentalHealthIndefiniteDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'mental_health_indefinite_date_effective', item.xpath(xpMentalHealthIndefiniteDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'mental_health_indefinite_data_collection_stage', item.xpath(xpMentalHealthIndefiniteDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'receive_mental_health_services', item.xpath(xpReceiveMentalHealthServices, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receive_mental_health_services_date_collected', item.xpath(xpReceiveMentalHealthServicesDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_mental_health_services_date_effective', item.xpath(xpReceiveMentalHealthServicesDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_mental_health_services_data_collection_stage', item.xpath(xpReceiveMentalHealthServicesDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.MentalHealthProblem)

            ''' Parse sub-tables '''
                        

def parse_length_of_stay_at_prior_residence(self, element):
    ''' Element paths '''
    xpLengthOfStayAtPriorResidence = 'hmis:LengthOfStayAtPriorResidence'
    xpLengthOfStayAtPriorResidenceDateCollected = '@hmis:dateCollected'
    xpLengthOfStayAtPriorResidenceDateEffective = '@hmis:dateEffective'
    xpLengthOfStayAtPriorResidenceDataCollectionStage = '@hmis:dataCollectionStage'

    itemElements = element.xpath(xpLengthOfStayAtPriorResidence, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'length_of_stay_at_prior_residence', item, 'text')
            existence_test_and_add(self, 'length_of_stay_at_prior_residence_date_collected', item.xpath(xpLengthOfStayAtPriorResidenceDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'length_of_stay_at_prior_residence_date_effective', item.xpath(xpLengthOfStayAtPriorResidenceDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'length_of_stay_at_prior_residence_data_collection_stage', item.xpath(xpLengthOfStayAtPriorResidenceDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.LengthOfStayAtPriorResidence)

            ''' Parse sub-tables '''
                        

def parse_income_total_monthly(self, element):
    ''' Element paths '''
    xpIncomeTotalMonthly = 'hmis:IncomeTotalMonthly'
    xpIncomeTotalMonthlyDateCollected = 'hmis:IncomeTotalMonthly/@hmis:dateCollected'
    xpIncomeTotalMonthlyDateEffective = 'hmis:IncomeTotalMonthly/@hmis:dateEffective'
    xpIncomeTotalMonthlyDataCollectionStage = 'hmis:IncomeTotalMonthly/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpIncomeTotalMonthly, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'income_total_monthly', item.xpath(xpIncomeTotalMonthly, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'income_total_monthly_date_collected', item.xpath(xpIncomeTotalMonthlyDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_total_monthly_date_effective', item.xpath(xpIncomeTotalMonthlyDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_total_monthly_data_collection_stage', item.xpath(xpIncomeTotalMonthlyDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.IncomeTotalMonthly)

            ''' Parse sub-tables '''
                        

def parse_hud_chronic_homeless(self, element):
    ''' Element paths '''
    xpHUDChronicHomeless = 'hmis:HUDChronicHomeless'
    xpHUDChronicHomelessDateCollected = 'hmis:HUDChronicHomeless/@hmis:dateCollected'
    xpHUDChronicHomelessDateEffective = 'hmis:HUDChronicHomeless/@hmis:dateEffective'
    xpHUDChronicHomelessDataCollectionStage = 'hmis:HUDChronicHomeless/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpHUDChronicHomeless, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'hud_chronic_homeless', item.xpath(xpHUDChronicHomeless, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hud_chronic_homeless_date_collected', item.xpath(xpHUDChronicHomelessDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'hud_chronic_homeless_date_effective', item.xpath(xpHUDChronicHomelessDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'hud_chronic_homeless_data_collection_stage', item.xpath(xpHUDChronicHomelessDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.HudChronicHomeless)

            ''' Parse sub-tables '''
                        

def parse_income_last_30_days(self, element):
    ''' Element paths '''
    xpIncomeLast30Days = 'hmis:IncomeLast30Days'
    xpIncomeLast30DaysDateCollected = 'hmis:IncomeLast30Days/@hmis:dateCollected'
    xpIncomeLast30DaysDateEffective = 'hmis:IncomeLast30Days/@hmis:dateEffective'
    xpIncomeLast30DaysDataCollectionStage = 'hmis:IncomeLast30Days/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpIncomeLast30Days, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'income_last_30_days', item.xpath(xpIncomeLast30Days, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'income_last_30_days_date_collected', item.xpath(xpIncomeLast30DaysDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_last_30_days_date_effective', item.xpath(xpIncomeLast30DaysDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_last_30_days_data_collection_stage', item.xpath(xpIncomeLast30DaysDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.IncomeLast30Days)

            ''' Parse sub-tables '''
                        

def parse_highest_school_level(self, element):
    ''' Element paths '''
    xpHighestSchoolLevel = 'hmis:HighestSchoolLevel'
    xpHighestSchoolLevelDateCollected = 'hmis:HighestSchoolLevel/@hmis:dateCollected'
    xpHighestSchoolLevelDateEffective = 'hmis:HighestSchoolLevel/@hmis:dateEffective'
    xpHighestSchoolLevelDataCollectionStage = 'hmis:HighestSchoolLevel/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpHighestSchoolLevel, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'highest_school_level', item.xpath(xpHighestSchoolLevel, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'highest_school_level_date_collected', item.xpath(xpHighestSchoolLevelDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'highest_school_level_date_effective', item.xpath(xpHighestSchoolLevelDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'highest_school_level_data_collection_stage', item.xpath(xpHighestSchoolLevelDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.HighestSchoolLevel)

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

    itemElements = element.xpath(xpHIVAIDSStatus, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'has_hiv_aids', item.xpath(xpHasHIVAIDS, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'has_hiv_aids_date_collected', item.xpath(xpHasHIVAIDSDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_hiv_aids_date_effective', item.xpath(xpHasHIVAIDSDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_hiv_aids_data_collection_stage', item.xpath(xpHasHIVAIDSDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'receive_hiv_aids_services', item.xpath(xpReceiveHIVAIDSServices, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receive_hiv_aids_services_date_collected', item.xpath(xpReceiveHIVAIDSServicesDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_hiv_aids_services_date_effective', item.xpath(xpReceiveHIVAIDSServicesDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_hiv_aids_services_data_collection_stage', item.xpath(xpReceiveHIVAIDSServicesDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.HivAidsStatus)

            ''' Parse sub-tables '''
                        

def parse_health_status(self, element):
    ''' Element paths '''
    xpHealthStatus = 'hmis:HealthStatus'
    xpHealthStatusDateCollected = 'hmis:HealthStatus/@hmis:dateCollected'
    xpHealthStatusDateEffective = 'hmis:HealthStatus/@hmis:dateEffective'
    xpHealthStatusDataCollectionStage = 'hmis:HealthStatus/@hmis:dataCollectionStage'     

    itemElements = element.xpath(xpHealthStatus, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'health_status', item.xpath(xpHealthStatus, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'health_status_date_collected', item.xpath(xpHealthStatusDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'health_status_date_effective', item.xpath(xpHealthStatusDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'health_status_data_collection_stage', item.xpath(xpHealthStatusDataCollectionStage, namespaces = self.nsmap), 'attribute_text')   

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.HealthStatus)

            ''' Parse sub-tables '''
                        

def parse_engaged_date(self, element):
    ''' Element paths '''
    xpEngagedDate = 'hmis:EngagedDate'
    xpEngagedDateDateCollected = 'hmis:EngagedDate/@hmis:dateCollected'
    xpEngagedDateDateEffective = 'hmis:EngagedDate/@hmis:dateEffective'
    xpEngagedDateDataCollectionStage = 'hmis:EngagedDate/@hmis:dataCollectionStage'  

    itemElements = element.xpath(xpEngagedDate, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'engaged_date', item.xpath(xpEngagedDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'engaged_date_date_collected', item.xpath(xpEngagedDateDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'engaged_date_data_collection_stage', item.xpath(xpEngagedDateDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.EngagedDate)

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

    itemElements = element.xpath(xpEmployment, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'employment_id_id_id_num', item.xpath(xpEmploymentIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'employment_id_id_id_str', item.xpath(xpEmploymentIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'employment_id_id_delete_occurred_date', item.xpath(xpEmploymentIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'employment_id_id_delete_effective_date', item.xpath(xpEmploymentIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'employment_id_id_delete', item.xpath(xpEmploymentIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'currently_employed', item.xpath(xpCurrentlyEmployed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'currently_employed_date_collected', item.xpath(xpCurrentlyEmployedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'currently_employed_date_effective', item.xpath(xpCurrentlyEmployedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'currently_employed_data_collection_stage', item.xpath(xpCurrentlyEmployedDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'hours_worked_last_week', item.xpath(xpHoursWorkedLastWeek, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'hours_worked_last_week_date_collected', item.xpath(xpHoursWorkedLastWeekDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'hours_worked_last_week_date_effective', item.xpath(xpHoursWorkedLastWeekDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'hours_worked_last_week_data_collection_stage', item.xpath(xpHoursWorkedLastWeekDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'employment_tenure', item.xpath(xpEmploymentTenure, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'employment_tenure_date_collected', item.xpath(xpEmploymentTenureDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'employment_tenure_date_effective', item.xpath(xpEmploymentTenureDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'employment_tenure_data_collection_stage', item.xpath(xpEmploymentTenureDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'looking_for_work', item.xpath(xpLookingForWork, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'looking_for_work_date_collected', item.xpath(xpLookingForWorkDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'looking_for_work_date_effective', item.xpath(xpLookingForWorkDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'looking_for_work_data_collection_stage', item.xpath(xpLookingForWorkDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Employment)

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

    itemElements = element.xpath(xpDomesticViolence, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'domestic_violence_survivor', item.xpath(xpDomesticViolenceSurvivor, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'domestic_violence_survivor_date_collected', item.xpath(xpDomesticViolenceSurvivorDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'domestic_violence_survivor_date_effective', item.xpath(xpDomesticViolenceSurvivorDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'domestic_violence_survivor_data_collection_stage', item.xpath(xpDomesticViolenceSurvivorDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'dv_occurred', item.xpath(xpDVOccurred, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'dv_occurred_date_collected', item.xpath(xpDVOccurredDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'dv_occurred_date_effective', item.xpath(xpDVOccurredDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'dv_occurred_data_collection_stage', item.xpath(xpDVOccurredDataCollectionStage, namespaces = self.nsmap), 'attribute_text')     

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.DomesticViolence)

            ''' Parse sub-tables '''
                        

def parse_disabling_condition(self, element):
    ''' Element paths '''
    xpDisablingCondition = 'hmis:DisablingCondition'
    xpDisablingConditionDateCollected = 'hmis:DisablingCondition/@hmis:dateCollected'
    xpDisablingConditionDateEffective = 'hmis:DisablingCondition/@hmis:dateEffective'
    xpDisablingConditionDataCollectionStage = 'hmis:DisablingCondition/@hmis:dataCollectionStage'    

    itemElements = element.xpath(xpDisablingCondition, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'disabling_condition', item.xpath(xpDisablingCondition, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'disabling_condition_date_collected', item.xpath(xpDisablingConditionDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'disabling_condition_date_effective', item.xpath(xpDisablingConditionDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'disabling_condition_data_collection_stage', item.xpath(xpDisablingConditionDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.DisablingCondition)

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

    itemElements = element.xpath(xpDevelopmentalDisability, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'has_developmental_disability', item.xpath(xpHasDevelopmentalDisability, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'has_developmental_disability_date_collected', item.xpath(xpHasDevelopmentalDisabilityDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_developmental_disability_date_effective', item.xpath(xpHasDevelopmentalDisabilityDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_developmental_disability_data_collection_stage', item.xpath(xpHasDevelopmentalDisabilityDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'receive_developmental_disability', item.xpath(xpReceiveDevelopmentalDisability, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receive_developmental_disability_date_collected', item.xpath(xpReceiveDevelopmentalDisabilityDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_developmental_disability_date_effective', item.xpath(xpReceiveDevelopmentalDisabilityDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_developmental_disability_data_collection_stage', item.xpath(xpReceiveDevelopmentalDisabilityDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.DevelopmentalDisability)

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

    itemElements = element.xpath(xpDestinations, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'destination_id_id_num', item.xpath(xpDestinationIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'destination_id_id_str', item.xpath(xpDestinationIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'destination_id_delete_occurred_date', item.xpath(xpDestinationIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'destination_id_delete_effective_date', item.xpath(xpDestinationIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'destination_id_delete', item.xpath(xpDestinationIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'destination_code', item.xpath(xpDestinationCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'destination_code_date_collected', item.xpath(xpDestinationCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'destination_code_date_effective', item.xpath(xpDestinationCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'destination_code_data_collection_stage', item.xpath(xpDestinationCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'destination_other', item.xpath(xpDestinationOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'destination_other_date_collected', item.xpath(xpDestinationOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'destination_other_date_effective', item.xpath(xpDestinationOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'destination_other_data_collection_stage', item.xpath(xpDestinationOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Destinations)

            ''' Parse sub-tables '''
                        

def parse_degree(self, element):
    ''' Element paths '''
    xpDegree = 'hmis:Degree'
    xpDegreeIDIDNum = './hmis:IDNum'
    xpDegreeIDIDStr = './hmis:IDStr'
    xpDegreeIDDeleteOccurredDate = './@hmis:deleteOccurredDate'
    xpDegreeIDDeleteEffective = './@hmis:deleteEffective'
    xpDegreeIDDelete = './@hmis:delete'
    xpDegreeOther = 'hmis:DegreeOther'
    xpDegreeOtherDateCollected = 'hmis:DegreeOther/@hmis:dateCollected'
    xpDegreeOtherDateEffective = 'hmis:DegreeOther/@hmis:dateEffective'
    xpDegreeOtherDataCollectionStage = 'hmis:DegreeOther/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpDegree, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'degree_id_id_num', item.xpath(xpDegreeIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'degree_id_id_str', item.xpath(xpDegreeIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'degree_id_delete_occurred_date', item.xpath(xpDegreeIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'degree_id_delete_effective_date', item.xpath(xpDegreeIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'degree_id_delete', item.xpath(xpDegreeIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'degree_other', item.xpath(xpDegreeOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'degree_other_date_collected', item.xpath(xpDegreeOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'degree_other_date_effective', item.xpath(xpDegreeOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'degree_other_data_collection_stage', item.xpath(xpDegreeOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Degree)

            ''' Parse sub-tables '''
            parse_degree_code(self, item)            

def parse_degree_code(self, element):
    ''' Element paths '''
    xpDegreeCode = 'hmis:DegreeCode'
    xpDegreeCodeDateCollected = 'hmis:DegreeCode/@hmis:dateCollected'
    xpDegreeCodeDateEffective = 'hmis:DegreeCode/@hmis:dateEffective'
    xpDegreeCodeDataCollectionStage = 'hmis:DegreeCode/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpDegreeCode, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'degree_code', item.xpath(xpDegreeCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'degree_date_collected', item.xpath(xpDegreeCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'degree_date_effective', item.xpath(xpDegreeCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'degree_data_collection_stage', item.xpath(xpDegreeCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'degree_index_id', self.degree_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.DegreeCode)

            ''' Parse sub-tables '''
                        

def parse_currently_in_school(self, element):
    ''' Element paths '''
    xpCurrentlyInSchool = 'hmis:CurrentlyInSchool'
    xpCurrentlyInSchoolDateCollected = 'hmis:CurrentlyInSchool/@hmis:dateCollected'
    xpCurrentlyInSchoolDateEffective = 'hmis:CurrentlyInSchool/@hmis:dateEffective'
    xpCurrentlyInSchoolDataCollectionStage = 'hmis:CurrentlyInSchool/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpCurrentlyInSchool, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'currently_in_school', item.xpath(xpCurrentlyInSchool, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'currently_in_school_date_collected', item.xpath(xpCurrentlyInSchoolDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'currently_in_school_date_effective', item.xpath(xpCurrentlyInSchoolDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'currently_in_school_data_collection_stage', item.xpath(xpCurrentlyInSchoolDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.CurrentlyInSchool)

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

    itemElements = element.xpath(xpContactsMade, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'contact_id_id_num', item.xpath(xpContactIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'contact_id_id_str', item.xpath(xpContactIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'contact_id_delete_occurred_date', item.xpath(xpContactIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'contact_id_delete_effective_date', item.xpath(xpContactIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'contact_id_delete', item.xpath(xpContactIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'contact_date', item.xpath(xpContactDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'contact_date_data_collection_stage', item.xpath(xpContactDateDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'contact_location', item.xpath(xpContactLocation, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'contact_location_data_collection_stage', item.xpath(xpContactLocationDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ContactMade)

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

    itemElements = element.xpath(xpChildEnrollmentStatus, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'child_enrollment_status_id_id_num', item.xpath(xpChildEnrollmentStatusIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'child_enrollment_status_id_id_str', item.xpath(xpChildEnrollmentStatusIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'child_enrollment_status_id_delete_occurred_date', item.xpath(xpChildEnrollmentStatusIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_enrollment_status_id_delete_effective_date', item.xpath(xpChildEnrollmentStatusIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_enrollment_status_id_delete', item.xpath(xpChildEnrollmentStatusIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'child_currently_enrolled_in_school', item.xpath(xpChildCurrentlyEnrolledInSchool, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'child_currently_enrolled_in_school_date_collected', item.xpath(xpChildCurrentlyEnrolledInSchoolDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_currently_enrolled_in_school_date_effective', item.xpath(xpChildCurrentlyEnrolledInSchoolDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_currently_enrolled_in_school_data_collection_stage', item.xpath(xpChildCurrentlyEnrolledInSchoolDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'child_school_name', item.xpath(xpChildSchoolName, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'child_school_name_date_collected', item.xpath(xpChildSchoolNameDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_school_name_date_effective', item.xpath(xpChildSchoolNameDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_school_name_data_collection_stage', item.xpath(xpChildSchoolNameDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'child_mckinney_vento_liaison', item.xpath(xpChildMcKinneyVentoLiaison, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'child_mckinney_vento_liaison_date_collected', item.xpath(xpChildMcKinneyVentoLiaisonDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_mckinney_vento_liaison_date_effective', item.xpath(xpChildMcKinneyVentoLiaisonDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_mckinney_vento_liaison_data_collection_stage', item.xpath(xpChildMcKinneyVentoLiaisonDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'child_school_type', item.xpath(xpChildSchoolType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'child_school_type_date_collected', item.xpath(xpChildSchoolTypeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_school_type_date_effective', item.xpath(xpChildSchoolTypeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_school_type_data_collection_stage', item.xpath(xpChildSchoolTypeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'child_school_last_enrolled_date', item.xpath(xpChildSchoolLastEnrolledDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'child_school_last_enrolled_date_date_collected', item.xpath(xpChildSchoolLastEnrolledDateDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'child_school_last_enrolled_date_data_collection_stage', item.xpath(xpChildSchoolLastEnrolledDateDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ChildEnrollmentStatus)

            ''' Parse sub-tables '''
            parse_child_enrollment_status_barrier(self, item)            

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

    itemElements = element.xpath(xpChildEnrollmentBarrier, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'barrier_id_id_num', item.xpath(xpBarrierIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'barrier_id_id_str', item.xpath(xpBarrierIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'barrier_id_delete_occurred_date', item.xpath(xpBarrierIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'barrier_id_delete_effective_date', item.xpath(xpBarrierIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'barrier_id_delete', item.xpath(xpBarrierIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'barrier_code', item.xpath(xpBarrierCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'barrier_code_date_collected', item.xpath(xpBarrierCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'barrier_code_date_effective', item.xpath(xpBarrierCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'barrier_code_data_collection_stage', item.xpath(xpBarrierCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'barrier_other', item.xpath(xpBarrierOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'barrier_other_date_collected', item.xpath(xpBarrierOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'barrier_other_date_effective', item.xpath(xpBarrierOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'barrier_other_data_collection_stage', item.xpath(xpBarrierOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'child_enrollment_status_index_id', self.child_enrollment_status_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ChildEnrollmentStatusBarrier)

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

    itemElements = element.xpath(xpChronicHealthCondition, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'has_chronic_health_condition', item.xpath(xpHasChronicHealthCondition, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'has_chronic_health_condition_date_collected', item.xpath(xpHasChronicHealthConditionDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_chronic_health_condition_date_effective', item.xpath(xpHasChronicHealthConditionDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'has_chronic_health_condition_data_collection_stage', item.xpath(xpHasChronicHealthConditionDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'receive_chronic_health_services', item.xpath(xpReceiveChronicHealthServices, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receive_chronic_health_services_date_collected', item.xpath(xpReceiveChronicHealthServicesDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_chronic_health_services_date_effective', item.xpath(xpReceiveChronicHealthServicesDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receive_chronic_health_services_data_collection_stage', item.xpath(xpReceiveChronicHealthServicesDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ChronicHealthCondition)

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
    
    itemElements = element.xpath(xpReleaseOfInformation, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'release_of_information_idid_num', item.xpath(xpReleaseOfInformationIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'release_of_information_idid_str', item.xpath(xpReleaseOfInformationIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'release_of_information_idid_str_date_collected', item.xpath(xpReleaseOfInformationIDDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'release_of_information_id_date_effective', item.xpath(xpReleaseOfInformationIDDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'release_of_information_id_data_collection_stage', item.xpath(xpReleaseOfInformationIDDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'site_service_idid_str', item.xpath(xpSiteServiceID, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'documentation', item.xpath(xpDocumentation, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'documentation_date_collected', item.xpath(xpDocumentationDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'documentation_date_effective', item.xpath(xpDocumentationDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'documentation_data_collection_stage', item.xpath(xpDocumentationDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'start_date', item.xpath(xpStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'end_date', item.xpath(xpEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'release_granted', item.xpath(xpReleaseGranted, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'release_granted_date_collected', item.xpath(xpReleaseGrantedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'release_granted_date_effective', item.xpath(xpReleaseGrantedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'release_granted_data_collection_stage', item.xpath(xpReleaseGrantedDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ReleaseOfInformation)

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

    itemElements = element.xpath(xpIncomeAndSources, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'income_and_source_id_id_id_num', item.xpath(xpIncomeAndSourceIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'income_and_source_id_id_id_str', item.xpath(xpIncomeAndSourceIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'income_and_source_id_id_delete_occurred_date', item.xpath(xpIncomeAndSourceIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_and_source_id_id_delete_effective_date', item.xpath(xpIncomeAndSourceIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_and_source_id_id_delete', item.xpath(xpIncomeAndSourceIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'income_source_code', item.xpath(xpIncomeSourceCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'income_source_code_date_collected', item.xpath(xpIncomeSourceCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_source_code_date_effective', item.xpath(xpIncomeSourceCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_source_code_data_collection_stage', item.xpath(xpIncomeSourceCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'income_source_other', item.xpath(xpIncomeSourceOther, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'income_source_other_date_collected', item.xpath(xpIncomeSourceOtherDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_source_other_date_effective', item.xpath(xpIncomeSourceOtherDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_source_other_data_collection_stage', item.xpath(xpIncomeSourceOtherDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'receiving_income_source', item.xpath(xpReceivingIncomingSource, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receiving_income_source_date_collected', item.xpath(xpReceivingIncomingSourceDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receiving_income_source_date_effective', item.xpath(xpReceivingIncomingSourceDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'receiving_income_source_data_collection_stage', item.xpath(xpReceivingIncomingSourceDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'income_source_amount', item.xpath(xpIncomeSourceAmount, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'income_source_amount_date_collected', item.xpath(xpIncomeSourceAmountDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_source_amount_date_effective', item.xpath(xpIncomeSourceAmountDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'income_source_amount_data_collection_stage', item.xpath(xpIncomeSourceAmountDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.IncomeAndSources)

            ''' Parse sub-tables '''
                        


def parse_hud_homeless_episodes(self, element):
    ''' Element paths '''
    xpHudHomelessEpisodes = 'hmis:HUDHomelessEpisodes'
    xpStartDate = 'hmis:StartDate'
    xpEndDate = 'hmis:EndDate'

    itemElements = element.xpath(xpHudHomelessEpisodes, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'start_date', item.xpath(xpStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'end_date', item.xpath(xpEndDate, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.HUDHomelessEpisodes)

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

    itemElements = element.xpath(xpPersonAddress, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'address_period_start_date', item.xpath(xpAddressPeriodStartDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'address_period_end_date', item.xpath(xpAddressPeriodEndDate, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pre_address_line', item.xpath(xpPreAddressLine, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'pre_address_line_date_collected', item.xpath(xpPreAddressLineDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'pre_address_line_date_effective', item.xpath(xpPreAddressLineDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'pre_address_line', item.xpath(xpPreAddressLineDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'line1', item.xpath(xpLine1, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'line1_date_collected', item.xpath(xpLine1DateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'line1_date_effective', item.xpath(xpLine1DateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'line1_data_collection_stage', item.xpath(xpLine1DataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'line2', item.xpath(xpLine2, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'line2_date_collected', item.xpath(xpLine2DateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'line2_date_effective', item.xpath(xpLine2DateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'line2_data_collection_stage', item.xpath(xpLine2DataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'city', item.xpath(xpCity, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'city_date_collected', item.xpath(xpCityDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'city_date_effective', item.xpath(xpCityDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'city_data_collection_stage', item.xpath(xpCityDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'county', item.xpath(xpCounty, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'county_date_collected', item.xpath(xpCountyDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'county_date_effective', item.xpath(xpCountyDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'county_data_collection_stage', item.xpath(xpCountyDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'state', item.xpath(xpState, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'state_date_collected', item.xpath(xpStateDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'state_date_effective', item.xpath(xpStateDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'state_data_collection_stage', item.xpath(xpStateDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'zipcode', item.xpath(xpZIPCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'zipcode_date_collected', item.xpath(xpZIPCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'zipcod_date_effectivee', item.xpath(xpZIPCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'zipcode_data_collection_stage', item.xpath(xpZIPCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'country', item.xpath(xpCountry, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'country_date_collected', item.xpath(xpCountryDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'country_date_effective', item.xpath(xpCountryDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'country_data_collection_stage', item.xpath(xpCountryDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'is_last_permanent_zip', item.xpath(xpIsLastPermanentZip, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'is_last_permanent_zip_date_collected', item.xpath(xpIsLastPermanentZIPDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'is_last_permanent_zip_date_effective', item.xpath(xpIsLastPermanentZIPDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'is_last_permanent_zip_data_collection_stage', item.xpath(xpIsLastPermanentZIPDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'zip_quality_code', item.xpath(xpZipQualityCode, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'zip_quality_code_date_collected', item.xpath(xpZIPQualityCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'zip_quality_code_date_effective', item.xpath(xpZIPQualityCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'zip_quality_code_data_collection_stage', item.xpath(xpZIPQualityCodeDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.PersonAddress)

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

    itemElements = element.xpath(xpOtherNames, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'other_first_name_unhashed', item.xpath(xpOtherFirstNameUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'other_first_name_hashed', item.xpath(xpOtherFirstNameHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'other_first_name_date_collected', item.xpath(xpOtherFirstNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'other_first_name_date_effective', item.xpath(xpOtherFirstNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'other_first_name_data_collection_stage', item.xpath(xpOtherFirstNameHashedDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'other_last_name_unhashed', item.xpath(xpOtherLastNameUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'other_last_name_hashed', item.xpath(xpOtherLastNameHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'other_last_name_date_collected', item.xpath(xpOtherLastNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'other_last_name_date_effective', item.xpath(xpOtherLastNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'other_last_name_data_collection_stage', item.xpath(xpOtherLastNameHashedDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'other_middle_name_unhashed', item.xpath(xpOtherMiddleNameUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'other_middle_name_hashed', item.xpath(xpOtherMiddleNameHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'other_middle_name_date_collected', item.xpath(xpOtherMiddleNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'other_middle_name_date_effective', item.xpath(xpOtherMiddleNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'other_middle_name_data_collection_stage', item.xpath(xpOtherMiddleNameHashedDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'other_suffix_unhashed', item.xpath(xpOtherSuffixUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'other_suffix_hashed', item.xpath(xpOtherSuffixHashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'other_suffix_date_collected', item.xpath(xpOtherSuffixHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'other_suffix_date_effective', item.xpath(xpOtherSuffixHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'other_suffix_data_collection_stage', item.xpath(xpOtherSuffixHashedDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            
            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.OtherNames)

            ''' Parse sub-tables '''
                        
def parse_races(self, element):
    ''' Element paths '''
    xpRaces = 'hmis:Race'
    xpRaceUnhashed = 'hmis:Unhashed'
    xpRaceUnhashedDateCollected = 'hmis:Unhashed/@hmis:dateCollected'
    xpRaceUnhashedDataCollectionStage = 'hmis:Unhashed/@hmis:dataCollectionStage'
    xpRaceHashed = 'hmis:Hashed'

    itemElements = element.xpath(xpRaces, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'race_unhashed', item.xpath(xpRaceUnhashed, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'race_date_collected', item.xpath(xpRaceUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'race_data_collection_stage', item.xpath(xpRaceUnhashedDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'race_hashed', item.xpath(xpRaceHashed, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Races)

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

    itemElements = element.xpath(xpFundingSource, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'funding_source_id_id_num', item.xpath(xpFundingSourceIDIDNum, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'funding_source_id_id_str', item.xpath(xpFundingSourceIDIDStr, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'funding_source_id_delete_occurred_date', item.xpath(xpFundingSourceIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'funding_source_id_delete_effective_date', item.xpath(xpFundingSourceIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'funding_source_id_delete', item.xpath(xpFundingSourceIDDelete, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'federal_cfda_number', item.xpath(xpFederalCFDA, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'receives_mckinney_funding', item.xpath(xpReceivesMcKinneyFunding, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'advance_or_arrears', item.xpath(xpAdvanceOrArrears, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'financial_assistance_amount', item.xpath(xpFinancialAssistanceAmount, namespaces = self.nsmap), 'text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'service_index_id', self.service_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'service_event_index_id', self.service_event_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.FundingSource)

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

    itemElements = element.xpath(xpResourceInfo, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'resource_specialist', item.xpath(xpResourceSpecialist, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'available_for_directory', item.xpath(xpAvailableForDirectory, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'available_for_referral', item.xpath(xpAvailableForReferral, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'available_for_research', item.xpath(xpAvailableForResearch, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'date_added', item.xpath(xpDateAdded, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'date_last_verified', item.xpath(xpDateLastVerified, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'date_of_last_action', item.xpath(xpDateOfLastAction, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'last_action_type', item.xpath(xpLastActionType, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_service_index_id', self.site_service_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.ResourceInfo)

            ''' Parse sub-tables '''
            parse_contact(self, item)            
            parse_email(self, item)      
            parse_phone(self, item)      
        
def parse_contact(self, element):
    ''' Element paths '''
    xpContact = 'airs:Contact'
    xpTitle = 'airs:Title'
    xpName = 'airs:Name'
    xpType = "../%s/%s" % (xpContact, '@Type')

    itemElements = element.xpath(xpContact, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'title', item.xpath(xpTitle, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'name', item.xpath(xpName, namespaces = self.nsmap), 'text')
            # SBB20100909 wrong type element (attribute)
            existence_test_and_add(self, 'type', item.xpath(xpType, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            except: pass
            # SBB20100908 Need to test this.  A site doesn't have resource Info but contacts do under other elements
            try: existence_test_and_add(self, 'resource_info_index_id', self.resource_info_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Contact)

            ''' Parse sub-tables '''
            parse_email(self, item)      
            parse_phone(self, item)      

def parse_email(self, element):
    ''' Element paths '''
    xpEmail = 'airs:Email'
    xpAddress = 'airs:Address'
    xpNote = 'airs:Note'
    xpPersonEmail = 'airs:PersonEmail'
    xpPersonEmailDateCollected = 'hmis:PersonEmail/@hmis:dateCollected'
    xpPersonEmailDateEffective = 'hmis:PersonEmail/@hmis:dateEffective'
    xpPersonEmailDataCollectionStage = 'hmis:PersonEmail/@hmis:dataCollectionStage'

    itemElements = element.xpath(xpEmail, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'address', item.xpath(xpAddress, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'note', item.xpath(xpNote, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_email', item.xpath(xpPersonEmail, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'person_email_date_collected', item.xpath(xpPersonEmailDateCollected, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_email_date_effective', item.xpath(xpPersonEmailDateEffective, namespaces = self.nsmap), 'attribute_date')
            existence_test_and_add(self, 'person_email_data_collection_stage', item.xpath(xpPersonEmailDataCollectionStage, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'contact_index_id', self.contact_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'resource_info_index_id', self.resource_info_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Email)

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

    itemElements = element.xpath(xpPhone, namespaces = self.nsmap)
    if itemElements is not None:
        for item in itemElements:
            self.parse_dict = {}
            
            ''' Map elements to database columns '''
            existence_test_and_add(self, 'phone_number', item.xpath(xpPhoneNumber, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'reason_withheld', item.xpath(xpReasonWithheld, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'extension', item.xpath(xpExtension, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'description', item.xpath(xpDescription, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'type', item.xpath(xpType, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'function', item.xpath(xpFunction, namespaces = self.nsmap), 'text')
            existence_test_and_add(self, 'toll_free', item.xpath(xpTollFree, namespaces = self.nsmap), 'attribute_text')
            existence_test_and_add(self, 'confidential', item.xpath(xpConfidential, namespaces = self.nsmap), 'attribute_text')

            ''' Foreign Keys '''
            try: existence_test_and_add(self, 'agency_location_index_id', self.agency_location_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'contact_index_id', self.contact_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'resource_info_index_id', self.resource_info_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'site_index_id', self.site_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'service_index_id', self.service_index_id, 'no_handling')
            except: pass
            try: existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
            except: pass
                            
            ''' Shred to database '''
            shred(self, self.parse_dict, dbobjects.Phone)

            ''' Parse sub-tables '''
                        

''' Build link/bridge tables '''
        
def record_source_export_link(self):
    ''' record the link between source and export '''
    existence_test_and_add(self, 'source_index_id', self.source_index_id, 'no_handling')
    existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
    shred(self, self.parse_dict, dbobjects.SourceExportLink)
    return            

def record_agency_child_link(self):
    ''' record the link between agency and any children '''
    existence_test_and_add(self, 'agency_index_id', self.agency_index_id, 'no_handling')
    existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
    shred(self, self.parse_dict, dbobjects.AgencyChild)
    return            

''' Utility methods '''
        

def existence_test_and_add(self, db_column, query_string, handling):
    ''' Checks that the query actually has a result and adds to dictionary '''
    if handling == 'no_handling':
            persist(self, db_column, query_string = query_string)
            #print query_string
            return True
    elif len(query_string) is not 0 or None:
        if handling == 'attribute_text':
            persist(self, db_column, query_string = str(query_string[0]))
            #print query_string
            return True
        if handling == 'text':
            persist(self, db_column, query_string = query_string[0].text)
            #print query_string
            return True
        elif handling == 'attribute_date':
            #print "dateutil.parser.parse(query_string[0]) is: ", dateutil.parser.parse(query_string[0])
            persist(self, db_column, query_string = dateutil.parser.parse(query_string[0]))
            #print query_string
            return True
        elif handling == 'element_date':
            persist(self, db_column, query_string = dateutil.parser.parse(query_string[0].text))
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
                persist(self, db_column, query_string = str(query_string))
                #print query_string
                return True
            if handling == 'text':
                #print "query_string.text", query_string.text
                persist(self, db_column, query_string = query_string.text)
                #print query_string
                return True
            elif handling == 'attribute_date':
                persist(self, db_column, query_string = dateutil.parser.parse(query_string))
                #print query_string
                return True
            elif handling == 'element_date':
                persist(self, db_column, query_string = dateutil.parser.parse(query_string.text))
                #print query_string
                return True
        
def persist(self, db_column, query_string):
    ''' Adds dictionary item with database column and associated data element '''
    self.parse_dict.__setitem__(db_column, query_string)
    return
    
def shred(self, parse_dict, mapping):
    ''' commits the record set to the database '''
    mapped = mapping(parse_dict)
    self.session.add(mapped)
    self.session.commit()
    
    ''' store foreign keys '''
    if mapping.__name__ == "Source":
        self.source_index_id = mapped.id
        print "Source: ", self.source_index_id

    if mapping.__name__ == "Export":
        self.export_index_id = mapped.id
        print "Export: ", self.export_index_id
        
    if mapping.__name__ == "Household":
        self.household_index_id = mapped.id
        print "Household: ", self.household_index_id

    if mapping.__name__ == "Agency":
        self.agency_index_id = mapped.id
        print "Agency: ", self.agency_index_id
        
    if mapping.__name__ == "AgencyLocation":
        self.agency_location_index_id = mapped.id
        print "Agency Location: ", self.agency_location_index_id

    if mapping.__name__ == "Site":
        self.site_index_id = mapped.id
        print "Site: ", self.site_index_id

    if mapping.__name__ == "SiteService":
        self.site_service_index_id = mapped.id
        print "SiteService: ", self.site_service_index_id

    if mapping.__name__ == "PitCountSet":
        self.pit_count_set_index_id = mapped.id
        print "PitCountSet: ", self.pit_count_set_index_id

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
    return
        

        
def main(argv=None):  
    ''' Manually test this Reader class '''
    if argv is None:
        argv = sys.argv

    ## clear db tables (may have to run twice to get objects linked properly)
    from synthesis import postgresutils
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