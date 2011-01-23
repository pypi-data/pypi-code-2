#!/usr/bin/python env

import sys, os
from reader import Reader
from zope.interface import implements
from lxml import etree
import dateutil.parser
import dbobjects
from conf import settings
from datetime import datetime

class JFCSXMLReader(dbobjects.DatabaseObjects):
    ''' Synthesis import plugin for JFCS XML 
        JFCS provides 2 simple XML files
        - 1 for service data
        - 1 for client data
        This module parses the XML, maps the
        elements to database fields and 
        commits data to the database
    '''
    
    implements (Reader)
    
    def __init__(self, xml_file):
        self.xml_file = xml_file
        ''' instantiate database object '''
        self.dbo = dbobjects.DatabaseObjects()
        self.session = self.dbo.Session()
    
    def read(self):
        ''' suck in raw xml file and build etree object '''
        tree = etree.parse(self.xml_file)
        return tree
    
    def process_data(self, tree, data_type):
        self.data_type = data_type
        '''set hard-coded elements for this particular data integration'''
        '''we need to set agency id, service id, but the xml has site service (qprogram)'''
        self.source_id = str(settings.JFCS_SOURCE_ID)
        self.agency_airs_key = settings.JFCS_AGENCY_ID
        self.service_airs_key = settings.JFCS_SERVICE_ID
        self.source_email = 'kwright@jfcs-cares.org'
           
        ''' call parser based on incoming data type (client or service) '''
        if self.data_type == 'service_event': self.parse_service_event_xml(tree)
        elif self.data_type == 'client':  self.parse_client_xml(tree)
        return
    
    def parse_service_event_xml(self, tree):
        ''' iterate through JFCS service simple xml calling appropriate parsers '''
        ''' we have to lookup person_index_id and site_service_participation_index_id '''

        '''Fetch or create a source_id, export_id, service_id, site_id, and source_export_link  That will link everything together'''
        '''we have to do all here instead of parsing from xml, because jfcs xml doesn't provide all these things as does hmis xml'''
        
        '''related table stuff'''
        lookup_or_add_source_id(self, self.source_id)

        ''' insert xml data into native data structure '''
        for row_element in tree.getiterator(tag="row"):
            self.row_dict = {}
            for child in row_element:
                if child.text is not None:
                    #print "%s - %s" % (child.tag, child.text)
                    if child.tag == 'c4clientid': self.row_dict.__setitem__('c4clientid', child.text)
                    if child.tag == 'qprogram': self.row_dict.__setitem__('qprogram', child.text)
                    if child.tag == 'serv_code': self.row_dict.__setitem__('serv_code', child.text)
                    if child.tag == 'trdate': self.row_dict.__setitem__('trdate', child.text)
                    if child.tag == 'end_date': self.row_dict.__setitem__('end_date', child.text)
                    if child.tag == 'cunits': self.row_dict.__setitem__('cunits', child.text)
            ''' data fetched, now call the parsers '''
            if self.row_dict.has_key('qprogram'):    
                lookup_or_add_site_service_id(self, self.row_dict.__getitem__('qprogram'))
            self.parse_service_event()
        return
    
    def parse_client_xml(self, tree):
        ''' iterate through JFCS service simple xml calling appropriate parsers '''
        ''' insert xml data into native data structure '''
        
        '''related table stuff'''
        lookup_or_add_source_id(self, self.source_id)
        
        for row_element in tree.getiterator(tag="row"):
            self.row_dict = {}
            #print '** NEW ROW'
            for child in row_element:
                if child.text is not None:
                    #print "%s - %s" % (child.tag, child.text)
                    if child.tag == 'c4clientid': self.row_dict.__setitem__('c4clientid', child.text)
                    if child.tag == 'c4dob': self.row_dict.__setitem__('c4dob', child.text)
                    if child.tag == 'c4sex': self.row_dict.__setitem__('c4sex', child.text)
                    if child.tag == 'c4firstname': self.row_dict.__setitem__('c4firstname', child.text)
                    if child.tag == 'c4lastname': self.row_dict.__setitem__('c4lastname', child.text)
                    if child.tag == 'c4mi': self.row_dict.__setitem__('c4mi', child.text)
                    if child.tag == 'hispanic': self.row_dict.__setitem__('hispanic', child.text)
                    if child.tag == 'c4ssno': self.row_dict.__setitem__('c4ssno', child.text)
                    if child.tag == 'c4last_s01': self.row_dict.__setitem__('c4last_s01', child.text)
                    if child.tag == 'ethnicity': self.row_dict.__setitem__('ethnicity', child.text)
                    if child.tag == 'aprgcode': self.row_dict.__setitem__('aprgcode', child.text)
                    if child.tag == 'a_date': self.row_dict.__setitem__('a_date', child.text)
                    if child.tag == 't_date': self.row_dict.__setitem__('t_date', child.text)
                    if child.tag == 'family_id': self.row_dict.__setitem__('family_id', child.text)
            ''' data fetched, now call the parsers '''
            self.parse_person()
        return
    
    ''' Parsers for each database table and sub-table relative to input data source '''
    ''' service:
        - service_event
        client:
        - person -> other_names
        - person -> races
        - person -> site_service_participation
        - household -> members
    ''' 

    def parse_service_event(self):
        ''' parse data for service_event table '''
        self.parse_dict = {}
        self.person_index_id = ''
        ''' fetch person.id and site_service_participation.id from separate imports of client data'''
        '''I think it would be better to match person id from the same source id'''
        #save self.site_service_index_id state because somewhere in the  self.lookup_or_add_person_index_id(), it is wiped
        self.lookup_or_add_person_index_id()
        '''if there is a person, add them'''
        if self.person_index_id is None:
            if settings.DEBUG:
                print "Error: no person index id found!"
        else: 
            self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
        try:
            self.site_service_participation_index_id
            if self.site_service_participation_index_id != None:
                self.existence_test_and_add('site_service_participation_index_id', self.site_service_participation_index_id, 'no_handling')
        except AttributeError:
            pass
        if self.row_dict.has_key('serv_code'): self.existence_test_and_add('jfcs_type_of_service', self.row_dict.__getitem__('serv_code'), 'text')
        ''' dates may come in filled, blank, or contain just dashes'''
        ''' normalize the date field before sending to db '''
