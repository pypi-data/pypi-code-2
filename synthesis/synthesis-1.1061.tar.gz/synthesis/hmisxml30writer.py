from clsexceptions import SoftwareCompatibilityError
import os.path
import dbobjects as dbobjects
import xmlutilities
from sys import version
from conf import settings
from datetime import datetime
from sqlalchemy import or_, and_, between

''' HUD 3.0 XML export plugin '''

'''
ToDo:

Generate these elements (Just reverse of Reader Steps)
parse_source(root_element)

    Get Related:
    self.parse_export(item)
    
        Get Related:
        self.parse_household(item)
            Get Related:
            self.parse_members(item)
            
        self.parse_region(item)
        self.parse_agency(item)
        
            Get Related:
            self.parse_service_group(item)
            self.parse_license_accreditation(item)
            self.parse_agency_service(item)
            self.parse_url(item)
            self.parse_aka(item)
            self.parse_resource_info(item)
            
                Get Related:
                self.parse_contact(item)            
                self.parse_email(item)      
                self.parse_phone(item)
                        
            self.parse_contact(item)
            
                Get  Related:
                self.parse_email(item)      
                self.parse_phone(item)
                    
            self.parse_email(item)      
            self.parse_phone(item)      
            self.parse_site(item)
            
                Get Related:
                self.parse_url(item)
                self.parse_spatial_location(item)
                self.parse_other_address(item)
                self.parse_cross_street(item)
                self.parse_aka(item)
                self.parse_site_service(item)
                    
                    Get Related:
                    self.parse_seasonal(item)
                    self.parse_residency_requirements(item)
                    self.parse_pit_count_set(item)
                    
                        Get Related:
                        self.parse_pit_counts(item)
                        
                    self.parse_other_requirements(item)
                    self.parse_languages(item)
                    
                        Get Related:
                        self.parse_time_open(item)
                        
                            Get Related:
                            self.parse_time_open_day(item, day)
                        
                    self.parse_time_open(item)
                    
                        Get Related:
                        self.parse_time_open_day(item, day)
                    
                    self.parse_inventory(item)
                    self.parse_income_requirements(item)
                    self.parse_hmis_asset(item)
                    
                        Get Related:
                        self.parse_assignment_period(item)
                        
                    self.parse_geographic_area_served(item)
                    self.parse_documents_required(item)
                    self.parse_aid_requirements(item)
                    self.parse_age_requirements(item)
                    self.parse_application_process(item)
                    self.parse_taxonomy(item)
                    self.parse_family_requirements(item)
                    self.parse_resource_info(item)
                    
                        Get Related:
                        self.parse_contact(item)
                        
                            Get Related:
                            self.parse_email(item)      
                            self.parse_phone(item)
                        
                        self.parse_email(item)      
                        self.parse_phone(item)
                
                self.parse_languages(item)
                
                    Get Related:
                    self.parse_time_open(item)
                    
                        Get Related:
                        self.parse_time_open_day(item, day)
                            
                self.parse_time_open(item)
                
                    Get Related:
                    self.parse_time_open_day(item, day)
                    
                self.parse_inventory(item)
                self.parse_contact(item)
                    
                    Get  Related:
                    self.parse_email(item)      
                    self.parse_phone(item)
                    
                self.parse_email(item)      
                self.parse_phone(item)
        
        self.parse_person(item)
        
            Get Related:
            self.parse_site_service_participation(item)
            
                Get Related:
                self.parse_reasons_for_leaving(item)  
                self.parse_need(item)
                    
                    Get Related:
                    self.parse_taxonomy(item)
                    self.parse_service_event(item)
                        
                self.parse_service_event(item)
                
                    Get Related:
                    self.parse_service_event_notes(item)     
                    self.parse_funding_source(item)
                    
                self.parse_person_historical(item)
                
                    Get Related:
                    self.parse_housing_status(item)   
                    self.parse_veteran(item)
                    
                        Get Related:
                        self.parse_veteran_military_branches(item)
                        self.parse_veteran_military_service_duration(item)  
                        self.parse_veteran_served_in_war_zone(item)         
                        self.parse_veteran_service_era(item)         
                        self.parse_veteran_veteran_status(item)         
                        self.parse_veteran_warzones_served(item)
                        
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
                    
                        Get Related:
                        self.parse_degree_code(item)
                    
                    self.parse_currently_in_school(item)         
                    self.parse_contact_made(item)         
                    self.parse_child_enrollment_status(item)
                    
                        Get Related:
                        self.parse_child_enrollment_status_barrier(item)
                    
                    self.parse_chronic_health_condition(item) 
                    self.parse_income_and_sources(item)
                    self.parse_hud_homeless_episodes(item)
                    self.parse_person_address(item)
                    self.parse_email(item)                              
                    self.parse_phone(item)
                
            self.parse_need(item)
            
                Get Related:
                self.parse_taxonomy(item)
                self.parse_service_event(item)
                
                    Get Related:
                    self.parse_service_event_notes(item)     
                    self.parse_funding_source(item)
                    
            self.parse_service_event(item)
            
                Get Related:
                self.parse_service_event_notes(item)     
                self.parse_funding_source(item)
            
            self.parse_person_historical(item)
            self.parse_release_of_information(item)
            self.parse_other_names(item)
            self.parse_races(item)
            
        self.parse_service(item)
        
            Get Related:
            self.parse_funding_source(item)
            self.parse_inventory(item)
            
        self.parse_site(item)
            
            Get Related:
            self.parse_url(item)
            self.parse_spatial_location(item)
            self.parse_other_address(item)
            self.parse_cross_street(item)
            self.parse_aka(item)
            self.parse_site_service(item)
            
                Get Related:
                self.parse_seasonal(item)
                self.parse_residency_requirements(item)
                self.parse_pit_count_set(item)
                
                    Get Related:
                    self.parse_pit_counts(item)
                    
                self.parse_other_requirements(item)
                self.parse_languages(item)
                
                    Get Related:
                    self.parse_time_open(item)
                    
                        Get Related:
                        self.parse_time_open_day(item, day)
                    
                self.parse_time_open(item)
                
                    Get Related:
                    self.parse_time_open_day(item, day)
                
                self.parse_inventory(item)
                self.parse_income_requirements(item)
                self.parse_hmis_asset(item)
                
                    Get Related:
                    self.parse_assignment_period(item)
                    
                self.parse_geographic_area_served(item)
                self.parse_documents_required(item)
                self.parse_aid_requirements(item)
                self.parse_age_requirements(item)
                self.parse_application_process(item)
                self.parse_taxonomy(item)
                self.parse_family_requirements(item)
                self.parse_resource_info(item)
                
                    Get Related:
                    self.parse_contact(item)
                    
                        Get Related:
                        self.parse_email(item)      
                        self.parse_phone(item)
                    
                    self.parse_email(item)      
                    self.parse_phone(item)
            
            self.parse_languages(item)
            self.parse_time_open(item)            
            self.parse_inventory(item)
            self.parse_contact(item)
            
                Get Related:
                self.parse_email(item)      
                self.parse_phone(item)
            
            self.parse_email(item)      
            self.parse_phone(item) 
        
        self.parse_site_service(item)



'''
thisVersion = version[0:3]
if float(settings.MINPYVERSION) < float(thisVersion):
    try:
        # FIXME ( remove this once done debugging namespace issue )
        #import xml.etree.cElementTree as ET
        import xml.etree.ElementTree as ET
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

