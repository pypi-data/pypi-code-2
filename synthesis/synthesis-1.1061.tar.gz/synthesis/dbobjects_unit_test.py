'''Unit-tests various XML/CSV validation scenarios (called tests also) in 
selector.py.'''
#from dbobjects import DatabaseObjects, Export, Database, Household, HUDHomelessEpisodes, IncomeAndSources, Members, OtherNames, Person, PersonAddress, PersonHistorical, Races,
import dbobjects
import unittest
#import os
#from synthesis import postgresutils

class SelectorTestCase(unittest.TestCase):
    '''see if the return value is a file path'''
    def test_get_export(self):
        '''Tests if you can pull the export record from the database that have been imported/shredded.'''
        mappedObjects = dbobjects.DatabaseObjects(pg_db)
        theExport = mappedObjects.queryDB(dbobjects.Export)[0]
        if settings.DEBUG:
            print theExport.export_software_vendor
        self.assertEqual(theExport.export_software_vendor, "HMIS_'R_Us")
        
    
    def test_get_export_children(self):
        '''Tests if you can pull the exports related records from the database that have been imported/shredded.
        mapper(Export, export_table, properties={'fk_export_to_person': relation(Person), 'fk_export_to_database': relation(Database)})
        '''
        mappedObjects = dbobjects.DatabaseObjects(pg_db)
        # first get the export object then get it's related objects
        theExports = mappedObjects.queryDB(dbobjects.Export)
        for export in theExports:
            child = export.fk_export_to_person[0]
        if settings.DEBUG:
            print child.person_legal_first_name_unhashed
            
        #self.assertEqual(child.person_legal_first_name_unhashed, "George")
        self.assertTrue((child.person_social_security_number_unhashed=="111111111") and (child.person_legal_first_name_unhashed=="George"))
        
    def test_get_exports_children_backref(self):
        '''Tests if you can pull the exports related records from the database that have been imported/shredded.
        mapper(Export, export_table, properties={'fk_export_to_person': relation(Person), 'fk_export_to_database': relation(Database)})
        '''
        mappedObjects = dbobjects.DatabaseObjects(pg_db)
        theExports = mappedObjects.queryDB(dbobjects.Export).first()
        if settings.DEBUG:
            print 'Software Vendor: %s' % theExports.export_software_vendor
            
        dbo = theExports.fk_export_to_database[0]
        print 'type: %s' % type(dbo)
        
        if settings.DEBUG:
            print 'dbo.database_contact_phone=%s' %dbo.database_contact_phone
        
        self.assertTrue(dbo.database_email=='test@test.com')
    
#    def test_get_exports_from_database(self):
#        '''Tests if you can pull the exports related records from the database that have been imported/shredded.
#        mapper(Export, export_table, properties={'fk_export_to_person': relation(Person), 'fk_export_to_database': relation(Database)})
#        '''
#        mappedObjects = dbobjects.DatabaseObjects(pg_db)
#        dbo = mappedObjects.queryDB(dbobjects.Database).one()
#        if settings.DEBUG:
#            print 'dbo.database_contact_phone=%s' %dbo.database_contact_phone
#
#        theExport = dbo.fk_database_to_export
#        print 'export_software_vendor = %s' % theExport.export_software_vendor
#
#        if settings.DEBUG:        
#            print theExport.export_date
#        
#        self.assertTrue(theExport.export_date.strftime("%Y-%m-%dT%H:%M:%S")=='2004-12-15T00:00:00')
    
#    def test_get_persons_from_database(self):
#        '''Tests if you can pull the exports related records from the database that have been imported/shredded.
#        mapper(Export, export_table, properties={'fk_export_to_person': relation(Person), 'fk_export_to_database': relation(Database)})
#        '''
#        mappedObjects = dbobjects.DatabaseObjects(pg_db)
#        dbo = mappedObjects.queryDB(dbobjects.Database).one()
#        if settings.DEBUG:
#            print 'dbo.database_contact_last=%s' %dbo.database_contact_last
#
#        # pull the related export record
#        theExport = dbo.fk_database_to_export
#        if settings.DEBUG:
#            print 'export_software_vendor = %s' % theExport.export_software_vendor
#            
#        thePersons = dbo.fk_database_to_export.fk_export_to_person
#        
#        for thePerson in thePersons:
#            print thePerson.person_legal_first_name_unhashed
#            if thePerson.person_social_security_number_unhashed=='111678912':
#                break
            
        # pull one person using ssn to find
        #thePerson = thePersons.filter(Person.person_social_security_number_unhashed=='111678912')