#trdate is only the billing date, we only get end_date
#        if self.row_dict.has_key('trdate'):
#            test = self.normalize_date(self.row_dict.__getitem__('trdate'))
#            if test == True: self.existence_test_and_add('service_period_start_date', self.row_dict.__getitem__('trdate'), 'element_date')
        if self.row_dict.has_key('end_date'):
            test = self.normalize_date(self.row_dict.__getitem__('end_date'))
            if test == True: self.existence_test_and_add('service_period_end_date', self.row_dict.__getitem__('end_date'), 'element_date')
        if self.row_dict.has_key('cunits'): self.existence_test_and_add('quantity_of_service', self.row_dict.__getitem__('cunits'), 'text')
        self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
        self.existence_test_and_add('export_index_id', self.export_index_id, 'no_handling')
        thetimenow = str(datetime.now())
        self.existence_test_and_add('site_service_recorded_date', thetimenow, 'element_date')
        self.shred(self.parse_dict, dbobjects.ServiceEvent)
    
    def parse_person(self):
        ''' parse data for person table '''
        self.parse_dict = {}
        if self.row_dict.has_key('c4clientid'): self.existence_test_and_add('person_id_unhashed', self.row_dict.__getitem__('c4clientid'), 'text')
        if self.row_dict.has_key('c4dob'): self.existence_test_and_add('person_date_of_birth_unhashed', self.row_dict.__getitem__('c4dob'), 'text')
        if self.row_dict.has_key('c4sex'):
            ''' convert gender to code '''
            if self.row_dict.__getitem__('c4sex').upper() == 'F': gender = "0"
            elif self.row_dict.__getitem__('c4sex').upper() == 'M': gender = "1"
            if gender is not None:
                self.existence_test_and_add('person_gender_unhashed', gender, 'text')
        if self.row_dict.has_key('c4firstname'): self.existence_test_and_add('person_legal_first_name_unhashed', self.row_dict.__getitem__('c4firstname'), 'text')
        if self.row_dict.has_key('c4lastname'): self.existence_test_and_add('person_legal_last_name_unhashed', self.row_dict.__getitem__('c4lastname'), 'text')
        if self.row_dict.has_key('c4mi'): self.existence_test_and_add('person_legal_middle_name_unhashed', self.row_dict.__getitem__('c4mi'), 'text')
        ''' convert ethnicity to code '''
        if self.row_dict.has_key('hispanic'):
            if self.row_dict.__getitem__('hispanic').upper() == 'N': ethnicity = "0"
            elif self.row_dict.__getitem__('hispanic').upper() == 'Y': ethnicity = "1"
            if ethnicity is not None:
                self.existence_test_and_add('person_ethnicity_unhashed', ethnicity, 'text')
        if self.row_dict.has_key('c4ssno'): self.existence_test_and_add('person_social_security_number_unhashed', self.row_dict.__getitem__('c4ssno').replace('-', ''), 'text')
        self.existence_test_and_add('export_index_id', self.export_index_id, 'no_handling')
        self.shred(self.parse_dict, dbobjects.Person)
        ''' person index id is now in memory, go to the sub-table parsers '''
        self.parse_other_names()
        self.parse_races()
        self.parse_site_service_participation()
        self.parse_household()
        
    def parse_other_names(self):
        ''' parse data for other_names table '''
        self.parse_dict = {}
        ''' check if other last name is unique '''
        if self.row_dict.has_key('c4last_s01') & self.row_dict.has_key('c4lastname'):
            if self.row_dict.__getitem__('c4lastname').lower() != self.row_dict.__getitem__('c4last_s01').lower():
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                self.existence_test_and_add('other_last_name_unhashed', self.row_dict.__getitem__('c4last_s01'), 'text')     
                self.shred(self.parse_dict, dbobjects.OtherNames)

    def parse_races(self):
        ''' parse data for races table '''
        self.parse_dict = {}
        ''' convert race to code '''
        ''' JFCS uses ethnicity to define race '''
        if self.row_dict.has_key('ethnicity'):
            if self.row_dict.__getitem__('ethnicity').upper() == 'M': race = '5'
            elif self.row_dict.__getitem__('ethnicity').upper() == 'H': race = '5'
            elif self.row_dict.__getitem__('ethnicity').upper() == 'W': race = '5'
            elif self.row_dict.__getitem__('ethnicity').upper() == 'B': race = '3'
            if race is not None:
                self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
                self.existence_test_and_add('race_unhashed', race, 'text')
                self.shred(self.parse_dict, dbobjects.Races)
        
    def parse_site_service_participation(self):
        ''' parse data for site_service_participation table '''
        self.parse_dict = {}
        self.existence_test_and_add('person_index_id', self.person_index_id, 'no_handling')
        self.existence_test_and_add('export_index_id', self.export_index_id, 'no_handling')
        try:
            self.existence_test_and_add('site_service_index_id', self.site_service_index_id, 'no_handling')
        except AttributeError:
            pass
        if self.row_dict.has_key('aprgcode'): self.existence_test_and_add('site_service_idid_num', self.row_dict.__getitem__('aprgcode'), 'text')
        if self.row_dict.has_key('a_date'):
            test = self.normalize_date(self.row_dict.__getitem__('a_date'))
            if test == True: self.existence_test_and_add('participation_dates_start_date', self.row_dict.__getitem__('a_date'), 'element_date')
        if self.row_dict.has_key('t_date'):
            test = self.normalize_date(self.row_dict.__getitem__('t_date'))
            if test == True: self.existence_test_and_add('participation_dates_end_date', self.row_dict.__getitem__('t_date'), 'element_date')                
        self.shred(self.parse_dict, dbobjects.SiteServiceParticipation)
        
    def parse_household(self):
        ''' parse data for household table '''
        self.parse_dict = {}
        
        if self.row_dict.has_key('family_id'):
            famid = self.row_dict.__getitem__('family_id')
            '''first check if household id exists before adding it'''
            household = self.session.query(dbobjects.Household).filter(dbobjects.Household.household_id_num == famid).first()#IGNORE:@UndefinedVariable
            if household is None:
                self.existence_test_and_add('household_id_num', famid, 'text')
                self.shred(self.parse_dict, dbobjects.Household)
                ''' household index id is now in memory, go to the sub-table parsers '''
                self.parse_members()
            else:
                if settings.DEBUG:
                    print "Household ID ", famid, "is already in the database; not adding."

    def parse_members(self):
        ''' parse data for members table '''
        self.parse_dict = {}
        if self.row_dict.has_key('c4clientid'):
            clientid= self.row_dict.__getitem__('c4clientid')
            '''first check if household membership exists before adding it'''
            householdmemberships = self.session.query(dbobjects.Members).filter(dbobjects.Members.household_index_id == self.household_index_id and dbobjects.Members.person_index_id == clientid).first()#IGNORE:@UndefinedVariable
            if householdmemberships is None:
                self.existence_test_and_add('household_index_id', self.household_index_id, 'no_handling')
                #get the Person.id for the Person record containing  clientid
                personrecord = self.session.query(dbobjects.Person).filter(dbobjects.Person.person_id_unhashed == clientid).first()#IGNORE:@UndefinedVariable
                self.existence_test_and_add('export_index_id', self.export_index_id, 'no_handling')
                self.existence_test_and_add('person_index_id', personrecord.id, 'no_handling')
                self.existence_test_and_add('household_index_id', self.household_index_id, 'no_handling')
                self.shred(self.parse_dict, dbobjects.Members)

            else:
                if settings.DEBUG:
                    print "Household ID ", self.household_index_id, " is already in the database with member id", clientid, "; not adding."
        
    def shred(self, parse_dict, mapping):
        '''Commits the record set to the database'''
        mapped = mapping(parse_dict)
        self.session.add(mapped)
        self.session.commit()
        #Save the indexes generated at run-time so can be used in dependent tables
        if mapping.__name__ == "Export":
            self.export_index_id = mapped.id
        if mapping.__name__ == "Household":
            self.household_index_id = mapped.id
        if mapping.__name__ == "PersonHistorical":
            self.person_historical_index_id = mapped.id
        if mapping.__name__ == "Person":
            self.person_index_id = mapped.id
            #had to remove this as it was wrecking service_event parsing
            #self.site_service_index_id = None
        if mapping.__name__ == "Service":
            self.service_index_id = mapped.id  
        if mapping.__name__ == "ServiceEvent":
            self.service_event_index_id = mapped.id 
        if mapping.__name__ == "Site":
            self.site_index_id = mapped.id     
        if mapping.__name__ == "SiteService":
            self.site_service_index_id = mapped.id 
        if mapping.__name__ == "SiteServiceParticipation":
            self.site_service_participation_index_id = mapped.id
        if mapping.__name__ == "Source":
            self.source_index_id = mapped.id  
        
    def existence_test_and_add(self, db_column, query_string, handling):
        '''checks that the query actually has a result and adds to dict'''
        #if len(query_string) is not 0:
        if handling == 'no_handling':
                self.persist(db_column, query_string = query_string)
                return True
        elif len(query_string) is not 0 or None:
            if handling == 'attribute_text':
                self.persist(db_column, query_string)
                return True
            if handling == 'text':
                self.persist(db_column, query_string)
                return True
            elif handling == 'attribute_date':
                self.persist(db_column, query_string = dateutil.parser.parse(query_string))
                return True
            elif handling == 'element_date':
                self.persist(db_column, query_string = dateutil.parser.parse(query_string))
                return True
            else:
                print "need to specify the handling"
                return False
        else:
            return False
    
    def persist(self, db_column, query_string):
        ''' build dictionary of db_column:data '''
        self.parse_dict.__setitem__(db_column, query_string)
        return
    
    def normalize_date(self, raw_date):
        if raw_date.replace(' ', '') == '--':
            return False
        elif raw_date.replace(' ', '') == '':
            return False
        else:
            return True
    
    def lookup_or_add_person_index_id(self):
        clientid = self.row_dict.__getitem__('c4clientid')
        '''try to look up person_index_id from person table '''
        person = self.session.query(dbobjects.Person).filter(dbobjects.Person.person_id_unhashed == clientid).first()#IGNORE:@UndefinedVariable
        if person is not None:
            #set the person_index_id foreign key for use in related tables
            self.person_index_id = person.id
            #get more foreign keys to link up our data
            self.lookup_site_service_participation_index_id() 
        else:
            '''if person is not there, add them to the person table'''
            self.parse_person()
        
               
        
    def lookup_site_service_participation_index_id(self):
        ''' lookup site_service_participation_index_id from site_service_participation table '''  
        #not sure if this is the right thing to do, but this finds SiteServiceParticipations for the particular individual at hand
        site_service_participations = self.session.query(dbobjects.SiteServiceParticipation).filter(dbobjects.SiteServiceParticipation.person_index_id == self.person_index_id)#IGNORE:@UndefinedVariable
        for site_service_participation in site_service_participations:
            #set the service_index_id foreign key for use in related tables
            #this makes no sense, because what if there are two siteserviceparticipations?  self.siteserviceindexid gets set and reset
            self.service_index_id = site_service_participation.id        

