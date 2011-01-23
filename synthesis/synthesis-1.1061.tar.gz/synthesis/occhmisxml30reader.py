''' 
    Reads a HUD HMIS XML 3.0 Document into memory and parses its contents storing them into a postgresql database.
    This is a log database, so it holds everything and doesn't worry about deduplication.
    The only thing it enforces are exportids, which must be unique.
'''

import sys, os
from synthesis.reader import Reader
from zope.interface import implements
from lxml import etree
from conf import settings
import dbobjects
from synthesis import hmisxml30reader

class OCCHUDHMISXML30Reader(dbobjects.DatabaseObjects): 
    ''' Implements reader interface '''
    implements (Reader) 

    ''' Define XML namespaces '''
    hmis_namespace = "http://www.hmis.info/schema/3_0/HUD_HMIS.xsd" 
    airs_namespace = "http://www.hmis.info/schema/3_0/AIRS_3_0_mod.xsd"
    occ_namespace = "http://xsd.alexandriaconsulting.com/repos/trunk/HUD_HMIS_XML/OCC_Extend_HUD_HMIS.xsd"
    nsmap = {"hmis" : hmis_namespace, "airs" : airs_namespace, "ext" : occ_namespace}


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
        self.parse_source(root_element)
        return
        
    ''' Parse each table '''
    def parse_source(self, root_element):
        ''' Loop through all sources and then traverse the tree for each export '''
        ''' There can be multiple sources with multiple exports inside each source '''
        
        xpSources = '/ext:Sources/ext:Source'
        source_list = root_element.xpath(xpSources, namespaces = self.nsmap)
        if source_list is not None:
            for item in source_list:
                self.parse_dict = {}
                ''' Element paths '''
                xpSourceVersion = '../../@ext:version'                
                xpSourceIDIDNum = 'ext:SourceID/hmis:IDNum'
                xpSourceIDIDStr = 'ext:SourceID/hmis:IDStr'
                xpSourceDelete = 'ext:SourceID/@hmis:Delete'
                xpSourceDeleteOccurredDate = 'ext:SourceID/@hmis:DeleteOccurredDate'
                xpSourceDeleteEffective = 'ext:SourceID/@hmis:DeleteEffective'
                xpSourceSoftwareVendor = 'ext:SoftwareVendor'
                xpSourceSoftwareVersion = 'ext:SoftwareVersion'
                xpSourceContactEmail = 'ext:SourceContactEmail'
                xpSourceContactExtension = 'ext:SourceContactExtension'
                xpSourceContactFirst = 'ext:SourceContactFirst'        
                xpSourceContactLast = 'ext:SourceContactLast'        
                xpSourceContactPhone = 'ext:SourceContactPhone'
                xpSourceName = 'ext:SourceName'
                #xp_source_exports = 'ext:Export'
                               
                ''' Map elements to database columns '''
                hmisxml30reader.existence_test_and_add(self, 'schema_version', item.xpath(xpSourceVersion, namespaces = self.nsmap), 'attribute_text')
                hmisxml30reader.existence_test_and_add(self, 'source_id_id_id_num', item.xpath(xpSourceIDIDNum, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'source_id_id_id_str', item.xpath(xpSourceIDIDStr, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'source_id_id_delete', item.xpath(xpSourceDelete, namespaces = self.nsmap), 'attribute_text')
                hmisxml30reader.existence_test_and_add(self, 'source_id_id_delete_occurred_date', item.xpath(xpSourceDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'source_id_id_delete_effective', item.xpath(xpSourceDeleteEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'software_vendor', item.xpath(xpSourceSoftwareVendor, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'software_version', item.xpath(xpSourceSoftwareVersion, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'source_contact_email', item.xpath(xpSourceContactEmail, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'source_contact_extension', item.xpath(xpSourceContactExtension, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'source_contact_first', item.xpath(xpSourceContactFirst, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'source_contact_last', item.xpath(xpSourceContactLast, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'source_contact_phone', item.xpath(xpSourceContactPhone, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'source_name', item.xpath(xpSourceName, namespaces = self.nsmap), 'text')
                source_id_str = item.xpath(xpSourceIDIDStr, namespaces = self.nsmap)
                source_id_num = item.xpath(xpSourceIDIDNum, namespaces = self.nsmap)

                if source_id_str is not None:
                    #source_id = source_id_str[0].text 
                    hmisxml30reader.existence_test_and_add(self, 'source_id', source_id_str, 'text')

                elif source_id_num is not None:
                    #source_id = source_id_num[0].text 
                    hmisxml30reader.existence_test_and_add(self, 'source_id', source_id_num, 'text')

                ''' Shred to database '''
                hmisxml30reader.shred(self, self.parse_dict, dbobjects.Source)
                
                
                
                #print "self.source_index_id is: ", self.source_index_id
                

                ''' Parse all exports for this specific source '''
                self.parse_export(item)
        return                

    def parse_export(self, element):
        ''' loop through all exports and traverse the tree '''
        
        ''' Element paths '''
        xpExport = 'ext:Export'
        xpExportIDIDNum = 'ext:ExportID/hmis:IDNum'
        xpExportIDIDStr = 'ext:ExportID/hmis:IDStr'
        xpExportDelete = 'ext:ExportID/@hmis:Delete'
        xpExportDeleteOccurredDate = 'ext:ExportID/@hmis:DeleteOccurredDate'
        xpExportDeleteEffective = 'ext:ExportID/@hmis:DeleteEffective'
        xpExportExportDate = 'ext:ExportDate'
        xpExportPeriodStartDate = 'ext:ExportPeriod/hmis:StartDate'
        xpExportPeriodEndDate = 'ext:ExportPeriod/hmis:EndDate'
        
        itemElements = element.xpath(xpExport, namespaces = self.nsmap)
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}

                ''' Map elements to database columns '''
                test = item.xpath(xpExportIDIDNum, namespaces = self.nsmap) 
                if len(test) is 0:
                    test = item.xpath(xpExportIDIDStr, namespaces = self.nsmap)
                    self.export_id = test
                    hmisxml30reader.existence_test_and_add(self, 'export_id', test, 'text')
                else:
                    self.export_id = test
                    hmisxml30reader.existence_test_and_add(self, 'export_id', test, 'text')
                hmisxml30reader.existence_test_and_add(self, 'export_id_id_num', item.xpath(xpExportIDIDNum, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'export_id_id_str', item.xpath(xpExportIDIDStr, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'export_id_delete', item.xpath(xpExportDelete, namespaces = self.nsmap), 'attribute_text')
                hmisxml30reader.existence_test_and_add(self, 'export_id_delete_occurred_date', item.xpath(xpExportDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'export_id_delete_effective', item.xpath(xpExportDeleteEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'export_date', item.xpath(xpExportExportDate, namespaces = self.nsmap), 'element_date') 
                hmisxml30reader.existence_test_and_add(self, 'export_period_start_date', item.xpath(xpExportPeriodStartDate, namespaces = self.nsmap), 'element_date')
                hmisxml30reader.existence_test_and_add(self, 'export_period_end_date', item.xpath(xpExportPeriodEndDate, namespaces = self.nsmap), 'element_date')

                ''' Shred to database '''
                hmisxml30reader.shred(self, self.parse_dict, dbobjects.Export)
                
                ''' Create source to export link '''
                hmisxml30reader.record_source_export_link(self)

                ''' Parse sub-tables '''
                hmisxml30reader.parse_household(self, item)
                hmisxml30reader.parse_region(self, item)
                hmisxml30reader.parse_agency(self, item)
                self.parse_person(item)
                hmisxml30reader.parse_service(self, item)
                hmisxml30reader.parse_site(self, item)
                hmisxml30reader.parse_site_service(self, item)
        return
               
    def parse_person(self, element):
        ''' Element paths '''
        xpPerson = 'ext:Person'
        xpPersonIDNum = 'ext:PersonID/hmis:IDNum'
        xpPersonIDStr = 'ext:PersonID/hmis:IDStr'
        xpPersonIDDeleteOccurredDate = 'ext:PersonID/@hmis:DeleteOccurredDate'
        xpPersonIDDeleteEffective = 'ext:PersonID/@hmis:DeleteEffective'
        xpPersonDelete = 'ext:PersonID/@hmis:Delete'
        xpPersonDateOfBirthHashed = 'ext:DateOfBirth/hmis:Hashed'
        xpPersonDateOfBirthHashedDateCollected = 'ext:DateOfBirth/hmis:Hashed/@hmis:dateCollected'
        xpPersonDateOfBirthUnhashed = 'ext:DateOfBirth/hmis:Unhashed'
        xpPersonDateOfBirthUnhashedDateCollected = 'ext:DateOfBirth/hmis:Unhashed/@hmis:dateCollected'
        xpPersonDateOfBirthType = 'ext:DateOfBirth/hmis:DateOfBirthType'
        xpPersonDateOfBirthTypeDateCollected = 'ext:DateOfBirth/hmis:DateOfBirthType/@hmis:dateCollected'
        xpPersonEthnicityHashedDateCollected = 'ext:Ethnicity/hmis:Hashed/@hmis:dateCollected'
        xpPersonEthnicityUnhashedDateCollected = 'ext:Ethnicity/hmis:Unhashed/@hmis:dateCollected'
        xpPersonEthnicityHashed = 'ext:Ethnicity/hmis:Hashed'
        xpPersonEthnicityUnhashed = 'ext:Ethnicity/hmis:Unhashed'
        xpPersonGenderHashed = 'ext:Gender/hmis:Hashed'
        xpPersonGenderUnhashed = 'ext:Gender/hmis:Unhashed'
        xpPersonGenderHashedDateCollected = 'ext:Gender/hmis:Hashed/@hmis:dateCollected'
        xpPersonGenderUnhashedDateCollected = 'ext:Gender/hmis:Unhashed/@hmis:dateCollected'        
        xpPersonGenderHashedDateEffective = 'ext:Gender/hmis:Hashed/@hmis:dateEffective'
        xpPersonGenderUnhashedDateEffective = 'ext:Gender/hmis:Unhashed/@hmis:dateEffective'                
        xpPersonLegalFirstNameHashed = 'ext:LegalFirstName/hmis:Hashed'
        xpPersonLegalFirstNameUnhashed = 'ext:LegalFirstName/hmis:Unhashed'
        xpPersonLegalFirstNameHashedDateEffective = 'ext:LegalFirstName/hmis:Hashed/@hmis:dateEffective'
        xpPersonLegalFirstNameUnhashedDateEffective = 'ext:LegalFirstName/hmis:Unhashed/@hmis:dateEffective'        
        xpPersonLegalFirstNameHashedDateCollected = 'ext:LegalFirstName/hmis:Hashed/@hmis:dateCollected'
        xpPersonLegalFirstNameUnhashedDateCollected = 'ext:LegalFirstName/hmis:Unhashed/@hmis:dateCollected'        
        xpPersonLegalLastNameHashed = 'ext:LegalLastName/hmis:Hashed'
        xpPersonLegalLastNameUnhashed = 'ext:LegalLastName/hmis:Unhashed'
        xpPersonLegalLastNameHashedDateEffective = 'ext:LegalLastName/hmis:Hashed/@hmis:dateEffective'
        xpPersonLegalLastNameUnhashedDateEffective = 'ext:LegalLastName/hmis:Unhashed/@hmis:dateEffective'        
        xpPersonLegalLastNameHashedDateCollected = 'ext:LegalLastName/hmis:Hashed/@hmis:dateCollected'
        xpPersonLegalLastNameUnhashedDateCollected = 'ext:LegalLastName/hmis:Unhashed/@hmis:dateCollected'        
        xpPersonLegalMiddleNameHashed = 'ext:LegalMiddleName/hmis:Hashed'
        xpPersonLegalMiddleNameUnhashed = 'ext:LegalMiddleName/hmis:Unhashed'
        xpPersonLegalMiddleNameHashedDateEffective = 'ext:LegalMiddleName/hmis:Hashed/@hmis:dateEffective'
        xpPersonLegalMiddleNameUnhashedDateEffective = 'ext:LegalMiddleName/hmis:Unhashed/@hmis:dateEffective'        
        xpPersonLegalMiddleNameHashedDateCollected = 'ext:LegalMiddleName/hmis:Hashed/@hmis:dateCollected'
        xpPersonLegalMiddleNameUnhashedDateCollected = 'ext:LegalMiddleName/hmis:Unhashed/@hmis:dateCollected'        
        xpPersonLegalSuffixHashed = 'ext:LegalSuffix/hmis:Hashed'
        xpPersonLegalSuffixUnhashed = 'ext:LegalSuffix/hmis:Unhashed'
        xpPersonLegalSuffixHashedDateEffective = 'ext:LegalSuffix/hmis:Hashed/@hmis:dateEffective'
        xpPersonLegalSuffixUnhashedDateEffective = 'ext:LegalSuffix/hmis:Unhashed/@hmis:dateEffective'        
        xpPersonLegalSuffixHashedDateCollected = 'ext:LegalSuffix/hmis:Hashed/@hmis:dateCollected'
        xpPersonLegalSuffixUnhashedDateCollected = 'ext:LegalSuffix/hmis:Unhashed/@hmis:dateCollected'        
        xpPersonSocialSecurityNumberHashed = 'ext:SocialSecurityNumber/hmis:Hashed'
        xpPersonSocialSecurityNumberUnhashed = 'ext:SocialSecurityNumber/hmis:Unhashed'
        xpPersonSocialSecurityNumberHashedDateCollected = 'ext:SocialSecurityNumber/hmis:Hashed/@hmis:dateCollected'
        xpPersonSocialSecurityNumberUnhashedDateCollected = 'ext:SocialSecurityNumber/hmis:Unhashed/@hmis:dateCollected'
        xpPersonSocialSecurityNumberHashedDateEffective = 'ext:SocialSecurityNumber/hmis:Hashed/@hmis:dateEffective'
        xpPersonSocialSecurityNumberUnhashedDateEffective = 'ext:SocialSecurityNumber/hmis:Unhashed/@hmis:dateEffective' 
        xpPersonSocialSecurityNumberQualityCode = 'ext:SocialSecurityNumber/hmis:SocialSecNumberQualityCode'
        xpPersonSocialSecurityNumberQualityCodeDateEffective = 'ext:SocialSecurityNumber/hmis:SocialSecNumberQualityCode/@hmis:dateEffective'
        xpPersonSocialSecurityNumberQualityCodeDateCollected = 'ext:SocialSecurityNumber/hmis:SocialSecNumberQualityCode/@hmis:dateCollected' 

        itemElements = element.xpath(xpPerson, namespaces = self.nsmap)
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                hmisxml30reader.existence_test_and_add(self, 'person_id_id_num', item.xpath(xpPersonIDNum, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_id_id_str', item.xpath(xpPersonIDStr, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_id_delete_occurred_date', item.xpath(xpPersonIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_id_delete_effective', item.xpath(xpPersonIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_id_delete', item.xpath(xpPersonDelete, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_date_of_birth_hashed', item.xpath(xpPersonDateOfBirthHashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_date_of_birth_hashed_date_collected', item.xpath(xpPersonDateOfBirthHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_date_of_birth_unhashed', item.xpath(xpPersonDateOfBirthUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_date_of_birth_unhashed_date_collected', item.xpath(xpPersonDateOfBirthUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_date_of_birth_type', item.xpath(xpPersonDateOfBirthType, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_date_of_birth_type_date_collected', item.xpath(xpPersonDateOfBirthTypeDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_ethnicity_hashed', item.xpath(xpPersonEthnicityHashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_ethnicity_unhashed', item.xpath(xpPersonEthnicityUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_ethnicity_unhashed_date_collected', item.xpath(xpPersonEthnicityUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_ethnicity_hashed_date_collected', item.xpath(xpPersonEthnicityHashedDateCollected, namespaces = self.nsmap), 'attribute_date')                                
                hmisxml30reader.existence_test_and_add(self, 'person_gender_hashed', item.xpath(xpPersonGenderHashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_gender_unhashed', item.xpath(xpPersonGenderUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_gender_unhashed_date_collected', item.xpath(xpPersonGenderUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_gender_hashed_date_collected', item.xpath(xpPersonGenderHashedDateCollected, namespaces = self.nsmap), 'attribute_date')                                                
                hmisxml30reader.existence_test_and_add(self, 'person_gender_unhashed_date_effective', item.xpath(xpPersonGenderUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_gender_hashed_date_effective', item.xpath(xpPersonGenderHashedDateEffective, namespaces = self.nsmap), 'attribute_date')                                                                
                hmisxml30reader.existence_test_and_add(self, 'person_legal_first_name_hashed', item.xpath(xpPersonLegalFirstNameHashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_first_name_unhashed', item.xpath(xpPersonLegalFirstNameUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_first_name_hashed_date_collected', item.xpath(xpPersonLegalFirstNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_first_name_unhashed_date_collected', item.xpath(xpPersonLegalFirstNameUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_first_name_hashed_date_effective', item.xpath(xpPersonLegalFirstNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_first_name_unhashed_date_effective', item.xpath(xpPersonLegalFirstNameUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_legal_last_name_hashed', item.xpath(xpPersonLegalLastNameHashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_last_name_unhashed', item.xpath(xpPersonLegalLastNameUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_last_name_hashed_date_collected', item.xpath(xpPersonLegalLastNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_last_name_unhashed_date_collected', item.xpath(xpPersonLegalLastNameUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_legal_last_name_hashed_date_effective', item.xpath(xpPersonLegalLastNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_last_name_unhashed_date_effective', item.xpath(xpPersonLegalLastNameUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                                
                hmisxml30reader.existence_test_and_add(self, 'person_legal_middle_name_hashed', item.xpath(xpPersonLegalMiddleNameHashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_middle_name_unhashed', item.xpath(xpPersonLegalMiddleNameUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_middle_name_hashed_date_collected', item.xpath(xpPersonLegalMiddleNameHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_middle_name_unhashed_date_collected', item.xpath(xpPersonLegalMiddleNameUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_legal_middle_name_hashed_date_effective', item.xpath(xpPersonLegalMiddleNameHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_middle_name_unhashed_date_effective', item.xpath(xpPersonLegalMiddleNameUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                                           
                hmisxml30reader.existence_test_and_add(self, 'person_legal_suffix_hashed', item.xpath(xpPersonLegalSuffixHashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_suffix_unhashed', item.xpath(xpPersonLegalSuffixUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_suffix_hashed_date_collected', item.xpath(xpPersonLegalSuffixHashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_suffix_unhashed_date_collected', item.xpath(xpPersonLegalSuffixUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_legal_suffix_hashed_date_effective', item.xpath(xpPersonLegalSuffixHashedDateEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_legal_suffix_unhashed_date_effective', item.xpath(xpPersonLegalSuffixUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')                                           
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_unhashed', item.xpath(xpPersonSocialSecurityNumberUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_hashed', item.xpath(xpPersonSocialSecurityNumberHashed, namespaces = self.nsmap), 'text')                
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_hashed_date_collected', item.xpath(xpPersonSocialSecurityNumberHashedDateCollected, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_unhashed_date_collected', item.xpath(xpPersonSocialSecurityNumberUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_hashed_date_effective', item.xpath(xpPersonSocialSecurityNumberHashedDateEffective, namespaces = self.nsmap), 'attribute_date')                
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_unhashed_date_effective', item.xpath(xpPersonSocialSecurityNumberUnhashedDateEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_quality_code', item.xpath(xpPersonSocialSecurityNumberQualityCode, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_quality_code_date_effective', item.xpath(xpPersonSocialSecurityNumberQualityCodeDateEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_social_security_number_quality_code_date_collected', item.xpath(xpPersonSocialSecurityNumberQualityCodeDateCollected, namespaces = self.nsmap), 'attribute_date')
                
                ''' Foreign Keys '''
                hmisxml30reader.existence_test_and_add(self, 'export_index_id', self.export_index_id, 'no_handling')
                
                ''' Shred to database '''
                hmisxml30reader.shred(self, self.parse_dict, dbobjects.Person)
    
                ''' Parse sub-tables '''
                hmisxml30reader.parse_site_service_participation(self, item)
                hmisxml30reader.parse_need(self, item)          
                hmisxml30reader.parse_service_event(self, item)
                self.parse_person_historical(item)
                hmisxml30reader.parse_release_of_information(self, item)
                hmisxml30reader.parse_other_names(self, item)
                self.parse_races(item)

    def parse_person_historical(self, element):
        ''' Element paths '''
        xpPersonHistorical = 'ext:PersonHistorical'        
        xpPersonHistoricalIDIDNum = 'ext:PersonHistoricalID/hmis:IDNum'
        xpPersonHistoricalIDIDStr = 'ext:PersonHistoricalID/hmis:IDStr'
        xpPersonHistoricalIDDelete = 'ext:PersonHistoricalID/@hmis:delete'
        xpPersonHistoricalIDDeleteEffective = 'ext:PersonHistoricalID/@hmis:deleteEffective'
        xpPersonHistoricalIDDeleteOccurredDate = 'ext:PersonHistoricalID/@hmis:deleteOccurredDate'
        xpSiteServiceID = 'hmis:SiteServiceID'

        itemElements = element.xpath(xpPersonHistorical, namespaces = self.nsmap)
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                hmisxml30reader.existence_test_and_add(self, 'person_historical_id_id_num', item.xpath(xpPersonHistoricalIDIDNum, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_historical_id_id_str', item.xpath(xpPersonHistoricalIDIDStr, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'person_historical_id_delete', item.xpath(xpPersonHistoricalIDDelete, namespaces = self.nsmap), 'attribute_text')
                hmisxml30reader.existence_test_and_add(self, 'person_historical_id_delete_effective', item.xpath(xpPersonHistoricalIDDeleteEffective, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'person_historical_id_delete_occurred_date', item.xpath(xpPersonHistoricalIDDeleteOccurredDate, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'site_service_id', item.xpath(xpSiteServiceID, namespaces = self.nsmap), 'text')

                ''' Foreign Keys '''
                try: hmisxml30reader.existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
                except: pass
                try: hmisxml30reader.existence_test_and_add(self, 'site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
                except: pass
                
                ''' Shred to database '''
                hmisxml30reader.shred(self, self.parse_dict, dbobjects.PersonHistorical)
    
                ''' Parse sub-tables '''
                hmisxml30reader.parse_housing_status(self, item)   
                hmisxml30reader.parse_veteran(self, item)
                hmisxml30reader.parse_vocational_training(self, item)         
                hmisxml30reader.parse_substance_abuse_problem(self, item)         
                hmisxml30reader.parse_pregnancy(self, item)         
                hmisxml30reader.parse_prior_residence(self, item)         
                hmisxml30reader.parse_physical_disability(self, item)         
                hmisxml30reader.parse_non_cash_benefits(self, item)         
                hmisxml30reader.parse_non_cash_benefits_last_30_days(self, item)         
                hmisxml30reader.parse_mental_health_problem(self, item)         
                hmisxml30reader.parse_length_of_stay_at_prior_residence(self, item)         
                hmisxml30reader.parse_income_total_monthly(self, item)         
                hmisxml30reader.parse_hud_chronic_homeless(self, item)         
                hmisxml30reader.parse_income_last_30_days(self, item)         
                hmisxml30reader.parse_highest_school_level(self, item)         
                hmisxml30reader.parse_hiv_aids_status(self, item)         
                hmisxml30reader.parse_health_status(self, item)         
                hmisxml30reader.parse_engaged_date(self, item)         
                hmisxml30reader.parse_employment(self, item)         
                hmisxml30reader.parse_domestic_violence(self, item)         
                hmisxml30reader.parse_disabling_condition(self, item)         
                hmisxml30reader.parse_developmental_disability(self, item)         
                hmisxml30reader.parse_destinations(self, item)         
                hmisxml30reader.parse_degree(self, item)         
                hmisxml30reader.parse_currently_in_school(self, item)         
                hmisxml30reader.parse_contact_made(self, item)         
                hmisxml30reader.parse_child_enrollment_status(self, item)         
                hmisxml30reader.parse_chronic_health_condition(self, item) 
                hmisxml30reader.parse_income_and_sources(self, item)
                hmisxml30reader.parse_hud_homeless_episodes(self, item)
                hmisxml30reader.parse_person_address(self, item)
                hmisxml30reader.parse_email(self, item)                              
                hmisxml30reader.parse_phone(self, item)      
                self.parse_foster_child_ever(item)
                            
    def parse_foster_child_ever(self, element):
        ''' Element paths '''
        itemElements = element.xpath('ext:FosterChildEver', namespaces = self.nsmap)
        if itemElements is not None:
            xpFosterChildEver = '.'
            xpFosterChildEverDateCollected = './@hmis:dateCollected'
            xpFosterChildEverDateEffective = './@hmis:dateEffective'
            for item in itemElements:
                self.parse_dict = {}

                ''' Map elements to database columns '''
                hmisxml30reader.existence_test_and_add(self, 'foster_child_ever', item.xpath(xpFosterChildEver, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'foster_child_ever_date_collected', item.xpath(xpFosterChildEverDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'foster_child_ever_date_effective', item.xpath(xpFosterChildEverDateEffective, namespaces = self.nsmap), 'attribute_date')
                ''' Foreign Keys '''
                hmisxml30reader.existence_test_and_add(self, 'person_historical_index_id', self.person_historical_index_id, 'no_handling')
                
                ''' Shred to database '''
                hmisxml30reader.shred(self, self.parse_dict, dbobjects.FosterChildEver)
    
                ''' Parse sub-tables '''
                         
    def parse_races(self, element):
        ''' Element paths '''
        xpRaces = 'ext:Race'
        xpRaceUnhashed = 'hmis:Unhashed'
        xpRaceUnhashedDateCollected = 'hmis:Unhashed/@hmis:dateCollected'
        xpRaceUnhashedDataCollectionStage = 'hmis:Unhashed/@hmis:dataCollectionStage'
        xpRaceHashed = 'hmis:Hashed'

        itemElements = element.xpath(xpRaces, namespaces = self.nsmap)
        if itemElements is not None:
            for item in itemElements:
                self.parse_dict = {}
                
                ''' Map elements to database columns '''
                hmisxml30reader.existence_test_and_add(self, 'race_unhashed', item.xpath(xpRaceUnhashed, namespaces = self.nsmap), 'text')
                hmisxml30reader.existence_test_and_add(self, 'race_date_collected', item.xpath(xpRaceUnhashedDateCollected, namespaces = self.nsmap), 'attribute_date')
                hmisxml30reader.existence_test_and_add(self, 'race_data_collection_stage', item.xpath(xpRaceUnhashedDataCollectionStage, namespaces = self.nsmap), 'attribute_text')
                hmisxml30reader.existence_test_and_add(self, 'race_hashed', item.xpath(xpRaceHashed, namespaces = self.nsmap), 'text')

                ''' Foreign Keys '''
                hmisxml30reader.existence_test_and_add(self, 'person_index_id', self.person_index_id, 'no_handling')
                
                ''' Shred to database '''
                hmisxml30reader.shred(self, self.parse_dict, dbobjects.Races)
    
                ''' Parse sub-tables '''

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
            
        reader = OCCHUDHMISXML30Reader(xml_file)
        tree = reader.read()
        reader.process_data(tree)
        xml_file.close()

if __name__ == "__main__":
    sys.exit(main())