# SBB20100810 Making this generic so it can be configured from the settings file
class HMISXMLWriter(dbobjects.DatabaseObjects):
    
    
    hmis_namespace = "http://www.hmis.info/schema/3_0/HUD_HMIS.xsd" 
    airs_namespace = "http://www.hmis.info/schema/3_0/AIRS_3_0_mod.xsd"
    nsmap = {"hmis" : hmis_namespace, "airs" : airs_namespace}  


    #####  insert xml specific stuff from 2.8
    
    def __init__(self, poutDirectory, processingOptions, debug=False): #, debugMessages=None):
        self.errorMsgs = []
        self.iDG = xmlutilities.IDGeneration()
        # adding a debug switch that is managed in the INI
        self.debug = debug
        self.outDirectory = poutDirectory
        self.mappedObjects = dbobjects.DatabaseObjects()
        self.options = processingOptions
        
    def write(self):    
        self.startTransaction()
        self.processXML()
        self.prettify()
        #self.writeOutXML()
        #xmlutilities.writeOutXML()
        xmlutilities.writeOutXML(self)
        #self.commitTransaction()
        return True

    def prettify(self):
        xmlutilities.indent(self.root_element)
    
    def startTransaction(self):
        # fixme (when in VirtualEnv)
        #self.session = self.mappedObjects.session(echo_uow=True)
        self.session = self.mappedObjects.session(echo_uow=True)
        #pass
    # instantiate DB Object layer
    # Create the transaction
    # get a handle to our session object
    
    def createDoc(self):
        root_element = ET.Element("hmis:Sources")
        root_element.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        root_element.attrib["xmlns:airs"]="http://www.hmis.info/schema/3_0/AIRS_3_0_mod.xsd"
        root_element.attrib["xmlns:hmis"]="http://www.hmis.info/schema/3_0/HUD_HMIS.xsd"
        #root_element.attrib["xsi:noNamespaceSchemaLocation"] = "HUD_HMIS.xsd" 
        root_element.attrib["xsi:schemaLocation"] = "http://www.hmis.info/schema/3_0/HUD_HMIS.xsd http://www.hmis.info/schema/3_0/HUD_HMIS.xsd"
        root_element.attrib["hmis:version"] = "3.0"
        root_element.text = "\n"
        return root_element

    def createOtherNames(self, xml):
        othernames = ET.SubElement(xml, "hmis:OtherNames")
        return othernames
    
    def customizeOtherNames(self, xml):
        attributes = [
        ]
        elements = [
            'OtherFirstName',
            'OtherMiddleName',
            'OtherLastName',
            'OtherSuffix',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        return xml
    
    def createPersonHistorical(self, xml):
        personhistorical = ET.SubElement(xml, "hmis:PersonHistorical")
        return personhistorical
    
    def customizePersonHistorical(self, xml):
        attributes = [
        ]
        elements = [
            'PersonHistoricalID',
            'SiteServiceID',
            'ChildEnrollmentStatus',
            'ChronicHealthCondition',
            'CurrentlyInSchool',
            'ContactsMade',
            'Degree',
            'Destinations',
            'DisablingCondition',
            'DevelopmentalDisability',
            'DomesticViolence',
            'Employment',
            'EngagedDate',
            'HealthStatus',
            'HighestSchoolLevel',
            'HIVAIDSStatus',
            'HousingStatus',
            'HUDChronicHomeless',
            'HUDHomelessEpisodes',
            'IncomeLast30Days',
            'IncomeAndSources',
            'IncomeTotalMonthly',
            'LengthOfStayAtPriorResidence',
            'MentalHealthProblem',
            'NonCashBenefitsLast30Days',
            'NonCashBenefits',
            'PersonAddress',
            'PersonEmail',
            'PersonPhoneNumber',
            'PhysicalDisability',
            'Pregnancy',
            'PriorResidence',
            'SubstanceAbuseProblem',
            'Veteran',
            'VocationalTraining',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        # customize IncomeAndSources Subelements
        se = theElements['IncomeAndSources']
        subElements = ['IncomeSourceCode', 'IncomeSourceOther']
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # HIVAIDSStatus
        elementName = "HIVAIDSStatus"
        se = theElements[elementName]
        subElements = ['HasHIVAIDS', 'ReceiveHIVAIDSServices']
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # MentalHealthProblem
        elementName = "MentalHealthProblem"
        se = theElements[elementName]
        subElements = ['HasMentalHealthProblem', 'MentalHealthIndefinite', 'ReceiveMentalHealthServices']
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # NonCashBenefits
        elementName = "NonCashBenefits"
        se = theElements[elementName]
        NonCashBenefit = self.createSubElement(se, 'hmis', "NonCashBenefit")
        
        subElements = ['NonCashBenefitID',]
        self.customizeSubElements(NonCashBenefit, 'hmis', subElements, data=[])
        
        # PersonAddress
        elementName = "PersonAddress"
        se = theElements[elementName]
        subElements = ['AddressPeriod', 'PreAddressLine', 'Line1','Line2','City','County','State','ZIPCode', 'Country','IsLastPermanentZIP','ZIPQualityCode',]
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # PersonEmail
        elementName = "PersonEmail"
        se = theElements[elementName]
        
        # PersonPhoneNumber
        elementName = "PersonEmail"
        se = theElements[elementName]
        
        # PhysicalDisability
        elementName = "PhysicalDisability"
        se = theElements[elementName]
        subElements = ['HasPhysicalDisability', 'ReceivePhysicalDisabilityServices', ]
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # Pregnancy
        elementName = "Pregnancy"
        se = theElements[elementName]
        subElements = ['PregnancyID', 'PregnancyStatus', 'DueDate', ]
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # PriorResidence
        elementName = "PriorResidence"
        se = theElements[elementName]
        subElements = ['PriorResidenceID', 'PriorResidenceCode', 'PriorResidenceOther',  ]
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # SubstanceAbuseProblem
        elementName = "SubstanceAbuseProblem"
        se = theElements[elementName]
        subElements = ['HasSubstanceAbuseProblem', 'SubstanceAbuseIndefinite', 'ReceiveSubstanceAbuseServices',  ]
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # Veteran
        elementName = "Veteran"
        se = theElements[elementName]
        subElements = ['MilitaryBranches', 'MilitaryServiceDuration', 'ServedInWarZone', 'ServiceEra', 'VeteranStatus', 'WarZonesServed']
        self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        # VocationalTraining
        elementName = "VocationalTraining"
        se = theElements[elementName]
        
        # assing data values...
        
        return xml
    
    def createRace(self, xml):
        race = ET.SubElement(xml, "hmis:Race")
        return race
    
    def customizeRace(self, xml):
        # lookup the value and assign it
        pass
    
    def createReleaseOfInformation(self, xml):
        releaseofinformation = ET.SubElement(xml, "hmis:ReleaseOfInformation")
        return releaseofinformation
    
    def customizeReleaseOfInformation(self, xml):
        attributes = [
        ]
        elements = [
            'ReleaseOfInformationID',
            'SiteServiceID',
            'Documentation',
            'EffectivePeriod',
            'ReleaseGranted',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        return xml
    
    def createServiceEvent(self, xml):
        serviceevent = ET.SubElement(xml, "hmis:ServiceEvent")
        return serviceevent
    
    def customizeServiceEvent(self, xml):
        attributes = [
        ]
        elements = [
            'ServiceEventID',
            'SiteServiceID',
            'HouseholdID',
            'FundingSources',
            'IsReferral',
            'QuantityOfServiceEvent',
            'QuantityOfServiceEventUnit',
            'ServiceEventAIRSCode',
            'ServiceEventEffectivePeriod',
            'ServiceEventProvisionDate',
            'ServiceEventRecordedDate',
            'ServiceEventNotes',
            'ServiceEventIndFam',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        return xml
    
    def createSiteServiceParticipation(self, xml):
        siteserviceparticipation = ET.SubElement(xml, "hmis:SiteServiceParticipation")
        return siteserviceparticipation
    
    def customizeSiteServiceParticipation(self, xml):
        attributes = [
        ]
        elements = [
            'SiteServiceParticipationID',
            'SiteServiceID',
            'HouseholdID',
            'Need',
            'ParticipationDates',
            'PersonHistorical',
            'ReasonsForLeaving',
            'ServiceEvent',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        return xml

    def createTaxonomy(self, xml):
        taxonomy = ET.SubElement(xml, "hmis:Taxonomy")
        return taxonomy
    
    def customizeTaxonomy(self, xml, taxonomyData=[]):
        
        #bHasParentElement = False
        elementCounter = 0
        taxonomyElement = ET.SubElement(xml, "airs:%s" % 'Taxonomy')
        
        for taxonomyRow in taxonomyData:
            
            if elementCounter == 2:
                elementCounter = 0
                taxonomyElement = ET.SubElement(xml, "airs:%s" % 'Taxonomy')
                
            # make subelements
            taxonomySubElement = ET.SubElement(taxonomyElement, "airs:%s" % 'Code')
            taxonomySubElement.text = taxonomyRow.code
            
            elementCounter += 1
    
    def createPerson(self, records):
        person = ET.SubElement(records, "hmis:Person")
        return person
    
    def customizePerson(self, xml):
        attributes = [
        ]
        elements = [
            'PersonID',
            'DateOfBirth',
            'Ethnicity',
            'Gender',
            'LegalFirstName',
            'LegalLastName',
            'LegalMiddleName',
            'LegalSuffix',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        return xml
    
    def customizePersonSSN(self, xml):
        pass
    
    def createHousehold(self, records):
        household = ET.SubElement(records, "hmis:Household")
        return household
        
    def customizeHousehold(self, xml):
        attributes = [
        ]
        elements = [
            'HouseholdID',
            'HeadOfHouseholdID',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        return xml
    
    def generateElements(self, xml, namespaceString, elementDictionary):
        
        theElements = {}
        for element in elementDictionary:
            theElements[element] = ET.SubElement(xml, namespaceString + ":%s" % element)
            
        return theElements
    
    def createMembers(self, household):
        members = ET.SubElement(household, "members")
        return members
    
    def createMember(self, members):
        keyval = 'member'
        recID = self.iDG.generateRecID(keyval) 
        member = ET.SubElement(members, "member")
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

    def createRegion(self, records):
        region = ET.SubElement(records, "region")
        return region
        
        
        
        
        
        
        
        
        
        
        
        xpAgency = 'hmis:Agency'
        xpAgencyDelete = '@hmis:Delete'
        xpAgencyDeleteOccurredDate = '@hmis:DeleteOccurredDate'
        xpAgencyDeleteEffective = '@hmis:DeleteEffective'
        xpAirsKey = 'airs:Key'
        xpAirsName = 'airs:Name'
        xpAgencyDescription = 'airs:AgencyDescription'
        xpIRSStatus = 'airs:IRSStatus'
        xpSourceOfFunds = 'airs:SourceOfFunds'
        xpRecordOwner = '@hmis:RecordOwner'
        xpFEIN = '@hmis:FEIN'
        xpYearInc = '@hmis:YearInc'
        xpAnnualBudgetTotal = '@hmis:AnnualBudgetTotal'
        xpLegalStatus = '@hmis:LegalStatus'
        xpExcludeFromWebsite = '@hmis:ExcludeFromWebsite'
        xpExcludeFromDirectory = '@hmis:ExcludeFromDirectory'       

    def createAgency_old2(self, records):
        agency = ET.SubElement(records, "agency")
        return agency
        
    def createAgency_old(self, records):



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
        xpPublicAccessToTransportation = 'airs:PublicAccessToTransportation'
        xpYearInc = 'airs:YearInc'
        xpAnnualBudgetTotal = 'airs:AnnualBudgetTotal'
        xpLegalStatus = 'airs:LegalStatus'
        xpExcludeFromWebsite = 'airs:ExcludeFromWebsite'
        xpExcludeFromDirectory = 'airs:ExcludeFromDirectory'
        xpAgencyKey = 'airs:AgencyKey'


    def createSite_AKA(self, xml):
        aka = ET.SubElement(xml, "airs:AKA")
        return aka
    
    def customizeSite_AKA(self, xml):
        attributes = [
        ]
        elements = [
            'Name',
            'Confidential',
            'Description',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "airs", elements)
        
        # push data into elements here..
        
        return xml
    
    def createSite(self, xml):
        site = ET.SubElement(xml, "hmis:Site")
        return site
    
    def customizeSite(self, xml):
        
        attributes = [
        ]
        elements = [
            'Key',
            'Name',
            'SiteDescription',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "airs", elements)
        
        # push data into elements here..
        
        return xml
    
    def customizeDOW(self, xml, data=[]):
        
        DsOW = ["Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            ]
        
        for DOW in DsOW:
            elementDOW = self.createSiteService_TimeOpen_DayOfWeek(xml, DOW)
            # now customize the DOW
            self.customizeSiteService_TimeOpen_DayOfWeek(elementDOW)
            
    
    def manageSiteService(self, export):
        # SiteService
        siteservice = self.createSiteService(export)
        siteservice = self.customizeSiteService(siteservice, siteServiceData=None)
        
        # Sub Element of SiteService
        phone = self.createSiteServicePhone(siteservice)
        phone = self.customizeSiteServicePhone(phone)
        
        ###########################################################################
        # the fix is to make timeOpen a subroutine so it can be callled from other elements
        # self.processTimeOpen(element)
        # take the lines between hashes and push this into a seperate function, then call that function.
        
        # TimeOpen SubElement
        timeopen = self.createSiteService_TimeOpen(siteservice)
        timeopen = self.customizeSiteService_TimeOpen(timeopen)
        
        # monday, tuesday, wednesday...
        self.customizeDOW(timeopen, data=[])
        
        #DsOW = ["Sunday",
        #   "Monday",
        #   "Tuesday",
        #   "Wednesday",
        #   "Thursday",
        #   "Friday",
        #   "Saturday",
        #   ]
        #for DOW in DsOW:
        #   elementDOW = self.createSiteService_TimeOpen_DayOfWeek(timeopen, DOW)
        #   # now customize the DOW
        #   self.customizeSiteService_TimeOpen_DayOfWeek(elementDOW)
            
        # now terminate the timeopen element with notes
        elementnotes = self.createSiteService_TimeOpen_Notes(timeopen, 'Notes')
        
        ###########################################################################
        
        # Seasonal element
        seasonal = self.createSiteService_Seasonal(siteservice)
        seasonal = self.customizeSiteService_Seasonal(seasonal)
        
        # Taxonomy
        taxonomy = self.createTaxonomy(siteservice)
        taxonomy = self.customizeTaxonomy(taxonomy, [])
        
        # Languages
        languages = self.createSubElement(siteservice, ns = 'airs', element = 'Languages')
        subElements = ['Name',]
        languages = self.customizeSubElements(languages, 'airs', subElements, data=[])
        
        # monday, tuesday, wednesday...
        timeopen = self.createSiteService_TimeOpen(languages)
        self.customizeDOW(timeopen, data=[])
        
        # now terminate the timeopen element with notes
        elementnotes = self.createSiteService_TimeOpen_Notes(timeopen, 'Notes')
        
        # GeographicAreaServed
        #elementName = "GeographicAreaServed"
        #se = theElements[elementName]
        #subElements = ['HasSubstanceAbuseProblem', 'SubstanceAbuseIndefinite', 'ReceiveSubstanceAbuseServices',  ]
        #self.customizeSubElements(se, 'hmis', subElements, data=[])
        
        
    # Generic Subelement creator, needs xml=element, ns=namespace and element=element name
    def createSubElement(self, xml, ns, element):
        subelement = ET.SubElement(xml, "%s:%s" % (ns, element))
        return subelement
    
    def customizeSubElements(self, xml, ns, subElements, data):
        
        attributes = [
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, ns, subElements)
        
        # push data into elements here..
        
        return xml
        
    def createSiteService_Seasonal(self, xml):
        ns = 'airs'
        element = 'Seasonal'
        seasonal = ET.SubElement(xml, "%s:%s" % (ns, element))
        return seasonal
    
    def customizeSiteService_Seasonal(self, xml):
        ns = 'airs'
        attributes = [
        ]
        elements = [
            'Description',
            'StartDate',
            'EndDate',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, ns, elements)
        
        # push data into elements here..
        
        return xml
    
    def createSiteService(self, xml):
        siteservice = ET.SubElement(xml, "hmis:SiteService")
        return siteservice
    
    def customizeSiteService(self, xml):
        attributes = [
        ]
        elements = [
            'Name',
            'Key',
            'Description',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "airs", elements)
        
        # push data into elements here..
        
        return xml
    
    def createSiteService_TimeOpen(self, xml):
        timeopen = ET.SubElement(xml, "airs:TimeOpen")
        return timeopen
    
    def createSiteService_TimeOpen_DayOfWeek(self, xml, dow):
        timeopen = ET.SubElement(xml, "airs:%s" % dow)
        return timeopen
    
    def createSiteService_TimeOpen_Notes(self, xml, elementName):
        to_notes = ET.SubElement(xml, "airs:%s" % elementName)
        return to_notes
    
    def customizeSiteService_TimeOpen_Notes(self, xml):
        pass
    
    def customizeSiteService_TimeOpen_DayOfWeek(self, xml):
        ns = 'airs'
        attributes = [
        ]
        elements = [
            'From',
            'To',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, ns, elements)
        
        # push data into elements here..
        
        return xml
    
    def customizeSiteService_TimeOpen(self, xml):
        ns = 'airs'             # check this either hmis or airs
        attributes = [
            
        ]
        elements = [
            
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, ns, elements)
        
        # push data into elements here..
        
        return xml
    
    def createSiteServicePhone(self, xml):
        phone = ET.SubElement(xml, "airs:Phone")
        return phone
    
    def customizeSiteServicePhone(self, xml):
        attributes = [
            'TollFree',
            'Confidential',
        ]
        elements = [
            'PhoneNumber',
            'ReasonWithheld',
            'Extension',
            'Description',
            'Type',
            'Function',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "airs", elements)
        
        # push data into elements here..
        
        return xml
    
    def createService(self, xml):
        service = ET.SubElement(xml, "hmis:Service")
        service.text = "\n"
        service.tail = "\n"
    
        return service
    def customizeService(self, xml):
        attributes = [
        ]
        elements = [
            'COCCode',
            'Configuration',
            'DirectServiceCode',
            'FundingSources',
            'GranteeIdentifier',
            'IndividualFamilyCode',
            'Inventory',
            'ResidentialTrackingMethod',
            'ServiceType',
            'ServiceEffectivePeriod',
            'ServiceRecordedDate',
            'TargetPopulationA',
            'TargetPopulationB',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        return xml
    
    
    def createNeed(self, xml):
        need = ET.SubElement(xml, "need")
        #need.attrib["date_added"] = datetime.now().isoformat()
        #need.attrib["date_updated"] = datetime.now().isoformat()
        return need
    
    def customizeNeed(self, xml):  
        attributes = [
        ]
        elements = [
            'NeedID',
            'SiteServiceID',
            'ServiceEventID',
            'NeedEffectivePeriod',
            'NeedRecordedDate',
            'NeedStatus',
        ]

        # Define the attributes
        theAttributes = {}
        #household.attrib["system_id"] = sysID
        for attribute in attributes:
            #theAttributes[attribute] = ET.SubElement(xml, "airs:%s" % field)
            xml.attrib[attribute] = ''
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        #for element in elements:
        #   theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        theElements = self.generateElements(xml, "hmis", elements)
        
        # push data into elements here..
        
        return xml
        
    def createSource(self, xml):
        source = ET.SubElement(xml, "hmis:Source")
        return source
    
    def createExport(self, xml):
        export = ET.SubElement(xml, "hmis:Export")
        return export
    
    def customizeExport(self, xml, exportData):
        exportID = ET.SubElement(xml, "hmis:ExportID")
        # setup the attributes
        self.processIDDeleteAttributes(exportID, exportData)
        IDStr = ET.SubElement(exportID, "hmis:IDStr")
        if exportData.export_id_id_id_num == "" or exportData.export_id_id_id_num is None:
            IDStr.text = exportData.export_id_id_id_str
        else:
            IDStr.text = exportData.export_id_id_id_num

        fields = [
        #'ExportID',
        'ExportDate',
        'ExportPeriod',
        #'Agency',
        #'Household',
        #'Person',
        #'Service',
        #'Site',
        #'SiteService',
        ]
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        for field in fields:
            theElements[field] = ET.SubElement(xml, "hmis:%s" % field)
        
        theElements['ExportDate'].text = exportData.export_date.isoformat()
        
        # create new elements for start period and end period
        startPeriod = ET.SubElement(theElements['ExportPeriod'], "hmis:StartDate")
        startPeriod.text = exportData.export_period_start_date.isoformat()
        
        # End Period
        endPeriod = ET.SubElement(theElements['ExportPeriod'], "hmis:EndDate")
        endPeriod.text = exportData.export_period_end_date.isoformat()

        return xml
    
    def processIDDeleteAttributes(self, xml, data):
        # Fixme, this is currently hardwired
        xml.attrib["hmis:delete"] = "1"
        xml.attrib["hmis:deleteOccurredDate"] = datetime.now().isoformat()
        xml.attrib["hmis:deleteEffective"] = datetime.now().isoformat()
        
    def customizeSource(self, xml, sourceData):
        sourceID = ET.SubElement(xml, "hmis:SourceID")
        # setup the attributes
        self.processIDDeleteAttributes(sourceID, sourceData)
        
        IDStr = ET.SubElement(sourceID, "hmis:IDStr")
        
        if sourceData.source_id_id_id_num == "" or sourceData.source_id_id_id_num is None:
            IDStr.text = sourceData.source_id_id_id_str
        else:
            IDStr.text = sourceData.source_id_id_id_num
        
        fields = [
        'SoftwareVendor',
        'SoftwareVersion',
        'SourceContactEmail',
        'SourceContactExtension',
        'SourceContactFirst',
        'SourceContactLast',
        'SourceContactPhone',
        'SourceName',
        ]
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        for field in fields:
            theElements[field] = ET.SubElement(xml, "hmis:%s" % field)
        
        theElements['SoftwareVendor'].text = sourceData.software_vendor
        theElements['SoftwareVersion'].text = sourceData.software_version
        theElements['SourceContactEmail'].text = sourceData.source_contact_email
        theElements['SourceContactExtension'].text = sourceData.source_contact_extension
        theElements['SourceContactFirst'].text = sourceData.source_contact_first
        theElements['SourceContactLast'].text = sourceData.source_contact_last
        theElements['SourceContactPhone'].text = sourceData.source_contact_phone
        theElements['SourceName'].text = sourceData.source_name
        
        return xml
        
    def pullConfiguration(self, pExportID):
        # need to use both ExportID and Processing Mode (Test or Prod)
        source = self.session.query(dbobjects.Source).filter(dbobjects.Source.export_id == pExportID).one()
        self.configurationRec = self.session.query(dbobjects.SystemConfiguration).filter(and_(dbobjects.SystemConfiguration.source_id == source.source_id, dbobjects.SystemConfiguration.processing_mode == settings.MODE)).one()
    
    def createAgency(self, xml):
        agency = ET.SubElement(xml, "hmis:Agency")
        return agency
    
    def queryTaxonomy(self, siteServiceID=None, needID=None):
        #Column('site_service_index_id', Integer, ForeignKey(SiteService.c.id)), 
        #Column('need_index_id', Integer, ForeignKey(Need.c.id)),
        return self.session.query(dbobjects.Taxonomy).filter(and_(dbobjects.Taxonomy.site_service_index_id == siteServiceID,
                                                                         dbobjects.Taxonomy.need_index_id == needID,
                                                                 )).all()
        
    def querySpatialLocation(self, siteID=None, agencyLocationID=None):
        return self.session.query(dbobjects.SpatialLocation).filter(and_(dbobjects.SpatialLocation.site_index_id == siteID,
                                                                         dbobjects.SpatialLocation.agency_location_index_id == agencyLocationID,
                                                                 )).all()
    def querySiteService(self, exportID=None, reportID=None, siteID=None, agencyLocationID=None):
#        Column('export_index_id', String(50), ForeignKey(Export.c.export_id)),
#        Column('report_index_id', String(50), ForeignKey(Report.c.report_id)), 
#        Column('site_index_id', Integer, ForeignKey(Site.c.id)),
#        Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.c.id)),
        return self.session.query(dbobjects.SiteService).filter(and_(dbobjects.SiteService.export_index_id == exportID,
                                                                   dbobjects.SiteService.report_index_id == reportID,
                                                                   dbobjects.SiteService.site_index_id == siteID,
                                                                   dbobjects.SiteService.agency_location_index_id == agencyLocationID,
                                                                 )).all()
    
    def queryLanguages(self, siteID=None, siteServiceID=None, agencyLocationID=None):
        #Column('site_index_id', Integer, ForeignKey(Site.c.id)), 
        #Column('site_service_index_id', Integer, ForeignKey(SiteService.c.id)), 
        return self.session.query(dbobjects.Languages).filter(and_(dbobjects.Languages.site_index_id == siteID,
                                                                   dbobjects.Languages.site_service_index_id == siteServiceID,
                                                                   dbobjects.Languages.agency_location_index_id == agencyLocationID,
                                                                 )).all()
        
    def queryCrossStreet(self, siteID=None):
        return self.session.query(dbobjects.CrossStreet).filter(and_(dbobjects.CrossStreet.site_index_id == siteID,
                                                                 )).all()
        
    def queryAKA(self, agencyID=None, siteID=None, agencyLocationID=None ):
#        Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
#        Column('site_index_id', Integer, ForeignKey(Site.c.id)),
#        Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.c.id)),
        
        return self.session.query(dbobjects.Aka).filter(and_(dbobjects.Aka.site_index_id == siteID,
                                                             dbobjects.Aka.agency_index_id == agencyID,
                                                             dbobjects.Aka.agency_location_index_id == agencyLocationID,
                                                                 )).all()
        
    def queryOtherAddress(self, siteID=None, agencyLocationID=None):
        return self.session.query(dbobjects.OtherAddress).filter(and_(dbobjects.OtherAddress.site_index_id == siteID,
                                                                      dbobjects.OtherAddress.agency_location_index_id == agencyLocationID,
                                                                 )).all()
    
    def queryResourceInfo(self, agencyID=None, siteServiceID=None):
        #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
        #Column('site_service_index_id', Integer, ForeignKey(SiteService.c.id)), 
        return self.session.query(dbobjects.ResourceInfo).filter(and_(dbobjects.ResourceInfo.agency_index_id == agencyID,
                                                                      dbobjects.ResourceInfo.site_service_index_id == siteServiceID,
                                                                 )).all()
        
    def querySite(self, exportID=None, reportID=None, agencyID=None):
        #Column('export_index_id', String(50), ForeignKey(Export.c.export_id)),
        #Column('report_index_id', String(50), ForeignKey(Report.c.report_id)), 
        #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
        return self.session.query(dbobjects.Site).filter(and_(dbobjects.Site.agency_index_id == agencyID,
                                                                 )).all()
        
    def queryService(self, agencyID=None):
        #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
        return self.session.query(dbobjects.Service).filter(and_(dbobjects.Service.agency_index_id == agencyID,
                                                                 )).all()
    
    def queryServiceGroup(self, agencyID=None):
        
        return self.session.query(dbobjects.ServiceGroup).filter(and_(dbobjects.ServiceGroup.agency_index_id == agencyID,
                                                                 )).all()
        
    def queryLicenseAccreditation(self, agencyID=None):
        #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)),
        return self.session.query(dbobjects.LicenseAccreditation).filter(and_(dbobjects.LicenseAccreditation.agency_index_id == agencyID,
                                                                 )).all()
        
    def queryTimeOpen(self, siteID=None, languageID=None, siteServiceID=None, agencyLocationID=None):
#        Column('site_index_id', Integer, ForeignKey(Site.c.id)), 
#        Column('languages_index_id', Integer, ForeignKey(Languages.c.id)), 
#        Column('site_service_index_id', Integer, ForeignKey(SiteService.c.id)),
#        Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.c.id)),
        return self.session.query(dbobjects.TimeOpen).filter(and_(dbobjects.TimeOpen.site_index_id == siteID,
                                                                  dbobjects.TimeOpen.languages_index_id == languageID,
                                                                 dbobjects.TimeOpen.site_service_index_id == siteServiceID,
                                                                 dbobjects.TimeOpen.agency_location_index_id == agencyLocationID
                                                                 )).all()
    
    def queryContact(self, agencyID=None, resourceID=None, siteID=None, agencyLocationID=None):
        # foreign keys include
        #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
        #Column('resource_info_index_id', Integer, ForeignKey(ResourceInfo.c.id)),
        #Column('site_index_id', Integer, ForeignKey(Site.c.id)), 
    
        return self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyID,
                                                                 dbobjects.Contact.resource_info_index_id == resourceID,
                                                                 dbobjects.Contact.site_index_id == siteID,
                                                                 dbobjects.Contact.agency_location_index_id == agencyLocationID
                                                                 )).all()
        
    def queryEmail(self, agencyID=None, contactID=None, resourceID=None, siteID=None, personHistoricalID=None):
        # foreign keys for email
        #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
        #Column('contact_index_id', Integer, ForeignKey(Contact.c.id)), 
        #Column('resource_info_index_id', Integer, ForeignKey(ResourceInfo.c.id)), 
        #Column('site_index_id', Integer, ForeignKey(Site.c.id)), 
        #Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.c.id)),
        
        return self.session.query(dbobjects.Email).filter(and_(dbobjects.Email.agency_index_id == agencyID,
                                                               dbobjects.Email.contact_index_id == contactID,
                                                               dbobjects.Email.resource_info_index_id == resourceID,
                                                               dbobjects.Email.site_index_id == siteID,
                                                               dbobjects.Email.person_historical_index_id == personHistoricalID,
                                                               )).all()
                                                               
    def queryAgencyLocationEmail(self, agencyID=None, agencyLocationID=None, contactID=None, resourceID=None, siteID=None, personHistoricalID=None):
        return self.session.query(dbobjects.Email).filter(and_(dbobjects.Email.agency_index_id == agencyID,
                                                               dbobjects.Email.contact_index_id == contactID,
                                                               dbobjects.Email.resource_info_index_id == resourceID,
                                                               dbobjects.Email.site_index_id == siteID,
                                                               dbobjects.Email.person_historical_index_id == personHistoricalID,
                                                               dbobjects.Email.agency_location_index_id == agencyLocationID
                                                               )).all()
     
                                                               
    def queryAgencyURL(self, agencyID=None, siteID=None):
        #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
        #Column('site_index_id', Integer, ForeignKey(Site.c.id)), 
#        print "Start of queryAgencyURL result"
#        print "agencyID is", agencyID
        filter_result = self.session.query(dbobjects.Url).filter(and_(dbobjects.Url.agency_index_id == agencyID, dbobjects.Url.site_index_id == siteID, dbobjects.Url.agency_location_index_id == None)).all()
#        print "queryAgencyURL result is: ", filter_result
#        print "End of queryAgencyURL result"
        return filter_result                                                     
                                                             
    def queryAgencyLocationURL(self, agencyLocationID=None, agencyID=None):
            #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
            #Column('site_index_id', Integer, ForeignKey(Site.c.id)), 
#            print "Start of queryAgencyLocationURL result"
#            print "agencyLocationID is", agencyLocationID
#            print "agencyID is", agencyID
            result = self.session.query(dbobjects.Url).filter(and_(dbobjects.Url.agency_index_id == agencyID, dbobjects.Url.agency_location_index_id == agencyLocationID, agencyLocationID != None)).all()
#            print "queryAgencyLocationURL result is: ", result
#            print "End of queryAgencyLocationURL result"
            return result
        
    def queryAgencyLocation(self, agencyID=None):
        return self.session.query(dbobjects.AgencyLocation).filter(and_(dbobjects.AgencyLocation.agency_index_id == agencyID,)).all()
        
    def queryPhone(self, agencyID=None, contactID=None, resourceID=None, siteID=None, siteServiceID=None, personHistoricalID=None, agencyLocationID=None):
        # Phone has these foreign keys, they must either be null or supplied by some value to query properly
        #Column('agency_index_id', Integer, ForeignKey(Agency.c.id)), 
        #Column('contact_index_id', Integer, ForeignKey(Contact.c.id)), 
        #Column('resource_info_index_id', Integer, ForeignKey(ResourceInfo.c.id)), 
        #Column('site_index_id', Integer, ForeignKey(Site.c.id)), 
        #Column('site_service_index_id', Integer, ForeignKey(SiteService.c.id)), 
        #Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.c.id)),
        
        return  self.session.query(dbobjects.Phone).filter(and_(dbobjects.Phone.agency_index_id == agencyID,
                                                                dbobjects.Phone.contact_index_id == contactID,
                                                                dbobjects.Phone.resource_info_index_id == resourceID,
                                                                dbobjects.Phone.site_index_id == siteID,
                                                                dbobjects.Phone.site_service_index_id == siteServiceID,
                                                                dbobjects.Phone.person_historical_index_id == personHistoricalID,
                                                                dbobjects.Phone.agency_location_index_id == agencyLocationID
                                                                )).all()
        
    def customizeAgency(self, xml, agencyData, siteIndexID = None):
        
        #sourceID = ET.SubElement(xml, "hmis:SourceID")

        # Create the attributes for the Agency first
        xml.attrib['RecordOwner'] = agencyData.record_owner
        xml.attrib['FEIN'] = agencyData.fein
        xml.attrib['YearInc'] = agencyData.year_inc
        xml.attrib['AnnualBudgetTotal'] = agencyData.annual_budget_total
        xml.attrib['LegalStatus'] = agencyData.legal_status
        xml.attrib['ExcludeFromWebsite'] = agencyData.exclude_from_website
        xml.attrib['ExcludeFromDirectory'] = agencyData.exclude_from_directory
        
        # next process the elements
        elements = [
            'Key',
            'Name',
            'AgencyDescription',
            'AKA',
            'AgencyLocation',
            'Phone',
            'URL',
            'Email',
            ]
        
        
        
        # Define the elements   
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)

        theElements['Key'].text = agencyData.airs_key
        theElements['Name'].text = agencyData.airs_name
        theElements['AgencyDescription'].text = agencyData.agency_description
        
        # pull the AKA record
        #theElements['AKA'].text = agencyData.
        
        #AKA = self.createAgencyAKA(agency)
        AKA = theElements['AKA']
        
        # Set this to None (FIXME) This needs to be the real thing when we are pulling AKA records that are under sites.
        AKARows = self.queryAKA(agencyData.id)
        #AKARows = self.session.query(dbobjects.Aka).filter(and_(dbobjects.Aka.agency_index_id == agencyData.id,dbobjects.Aka.site_index_id == siteIndexID)).all()
        
        for AKARow in AKARows:
            akarow = self.customizeAgencyAKA(AKA, AKARow)
        
        # FIXME (Eric is working on writing this code need to uncomment when he's done            
        # Agency Location
        AgencyLocationElement = theElements['AgencyLocation']
        AgencyLocationData = self.queryAgencyLocation(agencyID = agencyData.id)
        
        for agencylocationRows in AgencyLocationData:
            agencyLoc = self.customizeAgencyLocation(AgencyLocationElement, agencyData, agencylocationRows)
        
        # Phone
        PhoneElement = theElements['Phone']
        
        # Set this to None (FIXME) This needs to be the real thing when we are pulling AKA records that are under sites.
        AgencyPhoneData = self.queryPhone(agencyID = agencyData.id)
        #self.session.query(dbobjects.Phone).filter(and_(dbobjects.Phone.agency_index_id == agencyData.id,)).all()
        
        for phoneRow in AgencyPhoneData:
            phoneSubElement = self.customizeAgencyPhone(PhoneElement, phoneRow)
        
        # URL
        urlElement = theElements['URL']
        
        AgencyURLData = self.queryAgencyURL(agencyID = agencyData.id)
        #self.session.query(dbobjects.Url).filter(and_(dbobjects.Url.agency_index_id == agencyData.id,)).all()
        
        for urlRow in AgencyURLData:
            urlSubElement = self.addURL(urlElement, urlRow)
        
        # Email
        EmailElement = theElements['Email']
        
        AgencyEmailData = self.queryEmail(agencyID = agencyData.id)
        #self.session.query(dbobjects.Email).filter(and_(dbobjects.Email.agency_index_id == agencyData.id,)).all()
        
        for emailRow in AgencyEmailData:
            urlSubElement = self.customizeAgencyEmail(EmailElement, emailRow)
        
        
        # Contact        
        AgencyContactData = self.queryContact(agencyID = agencyData.id)
        #self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        if AgencyContactData:
            ContactElement = ET.SubElement(xml, "airs:%s" % 'Contact')
            for contactRow in AgencyContactData:
                contactSubElement = self.customizeAgencyContact(ContactElement, contactRow, agencyData)

        # LicenseAccreditation
        AgencyLicenseAccreditationData = self.queryLicenseAccreditation(agencyID = agencyData.id)
        #self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        
        for accreditationRow in AgencyLicenseAccreditationData:
            LicenseAccreditationElement = ET.SubElement(xml, "airs:LicenseAccreditation")
            licenseAcreditationSubElement = self.customizeAgencyLicenseAccreditation(LicenseAccreditationElement, accreditationRow)
        
        # Part II of the Agency elements, we had to do some backflips to get the data formatted properly, so now process the remaining elements
        elements = [
            #'LicenseAccreditation',
            'IRSStatus',
            'SourceOfFunds',
            'ServiceGroup',
            'Service',
            'Site',
            'ResourceInfo',
        ]
        
        theElements = {}
        # build a dictionary of the field names above then we can assign values spinning through the dictionary
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        # IRSStatus
        theElements['IRSStatus'] = agencyData.irs_status
        # SourceOfFunds
        theElements['SourceOfFunds'] = agencyData.source_of_funds
        
        # ServiceGroup
        ServiceGroupElement = theElements['ServiceGroup']
        
        AgencyServiceGroupData = self.queryServiceGroup(agencyID = agencyData.id)
        #self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        
        for serviceGroupRow in AgencyServiceGroupData:
            serviceGroupSubElement = self.customizeAgencyServiceGroup(ServiceGroupElement, serviceGroupRow)
        
        # Service
        #ServiceElement = theElements['Service']
        #
        #AgencyServiceData = self.queryService(agencyData.id)
        ##self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        #
        #for serviceRow in AgencyServiceData:
        #    serviceSubElement = self.customizeAgencyService(ServiceElement, serviceGroupRow)
        
        # Site
        SiteElement = theElements['Site']
        
        AgencySiteData = self.querySite(agencyID = agencyData.id)
        #self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        
        for siteRow in AgencySiteData:
            serviceGroupSubElement = self.customizeAgencySite(SiteElement, agencyData, siteRow)
        
        # ResourceInfo
        ResourceInfoElement = theElements['ResourceInfo']
        resourceInfoData = self.queryResourceInfo(agencyID = agencyData.id)
        #self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        
        for resourceInfoRow in resourceInfoData:
            serviceGroupSubElement = self.customizeAgencyResourceInfo(ResourceInfoElement, resourceInfoRow)
        
        
        
        #theElements[''].text = agencyData.
        #theElements[''].text = agencyData.
        #theElements[''].text = agencyData.
        #theElements[''].text = agencyData.
        

        return xml
    
    def createAgencyAKA(self, xml):
        AKA = ET.SubElement(xml, "airs:AKA")
        return AKA
    
    def customizeMailingAddress(self, xml, agencyLocationData):
        xml.attrib['Confidential'] = agencyLocationData.mailing_address_confidential
        xml.attrib['Description'] = agencyLocationData.mailing_address_description
        
        elements = [
            'PreAddressLine',
            'Line1',
            'Line2',
            'City',
            'County',
            'State',
            'ZipCode',
            'Country',
            #'ReasonWithheld',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)

        # PreAddressLine
        theElements['PreAddressLine'].text = agencyLocationData.mailing_address_pre_address_line
        
        # Line1
        theElements['Line1'].text = agencyLocationData.mailing_address_line_1
        
        # Line2
        theElements['Line2'].text = agencyLocationData.mailing_address_line_2
        
        # City
        theElements['City'].text = agencyLocationData.mailing_address_city
        
        # State
        theElements['State'].text = agencyLocationData.mailing_address_state
        
        # County
        theElements['County'].text = agencyLocationData.mailing_address_county
        
        # ZipCode
        theElements['ZipCode'].text = agencyLocationData.mailing_address_zip_code
        
        # Country
        theElements['Country'].text = agencyLocationData.mailing_address_country
        
        # ReasonWithheld
        #theElements['ReasonWithheld'].text = agencyLocationData.mailing_address_reason_withheld
        
        return
        
        
    def customizeAgencyAKA(self, xml, AKAData):
        # next process the elements
        
        elements = [
            'Name',
            'Confidential',
            'Description'
            ]
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['Name'].text = AKAData.name
        theElements['Confidential'].text = AKAData.confidential
        theElements['Description'].text = AKAData.description
        
    def customizeAgencyLocation(self, xml, agencyData, agencyLocationData):
        
        xml.attrib['PublicAccessToTransportation'] = agencyLocationData.public_access_to_transportation
        xml.attrib['YearInc'] = agencyLocationData.year_inc
        xml.attrib['AnnualBudgetTotal'] = agencyLocationData.annual_budget_total
        xml.attrib['LegalStatus'] = agencyLocationData.legal_status
        xml.attrib['ExcludeFromWebsite'] = agencyLocationData.exclude_from_website
        xml.attrib['ExcludeFromDirectory'] = agencyLocationData.exclude_from_directory
        
        elements = [
            'Key',
            'Name',
            'SiteDescription',
            'AKA',
            'MailingAddress',
            'OtherAddress',
            #'CrossStreet',
            'Phone',
            'URL',
            'Email',
            'Contact',
            'TimeOpen',
            'Languages',
            'DisabilitiesAccess',
            'PhysicalLocationDescription',
            'BusServiceAccess',
            'SiteService',
            'SpatialLocation',
            ]
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        # Key
        theElements['Key'].text = agencyLocationData.key
        
        # Name
        theElements['Name'].text = agencyLocationData.name
        
        # SiteDescription
        theElements['SiteDescription'].text = agencyLocationData.site_description
        
        # AKA
        akaElement = theElements['AKA']
        AKARows = self.queryAKA(agencyID=agencyData.id, agencyLocationID=agencyLocationData.id)
        
        for AKARow in AKARows:
            akarow = self.customizeAgencyAKA(akaElement, AKARow)
            
        # MailingAddress
        mailAddressElement = theElements['MailingAddress']
        self.customizeMailingAddress(mailAddressElement, agencyLocationData)
         
        # OtherAddress
        otheraddressElement = theElements['OtherAddress']
        
        OtherAddressData = self.queryOtherAddress(siteID=None, agencyLocationID=agencyLocationData.id)
        
        for otheraddressRow in OtherAddressData:
            otherAddressSubElement = self.customizeSiteOtherAddress(otheraddressElement, otheraddressRow)
        
         
        # CrossStreet
        # Unlike rest of model, these are created for each occurence of row in DB (make the element and assign data value)
        #crossStreeElement = theElements['CrossStreet']
        crossStreetData = self.queryCrossStreet(agencyLocationData.id)
        #self.session.query(dbobjects.Phone).filter(and_(dbobjects.Phone.agency_index_id == agencyData.id,)).all()
        
        for crossStreetRow in crossStreetData:
            crossStreetSubElement = ET.SubElement(xml, "airs:CrossStreet")
            crossStreetSubElement.text = crossStreetRow.cross_street
        
        # Phone
        phoneElement = theElements['Phone']
        sitePhoneData = self.queryPhone(agencyID=agencyData.id, contactID=None, resourceID=None, agencyLocationID=agencyLocationData.id)
        
        for phoneRow in sitePhoneData:
            phoneSubElement = self.customizeAgencyPhone(phoneElement, phoneRow)
                    
         
        # URL
        urlElement = theElements['URL']
        SiteURLData = self.queryAgencyLocationURL(agencyLocationData.id, agencyData.id)
        #self.session.query(dbobjects.Url).filter(and_(dbobjects.Url.agency_index_id == agencyData.id,)).all()
        
        for urlRow in SiteURLData:
            urlSubElement = self.addURL(urlElement, urlRow)
        
        # Email
        emailElement = theElements['Email']
        SiteEmailData = self.queryAgencyLocationEmail(agencyData.id, agencyLocationData.id, siteID=None)
        #self.session.query(dbobjects.Email).filter(and_(dbobjects.Email.agency_index_id == agencyData.id,)).all()
        
        for emailRow in SiteEmailData:
            emailSubElement = self.customizeAgencyEmail(emailElement, emailRow)        
         
        # Contact
        contactElement = theElements['Contact']
        siteContactData = self.queryContact(agencyID = agencyData.id, siteID=None,agencyLocationID=agencyLocationData.id)
        #self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        
        for siteContactRow in siteContactData:
            contactSubElement = self.customizeAgencyContact(contactElement, siteContactRow, agencyData)
        
        # TimeOpen
        timeopenElement = theElements['TimeOpen']
        timeOpenData = self.queryTimeOpen(siteID=None, languageID=None, siteServiceID=None, agencyLocationID=agencyLocationData.id)
        
        for timeOpenRow in timeOpenData:
            timeopenSubElement = self.customizeTimeOpen(timeopenElement, timeOpenRow)
         
        # Languages
        languagesElement = theElements['Languages']
        siteLanguageData = self.queryLanguages(agencyLocationID=agencyLocationData.id )
        
        for siteLanguageRow in siteLanguageData:
            languagesSubElement = self.customizeSiteLanguage(languagesElement, siteLanguageRow)
         
        # DisabilitiesAccess
        theElements['DisabilitiesAccess'].text = agencyLocationData.disabilities_access
        
         
        # PhysicalLocationDescription
        theElements['PhysicalLocationDescription'].text = agencyLocationData.physical_location_description
        
         
        # BusServiceAccess
        theElements['BusServiceAccess'].text = agencyLocationData.bus_service_access
        
        # SiteService
        siteServiceElement = theElements['SiteService']
        siteServiceData = self.querySiteService(agencyLocationID=agencyLocationData.id)
        
        for siteServiceRow in siteServiceData:
            siteServiceSubElement = self.customizeSiteService(siteServiceElement, siteServiceRow)
         
        # SpatialLocation
        spatiallocationElement = theElements['SpatialLocation']
        siteSpatialLocationData = self.querySpatialLocation(agencyLocationID=agencyLocationData.id)
        
        for siteSpatialLocationRow in siteSpatialLocationData:
            languagesSubElement = self.customizeSpatialLocation(spatiallocationElement, siteSpatialLocationRow)
        
    def customizeAgencyPhone(self, xml, phoneData):
        # next process the elements
        
        xml.attrib['TollFree'] = phoneData.toll_free
        xml.attrib['Confidential'] = phoneData.confidential
        
        elements = [
            'PhoneNumber',
            #Reason withheld is a choice with PhoneNumber
            #'ReasonWithheld',
            'Extension',
            'Description',
            'Type',
            'Function',
            ]
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['PhoneNumber'].text = phoneData.phone_number
#        if not phoneData.reason_withheld is None:
#
#            theElements['ReasonWithheld'].text = phoneData.reason_withheld
        if not phoneData.extension is None:
            theElements['Extension'].text = phoneData.extension
        if not phoneData.description is None:
            theElements['Description'].text = phoneData.description
        if not phoneData.type is None:
            theElements['Type'].text = phoneData.type
        if not phoneData.function is None:
            theElements['Function'].text = phoneData.function
    
    def addURL(self, xml, URLData):
        
        elements = [
            'Address',
            'Note',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['Address'].text = URLData.address
        theElements['Note'].text = URLData.note
        
    def customizeAgencyEmail(self, xml, EmailData):
        elements = [
            'Address',
            'Note',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['Address'].text = EmailData.address
        theElements['Note'].text = EmailData.note
        
    def customizeSiteLanguage(self, xml, LanguagesData):
        elements = [
            'Name',
            'TimeOpen',
            'Notes'
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
            
        theElements['Name'].text = LanguagesData.name
        #theElements['TimeOpen'].text = LanguagesData.title
        theElements['Notes'].text = LanguagesData.notes
        
    def customizeSiteService(self, xml, siteServiceData):
        if siteServiceData is None:
            return xml
        
        xml.attrib['AreaFlexibility'] = siteServiceData.area_flexibility
        xml.attrib['ServiceNotAlwaysAvailable'] = siteServiceData.service_not_always_available
        xml.attrib['ServiceGroupKey'] = siteServiceData.service_group_key
        
        elements = [
            'Key',
            
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['Key'].text = siteServiceData.key
        
        taxonomyData = self.queryTaxonomy(siteServiceID=siteServiceData.id)
        if len(taxonomyData) > 0:            
            # Taxonomy
            #taxonomyElement =ET.SubElement(xml, "airs:%s" % 'Taxonomy')
            
            taxonomySubElement = self.customizeTaxonomy(xml, taxonomyData)
        
    def customizeSpatialLocation(self, xml, spatialLocationData):
        elements = [
            'Description',
            'Datum',
            'Latitude',
            'Longitude',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['Description'].text = spatialLocationData.description
        theElements['Datum'].text = spatialLocationData.datum
        theElements['Latitude'].text = spatialLocationData.latitude
        theElements['Longitude'].text = spatialLocationData.longitude
    
    def customizeTimeOpen(self, xml, TimeOpenData):
        pass
    
    def customizeAgencyContact(self, xml, ContactData, agencyData):
        xml.attrib['Type'] = ContactData.type
        
#        elements = [
#            'Title',
#            'Name',
#            'Email',
#            'Phone',
#            ]
#        
#        theElements = {}
#        for element in elements:
#            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        if ContactData.title:
            title = ET.SubElement(xml, "airs:%s" % 'Title')
            title.text = ContactData.title
        if ContactData.name:
            name = ET.SubElement(xml, "airs:%s" % 'Name')
            name.text = ContactData.name
        # Email        
        AgencyEmailData = self.queryEmail(agencyData.id, ContactData.id)
        print 'agency contact email results:', AgencyEmailData
        if AgencyEmailData:
        #self.session.query(dbobjects.Email).filter(and_(dbobjects.Email.agency_index_id == agencyData.id,)).all()
            email = ET.SubElement(xml, "airs:%s" % 'Email')
            for emailRow in AgencyEmailData:
                urlSubElement = self.customizeAgencyEmail(email, emailRow)
        
        # now get the phone and email subelements of Contact
        # Set this to None (FIXME) This needs to be the real thing when we are pulling AKA records that are under sites.
        AgencyPhoneData = self.queryPhone(agencyData.id, ContactData.id)
        print 'agency contact phone results:', AgencyPhoneData
        #self.session.query(dbobjects.Phone).filter(and_(dbobjects.Phone.agency_index_id == agencyData.id,)).all()
        if AgencyPhoneData:
            phone = ET.SubElement(xml, "airs:%s" % 'Phone')
            for phoneRow in AgencyPhoneData:
                phoneSubElement = self.customizeAgencyPhone(phone, phoneRow)
    
    def customizeAgencyLicenseAccreditation(self, xml, AccreditationData):
        elements = [
            'License',
            'LicensedBy',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['License'].text = AccreditationData.license
        theElements['LicensedBy'].text = AccreditationData.licensed_by
        
    def customizeAgencyServiceGroup(self, xml, serviceGroupData):
        elements = [
            'Key',
            'Name',
            'ProgramName',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['Key'].text = serviceGroupData.key
        theElements['Name'].text = serviceGroupData.name
        theElements['ProgramName'].text = serviceGroupData.program_name
    
    def customizeSiteOtherAddress(self, xml, siteOtherAddress):
        xml.attrib['Confidential'] = siteOtherAddress.confidential
        xml.attrib['Description'] = siteOtherAddress.description
        
        elements = [
            'Line1',
            'Line2',
            'City',
            'State',
            #'County',
            'ZipCode',
            'Country',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
            
        # Line1
        theElements['Line1'].text = siteOtherAddress.line_1
        
        # Line2
        theElements['Line2'].text = siteOtherAddress.line_2
        
        # City
        theElements['City'].text = siteOtherAddress.city
        
        # State
        theElements['State'].text = siteOtherAddress.state
        
        # County
        #theElements['County'].text = siteOtherAddress.county
        
        # ZipCode
        theElements['ZipCode'].text = siteOtherAddress.zip_code
        
        # Country
        theElements['Country'].text = siteOtherAddress.country
        
    def customizeAgencyResourceInfo(self, xml, agencyData):
        xml.attrib['AvailableForDirectory'] = agencyData.available_for_directory
        xml.attrib['AvailableForReferral'] = agencyData.available_for_referral
        xml.attrib['AvailableForResearch'] = agencyData.available_for_research
        xml.attrib['DateAdded'] = agencyData.date_added.isoformat()
        xml.attrib['DateLastVerified'] = agencyData.date_last_verified.isoformat()
        xml.attrib['DateOfLastAction'] = agencyData.date_of_last_action.isoformat()
        xml.attrib['LastActionType'] = agencyData.last_action_type
        
        elements = [
            'Contact',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
            
        # Contact
        contactElement = theElements['Contact']
        siteContactData = self.queryContact(agencyID = agencyData.id, siteID=None)
        #self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        
        for siteContactRow in siteContactData:
            contactSubElement = self.customizeAgencyContact(contactElement, siteContactRow, agencyData)
        
    def customizeAgencySite(self, xml, agencyData, siteData):
        
        xml.attrib['PublicAccessToTransportation'] = siteData.public_access_to_transportation
        xml.attrib['YearInc'] = siteData.year_inc
        xml.attrib['AnnualBudgetTotal'] = siteData.annual_budget_total
        xml.attrib['LegalStatus'] = siteData.legal_status
        xml.attrib['ExcludeFromWebsite'] = siteData.exclude_from_website
        xml.attrib['ExcludeFromDirectory'] = siteData.exclude_from_directory
        
        elements = [
            'Key',
            'Name',
            'SiteDescription',
            'AKA',
            'OtherAddress',
            #'CrossStreet',
            'Phone',
            'URL',
            'Email',
            'Contact',
            'TimeOpen',
            'Languages',
            'DisabilitiesAccess',
            'PhysicalLocationDescription',
            'BusServiceAccess',
            'SpatialLocation',
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
            
        # Key
        theElements['Key'].text = siteData.airs_key
        
        # Name
        theElements['Name'].text = siteData.airs_name
        
        # SiteDescription
        theElements['SiteDescription'].text = siteData.site_description
        
        # AKA
        akaElement = theElements['AKA']
        AKARows = self.queryAKA(agencyID=agencyData.id, siteID=siteData.id)
        #AKARows = self.session.query(dbobjects.Aka).filter(and_(dbobjects.Aka.agency_index_id == agencyData.id,dbobjects.Aka.site_index_id == siteData.id)).all()
        
        for AKARow in AKARows:
            akarow = self.customizeAgencyAKA(akaElement, AKARow)
         
        # OtherAddress
        otheraddressElement = theElements['OtherAddress']
        
        OtherAddressData = self.queryOtherAddress(siteData.id)
        #self.session.query(dbobjects.Phone).filter(and_(dbobjects.Phone.agency_index_id == agencyData.id,)).all()
        
        for otheraddressRow in OtherAddressData:
            otherAddressSubElement = self.customizeSiteOtherAddress(otheraddressElement, otheraddressRow)
        
         
        # CrossStreet
        # Unlike rest of model, these are created for each occurence of row in DB (make the element and assign data value)
        #crossStreeElement = theElements['CrossStreet']
        crossStreetData = self.queryCrossStreet(siteData.id)
        #self.session.query(dbobjects.Phone).filter(and_(dbobjects.Phone.agency_index_id == agencyData.id,)).all()
        
        for crossStreetRow in crossStreetData:
            crossStreetSubElement = ET.SubElement(xml, "airs:CrossStreet")
            crossStreetSubElement.text = crossStreetRow.cross_street
        
        # Phone
        phoneElement = theElements['Phone']
        sitePhoneData = self.queryPhone(agencyID=agencyData.id, contactID=None, resourceID=None, siteID=siteData.id)
        
        for phoneRow in sitePhoneData:
            phoneSubElement = self.customizeAgencyPhone(phoneElement, phoneRow)
                    
         
        # URL
        #ECJ20100923 We have a problem with this: it's also pulling AgencyLocation URLs in addition to the base URL, need to change the query.
        urlElement = theElements['URL']
        SiteURLData = self.queryAgencyURL(agencyID = agencyData.id, siteID=siteData.id)
        #self.session.query(dbobjects.Url).filter(and_(dbobjects.Url.agency_index_id == agencyData.id,)).all()
        
        for urlRow in SiteURLData:
            urlSubElement = self.addURL(urlElement, urlRow)
        
        # Email
        emailElement = theElements['Email']
        SiteEmailData = self.queryEmail(agencyData.id, siteID=siteData.id)
        #self.session.query(dbobjects.Email).filter(and_(dbobjects.Email.agency_index_id == agencyData.id,)).all()
        
        for emailRow in SiteEmailData:
            emailSubElement = self.customizeAgencyEmail(emailElement, emailRow)        
         
        # Contact
        contactElement = theElements['Contact']
        siteContactData = self.queryContact(agencyID = agencyData.id, siteID=siteData.id)
        #self.session.query(dbobjects.Contact).filter(and_(dbobjects.Contact.agency_index_id == agencyData.id,)).all()
        
        for siteContactRow in siteContactData:
            contactSubElement = self.customizeAgencyContact(contactElement, siteContactRow, agencyData)
        
        
        # TimeOpen
        timeopenElement = theElements['TimeOpen']
        
         
        # Languages
        languagesElement = theElements['Languages']
        siteLanguageData = self.queryLanguages(siteID=siteData.id)
        
        for siteLanguageRow in siteLanguageData:
            languagesSubElement = self.customizeSiteLanguage(languagesElement, siteLanguageRow)
         
        # DisabilitiesAccess
        theElements['DisabilitiesAccess'].text = siteData.disabilities_access
        
         
        # PhysicalLocationDescription
        theElements['PhysicalLocationDescription'].text = siteData.physical_location_description
        
         
        # BusServiceAccess
        theElements['BusServiceAccess'].text = siteData.bus_service_access
        
         
        # SpatialLocation
        spatiallocationElement = theElements['SpatialLocation']
        siteSpatialLocationData = self.querySpatialLocation(siteID=siteData.id)
        
        for siteSpatialLocationRow in siteSpatialLocationData:
            languagesSubElement = self.customizeSpatialLocation(spatiallocationElement, siteSpatialLocationRow)
        
        
        # Start plugging data in here...
        #theElements['Key'].text = siteData.key
        #theElements['Name'].text = siteData.name
        #theElements['ProgramName'].text = siteData.program_name
        
    def customizeAgencyService(self):
        elements = [
            'Name',
            'Confidential',
            'Description'
            ]
        
        theElements = {}
        for element in elements:
            theElements[element] = ET.SubElement(xml, "airs:%s" % element)
        
        theElements['Name'].text = AKAData.name
        theElements['Confidential'].text = AKAData.confidential
        theElements['Description'].text = AKAData.description
        
    
    def processXML(self):
        self.root_element = self.createDoc() #makes root element with XML header attributes
        
        # This is the start, we pull from the top and work our way down.
        if self.options.reported == True:
            #Source = self.session.query(dbobjects.Source).filter(dbobjects.Person.reported == True)
            Sources = self.session.query(dbobjects.Source)
        elif self.options.unreported == True:
            #Source = self.session.query(dbobjects.Source).filter(or_(dbobjects.Person.reported == False, dbobjects.Person.reported == None))
            Sources = self.session.query(dbobjects.Source)
        elif self.options.reported == None:
            Sources = self.session.query(dbobjects.Source)
        else:
            pass
        
        for sourceData in Sources:
            source = self.createSource(self.root_element)
            
            # This needs a parameter with datavalues passed in, right now it's structure only.
            source = self.customizeSource(source, sourceData)
            # pull the link
            link = self.session.query(dbobjects.SourceExportLink).filter(dbobjects.SourceExportLink.source_index_id == sourceData.id).one()
            export_rec_id = link.export_index_id
            
            # pull the export record
            exportRecs = self.session.query(dbobjects.Export).filter(dbobjects.Export.export_id == export_rec_id).all()            
            for exportData in exportRecs:
                export = self.createExport(source)
            
                #exportData = sourceData.
            
                export = self.customizeExport(export, exportData)
            
                # off export you need to make (Agency, Household, Person, Service, Site, SiteService)
                agency = self.createAgency(export)
                
                # pull agency from the export data
                agencyRecs = self.session.query(dbobjects.Agency).filter(dbobjects.Agency.export_index_id == export_rec_id).all()
                for agencyData in agencyRecs:
                    agency = self.customizeAgency(agency, agencyData)
                
                    
            
                houseHold = self.createHousehold(export)
                houseHold = self.customizeHousehold(houseHold)
                
                person = self.createPerson(export)
                
            person = self.customizePerson(person)
            
            # off person you need to make (Need, OtherNames, PersonHistorical, Race, ReleaseOfInformation, ServiceEvent, SiteServiceParticipation, )
            need = self.createNeed(person)
            need = self.customizeNeed(need)
            
            # subelement of need
            taxonomy = self.createTaxonomy(need)
            taxonomy = self.customizeTaxonomy(taxonomy, [])
            
            # OtherNames - subelement of person
            othernames = self.createOtherNames(person)
            othernames = self.customizeOtherNames(othernames)
            
            # PersonHistorical - subelement of person
            personhistorical = self.createPersonHistorical(person)
            personhistorical = self.customizePersonHistorical(personhistorical)
            
            # Race - subelement of person
            race = self.createRace(person)
            race = self.customizeRace(race)
            
            # ReleaseOfInformation - subelement of person
            releaseofinformation = self.createReleaseOfInformation(person)
            releaseofinformation = self.customizeReleaseOfInformation(releaseofinformation)
            
            # ServiceEvent - subelement of person
            serviceevent = self.createServiceEvent(person)
            serviceevent = self.customizeServiceEvent(serviceevent)
            
            # SiteServiceParticipation - subelement of person
            siteserviceparticipation = self.createSiteServiceParticipation(person)
            siteserviceparticipation = self.customizeSiteServiceParticipation(siteserviceparticipation)
            
            # back to person final element is to append the SSN Information
            
            person = self.customizePersonSSN(person)
            
            # Back to Export sub-elements
            service = self.createService(export)
            service = self.customizeService(service)
            
            # Site
            site = self.createSite(export)
            site = self.customizeSite(site)
            
            # sub element of Site
            aka = self.createSite_AKA(site)
            aka = self.customizeSite_AKA(aka)
            
            # this is a wrapper function to process Site Services too many processes
            self.manageSiteService(export)


#    def writeOutXML(self):
#        tree = ET.ElementTree(self.root_element)
#        if self.debug == True:
#            print "trying to write XML to: %s " % os.path.join(self.outDirectory, "page.xml")
#        
#        tree.write(os.path.join(self.outDirectory, "page.xml"), encoding="UTF-8")

    
if __name__ == "__main__":
    
    from queryobject import QueryObject
    
    optParse = QueryObject()
    options = optParse.getOptions()
    
    if options != None:
        try:
            
            vld = HMISXMLWriter(".", options)
            vld.write()        
            
        except clsexceptions.UndefinedXMLWriter:
            print "Please specify a format for outputting your XML"
            raise
    
    
    