def lookup_or_add_site_service_id(self, proposed_site_service_id ):
    '''the jfcs xml has the qprogram code in it, which is 'service' in AIRS parlance'''
    '''check if the code is already in the service table.  if not, add it.'''
    self.parse_dict = {}
    '''look it up'''
    site_service_id = self.session.query(dbobjects.SiteService).filter(dbobjects.SiteService.site_service_id == proposed_site_service_id).first()#IGNORE:@UndefinedVariable
    '''If JFCS site_service_id not there, add it'''
    if not site_service_id:
        self.existence_test_and_add('site_service_id', proposed_site_service_id, 'no_handling')
        self.existence_test_and_add('export_index_id', self.export_index_id, 'no_handling')
        thetimenow = str(datetime.now()) 
        self.existence_test_and_add('site_service_recorded_date', thetimenow, 'element_date')
        self.shred(self.parse_dict, dbobjects.SiteService)
    
    #Now that the site service record is for sure in the db, set the service_index_id foreign key for use in related tables, need to get the service.id though for that
    siteserviceid = self.session.query(dbobjects.SiteService.id).filter(dbobjects.SiteService.site_service_id == proposed_site_service_id).first() #IGNORE:@UndefinedVariable
    self.site_service_index_id = siteserviceid  
            
def lookup_or_add_source_id(self, proposed_source_id):
    '''check to see if  JFCS has a source_id assigned.  If it does, retrieve it.  If it doesn't, create one.'''
    '''look up JFCS source_id'''
    self.parse_dict = {}
    source_id = self.session.query(dbobjects.Source).filter(dbobjects.Source.source_id == proposed_source_id).first()#IGNORE:@UndefinedVariable
    
    '''If JFCS source_id not there, add it'''
    if not source_id:
        self.existence_test_and_add('source_id', proposed_source_id, 'no_handling')
        self.existence_test_and_add('source_contact_email', self.source_email, 'text')
        self.existence_test_and_add('source_name', 'JFCS', 'text')

        self.shred(self.parse_dict, dbobjects.Source)
        
    #Now that the source record is for sure in the db, set the source_index_id foreign key for use in related tables, need to get the source.id though for that
    sourceid = self.session.query(dbobjects.Source.id).filter(dbobjects.Source.source_id == proposed_source_id).first() #IGNORE:@UndefinedVariable
    self.source_index_id = sourceid  
    lookup_or_add_source_export_link(self, sourceid)
    