#        if settings.DEBUG:
#            print 'ssn: %s' % thePerson.person_social_security_number_unhashed
#        
#        self.assertTrue(thePerson.person_legal_last_name_unhashed=='Kennedy')
#    
    def test_get_person_historical(self):
        '''Test if you can pull person_historical records from the database that have been imported/shredded
        '''
        mappedObjects = dbobjects.DatabaseObjects(pg_db)
        ph = mappedObjects.queryDB(dbobjects.PersonHistorical).all()
        
        for historical in ph:    
            if settings.DEBUG:
                print 'historical.person_historical_id_num=%s' %historical.person_historical_id_num
            
        self.assertEqual(len(ph),6)
            
    
    def test_get_person_historicals_children_backref(self):
        '''Tests if you can pull the children (IncomeAndSources) of person historical and get back to the person record for all records who earned $100
        mapper(PersonHistorical, person_historical_table, properties={'fk_income_and_sources': relation(IncomeAndSources), 'fk_veteran': relation(Veteran),'fk_hud_homeless_episodes': relation(HUDHomelessEpisodes),'fk_person_address': relation(PersonAddress)})
        '''
        
        mappedObjects = dbobjects.DatabaseObjects(pg_db)
        ias = mappedObjects.queryDB(dbobjects.IncomeAndSources).filter_by(amount=100).all()
        
        for ia in ias:
            if settings.DEBUG:
                print 'IncomeAndSources.person_historical_id_num=%s' % ia.income_source_code
        
        p = ias[0].fk_income_and_sources_to_person_historical.fk_person_historical_to_person
        
        self.assertEqual(p.person_social_security_number_unhashed,'111111111')
        
    
    def test_get_other_names(self):
        '''Tests that there are 0 'othername' records in the database
        '''
        mappedObjects = dbobjects.DatabaseObjects(pg_db)
        cnt_other_names = mappedObjects.queryDB(dbobjects.OtherNames).count()
        
        self.assertEqual(cnt_other_names,0)
            
#    def test_count_persons_who_are_looking_for_work(self):
#        '''Query database for all persons who are looking for work.
#        '''
#        settings.DEBUG_ALCHEMY = True
#        mappedObjects = dbobjects.DatabaseObjects(pg_db)
#        '''
#            session.query(User).join('addresses').\
#        ...     filter(Address.email_address=='jack@google.com').all()
#            .join(['bars', 'bats', 'widgets'])
#        '''
#        personVet_count = mappedObjects.queryDB(dbobjects.Person).\
#        join('fk_person_to_person_historical').filter(dbobjects.PersonHistorical.looking_for_work==1).count()
#        
#        self.assertEqual(personVet_count,1)
        
#    def test_count_persons_who_are_veterans(self):
#        '''Query database for all persons who are veterans.
#        '''
#        settings.DEBUG_ALCHEMY = True
#        mappedObjects = dbobjects.DatabaseObjects(pg_db)
#        '''
#            session.query(User).join('addresses').\
#        ...     filter(Address.email_address=='jack@google.com').all()
#            .join(['bars', 'bats', 'widgets'])
#        '''
#        personVet_count = mappedObjects.queryDB(dbobjects.Person).\
#        join(['fk_person_to_person_historical','fk_person_historical_to_veteran']).\
#        filter(dbobjects.Veteran.service_era==1).distinct().count()
#        
#        self.assertEqual(personVet_count,1)
        
#    def test_george_washington_was_minuteman(self):
#        '''Query database for first person who was a minuteman that will show his last name is Washington
#        '''
#        settings.DEBUG_ALCHEMY = True
#        mappedObjects = dbobjects.DatabaseObjects(pg_db)
#        '''
#            session.query(User).join('addresses').\
#        ...     filter(Address.email_address=='jack@google.com').all()
#            .join(['bars', 'bats', 'widgets'])
#        '''
#        veteran = mappedObjects.queryDB(dbobjects.Person).\
#        join(['fk_person_to_person_historical','fk_person_historical_to_veteran']).\
#        filter(dbobjects.Veteran.military_branch_other=='Minutemen').all()
#        
#        self.assertEqual(veteran[0].person_legal_last_name_unhashed,'Washington')
#        
    def test_number_of_persons_who_live_in_anytown_florida(self):
        '''Query database for count of people who live in anytown Florida
        '''
        settings.DEBUG_ALCHEMY = True
        mappedObjects = dbobjects.DatabaseObjects(pg_db)
        '''
            session.query(User).join('addresses').\
        ...     filter(Address.email_address=='jack@google.com').all()
            .join(['bars', 'bats', 'widgets'])
        '''
        veteranCnt = mappedObjects.queryDB(dbobjects.Person).\
        join(['fk_person_to_person_historical','fk_person_historical_to_person_address']).\
        filter_by(city='Anytown', state='Florida').count()
        
        if settings.DEBUG:
            people = mappedObjects.queryDB(dbobjects.Person).\
                join(['fk_person_to_person_historical','fk_person_historical_to_person_address']).\
                filter_by(city='Anytown', state='Florida').all()
            for person in people:
                print '%s is from AnyTown, FL' % person.person_legal_first_name_unhashed
        
        self.assertEqual(veteranCnt,1)
         
if __name__ == '__main__':
    # Wipe the DB first
    #import postgresutils
    #UTILS = postgresutils.Utils()
    #UTILS.blank_database()
    from sqlalchemy import create_engine#, Table, Column, Numeric, Integer, String, Boolean, MetaData, ForeignKey, Sequence
    #from sqlalchemy.orm import sessionmaker, mapper, backref, relation, clear_mappers
    #from sqlalchemy.types import DateTime, Date
    from conf import settings
    
    print 'Settings _debug val: %s' % settings.DEBUG
    
    if settings.DB_PASSWD == "":
        settings.DB_PASSWD = raw_input("Please enter your password: ")
        
    pg_db = create_engine('postgresql://%s:%s@localhost:5432/%s' % (settings.DB_USER, settings.DB_PASSWD, settings.DB_DATABASE), echo=settings.DEBUG_ALCHEMY)#, server_side_cursors=True)
    
    
    
    unittest.main()