def lookup_or_add_source_export_link(self, sourceprimarykey):
    self.parse_dict = {}
    '''always make a new export and a new link to the source'''
    create_source_export_link(self)
#    '''Check if the export already exists.  To check this, a proper export is linked to a source, so first look for the source in the source/export link table/
#    ,then, locate the export_id in that record.  If the source is not there in the linker table, then we need to create the linkage record.
#    To create the linker record, first add a new export record to the export table.   Then use the export.id generated from that to use in the linker table.   '''
#    
#    '''so first look for the source in the source/export link table, then, locate the export_id in that record'''
#    source_export_link_id = self.session.query(dbobjects.SourceExportLink.id).filter(dbobjects.SourceExportLink.source_index_id == sourceprimarykey).first()#IGNORE:@UndefinedVariable
#    '''If the source is not there in the linker table, then we need to create the linkage record.'''
#    if not source_export_link_id:
#        create_source_export_link(self)

def create_source_export_link(self):
    '''To create the source export link record, first add a new export record to the export table.'''
    '''you don't need to search for it first, because it would have a linker'''
        #print 'time now is: ', datetime.now()
    thetimenow = str(datetime.now())    
    self.existence_test_and_add('export_date', thetimenow, 'element_date')
    self.shred(self.parse_dict, dbobjects.Export)
    '''Then use the export.id generated from that to use in the source export link table.'''
    self.parse_dict = {}
    self.existence_test_and_add('export_index_id', self.export_index_id, 'no_handling')
    self.existence_test_and_add('source_index_id', self.source_index_id, 'no_handling')
    self.shred(self.parse_dict, dbobjects.SourceExportLink)
    
def main(argv=None):
    ''' Test the JFCSXMLReader class '''
    
    ''' Check if arguments manually passed to main '''
    if argv is None:
        argv = sys.argv

    ''' Select input file '''
    inputFile = "/mnt/laptop01/Projects/Alexandria/DATA/StagingFiles/CRG.xml"
    #inputFile = "/mnt/laptop01/Projects/Alexandria/DATA/StagingFiles/CRG.xml.pgp"
    #inputFile = "/mnt/laptop01/Projects/Alexandria/DATA/StagingFiles/PEO.xml"
    #inputFile = "/mnt/laptop01/Projects/Alexandria/DATA/StagingFiles/PEO.xml.pgp"
    
    ''' Set the data_type '''
    data_type = 'service'
    
    ''' Test for existance and ability to read input file '''
    if os.path.isfile(inputFile) is True:
        try:
            xml_file = open(inputFile, 'r')
        except:
            print "Error opening input file"
                
        ''' Process input file '''
        reader = JFCSXMLReader(xml_file)
        tree = reader.read()
        reader.process_data(tree, data_type)
        xml_file.close()
            
if __name__ == "__main__":
    sys.exit(main())
    