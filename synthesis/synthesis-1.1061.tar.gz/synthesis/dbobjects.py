#!/usr/bin/env python

from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, MetaData, ForeignKey
from sqlalchemy.orm import sessionmaker, mapper, relation, clear_mappers
from sqlalchemy.types import DateTime, Date
from sqlalchemy import exceptions as sqlalchemyexceptions
import sys
from conf import settings
from logger import Logger

from synthesis import fileutils

class DatabaseObjects:

    #postgresql[+driver]://<user>:<pass>@<host>/<dbname>    #, server_side_cursors=True)    
    database_string = 'postgresql+psycopg2://' + settings.DB_USER + ':' + settings.DB_PASSWD + '@' + settings.DB_HOST + ':' + str(settings.DB_PORT) + '/' + settings.DB_DATABASE
    #print database_string
    pg_db_engine = create_engine(database_string, echo=settings.DEBUG_ALCHEMY)

    # this is needed to do real work.'
    #This Session is a class which you contruct as needed in reader classes
    Session = sessionmaker(bind=pg_db_engine)
    #print "session is: ", Session
    def __init__(self):
        try:
            
            # SBB20100210 Change the logging level based on configuration file.
            if settings.DEBUG_ALCHEMY:
                loglevel = 'info'
            else:
                loglevel = 'error'
            
            loglevel = 'debug'    
            log = Logger(settings.LOGGING_INI,loglevel=loglevel)
            log.getLogger('sqlalchemy.orm.unitofwork').setLevel(log.logger.debug)
            
            # map the ORM
            clear_mappers()
            self.createMappings()
            
        except sqlalchemyexceptions.OperationalError:
            msg = "Database [%s] does not exist." % settings.DB_DATABASE
           
            fileutils.makeBlock(msg)
            rc = raw_input('Would you like to create the database now? (y/N/C)')
            if rc == 'y':
                from synthesis import postgresutils
                UTILS = postgresutils.Utils()
                UTILS.create_database(settings.DB_DATABASE)
            else:
                msg = "Please create Database [%s] and restart process." % settings.DB_DATABASE
                fileutils.makeBlock(msg)
                
    def queryDB(self, object):
        #session = self.session()
        return self.session().query(object)
        
    def createMappings(self):
        self.export_map()
        self.report_map()
        self.source_map()
        self.person_map()        
        self.service_map()
        self.source_export_link_map()
        self.household_map()
        self.region_map()
        self.agency_map()
        self.agency_child_map()
        self.service_group_map()
        self.license_accreditation_map()
        self.agency_service_map()
        self.agency_location_map()
        self.site_map()
        self.url_map()
        self.spatial_location_map()
        self.other_address_map()
        self.cross_street_map()
        self.aka_map()
        self.site_service_map()
        self.seasonal_map()
        self.residency_requirements_map()
        self.pit_count_set_map()
        self.pit_counts_map()
        self.other_requirements_map()
        self.languages_map()
        self.time_open_map()
        self.time_open_days_map()
        self.inventory_map()
        self.income_requirements_map()
        self.hmis_asset_map()
        self.assignment_map()
        self.assignment_period_map()
        self.geographic_area_served_map()
        self.documents_required_map()
        self.aid_requirements_map()
        self.age_requirements_map()
        self.site_service_participation_map()
        self.reasons_for_leaving_map()
        self.application_process_map()
        self.need_map()
        self.taxonomy_map()
        self.service_event_map()
        self.service_event_notes_map()
        self.family_requirements_map()
        self.person_historical_map()
        self.housing_status_map()
        self.veteran_military_branches_map()
        self.veteran_military_service_duration_map()
        self.veteran_served_in_war_zone_map()
        self.veteran_service_era_map()
        self.veteran_veteran_status_map()
        self.veteran_warzones_served_map()
        self.vocational_training_map()
        self.foster_child_ever_map()
        self.substance_abuse_problem_map()
        self.pregnancy_map()
        self.prior_residence_map()
        self.physical_disability_map()
        self.non_cash_benefits_map()
        self.non_cash_benefits_last_30_days_map()
        self.mental_health_problem_map()
        self.length_of_stay_at_prior_residence_map()
        self.income_total_monthly_map()
        self.hud_chronic_homeless_map()
        self.income_last_30_days_map()
        self.highest_school_level_map()
        self.hiv_aids_status_map()
        self.health_status_map()
        self.engaged_date_map()
        self.employment_map()
        self.domestic_violence_map()
        self.disabling_condition_map()
        self.developmental_disability_map()
        self.destinations_map()
        self.degree_map()
        self.degree_code_map()      
        self.currently_in_school_map()
        self.contact_made_map()
        self.child_enrollment_status_map()
        self.child_enrollment_status_barrier_map()
        self.chronic_health_condition_map()
        self.release_of_information_map()
        self.income_and_sources_map()
        self.veteran_map()
        self.drug_history_map()
        self.emergency_contact_map()
        self.hud_homeless_episodes_map()
        self.person_address_map()
        self.other_names_map()
        self.races_map()
        self.member_map()       
        self.funding_source_map()
        self.resource_info_map()
        self.contact_map()
        self.email_map()
        self.phone_map()
        
        # SBB20100303 Adding objects to deduplicate the DB Entries
        #self.dedup_link_map()
        # SBB20100327 adding object to maintain odbid's for each site.  Svcpoint requires these for valid xml uploads
        self.system_configuration_map()
        
    def system_configuration_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db)
        system_configuration_table = Table(
        'sender_system_configuration', 
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('vendor_name', String(50)),
        Column('processing_mode', String(4)),                   # TEST or PROD
        Column('source_id', String(50)),
        Column('odbid', Integer),
        Column('providerid', Integer),
        Column('userid', Integer),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(SystemConfiguration, system_configuration_table) 
        return
        
#    def dedup_link_map(self):
#        table_metadata = MetaData(bind=self.pg_db_engine)
#        #table_metadata = MetaData(bind=self.sqlite_db)
#        dedup_link_table = Table(
#        'dedup_link', 
#        table_metadata,
#        #Column('id', Integer, primary_key=True),
#        Column('source_rec_id', Integer, ForeignKey(Person.id), primary_key=True),
#        Column('destination_rec_id', Integer, ForeignKey(Person.id), primary_key=True),
#        Column('weight_factor', Integer),
#        useexisting = True
#        )
#        table_metadata.create_all()
#        mapper(DeduplicationLink, dedup_link_table, properties={'fk_source_person': relation(Person, primaryjoin=Person.id==dedup_link_table.source_rec_id),
#                                                                'fk_dest_person': relation(Person, primaryjoin=Person.id==dedup_link_table.destination_rec_id)})
#        #mapper(Export, export_table, properties={'children': relation(Person), 'children': relation(Database)})
#        return
    
    def service_event_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        service_event_table = Table(
        'service_event',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)),
        Column('household_index_id',  Integer, ForeignKey(Household.id)),
        Column('person_index_id', Integer, ForeignKey(Person.id)),
        Column('need_index_id', Integer, ForeignKey(Need.id)),
        Column('site_service_participation_index_id', Integer, ForeignKey(SiteServiceParticipation.id)),
        Column('service_event_idid_num', String(32)),
        Column('service_event_idid_num_date_collected', DateTime(timezone=False)),
        Column('service_event_idid_str', String(32)),
        Column('service_event_idid_str_date_collected', DateTime(timezone=False)),
        Column('household_idid_num', String(32)),
        Column('is_referral', String(32)),
        Column('is_referral_date_collected', DateTime(timezone=False)),
        Column('quantity_of_service', String(32)),
        Column('quantity_of_service_date_collected', DateTime(timezone=False)),
        Column('quantity_of_service_measure', String(32)),
        Column('quantity_of_service_measure_date_collected', DateTime(timezone=False)),
        Column('service_airs_code', String(32)),
        Column('service_airs_code_date_collected', DateTime(timezone=False)),
        Column('service_period_start_date', DateTime(timezone=False)),
        Column('service_period_start_date_date_collected', DateTime(timezone=False)),
        Column('service_period_end_date', DateTime(timezone=False)),
        Column('service_period_end_date_date_collected', DateTime(timezone=False)),
        Column('service_unit', String(32)),
        Column('service_unit_date_collected', DateTime(timezone=False)),
        Column('type_of_service', String(32)),
        Column('type_of_service_date_collected', DateTime(timezone=False)),
        Column('type_of_service_other', String(32)),
        Column('type_of_service_other_date_collected', DateTime(timezone=False)),
        Column('type_of_service_par', Integer(2)),
        #adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),
        Column('service_event_id_delete', String(32)),
        Column('service_event_ind_fam', Integer),
        Column('site_service_id', String(50)),
        Column('hmis_service_event_code_type_of_service', String(50)),
        Column('hmis_service_event_code_type_of_service_other', String(50)),
        Column('hprp_financial_assistance_service_event_code', String(50)),
        Column('hprp_relocation_stabilization_service_event_code', String(50)),
        Column('service_event_id_delete_occurred_date', DateTime(timezone=False)),
        Column('service_event_id_delete_effective_date', DateTime(timezone=False)),
        Column('service_event_provision_date', DateTime(timezone=False)),
        Column('service_event_recorded_date', DateTime(timezone=False)),
        useexisting = True)
        table_metadata.create_all()
        mapper(ServiceEvent, service_event_table)#, properties={'children': relation(#tablename#), 'children': relation(#tablename#), 'children': relation(#tablename#)})
        return

    def need_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        need_table = Table(
        'need',
        table_metadata,
        
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteServiceParticipation.id)),
    
    # dbCol: need_idid_num
        Column('need_idid_num', String(32)),
        Column('need_idid_num_date_collected', DateTime(timezone=False)),
    
    # dbCol: need_idid_str
        Column('need_idid_str', String(32)),
        Column('need_idid_str_date_collected', DateTime(timezone=False)),
    
    # dbCol: site_service_idid_num
        Column('site_service_idid_num', String(32)),
        Column('site_service_idid_num_date_collected', DateTime(timezone=False)),
    
    # dbCol: site_service_idid_str
        Column('site_service_idid_str', String(32)),
        Column('site_service_idid_str_date_collected', DateTime(timezone=False)),
    
    # dbCol: service_event_idid_num
        Column('service_event_idid_num', String(32)),
        Column('service_event_idid_num_date_collected', DateTime(timezone=False)),
    
    # dbCol: service_event_idid_str
        Column('service_event_idid_str', String(32)),
        Column('service_event_idid_str_date_collected', DateTime(timezone=False)),
    
    # dbCol: need_status
        Column('need_status', String(32)),
        Column('need_status_date_collected', DateTime(timezone=False)),
    
    # dbCol: taxonomy
        Column('taxonomy', String(32)),
        
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),

        ## HUD 3.0
        Column('person_index_id', Integer, ForeignKey(Person.id)),
        Column('need_id_delete', String(32)),
        Column('need_id_delete_occurred_date', DateTime(timezone=False)),
        Column('need_id_delete_delete_effective_date', DateTime(timezone=False)),
        Column('need_effective_period_start_date', DateTime(timezone=False)),
        Column('need_effective_period_end_date', DateTime(timezone=False)),
        Column('need_recorded_date', DateTime(timezone=False)),

        useexisting = True)
        table_metadata.create_all()
    
        mapper(Need, need_table)#, properties={'children': relation(#tablename#), 'children': relation(#tablename#), 'children': relation(#tablename#)})
        return

    def site_service_participation_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        site_service_participation_table = Table(
        'site_service_participation',
        table_metadata,
    
        Column('id', Integer, primary_key=True),
        Column('person_index_id', Integer, ForeignKey(Person.id)),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)),
        Column('household_index_id', Integer, ForeignKey(Household.id)),
        Column('site_service_participation_idid_num', String(32)),
        Column('site_service_participation_idid_num_date_collected', DateTime(timezone=False)),
        Column('site_service_participation_idid_str', String(32)),
        Column('site_service_participation_idid_str_date_collected', DateTime(timezone=False)),
        Column('destination', String(32)),
        Column('destination_date_collected', DateTime(timezone=False)),
        Column('destination_other', String(32)),
        Column('destination_other_date_collected', DateTime(timezone=False)),
        Column('destination_tenure', String(32)),
        Column('destination_tenure_date_collected', DateTime(timezone=False)),
        Column('disabling_condition', String(32)),
        Column('disabling_condition_date_collected', DateTime(timezone=False)),
        Column('participation_dates_start_date', DateTime(timezone=False)),
        Column('participation_dates_start_date_date_collected', DateTime(timezone=False)),
        Column('participation_dates_end_date', DateTime(timezone=False)),
        Column('participation_dates_end_date_date_collected', DateTime(timezone=False)),
        Column('veteran_status', String(32)),
        Column('veteran_status_date_collected', DateTime(timezone=False)),
        #adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),
        Column('site_service_participation_id_delete', String(32)),
        Column('site_service_participation_id_delete_occurred_date', DateTime(timezone=False)),
        Column('site_service_participation_id_delete_effective_date', DateTime(timezone=False)),
    # dbCol: discharge_type (Operations PARS)
    #    Column('discharge_type', Integer(2)),
    #    Column('discharge_type_date_collected', DateTime(timezone=False)),
    #
    ## dbCol: health_status_at_discharge (Operations PARS)
    #    Column('health_status_at_discharge', Integer(2)),
    #    Column('health_status_at_discharge_date_collected', DateTime(timezone=False)),
    #
    ## dbCol: va_eligibility (Operations PARS)
    #    Column('va_eligibility', Integer(2)),
    #    Column('va_eligibility_date_collected', DateTime(timezone=False)),
        useexisting = True)
        table_metadata.create_all()
        
        mapper(SiteServiceParticipation, site_service_participation_table, properties={'fk_participation_to_need': relation(Need, backref='fk_need_to_participation'),
                                                                                       'fk_participation_to_serviceevent' : relation(ServiceEvent),
                                                                                       'fk_participation_to_personhistorical' : relation(PersonHistorical),
                                                                                       'fk_participation_to_person' : relation(Person)
                                                                                       }
               )#, 'children': relation(#tablename#), 'children': relation(#tablename#)})
        return
        
    def races_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db, reflect=False)
        races_table = Table(
        'races', 
        table_metadata, 
        Column('id', Integer, primary_key=True),
        Column('person_index_id', Integer, ForeignKey(Person.id)),
        Column('race_unhashed', Integer(2)),
        Column('race_hashed', String(32)),
        Column('race_date_collected', DateTime(timezone=False)),
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),

        ## HUD 3.0
        Column('race_data_collection_stage', String(32)),
        Column('race_date_effective', DateTime(timezone=False)),
                
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Races, races_table)
        return            
        
    def export_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db)
        export_table = Table(
        'export', 
        table_metadata, 
        Column('id', Integer, primary_key=True),
        Column('export_id', String(50), primary_key=False, unique=False), 
        Column('export_id_date_collected', DateTime(timezone=False)),
        Column('export_date', DateTime(timezone=False)),
        Column('export_date_date_collected', DateTime(timezone=False)),
        Column('export_period_start_date', DateTime(timezone=False)),
        Column('export_period_start_date_date_collected', DateTime(timezone=False)),
        Column('export_period_end_date', DateTime(timezone=False)),
        Column('export_period_end_date_date_collected', DateTime(timezone=False)),
        Column('export_software_vendor', String(50)),
        Column('export_software_vendor_date_collected', DateTime(timezone=False)),
        Column('export_software_version', String(10)),
        Column('export_software_version_date_collected', DateTime(timezone=False)),

        ## HUD 3.0
        Column('export_id_id_id_num', String(50)),
        Column('export_id_id_id_str', String(50)),
        Column('export_id_delete_occurred_date', DateTime(timezone=False)),
        Column('export_id_delete_effective_date', DateTime(timezone=False)),        
        Column('export_id_delete', String(32)),        
        useexisting = True
        )
        
        table_metadata.create_all()
        #mapper(Export, export_table, properties={'children': [relation(Person), relation(Database)]})
        mapper(Export, export_table, properties={
            'fk_export_to_person': relation(Person, backref='fk_person_to_export')
            ,'fk_export_to_household': relation(Household, backref='fk_household_to_export')
#            ,'fk_export_to_database': relation(Source, backref='fk_database_to_export')
            })
        #for debugging if the wrong sqlalchemy version is being used (>0.4.7)
        #if settings.DEBUG:
            #import pdb; pdb.set_trace()
            #print 'Export.c is', Export.c
            #import sqlalchemy
            #print 'sqlalchemy version is ', sqlalchemy.__version__, 'maybe it should be 0.4.7 and your os environment is contributing a higher version'
        return

    def report_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db)
        report_table = Table(
        'report', 
        table_metadata, 
        Column('report_id', String(50), primary_key=True, unique=True), 
        Column('report_id_date_collected', DateTime(timezone=False)),
        Column('report_date', DateTime(timezone=False)),
        Column('report_date_date_collected', DateTime(timezone=False)),
        Column('report_period_start_date', DateTime(timezone=False)),
        Column('report_period_start_date_date_collected', DateTime(timezone=False)),
        Column('report_period_end_date', DateTime(timezone=False)),
        Column('report_period_end_date_date_collected', DateTime(timezone=False)),
        Column('report_software_vendor', String(50)),
        Column('report_software_vendor_date_collected', DateTime(timezone=False)),
        Column('report_software_version', String(10)),
        Column('report_software_version_date_collected', DateTime(timezone=False)),

        ## HUD 3.0
        Column('report_id_id_id_num', String(50)),
        Column('report_id_id_id_str', String(50)),
        Column('report_id_id_delete_occurred_date', DateTime(timezone=False)),
        Column('report_id_id_delete_effective_date', DateTime(timezone=False)),        
        Column('report_id_id_delete', String(32)),        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Report, report_table, properties={
            'fk_report_to_person': relation(Person, backref='fk_person_to_report')
            ,'fk_report_to_household': relation(Household, backref='fk_household_to_report')
            ,'fk_report_to_database': relation(Source, backref='fk_database_to_report')
            })
        return

    
    def other_names_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db, reflect=False)
        other_names_table = Table(
        'other_names', 
        table_metadata, 
        Column('id', Integer, primary_key=True),
        Column('person_index_id', Integer, ForeignKey(Person.id)), 
        Column('other_first_name_unhashed', String(50)),
        Column('other_first_name_hashed', String(50)),
        Column('other_first_name_date_collected', DateTime(timezone=False)),
        Column('other_first_name_date_effective', DateTime(timezone=False)),
        Column('other_first_name_data_collection_stage', String(32)),
        Column('other_middle_name_unhashed', String(50)),
        Column('other_middle_name_hashed', String(50)),
        Column('other_middle_name_date_collected', DateTime(timezone=False)),
        Column('other_middle_name_date_effective', DateTime(timezone=False)),
        Column('other_middle_name_data_collection_stage', String(32)),
        Column('other_last_name_unhashed', String(50)),
        Column('other_last_name_hashed', String(50)),
        Column('other_last_name_date_collected', DateTime(timezone=False)),
        Column('other_last_name_date_effective', DateTime(timezone=False)),
        Column('other_last_name_data_collection_stage', String(32)),
        Column('other_suffix_unhashed', String(50)),
        Column('other_suffix_hashed', String(50)),
        Column('other_suffix_date_collected', DateTime(timezone=False)),
        Column('other_suffix_date_effective', DateTime(timezone=False)),
        Column('other_suffix_data_collection_stage', String(32)),

        useexisting = True
        )
        table_metadata.create_all()
        mapper(OtherNames, other_names_table)
        return
    
    
    def hud_homeless_episodes_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        hud_homeless_episodes_table = Table(
        'hud_homeless_episodes',
        table_metadata,
        
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)),
        
    # dbCol: start_date
        Column('start_date', String(32)),
        Column('start_date_date_collected', DateTime(timezone=False)),
    
    # dbCol: end_date
        Column('end_date', String(32)),
        Column('end_date_date_collected', DateTime(timezone=False)),
    
        useexisting = True)
        table_metadata.create_all()
    
        mapper(HUDHomelessEpisodes, hud_homeless_episodes_table)
            
        return
    
    def veteran_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db)
        veteran_table = Table(
        'veteran', 
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)),
    # dbCol: service_era
        Column('service_era', Integer),
        Column('service_era_date_collected', DateTime(timezone=False)),

    # dbCol: military_service_duration
        Column('military_service_duration', Integer),
        Column('military_service_duration_date_collected', DateTime(timezone=False)),

    # dbCol: served_in_war_zone
        Column('served_in_war_zone', Integer),
        Column('served_in_war_zone_date_collected', DateTime(timezone=False)),

    # dbCol: war_zone
        Column('war_zone', Integer),
        Column('war_zone_date_collected', DateTime(timezone=False)),

    # dbCol: war_zone_other
        Column('war_zone_other', String(50)),
        Column('war_zone_other_date_collected', DateTime(timezone=False)),

    # dbCol: months_in_war_zone
        Column('months_in_war_zone', Integer),
        Column('months_in_war_zone_date_collected', DateTime(timezone=False)),

    # dbCol: received_fire
        Column('received_fire', Integer),
        Column('received_fire_date_collected', DateTime(timezone=False)),

    # dbCol: military_branch
        Column('military_branch', Integer),
        Column('military_branch_date_collected', DateTime(timezone=False)),

    # dbCol: military_branch_other
        Column('military_branch_other', String(50)),
        Column('military_branch_other_date_collected', DateTime(timezone=False)),

    # dbCol: discharge_status
        Column('discharge_status', Integer),
        Column('discharge_status_date_collected', DateTime(timezone=False)),

    # dbCol: discharge_status_other
        Column('discharge_status_other', String(50)),
        Column('discharge_status_other_date_collected', DateTime(timezone=False)),
        
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),
        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Veteran, veteran_table)
        return

    def drug_history_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        drug_history_table = Table(
        'drug_history',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)),

        # dbCol: drug_history_id
            Column('drug_history_id', String(32)),
            Column('drug_history_id_date_collected', DateTime(timezone=False)),
        # dbCol: drug_code
            Column('drug_code', Integer(2)),
            Column('drug_code_date_collected', DateTime(timezone=False)),    
        # dbCol: drug_use_frequency
            Column('drug_use_frequency', Integer(2)),
            Column('drug_use_frequency_date_collected', DateTime(timezone=False)),

        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),

        useexisting = True
        )
        table_metadata.create_all()
        mapper(DrugHistory, drug_history_table)
        return

    def emergency_contact_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        emergency_contact_table = Table(
        'emergency_contact',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)),

        # dbCol: emergency_contact_id
            Column('emergency_contact_id', String(32)),
            Column('emergency_contact_id_date_collected', DateTime(timezone=False)),
        # dbCol: emergency_contact_name
            Column('emergency_contact_name', String(32)),
            Column('emergency_contact_name_date_collected', DateTime(timezone=False)),    
        # dbCol: emergency_contact_phone_number-0
            Column('emergency_contact_phone_number_0', String(32)),
            Column('emergency_contact_phone_number_date_collected_0', DateTime(timezone=False)),
            Column('emergency_contact_phone_number_type_0', String(32)),
        # dbCol: emergency_contact_phone_number-1
            Column('emergency_contact_phone_number_1', String(32)),
            Column('emergency_contact_phone_number_date_collected_1', DateTime(timezone=False)),
            Column('emergency_contact_phone_number_type_1', String(32)),
        # dbCol: emergency_contact_address
            Column('emergency_contact_address_date_collected', DateTime(timezone=False)),
        # dbCol: emergency_contact_address_start_date
            Column('emergency_contact_address_start_date', DateTime(timezone=False)),
            Column('emergency_contact_address_start_date_date_collected', DateTime(timezone=False)),
        # dbCol: emergency_contact_address_end_date
            Column('emergency_contact_address_end_date', DateTime(timezone=False)),
            Column('emergency_contact_address_end_date_date_collected', DateTime(timezone=False)),
        # dbCol: emergency_contact_address_line1
            Column('emergency_contact_address_line1', String(32)),
            Column('emergency_contact_address_line1_date_collected', DateTime(timezone=False)),
        # dbCol: emergency_contact_address_line2
            Column('emergency_contact_address_line2', String(32)),
            Column('emergency_contact_address_line2_date_collected', DateTime(timezone=False)),
        # dbCol: emergency_contact_address_city
            Column('emergency_contact_address_city', String(32)),
            Column('emergency_contact_address_city_date_collected', DateTime(timezone=False)),
        # dbCol: emergency_contact_address_state
            Column('emergency_contact_address_state', String(32)),
            Column('emergency_contact_address_state_date_collected', DateTime(timezone=False)),    
        # dbCol: emergency_contact_relation_to_client
            Column('emergency_contact_relation_to_client', String(32)),
            Column('emergency_contact_relation_to_client_date_collected', DateTime(timezone=False)),
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),

        useexisting = True
        )
        table_metadata.create_all()
        mapper(EmergencyContact, emergency_contact_table)
        return
                
    def person_address_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db)
        person_address_table = Table(
        'person_address', 
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)),
        Column('address_period_start_date',DateTime(timezone=False)),
        Column('address_period_start_date_date_collected',DateTime(timezone=False)),
        Column('address_period_end_date',DateTime(timezone=False)),
        Column('address_period_end_date_date_collected',DateTime(timezone=False)),
        Column('pre_address_line', String(100)),
        Column('pre_address_line_date_collected',DateTime(timezone=False)),
        Column('pre_address_line_date_effective', DateTime(timezone=False)),
        Column('pre_address_line_data_collection_stage', String(32)),
        Column('line1', String(100)),
        Column('line1_date_collected',DateTime(timezone=False)),
        Column('line1_date_effective', DateTime(timezone=False)),
        Column('line1_data_collection_stage', String(32)),
        Column('line2', String(100)),
        Column('line2_date_collected',DateTime(timezone=False)),
        Column('line2_date_effective', DateTime(timezone=False)),
        Column('line2_data_collection_stage', String(32)),
        Column('city', String(100)),
        Column('city_date_collected',DateTime(timezone=False)),
        Column('city_date_effective', DateTime(timezone=False)),
        Column('city_data_collection_stage', String(32)),
        Column('county', String(32)),
        Column('county_date_collected',DateTime(timezone=False)),
        Column('county_date_effective', DateTime(timezone=False)),
        Column('county_data_collection_stage', String(32)),
        Column('state', String(32)),
        Column('state_date_collected',DateTime(timezone=False)),
        Column('state_date_effective', DateTime(timezone=False)),
        Column('state_data_collection_stage', String(32)),
        Column('zipcode', String(10)),
        Column('zipcode_date_collected',DateTime(timezone=False)),
        Column('zipcode_date_effective', DateTime(timezone=False)),
        Column('zipcode_data_collection_stage', String(32)),
        Column('country', String(32)),
        Column('country_date_collected',DateTime(timezone=False)),
        Column('country_date_effective', DateTime(timezone=False)),
        Column('country_data_collection_stage', String(32)),
        Column('is_last_permanent_zip', Integer),
        Column('is_last_permanent_zip_date_collected', DateTime(timezone=False)),
        Column('is_last_permanent_zip_date_effective', DateTime(timezone=False)),
        Column('is_last_permanent_zip_data_collection_stage', String(32)),
        Column('zip_quality_code', Integer),
        Column('zip_quality_code_date_collected', DateTime(timezone=False)),
        Column('zip_quality_code_date_effective', DateTime(timezone=False)),
        Column('zip_quality_code_data_collection_stage', String(32)),
        
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),

        ## HUD 3.0
        Column('person_address_delete', String(32)),
        Column('person_address_delete_occurred_date', DateTime(timezone=False)),
        Column('person_address_delete_effective_date', DateTime(timezone=False)),        
        
        useexisting = True)
        table_metadata.create_all()
        mapper(PersonAddress, person_address_table)
    
        
    def person_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db)
        person_table = Table(
        'person', 
        table_metadata, 
        Column('id', Integer, primary_key=True),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_id', String(50), ForeignKey(Report.report_id)), 
        Column('person_id_hashed', String(32)),
        Column('person_id_unhashed', String(50)),
        Column('person_id_date_collected', DateTime(timezone=False)),
        Column('person_date_of_birth_hashed', String(32)),
        Column('person_date_of_birth_hashed_date_collected', DateTime(timezone=False)),
        Column('person_date_of_birth_unhashed', Date(timezone=False)),
        Column('person_date_of_birth_unhashed_date_collected', DateTime(timezone=False)),
        Column('person_ethnicity_hashed', String(32)),
        Column('person_ethnicity_unhashed', Integer(2)),
        Column('person_ethnicity_hashed_date_collected', DateTime(timezone=False)),
        Column('person_ethnicity_unhashed_date_collected', DateTime(timezone=False)),
        Column('person_gender_hashed', String(32)),
        Column('person_gender_unhashed', Integer(2)),
        Column('person_gender_hashed_date_collected', DateTime(timezone=False)),
        Column('person_gender_unhashed_date_collected', DateTime(timezone=False)),
        Column('person_gender_unhashed_date_effective', DateTime(timezone=False)),
        Column('person_gender_hashed_date_effective', DateTime(timezone=False)),
        Column('person_legal_first_name_hashed', String(32)),   
        Column('person_legal_first_name_unhashed', String(50)),
        Column('person_legal_first_name_hashed_date_collected', DateTime(timezone=False)),
        Column('person_legal_first_name_unhashed_date_collected', DateTime(timezone=False)),        
        Column('person_legal_last_name_hashed', String(32)),
        Column('person_legal_last_name_unhashed', String(50)),
        Column('person_legal_last_name_unhashed_date_collected', DateTime(timezone=False)),
        Column('person_legal_last_name_hashed_date_collected', DateTime(timezone=False)),        
        Column('person_legal_middle_name_hashed', String(32)),
        Column('person_legal_middle_name_unhashed', String(50)),
        Column('person_legal_middle_name_unhashed_date_collected', DateTime(timezone=False)),
        Column('person_legal_middle_name_hashed_date_collected', DateTime(timezone=False)),
        Column('person_legal_suffix_hashed', String(32)),
        Column('person_legal_suffix_unhashed', String(50)),
        Column('person_legal_suffix_unhashed_date_collected', DateTime(timezone=False)),
        Column('person_legal_suffix_hashed_date_collected', DateTime(timezone=False)),
        #OtherNames is in its own table as there can be multiple OtherNames
        #Race is in its own table as there can be multiple races
        Column('person_social_security_number_hashed', String(32)),
        Column('person_social_security_number_unhashed', String(9)),
        Column('person_social_security_number_unhashed_date_collected', DateTime(timezone=False)),
        Column('person_social_security_number_hashed_date_effective', DateTime(timezone=False)),
        Column('person_social_security_number_unhashed_date_effective', DateTime(timezone=False)),
        Column('person_social_security_number_hashed_date_collected', DateTime(timezone=False)),
        Column('person_social_security_number_quality_code', String(2)),
        Column('person_social_security_number_quality_code_date_collected', DateTime(timezone=False)),
        Column('person_social_security_number_quality_code_date_effective', DateTime(timezone=False)),

        #PersonHistorical has its own table
        #SiteServiceParticipation has its own table
        #ReleaseOfInformation has its own table
        
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),
        
        ## HUD 3.0
        Column('person_id_id_num', String(50)),
        Column('person_id_id_str', String(50)),
        Column('person_id_delete', String(32)),
        Column('person_id_delete_occurred_date', DateTime(timezone=False)),
        Column('person_id_delete_effective_date', DateTime(timezone=False)),
        Column('person_date_of_birth_type', Integer(2)),
        Column('person_date_of_birth_type_date_collected', DateTime(timezone=False)),
        useexisting = True)
        table_metadata.create_all()
        
        mapper(Person, person_table, properties={
            'fk_person_to_other_names': relation(OtherNames, backref='fk_other_names_to_person')
            ,'fk_person_to_site_svc_part': relation(SiteServiceParticipation, backref='fk_site_svc_part_to_person')
            ,'fk_person_to_person_historical': relation(PersonHistorical, backref='fk_person_historical_to_person')
            ,'fk_person_to_release_of_information': relation(ReleaseOfInformation, backref='fk_release_of_information_to_person')
            ,'fk_person_to_races': relation(Races, backref='fk_races_to_person')})
        #
        
        return
    
    def person_historical_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db, reflect=False)
        person_historical_table = Table(
        'person_historical', 
        table_metadata, 
        Column('id', Integer, primary_key=True),
        Column('person_index_id', Integer, ForeignKey(Person.id)),
        Column('site_service_index_id', Integer, ForeignKey(SiteServiceParticipation.id)),
        Column('person_historical_id_id_num', String(32)),
        Column('person_historical_id_id_str', String(32)),
        Column('person_historical_id_delete_effective_date', DateTime(timezone=False)),
        Column('person_historical_id_delete', Integer),
        Column('person_historical_id_delete_occurred_date', DateTime(timezone=False)),

    # dbCol: barrier_code
        Column('barrier_code', String(32)),
        Column('barrier_code_date_collected', DateTime(timezone=False)),
    
    # dbCol: barrier_other
        Column('barrier_other', String(32)),
        Column('barrier_other_date_collected', DateTime(timezone=False)),
    
    # dbCol: child_currently_enrolled_in_school
        Column('child_currently_enrolled_in_school', String(32)),
        Column('child_currently_enrolled_in_school_date_collected', DateTime(timezone=False)),
    
    # dbCol: currently_employed
        Column('currently_employed', String(32)),
        Column('currently_employed_date_collected', DateTime(timezone=False)),
    
    # dbCol: currently_in_school
        Column('currently_in_school', String(32)),
        Column('currently_in_school_date_collected', DateTime(timezone=False)),
    
    # dbCol: degree_code
        Column('degree_code', String(32)),
        Column('degree_code_date_collected', DateTime(timezone=False)),
    
    # dbCol: degree_other
        Column('degree_other', String(32)),
        Column('degree_other_date_collected', DateTime(timezone=False)),
    
    # dbCol: developmental_disability
        Column('developmental_disability', String(32)),
        Column('developmental_disability_date_collected', DateTime(timezone=False)),
    
    # dbCol: domestic_violence
        Column('domestic_violence', String(32)),
        Column('domestic_violence_date_collected', DateTime(timezone=False)),
    
    # dbCol: domestic_violence_how_long
        Column('domestic_violence_how_long', String(32)),
        Column('domestic_violence_how_long_date_collected', DateTime(timezone=False)),
    
    # dbCol: due_date
        Column('due_date', String(32)),
        Column('due_date_date_collected', DateTime(timezone=False)),
    
    # dbCol: employment_tenure
        Column('employment_tenure', String(32)),
        Column('employment_tenure_date_collected', DateTime(timezone=False)),
    
    # dbCol: health_status
        Column('health_status', String(32)),
        Column('health_status_date_collected', DateTime(timezone=False)),
    
    # dbCol: highest_school_level
        Column('highest_school_level', String(32)),
        Column('highest_school_level_date_collected', DateTime(timezone=False)),
    
    # dbCol: hivaids_status
        Column('hivaids_status', String(32)),
        Column('hivaids_status_date_collected', DateTime(timezone=False)),
    
    # dbCol: hours_worked_last_week
        Column('hours_worked_last_week', String(32)),
        Column('hours_worked_last_week_date_collected', DateTime(timezone=False)),
    
    # dbCol: hud_chronic_homeless
        Column('hud_chronic_homeless', String(32)),
        Column('hud_chronic_homeless_date_collected', DateTime(timezone=False)),
    
    # dbCol: hud_homeless
        Column('hud_homeless', String(32)),
        Column('hud_homeless_date_collected', DateTime(timezone=False)),
    
        ###HUDHomelessEpisodes (subtable)
    
        ###IncomeAndSources (subtable)
    
    # dbCol: length_of_stay_at_prior_residence
        Column('length_of_stay_at_prior_residence', String(32)),
        Column('length_of_stay_at_prior_residence_date_collected', DateTime(timezone=False)),
    
    # dbCol: looking_for_work
        Column('looking_for_work', String(32)),
        Column('looking_for_work_date_collected', DateTime(timezone=False)),
    
    # dbCol: mental_health_indefinite
        Column('mental_health_indefinite', String(32)),
        Column('mental_health_indefinite_date_collected', DateTime(timezone=False)),
    
    # dbCol: mental_health_problem
        Column('mental_health_problem', String(32)),
        Column('mental_health_problem_date_collected', DateTime(timezone=False)),
    
    # dbCol: non_cash_source_code
        Column('non_cash_source_code', String(32)),
        Column('non_cash_source_code_date_collected', DateTime(timezone=False)),
    
    # dbCol: non_cash_source_other
        Column('non_cash_source_other', String(32)),
        Column('non_cash_source_other_date_collected', DateTime(timezone=False)),
    
        ###PersonAddress (subtable)
    
    # dbCol: person_email
        Column('person_email', String(32)),
        Column('person_email_date_collected', DateTime(timezone=False)),
    
    # dbCol: person_phone_number
        Column('person_phone_number', String(32)),
        Column('person_phone_number_date_collected', DateTime(timezone=False)),
    
    # dbCol: physical_disability
        Column('physical_disability', String(32)),
        Column('physical_disability_date_collected', DateTime(timezone=False)),
    
    # dbCol: pregnancy_status
        Column('pregnancy_status', String(32)),
        Column('pregnancy_status_date_collected', DateTime(timezone=False)),
    
    # dbCol: prior_residence
        Column('prior_residence', String(32)),
        Column('prior_residence_date_collected', DateTime(timezone=False)),
    
    # dbCol: prior_residence_other
        Column('prior_residence_other', String(32)),
        Column('prior_residence_other_date_collected', DateTime(timezone=False)),
    
    # dbCol: reason_for_leaving
        Column('reason_for_leaving', String(32)),
        Column('reason_for_leaving_date_collected', DateTime(timezone=False)),
    
    # dbCol: reason_for_leaving_other
        Column('reason_for_leaving_other', String(32)),
        Column('reason_for_leaving_other_date_collected', DateTime(timezone=False)),
    
    # dbCol: school_last_enrolled_date
        Column('school_last_enrolled_date', String(32)),
        Column('school_last_enrolled_date_date_collected', DateTime(timezone=False)),
    
    # dbCol: school_name
        Column('school_name', String(32)),
        Column('school_name_date_collected', DateTime(timezone=False)),
    
    # dbCol: school_type
        Column('school_type', String(32)),
        Column('school_type_date_collected', DateTime(timezone=False)),
    
    # dbCol: subsidy_other
        Column('subsidy_other', String(32)),
        Column('subsidy_other_date_collected', DateTime(timezone=False)),
    
    # dbCol: subsidy_type
        Column('subsidy_type', String(32)),
        Column('subsidy_type_date_collected', DateTime(timezone=False)),
    
    # dbCol: substance_abuse_indefinite
        Column('substance_abuse_indefinite', String(32)),
        Column('substance_abuse_indefinite_date_collected', DateTime(timezone=False)),
    
    # dbCol: substance_abuse_problem
        Column('substance_abuse_problem', String(32)),
        Column('substance_abuse_problem_date_collected', DateTime(timezone=False)),
    
    # dbCol: total_income
        Column('total_income', String(32)),
        Column('total_income_date_collected', DateTime(timezone=False)),
    
        ###Veteran (subtable)
    
    # dbCol: vocational_training
        Column('vocational_training', String(32)),
        Column('vocational_training_date_collected', DateTime(timezone=False)),
        
    # dbCol: annual_personal_income
        #Column('annual_personal_income', Integer(2)),
        #Column('annual_personal_income_date_collected', DateTime(timezone=False)),
        
    # dbCol: employment_status
        #Column('employment_status', Integer(2)),
        #Column('employment_status_date_collected', DateTime(timezone=False)),
        
    # dbCol: family_size
        #Column('family_size', Integer(2)),
        #Column('family_size_date_collected', DateTime(timezone=False)),

    # dbCol: hearing_impaired
        #Column('hearing_impaired', Integer(2)),
        #Column('hearing_impaired_date_collected', DateTime(timezone=False)),            

    # dbCol: marital_status
        #Column('marital_status', Integer(2)),
        #Column('marital_status_date_collected', DateTime(timezone=False)),

    # dbCol: non_ambulatory
    #    Column('non_ambulatory', Integer(2)),
    #    Column('non_ambulatory_date_collected', DateTime(timezone=False)),
    #
    ## dbCol: residential_status
    #    Column('residential_status', Integer(2)),
    #    Column('residential_status_date_collected', DateTime(timezone=False)),
    #
    ## dbCol: visually_impaired
    #    Column('visually_impaired', Integer(2)),
    #    Column('visually_impaired_date_collected', DateTime(timezone=False)),
        
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),

        useexisting = True
        )
        table_metadata.create_all()
        mapper(PersonHistorical, person_historical_table,
               properties={'fk_person_historical_to_income_and_sources': relation(IncomeAndSources, backref='fk_income_and_sources_to_person_historical')
                           ,'fk_person_historical_to_veteran': relation(Veteran, backref='fk_veteran_to_person_historical')
                           ,'fk_person_historical_to_hud_homeless_episodes': relation(HUDHomelessEpisodes, backref='fk_hud_homeless_episodes_to_person_historical')
                           ,'fk_person_historical_to_person_address': relation(PersonAddress, backref='fk_person_address_to_person_historical')
                           })
        return
    
    def income_and_sources_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db)
        income_and_sources_table = Table(
        'income_and_sources', 
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)),
        Column('amount', Integer),
        Column('amount_date_collected', DateTime(timezone=False)),
        Column('income_source_code', Integer),
        Column('income_source_code_date_collected', DateTime(timezone=False)),
        Column('income_source_other', String(32)),
        Column('income_source_other_date_collected', DateTime(timezone=False)),

        ## HUD 3.0
        Column('income_and_source_id_id_id_num', String(32)),
        Column('income_and_source_id_id_id_str', String(32)),
        Column('income_and_source_id_id_delete_occurred_date', DateTime(timezone=False)),
        Column('income_and_source_id_id_delete_effective_date', DateTime(timezone=False)),
        Column('income_source_code_date_effective', DateTime(timezone=False)),
        Column('income_source_other_date_effective', DateTime(timezone=False)),
        Column('receiving_income_source_date_collected', DateTime(timezone=False)),
        Column('receiving_income_source_date_effective', DateTime(timezone=False)),
        Column('income_source_amount_date_effective', DateTime(timezone=False)),
        Column('income_and_source_id_id_delete', Integer),
        Column('income_source_code_data_collection_stage', String(32)),
        Column('income_source_other_data_collection_stage', String(32)),
        Column('receiving_income_source', Integer),
        Column('receiving_income_source_data_collection_stage', String(32)),
        Column('income_source_amount_data_collection_stage', String(32)),

        useexisting = True)
        table_metadata.create_all()
        mapper(IncomeAndSources, income_and_sources_table)
        
        return
    
    def member_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        member_table = Table(
        'members',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('household_index_id', Integer, ForeignKey(Household.id)),
        Column('person_index_id', Integer, ForeignKey(Person.id)),
        Column('relationship_to_head_of_household', String(32)),
        Column('relationship_to_head_of_household_date_collected', DateTime(timezone=False)),
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),
        useexisting = True)
        table_metadata.create_all()
        mapper(Members, member_table)
        return
    
    def household_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        household_table = Table(
        'household',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_id', String(50), ForeignKey(Report.report_id)),
        Column('household_id_num', String(32)),
        Column('household_id_num_date_collected', DateTime(timezone=False)),
        Column('household_id_str', String(32)),
        Column('household_id_str_date_collected', DateTime(timezone=False)),
        Column('head_of_household_id_unhashed', String(32)),
        Column('head_of_household_id_unhashed_date_collected', DateTime(timezone=False)),
        Column('head_of_household_id_hashed', String(32)),
        Column('head_of_household_id_hashed_date_collected', DateTime(timezone=False)),
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),
        useexisting = True)
        table_metadata.create_all()
    
        mapper(Household, household_table, properties=
               {'fk_household_to_members': relation(Members, backref='fk_members_to_household'),
                }
               )
        return
    
    def release_of_information_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        release_of_information_table = Table(
        'release_of_information',
        table_metadata,
        
        Column('id', Integer, primary_key=True),
        Column('person_index_id', Integer, ForeignKey(Person.id)),

    # dbCol: release_of_information_idid_num
        Column('release_of_information_idid_num', String(32)),
        Column('release_of_information_idid_num_date_collected', DateTime(timezone=False)),

    # dbCol: release_of_information_idid_str
        Column('release_of_information_idid_str', String(32)),
        Column('release_of_information_idid_str_date_collected', DateTime(timezone=False)),

    # dbCol: site_service_idid_num
        Column('site_service_idid_num', String(32)),
        Column('site_service_idid_num_date_collected', DateTime(timezone=False)),

    # dbCol: site_service_idid_str
        Column('site_service_idid_str', String(32)),
        Column('site_service_idid_str_date_collected', DateTime(timezone=False)),

    # dbCol: documentation
        Column('documentation', String(32)),
        Column('documentation_date_collected', DateTime(timezone=False)),

    ###EffectivePeriod (subtable)
    # dbCol: start_date
        Column('start_date', String(32)),
        Column('start_date_date_collected', DateTime(timezone=False)),
    
    # dbCol: end_date
        Column('end_date', String(32)),
        Column('end_date_date_collected', DateTime(timezone=False)),

    # dbCol: release_granted
        Column('release_granted', String(32)),
        Column('release_granted_date_collected', DateTime(timezone=False)),
        
        # SBB2009119 adding a reported column.  Hopefully this will append the column to the table def.
        Column('reported', Boolean),

        ## HUD 3.0
        Column('release_of_information_id_data_collection_stage', String(32)),
        Column('release_of_information_id_date_effective', DateTime(timezone=False)),
        Column('documentation_data_collection_stage', String(32)),
        Column('documentation_date_effective', DateTime(timezone=False)),
        Column('release_granted_data_collection_stage', String(32)),
        Column('release_granted_date_effective', DateTime(timezone=False)),
        
    useexisting = True)

        table_metadata.create_all()
        
        mapper(ReleaseOfInformation, release_of_information_table)
        return

    def source_map(self):
        '''Set up mapping'''
        table_metadata = MetaData(bind=self.pg_db_engine)
        #table_metadata = MetaData(bind=self.sqlite_db, reflect=False)
        self.source_table = Table(
        'source', 
        table_metadata, 
        Column('id', Integer, primary_key=True),
        Column('report_id', String(50), ForeignKey(Report.report_id)), 
        Column('source_id', String(50)), 
        Column('source_id_date_collected', DateTime(timezone=False)),
        Column('source_email', String(255)),
        Column('source_email_date_collected', DateTime(timezone=False)),
        Column('source_contact_extension', String(10)),
        Column('source_contact_extension_date_collected', DateTime(timezone=False)),
        Column('source_contact_first', String(20)),
        Column('source_contact_first_date_collected', DateTime(timezone=False)),
        Column('source_contact_last', String(20)),
        Column('source_contact_last_date_collected', DateTime(timezone=False)),
        Column('source_contact_phone', String(20)),
        Column('source_contact_phone_date_collected', DateTime(timezone=False)),
        Column('source_name', String(50)),
        Column('source_name_date_collected', DateTime(timezone=False)), 

        ## HUD 3.0
        Column('schema_version', String(50)),
        Column('source_id_id_num', String(50)),
        Column('source_id_id_str', String(50)),
        Column('source_id_delete', Integer),
        Column('source_id_delete_occurred_date', DateTime(timezone=False)),
        Column('source_id_delete_effective_date', DateTime(timezone=False)),
        Column('software_vendor', String(50)),
        Column('software_version', String(50)),
        Column('source_contact_email', String(255)),

        useexisting = True
        )
        table_metadata.create_all()
        mapper(Source, self.source_table, 
#               properties={ 
#                           'fk_source_to_export': relation(Export, backref='fk_export_to_source'), 
#                           } 
                           )
        
#        assign_mapper(Database, database_table, properties=dict(
#designs=relation(Design, private=True, backref="type")
#))
        return
        
        
        ## HUD 3.0 NEW TABLES

    def source_export_link_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
#        print "Source object is: ", Source
        source_export_link_table = Table(
        'source_export_link',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('source_index_id', Integer, ForeignKey(Source.id)),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_index_id', String(50), ForeignKey(Report.report_id)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(SourceExportLink, source_export_link_table)
        return    
                
    def region_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        region_table = Table(
        'region',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_index_id', String(50), ForeignKey(Report.report_id)), 
        Column('region_id_id_num', String(50)),
        Column('region_id_id_str', String(32)),
        Column('site_service_id', String(50)),
        Column('region_type', String(50)),
        Column('region_type_date_collected', DateTime(timezone=False)),
        Column('region_type_date_effective', DateTime(timezone=False)),
        Column('region_type_data_collection_stage', String(32)),
        Column('region_description', String(30)),
        Column('region_description_date_collected', DateTime(timezone=False)),
        Column('region_description_date_effective', DateTime(timezone=False)),
        Column('region_description_data_collection_stage', String(32)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Region, region_table)
        return
 
    def agency_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        agency_table = Table(
        'agency',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_index_id', String(50), ForeignKey(Report.report_id)),
        Column('agency_delete', Integer),
        Column('agency_delete_occurred_date', DateTime(timezone=False)),
        Column('agency_delete_effective_date', DateTime(timezone=False)),
        Column('airs_key', String(50)),
        Column('airs_name', String(50)),
        Column('agency_description', String(50)),
        Column('irs_status', String(50)),
        Column('source_of_funds', String(50)),
        Column('record_owner', String(50)),
        Column('fein', String(50)),
        Column('year_inc', String(50)),
        Column('annual_budget_total', String(50)),
        Column('legal_status', String(50)),
        Column('exclude_from_website', String(50)),
        Column('exclude_from_directory', String(50)),        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Agency, agency_table)
        return       

    def agency_child_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        agency_child_table = Table(
        'agency_child',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_index_id', String(50), ForeignKey(Report.report_id)),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(AgencyChild, agency_child_table)
        return       

    def service_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        service_table = Table(
        'service',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('service_id', String(50)),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_index_id', String(50), ForeignKey(Report.report_id)), 
        Column('service_delete', Integer),
        Column('service_delete_occurred_date', DateTime(timezone=False)),
        Column('service_delete_effective_date', DateTime(timezone=False)),
        Column('airs_key', String(50)),
        Column('airs_name', String(50)),
        Column('coc_code', String(5)),
        Column('configuration', String(50)),
        Column('direct_service_code', String(50)),
        Column('grantee_identifier', String(10)),
        Column('individual_family_code', String(50)),
        Column('residential_tracking_method', String(50)),
        Column('service_type', String(50)),
        Column('jfcs_service_type', String(50)),
        Column('service_effective_period_start_date', DateTime(timezone=False)),
        Column('service_effective_period_end_date', DateTime(timezone=False)),
        Column('service_recorded_date', DateTime(timezone=False)),
        Column('target_population_a', String(50)),
        Column('target_population_b', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Service, service_table)
        return

    def site_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        site_table = Table(
        'site',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_index_id', String(50), ForeignKey(Report.report_id)), 
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        #Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)), 
        Column('site_delete', Integer),
        Column('site_delete_occurred_date', DateTime(timezone=False)),
        Column('site_delete_effective_date', DateTime(timezone=False)),
        Column('airs_key', String(50)),
        Column('airs_name', String(50)),
        Column('site_description', String(50)),
        Column('physical_address_pre_address_line', String(100)),
        Column('physical_address_line_1', String(100)),
        Column('physical_address_line_2', String(100)),
        Column('physical_address_city', String(50)),
        Column('physical_address_country', String(50)),
        Column('physical_address_state', String(50)),
        Column('physical_address_zip_code', String(50)),
        Column('physical_address_country', String(50)),
        Column('physical_address_reason_withheld', String(50)),
        Column('physical_address_confidential', String(50)),
        Column('physical_address_description', String(50)),
        Column('mailing_address_pre_address_line', String(100)),
        Column('mailing_address_line_1', String(100)),
        Column('mailing_address_line_2', String(100)),
        Column('mailing_address_city', String(50)),
        Column('mailing_address_country', String(50)),
        Column('mailing_address_state', String(50)),
        Column('mailing_address_zip_code', String(50)),
        Column('mailing_address_country', String(50)),
        Column('mailing_address_reason_withheld', String(50)),
        Column('mailing_address_confidential', String(50)),
        Column('mailing_address_description', String(50)),
        Column('no_physical_address_description', String(50)),
        Column('no_physical_address_explanation', String(50)),
        Column('disabilities_access', String(50)),
        Column('physical_location_description', String(50)),
        Column('bus_service_access', String(50)),
        Column('public_access_to_transportation', String(50)),
        Column('year_inc', String(50)),
        Column('annual_budget_total', String(50)),
        Column('legal_status', String(50)),
        Column('exclude_from_website', String(50)),
        Column('exclude_from_directory', String(50)),
        Column('agency_key', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Site, site_table)
        return

    def site_service_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        site_service_table = Table(
        'site_service',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_id', String(50)),
        Column('export_index_id', Integer, ForeignKey(Export.id)),
        Column('report_index_id', String(50), ForeignKey(Report.report_id)), 
        Column('site_index_id', Integer, ForeignKey(Site.id)),
        Column('service_index_id', Integer, ForeignKey(Service.id)),
		# SBB20100916 Added Agency Location foreign key
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('site_service_delete', Integer),
        Column('site_service_delete_occurred_date', DateTime(timezone=False)),
        Column('site_service_delete_effective_date', DateTime(timezone=False)),
        Column('name', String(50)),
        Column('key', String(50)),
        Column('description', String(50)),
        Column('fee_structure', String(50)),
        Column('gender_requirements', String(50)),
        Column('area_flexibility', String(50)),
        Column('service_not_always_available', String(50)),
        Column('service_group_key', String(50)),
        Column('site_id', String(50)),
        Column('geographic_code', String(50)),
        Column('geographic_code_date_collected', DateTime(timezone=False)),
        Column('geographic_code_date_effective', DateTime(timezone=False)),        
        Column('geographic_code_data_collection_stage', String(50)),
        Column('housing_type', String(50)),
        Column('housing_type_date_collected', DateTime(timezone=False)),
        Column('housing_type_date_effective', DateTime(timezone=False)),
        Column('housing_type_data_collection_stage', String(50)),
        Column('principal', String(50)),
        Column('site_service_effective_period_start_date', DateTime(timezone=False)),
        Column('site_service_effective_period_end_date', DateTime(timezone=False)),
        Column('site_service_recorded_date', DateTime(timezone=False)),
        Column('site_service_type', String(50)),        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(SiteService, site_service_table)
        return

    def funding_source_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        funding_source_table = Table(
        'funding_source',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('service_index_id', Integer, ForeignKey(Service.id)), 
        Column('service_event_index_id', Integer, ForeignKey(ServiceEvent.id)), 
        Column('funding_source_id_id_num', String(50)),
        Column('funding_source_id_id_str', String(32)),
        Column('funding_source_id_delete', String(50)),
        Column('funding_source_id_delete_occurred_date', DateTime(timezone=False)),
        Column('funding_source_id_delete_effective_date', DateTime(timezone=False)),
        Column('federal_cfda_number', String(50)),
        Column('receives_mckinney_funding', String(50)),
        Column('advance_or_arrears', String(50)),
        Column('financial_assistance_amount', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(FundingSource, funding_source_table)
        return

    def resource_info_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        resource_info_table = Table(
        'resource_info',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('resource_specialist', String(50)),
        Column('available_for_directory', String(50)),
        Column('available_for_referral', String(50)),
        Column('available_for_research', String(50)),
        Column('date_added', DateTime(timezone=False)),
        Column('date_last_verified', DateTime(timezone=False)),
        Column('date_of_last_action', DateTime(timezone=False)),
        Column('last_action_type', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ResourceInfo, resource_info_table)
        return

        
    def inventory_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        inventory_table = Table(
        'inventory',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('service_index_id', Integer, ForeignKey(Service.id)), 
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('inventory_delete', Integer),
        Column('inventory_delete_occurred_date', DateTime(timezone=False)),
        Column('inventory_delete_effective_delete', DateTime(timezone=False)),
        Column('hmis_participation_period_start_date', DateTime(timezone=False)),
        Column('hmis_participation_period_end_date', DateTime(timezone=False)),
        Column('inventory_id_id_num', String(50)),
        Column('inventory_id_id_str', String(32)),
        Column('bed_inventory', String(50)),
        Column('bed_availability', String(50)),
        Column('bed_type', String(50)),
        Column('bed_individual_family_type', String(50)),
        Column('chronic_homeless_bed', String(50)),
        Column('domestic_violence_shelter_bed', String(50)),
        Column('household_type', String(50)),
        Column('hmis_participating_beds', String(50)),        
        Column('inventory_effective_period_start_date', DateTime(timezone=False)),
        Column('inventory_effective_period_end_date', DateTime(timezone=False)),
        Column('inventory_recorded_date', DateTime(timezone=False)),
        Column('unit_inventory', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Inventory, inventory_table)
        return

    def age_requirements_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        age_requirements_table = Table(
        'age_requirements',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('gender', String(50)),
        Column('minimum_age', String(50)),
        Column('maximum_age', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(AgeRequirements, age_requirements_table)
        return

    def aid_requirements_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        aid_requirements_table = Table(
        'aid_requirements',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('aid_requirements', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(AidRequirements, aid_requirements_table)
        return

    def aka_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        aka_table = Table(
        'aka',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('site_index_id', Integer, ForeignKey(Site.id)),
		# SBB20100914 Added Agency Location foreign key
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('name', String(50)),
        Column('confidential', String(50)),
        Column('description', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Aka, aka_table)
        return

    def application_process_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        application_process_table = Table(
        'application_process',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('step', String(50)),
        Column('description', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ApplicationProcess, application_process_table)
        return

    def assignment_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        assignment_table = Table(
        'assignment',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('hmis_asset_index_id', Integer, ForeignKey(HmisAsset.id)), 
        Column('assignment_id_id_num', String(50)),
        Column('assignment_id_id_str', String(32)),
        Column('assignment_id_delete', Integer),
        Column('assignment_id_delete_occurred_date', DateTime(timezone=False)),
        Column('assignment_id_delete_effective_date', DateTime(timezone=False)),
        Column('person_id_id_num', String(50)),
        Column('person_id_id_str', String(32)),
        Column('household_id_id_num', String(50)),
        Column('household_id_id_str', String(32)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Assignment, assignment_table)
        return


    def assignment_period_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        assignment_period_table = Table(
        'assignment_period',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('assignment_index_id', Integer, ForeignKey(Assignment.id)), 
        Column('assignment_period_start_date', DateTime(timezone=False)),
        Column('assignment_period_end_date', DateTime(timezone=False)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(AssignmentPeriod, assignment_period_table)
        return

    def child_enrollment_status_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        child_enrollment_status_table = Table(
        'child_enrollment_status',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('child_enrollment_status_id_id_num', String(50)),
        Column('child_enrollment_status_id_id_str', String(32)),
        Column('child_enrollment_status_id_delete', Integer),
        Column('child_enrollment_status_id_delete_occurred_date', DateTime(timezone=False)),
        Column('child_enrollment_status_id_delete_effective_date', DateTime(timezone=False)),
        Column('child_currently_enrolled_in_school', String(50)),
        Column('child_currently_enrolled_in_school_date_effective', DateTime(timezone=False)),
        Column('child_currently_enrolled_in_school_date_collected', DateTime(timezone=False)),        
        Column('child_currently_enrolled_in_school_data_collection_stage', String(50)),
        Column('child_school_name', String(50)),
        Column('child_school_name_date_effective', DateTime(timezone=False)),
        Column('child_school_name_date_collected', DateTime(timezone=False)),        
        Column('child_school_name_data_collection_stage', String(50)),        
        Column('child_mckinney_vento_liaison', String(50)),
        Column('child_mckinney_vento_liaison_date_effective', DateTime(timezone=False)),
        Column('child_mckinney_vento_liaison_date_collected', DateTime(timezone=False)),        
        Column('child_mckinney_vento_liaison_data_collection_stage', String(50)),   
        Column('child_school_type', String(50)),
        Column('child_school_type_date_effective', DateTime(timezone=False)),
        Column('child_school_type_date_collected', DateTime(timezone=False)),        
        Column('child_school_type_data_collection_stage', String(50)),   
        Column('child_school_last_enrolled_date', DateTime(timezone=False)),
        Column('child_school_last_enrolled_date_date_collected', DateTime(timezone=False)),        
        Column('child_school_last_enrolled_date_data_collection_stage', String(50)),           
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ChildEnrollmentStatus, child_enrollment_status_table)
        return

    def child_enrollment_status_barrier_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        child_enrollment_status_barrier_table = Table(
        'child_enrollment_status_barrier',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('child_enrollment_status_index_id', Integer, ForeignKey(ChildEnrollmentStatus.id)), 
        Column('barrier_id_id_num', String(50)),
        Column('barrier_id_id_str', String(32)),
        Column('barrier_id_delete', Integer),
        Column('barrier_id_delete_occurred_date', DateTime(timezone=False)),
        Column('barrier_id_delete_effective_date', DateTime(timezone=False)),
        Column('barrier_code', String(50)),
        Column('barrier_code_date_collected', DateTime(timezone=False)),
        Column('barrier_code_date_effective', DateTime(timezone=False)),        
        Column('barrier_code_data_collection_stage', String(50)),
        Column('barrier_other', String(50)),
        Column('barrier_other_date_collected', DateTime(timezone=False)),
        Column('barrier_other_date_effective', DateTime(timezone=False)),        
        Column('barrier_other_data_collection_stage', String(50)),        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ChildEnrollmentStatusBarrier, child_enrollment_status_barrier_table)
        return

    def chronic_health_condition_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        chronic_health_condition_table = Table(
        'chronic_health_condition',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('has_chronic_health_condition', String(50)),
        Column('has_chronic_health_condition_date_collected', DateTime(timezone=False)),
        Column('has_chronic_health_condition_date_effective', DateTime(timezone=False)),        
        Column('has_chronic_health_condition_data_collection_stage', String(50)),
        Column('receive_chronic_health_services', String(50)),
        Column('receive_chronic_health_services_date_collected', DateTime(timezone=False)),
        Column('receive_chronic_health_services_date_effective', DateTime(timezone=False)),        
        Column('receive_chronic_health_services_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ChronicHealthCondition, chronic_health_condition_table)
        return

    def contact_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        contact_table = Table(
        'contact',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('resource_info_index_id', Integer, ForeignKey(ResourceInfo.id)),
        Column('site_index_id', Integer, ForeignKey(Site.id)),
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('title', String(50)),
        Column('name', String(50)),
        Column('type', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Contact, contact_table)
        return

    def contact_made_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        contact_made_table = Table(
        'contact_made',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('contact_id_id_num', String(50)),
        Column('contact_id_id_str', String(32)),
        Column('contact_id_delete', Integer),
        Column('contact_id_delete_occurred_date', DateTime(timezone=False)),
        Column('contact_id_delete_effective_date', DateTime(timezone=False)),
        Column('contact_date', DateTime(timezone=False)),
        Column('contact_date_data_collection_stage', String(50)),
        Column('contact_location', String(50)),
        Column('contact_location_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ContactMade, contact_made_table)
        return

    def cross_street_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        cross_street_table = Table(
        'cross_street',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_index_id', Integer, ForeignKey(Site.id)),
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('cross_street', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(CrossStreet, cross_street_table)
        return

    def currently_in_school_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        currently_in_school_table = Table(
        'currently_in_school',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('currently_in_school', String(50)),
        Column('currently_in_school_date_collected', DateTime(timezone=False)),
        Column('currently_in_school_date_effective', DateTime(timezone=False)),        
        Column('currently_in_school_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(CurrentlyInSchool, currently_in_school_table)
        return

    def license_accreditation_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        license_accreditation_table = Table(
        'license_accreditation',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('license', String(50)),
        Column('licensed_by', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(LicenseAccreditation, license_accreditation_table)
        return

    def mental_health_problem_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        mental_health_problem_table = Table(
        'mental_health_problem',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('has_mental_health_problem', String(50)),
        Column('has_mental_health_problem_date_collected', DateTime(timezone=False)),
        Column('has_mental_health_problem_date_effective', DateTime(timezone=False)),        
        Column('has_mental_health_problem_data_collection_stage', String(50)),
        Column('mental_health_indefinite', String(50)),
        Column('mental_health_indefinite_date_collected', DateTime(timezone=False)),
        Column('mental_health_indefinite_date_effective', DateTime(timezone=False)),        
        Column('mental_health_indefinite_data_collection_stage', String(50)),
        Column('receive_mental_health_services', String(50)),
        Column('receive_mental_health_services_date_collected', DateTime(timezone=False)),
        Column('receive_mental_health_services_date_effective', DateTime(timezone=False)),        
        Column('receive_mental_health_services_data_collection_stage', String(50)),        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(MentalHealthProblem, mental_health_problem_table)
        return

#    def age_requirements_map(self):
#        table_metadata = MetaData(bind=self.pg_db_engine)
#        age_requirements_table = Table(
#        'age_requirements',
#        table_metadata,
#        Column('id', Integer, primary_key=True),
#        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
#        Column('gender', String(50)),
#        Column('minimum_age', String(50)),
#        Column('maximum_age', String(50)),
#        useexisting = True
#        )
#        table_metadata.create_all()
#        mapper(AgeRequirements, age_requirements_table)
#        return

    def non_cash_benefits_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        non_cash_benefits_table = Table(
        'non_cash_benefits',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('non_cash_benefit_id_id_id_num', String(50)),
        Column('non_cash_benefit_id_id_id_str', String(32)),
        Column('non_cash_benefit_id_id_delete', Integer),
        Column('non_cash_benefit_id_id_delete_occurred_date', DateTime(timezone=False)),
        Column('non_cash_benefit_id_id_delete_effective_date', DateTime(timezone=False)),
        Column('non_cash_source_code', String(50)),
        Column('non_cash_source_code_date_collected', DateTime(timezone=False)),
        Column('non_cash_source_code_date_effective', DateTime(timezone=False)),        
        Column('non_cash_source_code_data_collection_stage', String(50)),
        Column('non_cash_source_other', String(50)),
        Column('non_cash_source_other_date_collected', DateTime(timezone=False)),
        Column('non_cash_source_other_date_effective', DateTime(timezone=False)),        
        Column('non_cash_source_other_data_collection_stage', String(50)),
        Column('receiving_non_cash_source', String(50)),
        Column('receiving_non_cash_source_date_collected', DateTime(timezone=False)),
        Column('receiving_non_cash_source_date_effective', DateTime(timezone=False)),        
        Column('receiving_non_cash_source_data_collection_stage', String(50)),     
        useexisting = True
        )
        table_metadata.create_all()
        mapper(NonCashBenefits, non_cash_benefits_table)
        return
        
    def agency_location_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        agency_location_table = Table(
        'agency_location',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('key', String(50)),
        Column('name', String(50)),
        Column('site_description', String(50)),
        # address fields
        Column('physical_address_pre_address_line', String(100)),
        Column('physical_address_line_1', String(100)),
        Column('physical_address_line_2', String(100)),
        Column('physical_address_city', String(50)),
        Column('physical_address_country', String(50)),
        Column('physical_address_state', String(50)),
        Column('physical_address_zip_code', String(50)),
        Column('physical_address_county', String(50)),
        Column('physical_address_reason_withheld', String(50)),
        Column('physical_address_confidential', String(50)),
        Column('physical_address_description', String(50)),
        Column('mailing_address_pre_address_line', String(100)),
        Column('mailing_address_line_1', String(100)),
        Column('mailing_address_line_2', String(100)),
        Column('mailing_address_city', String(50)),
        Column('mailing_address_county', String(50)),
        Column('mailing_address_state', String(50)),
        Column('mailing_address_zip_code', String(50)),
        Column('mailing_address_country', String(50)),
        Column('mailing_address_reason_withheld', String(50)),
        Column('mailing_address_confidential', String(50)),
        Column('mailing_address_description', String(50)),
        Column('no_physical_address_description', String(50)),
        Column('no_physical_address_explanation', String(50)),
        Column('disabilities_access', String(50)),
        Column('physical_location_description', String(50)),
        Column('bus_service_access', String(50)),
        # Attributes
        Column('public_access_to_transportation', String(50)),
        Column('year_inc', String(50)),
        Column('annual_budget_total', String(50)),
        Column('legal_status', String(50)),
        Column('exclude_from_website', String(50)),
        Column('exclude_from_directory', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(AgencyLocation, agency_location_table)
        return
    
    def agency_service_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        agency_service_table = Table(
        'agency_service',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('key', String(50)),
        Column('agency_key', String(50)),
        Column('name', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(AgencyService, agency_service_table)
        return

    def non_cash_benefits_last_30_days_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        non_cash_benefits_last_30_days_table = Table(
        'non_cash_benefits_last_30_days',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('income_last_30_days', String(50)),
        Column('income_last_30_days_date_collected', DateTime(timezone=False)),
        Column('income_last_30_days_date_effective', DateTime(timezone=False)),        
        Column('income_last_30_days_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(NonCashBenefitsLast30Days, non_cash_benefits_last_30_days_table)
        return

#    def aid_requirements_map(self):
#        table_metadata = MetaData(bind=self.pg_db_engine)
#        aid_requirements_table = Table(
#        'aid_requirements',
#        table_metadata,
#        Column('id', Integer, primary_key=True),
#        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
#        Column('aid_requirements', String(50)),
#        useexisting = True
#        )
#        table_metadata.create_all()
#        mapper(AidRequirements, aid_requirements_table)
#        return

    def other_address_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        other_address_table = Table(
        'other_address',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_index_id', Integer, ForeignKey(Site.id)),
		# SBB20100914 Adding foreign key to agency_location
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
		#
        Column('pre_address_line', String(100)),
        Column('line_1', String(100)),
        Column('line_2', String(100)),
        Column('city', String(50)),
        Column('county', String(50)),
        Column('state', String(50)),
        Column('zip_code', String(50)),
        Column('country', String(50)),
        Column('reason_withheld', String(50)),
        Column('confidential', String(50)),
        Column('description', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(OtherAddress, other_address_table)
        return

    def other_requirements_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        other_requirements_table = Table(
        'other_requirements',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('other_requirements', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(OtherRequirements, other_requirements_table)
        return

    def phone_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        phone_table = Table(
        'phone',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('contact_index_id', Integer, ForeignKey(Contact.id)), 
        Column('resource_info_index_id', Integer, ForeignKey(ResourceInfo.id)), 
        Column('site_index_id', Integer, ForeignKey(Site.id)), 
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)),
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('phone_number', String(50)),
        Column('reason_withheld', String(50)),
        Column('extension', String(50)),
        Column('description', String(50)),
        Column('type', String(50)),
        Column('function', String(50)),
        Column('toll_free', String(50)),
        Column('confidential', String(50)),
        Column('person_phone_number', String(50)),
        Column('person_phone_number_date_collected', DateTime(timezone=False)),
        Column('person_phone_number_date_effective', DateTime(timezone=False)),        
        Column('person_phone_number_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Phone, phone_table)
        return

    def physical_disability_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        physical_disability_table = Table(
        'physical_disability',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('has_physical_disability', String(50)),
        Column('has_physical_disability_date_collected', DateTime(timezone=False)),
        Column('has_physical_disability_date_effective', DateTime(timezone=False)),        
        Column('has_physical_disability_data_collection_stage', String(50)),
        Column('receive_physical_disability_services', String(50)),
        Column('receive_physical_disability_services_date_collected', DateTime(timezone=False)),
        Column('receive_physical_disability_services_date_effective', DateTime(timezone=False)),        
        Column('receive_physical_disability_services_data_collection_stage', String(50)),        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(PhysicalDisability, physical_disability_table)
        return

    def pit_count_set_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        pit_count_set_table = Table(
        'pit_count_set',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('pit_count_set_id_id_num', String(50)),
        Column('pit_count_set_id_id_str', String(32)),
        Column('pit_count_set_id_delete', Integer),
        Column('pit_count_set_id_delete_occurred_date', DateTime(timezone=False)),
        Column('pit_count_set_id_delete_effective_date', DateTime(timezone=False)),
        Column('hud_waiver_received', String(50)),
        Column('hud_waiver_date', DateTime(timezone=False)),
        Column('hud_waiver_effective_period_start_date', DateTime(timezone=False)),
        Column('hud_waiver_effective_period_end_date', DateTime(timezone=False)),
        Column('last_pit_sheltered_count_date', DateTime(timezone=False)),
        Column('last_pit_unsheltered_count_date', DateTime(timezone=False)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(PitCountSet, pit_count_set_table)
        return

    def pit_counts_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        pit_counts_table = Table(
        'pit_counts',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('pit_count_set_index_id', Integer, ForeignKey(PitCountSet.id)), 
        Column('pit_count_value', String(50)),
        Column('pit_count_effective_period_start_date', DateTime(timezone=False)),
        Column('pit_count_effective_period_end_date', DateTime(timezone=False)),
        Column('pit_count_recorded_date', DateTime(timezone=False)),
        Column('pit_count_household_type', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(PitCounts, pit_counts_table)
        return

    def pregnancy_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        pregnancy_table = Table(
        'pregnancy',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('pregnancy_id_id_id_num', String(50)),
        Column('pregnancy_id_id_id_str', String(32)),
        Column('pregnancy_id_id_delete', Integer),
        Column('pregnancy_id_id_delete_occurred_date', DateTime(timezone=False)),
        Column('pregnancy_id_id_delete_effective_date', DateTime(timezone=False)),
        Column('pregnancy_status', String(50)),
        Column('pregnancy_status_date_collected', DateTime(timezone=False)),
        Column('pregnancy_status_date_effective', DateTime(timezone=False)),        
        Column('pregnancy_status_data_collection_stage', String(50)),
        Column('due_date', DateTime(timezone=False)),
        Column('due_date_date_collected', DateTime(timezone=False)),        
        Column('due_date_data_collection_stage', String(50)),        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Pregnancy, pregnancy_table)
        return

    def degree_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        degree_table = Table(
        'degree',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('degree_id_id_num', String(50)),
        Column('degree_id_id_str', String(32)),
        Column('degree_id_delete', Integer),
        Column('degree_id_delete_occurred_date', DateTime(timezone=False)),
        Column('degree_id_delete_effective_date', DateTime(timezone=False)),
        Column('degree_other', String(50)),
        Column('degree_other_date_collected', DateTime(timezone=False)),
        Column('degree_other_date_effective', DateTime(timezone=False)),        
        Column('degree_other_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Degree, degree_table)
        return

    def prior_residence_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        prior_residence_table = Table(
        'prior_residence',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('prior_residence_id_id_num', String(50)),
        Column('prior_residence_id_id_str', String(32)),
        Column('prior_residence_id_delete', Integer),
        Column('prior_residence_id_delete_occurred_date', DateTime(timezone=False)),
        Column('prior_residence_id_delete_effective_date', DateTime(timezone=False)),
        Column('prior_residence_code', String(50)),
        Column('prior_residence_code_date_collected', DateTime(timezone=False)),
        Column('prior_residence_code_date_effective', DateTime(timezone=False)),        
        Column('prior_residence_code_data_collection_stage', String(50)),
        Column('prior_residence_other', String(50)),
        Column('prior_residence_other_date_collected', DateTime(timezone=False)),
        Column('prior_residence_other_date_effective', DateTime(timezone=False)),        
        Column('prior_residence_other_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(PriorResidence, prior_residence_table)
        return

    def degree_code_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        degree_code_table = Table(
        'degree_code',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('degree_index_id', Integer, ForeignKey(Degree.id)), 
        Column('degree_code', String(50)),
        Column('degree_date_collected', DateTime(timezone=False)),
        Column('degree_date_effective', DateTime(timezone=False)),        
        Column('degree_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(DegreeCode, degree_code_table)
        return

    def destinations_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        destinations_table = Table(
        'destinations',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('destination_id_id_num', String(50)),
        Column('destination_id_id_str', String(32)),
        Column('destination_id_delete', Integer),
        Column('destination_id_delete_occurred_date', DateTime(timezone=False)),
        Column('destination_id_delete_effective_date', DateTime(timezone=False)),
        Column('destination_code', String(50)),
        Column('destination_code_date_collected', DateTime(timezone=False)),
        Column('destination_code_date_effective', DateTime(timezone=False)),        
        Column('destination_code_data_collection_stage', String(50)),
        Column('destination_other', String(50)),
        Column('destination_other_date_collected', DateTime(timezone=False)),
        Column('destination_other_date_effective', DateTime(timezone=False)),        
        Column('destination_other_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Destinations, destinations_table)
        return

    def reasons_for_leaving_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        reasons_for_leaving_table = Table(
        'reasons_for_leaving',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_participation_index_id', Integer, ForeignKey(SiteServiceParticipation.id)), 
        Column('reason_for_leaving_id_id_num', String(50)),
        Column('reason_for_leaving_id_id_str', String(32)),
        Column('reason_for_leaving_id_delete', Integer),
        Column('reason_for_leaving_id_delete_occurred_date', DateTime(timezone=False)),
        Column('reason_for_leaving_id_delete_effective_date', DateTime(timezone=False)),
        Column('reason_for_leaving', String(50)),
        Column('reason_for_leaving_date_collected', DateTime(timezone=False)),
        Column('reason_for_leaving_date_effective', DateTime(timezone=False)),        
        Column('reason_for_leaving_data_collection_stage', String(50)),
        Column('reason_for_leaving_other', String(50)),
        Column('reason_for_leaving_other_date_collected', DateTime(timezone=False)),
        Column('reason_for_leaving_other_date_effective', DateTime(timezone=False)),        
        Column('reason_for_leaving_other_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ReasonsForLeaving, reasons_for_leaving_table)
        return

    def developmental_disability_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        developmental_disability_table = Table(
        'developmental_disability',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('has_developmental_disability', String(50)),
        Column('has_developmental_disability_date_collected', DateTime(timezone=False)),
        Column('has_developmental_disability_date_effective', DateTime(timezone=False)),        
        Column('has_developmental_disability_data_collection_stage', String(50)),
        Column('receive_developmental_disability', String(50)),
        Column('receive_developmental_disability_date_collected', DateTime(timezone=False)),
        Column('receive_developmental_disability_date_effective', DateTime(timezone=False)),        
        Column('receive_developmental_disability_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(DevelopmentalDisability, developmental_disability_table)
        return

    def disabling_condition_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        disabling_condition_table = Table(
        'disabling_condition',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('disabling_condition', String(50)),
        Column('disabling_condition_date_collected', DateTime(timezone=False)),
        Column('disabling_condition_date_effective', DateTime(timezone=False)),        
        Column('disabling_condition_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(DisablingCondition, disabling_condition_table)
        return

    def documents_required_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        documents_required_table = Table(
        'documents_required',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('documents_required', String(50)),
        Column('description', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(DocumentsRequired, documents_required_table)
        return

    def residency_requirements_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        residency_requirements_table = Table(
        'residency_requirements',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('residency_requirements', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ResidencyRequirements, residency_requirements_table)
        return

    def domestic_violence_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        domestic_violence_table = Table(
        'domestic_violence',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('domestic_violence_survivor', String(50)),
        Column('domestic_violence_survivor_date_collected', DateTime(timezone=False)),
        Column('domestic_violence_survivor_date_effective', DateTime(timezone=False)),        
        Column('domestic_violence_survivor_data_collection_stage', String(50)),
        Column('dv_occurred', String(50)),
        Column('dv_occurred_date_collected', DateTime(timezone=False)),
        Column('dv_occurred_date_effective', DateTime(timezone=False)),        
        Column('dv_occurred_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(DomesticViolence, domestic_violence_table)
        return

    def email_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        email_table = Table(
        'email',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('contact_index_id', Integer, ForeignKey(Contact.id)), 
        Column('resource_info_index_id', Integer, ForeignKey(ResourceInfo.id)), 
        Column('site_index_id', Integer, ForeignKey(Site.id)), 
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)),
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('address', String(100)),
        Column('note', String(50)),
        Column('person_email', String(50)),
        Column('person_email_date_collected', DateTime(timezone=False)),
        Column('person_email_date_effective', DateTime(timezone=False)),        
        Column('person_email_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Email, email_table)
        return

    def seasonal_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        seasonal_table = Table(
        'seasonal',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('description', String(50)),
        Column('start_date', String(50)),
        Column('end_date', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Seasonal, seasonal_table)
        return

    def employment_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        employment_table = Table(
        'employment',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('employment_id_id_id_num', String(50)),
        Column('employment_id_id_id_str', String(32)),
        Column('employment_id_id_delete', Integer),
        Column('employment_id_id_delete_occurred_date', DateTime(timezone=False)),
        Column('employment_id_id_delete_effective_date', DateTime(timezone=False)),
        Column('currently_employed', String(50)),
        Column('currently_employed_date_collected', DateTime(timezone=False)),
        Column('currently_employed_date_effective', DateTime(timezone=False)),        
        Column('currently_employed_data_collection_stage', String(50)),
        Column('hours_worked_last_week', String(50)),
        Column('hours_worked_last_week_date_collected', DateTime(timezone=False)),
        Column('hours_worked_last_week_date_effective', DateTime(timezone=False)),        
        Column('hours_worked_last_week_data_collection_stage', String(50)),
        Column('employment_tenure', String(50)),
        Column('employment_tenure_date_collected', DateTime(timezone=False)),
        Column('employment_tenure_date_effective', DateTime(timezone=False)),        
        Column('employment_tenure_data_collection_stage', String(50)),
        Column('looking_for_work', String(50)),
        Column('looking_for_work_date_collected', DateTime(timezone=False)),
        Column('looking_for_work_date_effective', DateTime(timezone=False)),        
        Column('looking_for_work_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Employment, employment_table)
        return

    def engaged_date_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        engaged_date_table = Table(
        'engaged_date',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('engaged_date', DateTime(timezone=False)),
        Column('engaged_date_date_collected', DateTime(timezone=False)),        
        Column('engaged_date_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(EngagedDate, engaged_date_table)
        return

    def service_event_notes_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        service_event_notes_table = Table(
        'service_event_notes',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('service_event_index_id', Integer, ForeignKey(ServiceEvent.id)), 
        Column('note_id_id_num', String(50)),
        Column('note_id_id_str', String(32)),
        Column('note_delete', Integer),
        Column('note_delete_occurred_date', DateTime(timezone=False)),
        Column('note_delete_effective_date', DateTime(timezone=False)),
        Column('note_text', String(255)),
        Column('note_text_date_collected', DateTime(timezone=False)),
        Column('note_text_date_effective', DateTime(timezone=False)),        
        Column('note_text_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ServiceEventNotes, service_event_notes_table)
        return

    def family_requirements_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        family_requirements_table = Table(
        'family_requirements',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('family_requirements', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(FamilyRequirements, family_requirements_table)
        return

    def service_group_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        service_group_table = Table(
        'service_group',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('key', String(50)),
        Column('name', String(50)),
        Column('program_name', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(ServiceGroup, service_group_table)
        return

    def geographic_area_served_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        geographic_area_served_table = Table(
        'geographic_area_served',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('zipcode', String(50)),
        Column('census_track', String(50)),
        Column('city', String(50)),
        Column('county', String(50)),
        Column('state', String(50)),
        Column('country', String(50)),
        Column('description', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(GeographicAreaServed, geographic_area_served_table)
        return

    def health_status_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        health_status_table = Table(
        'health_status',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('health_status', String(50)),
        Column('health_status_date_collected', DateTime(timezone=False)),
        Column('health_status_date_effective', DateTime(timezone=False)),        
        Column('health_status_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(HealthStatus, health_status_table)
        return

    def highest_school_level_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        highest_school_level_table = Table(
        'highest_school_level',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('highest_school_level', String(50)),
        Column('highest_school_level_date_collected', DateTime(timezone=False)),
        Column('highest_school_level_date_effective', DateTime(timezone=False)),        
        Column('highest_school_level_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(HighestSchoolLevel, highest_school_level_table)
        return

    def hiv_aids_status_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        hiv_aids_status_table = Table(
        'hiv_aids_status',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('has_hiv_aids', String(50)),
        Column('has_hiv_aids_date_collected', DateTime(timezone=False)),
        Column('has_hiv_aids_date_effective', DateTime(timezone=False)),        
        Column('has_hiv_aids_data_collection_stage', String(50)),
        Column('receive_hiv_aids_services', String(50)),
        Column('receive_hiv_aids_services_date_collected', DateTime(timezone=False)),
        Column('receive_hiv_aids_services_date_effective', DateTime(timezone=False)),        
        Column('receive_hiv_aids_services_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(HivAidsStatus, hiv_aids_status_table)
        return

    def spatial_location_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        spatial_location_table = Table(
        'spatial_location',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_index_id', Integer, ForeignKey(Site.id)),
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('description', String(50)),
        Column('datum', String(50)),
        Column('latitude', String(50)),
        Column('longitude', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(SpatialLocation, spatial_location_table)
        return

    def hmis_asset_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        hmis_asset_table = Table(
        'hmis_asset',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_index_id', Integer, ForeignKey(Site.id)), 
        Column('asset_id_id_num', String(50)),
        Column('asset_id_id_str', String(32)),
        Column('asset_id_delete', Integer),
        Column('asset_id_delete_occurred_date', DateTime(timezone=False)),
        Column('asset_id_delete_effective_date', DateTime(timezone=False)),
        Column('asset_count', String(50)),
        Column('asset_count_bed_availability', String(50)),
        Column('asset_count_bed_type', String(50)),
        Column('asset_count_bed_individual_family_type', String(50)),
        Column('asset_count_chronic_homeless_bed', String(50)),
        Column('asset_count_domestic_violence_shelter_bed', String(50)),
        Column('asset_count_household_type', String(50)),
        Column('asset_type', String(50)),
        Column('asset_effective_period_start_date', DateTime(timezone=False)),
        Column('asset_effective_period_end_date', DateTime(timezone=False)),
        Column('asset_recorded_date', DateTime(timezone=False)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(HmisAsset, hmis_asset_table)
        return

    def substance_abuse_problem_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        substance_abuse_problem_table = Table(
        'substance_abuse_problem',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('has_substance_abuse_problem', String(50)),
        Column('has_substance_abuse_problem_date_collected', DateTime(timezone=False)),
        Column('has_substance_abuse_problem_date_effective', DateTime(timezone=False)),        
        Column('has_substance_abuse_problem_data_collection_stage', String(50)),
        Column('substance_abuse_indefinite', String(50)),
        Column('substance_abuse_indefinite_date_collected', DateTime(timezone=False)),
        Column('substance_abuse_indefinite_date_effective', DateTime(timezone=False)),        
        Column('substance_abuse_indefinite_data_collection_stage', String(50)),
        Column('receive_substance_abuse_services', String(50)),
        Column('receive_substance_abuse_services_date_collected', DateTime(timezone=False)),
        Column('receive_substance_abuse_services_date_effective', DateTime(timezone=False)),        
        Column('receive_substance_abuse_services_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(SubstanceAbuseProblem, substance_abuse_problem_table)
        return

    def housing_status_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        housing_status_table = Table(
        'housing_status',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('housing_status', String(50)),
        Column('housing_status_date_collected', DateTime(timezone=False)),
        Column('housing_status_date_effective', DateTime(timezone=False)),        
        Column('housing_status_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(HousingStatus, housing_status_table)
        return

    def taxonomy_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        taxonomy_table = Table(
        'taxonomy',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('need_index_id', Integer, ForeignKey(Need.id)), 
        Column('code', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Taxonomy, taxonomy_table)
        return

    def hud_chronic_homeless_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        hud_chronic_homeless_table = Table(
        'hud_chronic_homeless',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('hud_chronic_homeless', String(50)),
        Column('hud_chronic_homeless_date_collected', DateTime(timezone=False)),
        Column('hud_chronic_homeless_date_effective', DateTime(timezone=False)),        
        Column('hud_chronic_homeless_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(HudChronicHomeless, hud_chronic_homeless_table)
        return

    def time_open_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        time_open_table = Table(
        'time_open',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_index_id', Integer, ForeignKey(Site.id)), 
        Column('languages_index_id', Integer, ForeignKey(Languages.id)), 
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)),
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('notes', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(TimeOpen, time_open_table)
        return

    def time_open_days_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        time_open_days_table = Table(
        'time_open_days',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('time_open_index_id', Integer, ForeignKey(TimeOpen.id)), 
        Column('day_of_week', String(50)),
        Column('from', String(50)),
        Column('to', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(TimeOpenDays, time_open_days_table)
        return

    def url_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        url_table = Table(
        'url',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('agency_index_id', Integer, ForeignKey(Agency.id)), 
        Column('site_index_id', Integer, ForeignKey(Site.id)),
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('address', String(50)),
        Column('note', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Url, url_table)
        return

    def veteran_military_branches_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        veteran_military_branches_table = Table(
        'veteran_military_branches',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('military_branch_id_id_id_num', String(50)),
        Column('military_branch_id_id_id_str', String(32)),
        Column('military_branch_id_id_delete', Integer),
        Column('military_branch_id_id_delete_occurred_date', DateTime(timezone=False)),
        Column('military_branch_id_id_delete_effective_date', DateTime(timezone=False)),
        Column('discharge_status', String(50)),
        Column('discharge_status_date_collected', DateTime(timezone=False)),
        Column('discharge_status_date_effective', DateTime(timezone=False)),        
        Column('discharge_status_data_collection_stage', String(50)),
        Column('discharge_status_other', String(50)),
        Column('discharge_status_other_date_collected', DateTime(timezone=False)),
        Column('discharge_status_other_date_effective', DateTime(timezone=False)),        
        Column('discharge_status_other_data_collection_stage', String(50)),
        Column('military_branch', String(50)),
        Column('military_branch_date_collected', DateTime(timezone=False)),
        Column('military_branch_date_effective', DateTime(timezone=False)),        
        Column('military_branch_data_collection_stage', String(50)),
        Column('military_branch_other', String(50)),
        Column('military_branch_other_date_collected', DateTime(timezone=False)),
        Column('military_branch_other_date_effective', DateTime(timezone=False)),        
        Column('military_branch_other_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(VeteranMilitaryBranches, veteran_military_branches_table)
        return


    def income_last_30_days_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        income_last_30_days_table = Table(
        'income_last_30_days',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('income_last_30_days', String(50)),
        Column('income_last_30_days_date_collected', DateTime(timezone=False)),
        Column('income_last_30_days_date_effective', DateTime(timezone=False)),        
        Column('income_last_30_days_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(IncomeLast30Days, income_last_30_days_table)
        return

    def veteran_military_service_duration_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        veteran_military_service_duration_table = Table(
        'veteran_military_service_duration',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('military_service_duration', String(50)),
        Column('military_service_duration_date_collected', DateTime(timezone=False)),
        Column('military_service_duration_date_effective', DateTime(timezone=False)),        
        Column('military_service_duration_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(VeteranMilitaryServiceDuration, veteran_military_service_duration_table)
        return

    def income_requirements_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        income_requirements_table = Table(
        'income_requirements',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)), 
        Column('income_requirements', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(IncomeRequirements, income_requirements_table)
        return

    def veteran_served_in_war_zone_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        veteran_served_in_war_zone_table = Table(
        'veteran_served_in_war_zone',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('served_in_war_zone', String(50)),
        Column('served_in_war_zone_date_collected', DateTime(timezone=False)),
        Column('served_in_war_zone_date_effective', DateTime(timezone=False)),        
        Column('served_in_war_zone_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(VeteranServedInWarZone, veteran_served_in_war_zone_table)
        return

    def income_total_monthly_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        income_total_monthly_table = Table(
        'income_total_monthly',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('income_total_monthly', String(50)),
        Column('income_total_monthly_date_collected', DateTime(timezone=False)),
        Column('income_total_monthly_date_effective', DateTime(timezone=False)),        
        Column('income_total_monthly_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(IncomeTotalMonthly, income_total_monthly_table)
        return

    def veteran_service_era_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        veteran_service_era_table = Table(
        'veteran_service_era',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('service_era', String(50)),
        Column('service_era_date_collected', DateTime(timezone=False)),
        Column('service_era_date_effective', DateTime(timezone=False)),        
        Column('service_era_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(VeteranServiceEra, veteran_service_era_table)
        return

    def veteran_veteran_status_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        veteran_veteran_status_table = Table(
        'veteran_veteran_status',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('veteran_status', String(50)),
        Column('veteran_status_date_collected', DateTime(timezone=False)),
        Column('veteran_status_date_effective', DateTime(timezone=False)),        
        Column('veteran_status_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(VeteranVeteranStatus, veteran_veteran_status_table)
        return

    def languages_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        languages_table = Table(
        'languages',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('site_index_id', Integer, ForeignKey(Site.id)), 
        Column('site_service_index_id', Integer, ForeignKey(SiteService.id)),
		Column('agency_location_index_id', Integer, ForeignKey(AgencyLocation.id)),
        Column('name', String(50)),
        Column('notes', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(Languages, languages_table)
        return

    def veteran_warzones_served_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        veteran_warzones_served_table = Table(
        'veteran_warzones_served',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('war_zone_id_id_id_num', String(50)),
        Column('war_zone_id_id_id_str', String(32)),
        Column('war_zone_id_id_delete', Integer),
        Column('war_zone_id_id_delete_occurred_date', DateTime(timezone=False)),
        Column('war_zone_id_id_delete_effective_date', DateTime(timezone=False)),
        Column('months_in_war_zone', String(50)),
        Column('months_in_war_zone_date_collected', DateTime(timezone=False)),
        Column('months_in_war_zone_date_effective', DateTime(timezone=False)),        
        Column('months_in_war_zone_data_collection_stage', String(50)),
        Column('received_fire', String(50)),
        Column('received_fire_date_collected', DateTime(timezone=False)),
        Column('received_fire_date_effective', DateTime(timezone=False)),        
        Column('received_fire_data_collection_stage', String(50)),
        Column('war_zone', String(50)),
        Column('war_zone_date_collected', DateTime(timezone=False)),
        Column('war_zone_date_effective', DateTime(timezone=False)),        
        Column('war_zone_data_collection_stage', String(50)),
        Column('war_zone_other', String(50)),
        Column('war_zone_other_date_collected', DateTime(timezone=False)),
        Column('war_zone_other_date_effective', DateTime(timezone=False)),        
        Column('war_zone_other_data_collection_stage', String(50)),                
        useexisting = True
        )
        table_metadata.create_all()
        mapper(VeteranWarzonesServed, veteran_warzones_served_table)
        return

    def length_of_stay_at_prior_residence_map(self):
        table_metadata = MetaData(bind=self.pg_db_engine)
        length_of_stay_at_prior_residence_table = Table(
        'length_of_stay_at_prior_residence',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('length_of_stay_at_prior_residence', String(50)),
        Column('length_of_stay_at_prior_residence_date_collected', DateTime(timezone=False)),
        Column('length_of_stay_at_prior_residence_date_effective', DateTime(timezone=False)),        
        Column('length_of_stay_at_prior_residence_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(LengthOfStayAtPriorResidence, length_of_stay_at_prior_residence_table)
        return

    def vocational_training_map(self):    
        table_metadata = MetaData(bind=self.pg_db_engine)
        vocational_training_table = Table(
        'vocational_training',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('vocational_training', String(50)),
        Column('vocational_training_date_collected', DateTime(timezone=False)),
        Column('vocational_training_date_effective', DateTime(timezone=False)),        
        Column('vocational_training_data_collection_stage', String(50)),
        useexisting = True
        )
        table_metadata.create_all()
        mapper(VocationalTraining, vocational_training_table)
        return
    
    def foster_child_ever_map(self):    
        table_metadata = MetaData(bind=self.pg_db_engine)
        foster_child_ever_table = Table(
        'foster_child_ever',
        table_metadata,
        Column('id', Integer, primary_key=True),
        Column('person_historical_index_id', Integer, ForeignKey(PersonHistorical.id)), 
        Column('foster_child_ever', Integer(2)),
        Column('foster_child_ever_date_collected', DateTime(timezone=False)),
        Column('foster_child_ever_date_effective', DateTime(timezone=False)),        
        useexisting = True
        )
        table_metadata.create_all()
        mapper(FosterChildEver, foster_child_ever_table)
        return

class BaseObject(object):
    def __init__(self, field_dict):
        if settings.DEBUG:
            print "Base Class created: %s" % self.__class__.__name__
    #def __init__(self, field_dict):
        if settings.DEBUG:
            print field_dict
        for x, y in field_dict.iteritems():
            self.__setattr__(x,y)
        
    def __repr__(self):
        field_dict = vars(self)
        out = ''
        if len(field_dict) > 0:
            for x, y in field_dict.iteritems():
                if x[0] != "_":
                    out = out + "%s = %s, " % (x,y)
                    
            return "<%s(%s)>" % (self.__class__.__name__, out)
        else:
            return ''

class Agency(BaseObject):
    pass

class AgencyChild(BaseObject):
    pass

# SBB20100914 Missing..
class AgencyLocation(BaseObject):
    pass

class AgencyService(BaseObject):
    pass

class AgeRequirements(BaseObject):
    pass

class AidRequirements(BaseObject):
    pass

class Aka(BaseObject):
    pass

class ApplicationProcess(BaseObject):
    pass

class AssignmentPeriod(BaseObject):
    pass

class Assignment(BaseObject):
    pass

class ChildEnrollmentStatus(BaseObject):
    pass

class ChildEnrollmentStatusBarrier(BaseObject):
    pass

class ChronicHealthCondition(BaseObject):
    pass

class Contact(BaseObject):
    pass

class ContactMade(BaseObject):
    pass

class CrossStreet(BaseObject):
    pass

class CurrentlyInSchool(BaseObject):
    pass

class Degree(BaseObject):
    pass

class DegreeCode(BaseObject):
    pass

class Destinations(BaseObject):
    pass

class DevelopmentalDisability(BaseObject):
    pass

class DisablingCondition(BaseObject):
    pass

class DocumentsRequired(BaseObject):
    pass

class DomesticViolence(BaseObject):
    pass

class DrugHistory(BaseObject):
    pass

class Email(BaseObject):
    pass

class EmergencyContact(BaseObject):
    pass

class Employment(BaseObject):
    pass

class EngagedDate(BaseObject):
    pass

class Export(BaseObject):
    pass

class Report(BaseObject):
    pass

class FamilyRequirements(BaseObject):
    pass

class FosterChildEver(BaseObject):
    pass

class FundingSource(BaseObject):
    pass

class GeographicAreaServed(BaseObject):
    pass

class HealthStatus(BaseObject):
    pass

class HighestSchoolLevel(BaseObject):
    pass

class HivAidsStatus(BaseObject):
    pass

class HmisAsset(BaseObject):
    pass

class Household(BaseObject):
    pass

class HousingStatus(BaseObject):
    pass

class HUDHomelessEpisodes(BaseObject):
    pass

class HudChronicHomeless(BaseObject):
    pass

class IncomeAndSources(BaseObject):
    pass

class IncomeLast30Days(BaseObject):
    pass

class IncomeRequirements(BaseObject):
    pass

class IncomeTotalMonthly(BaseObject):
    pass

class Inventory(BaseObject):
    pass

class Languages(BaseObject):
    pass

class LengthOfStayAtPriorResidence(BaseObject):
    pass

class LicenseAccreditation(BaseObject):
    pass

class Members(BaseObject):
    pass

class MentalHealthProblem(BaseObject):
    pass

class Need(BaseObject):
    pass

class NonCashBenefits(BaseObject):
    pass

class NonCashBenefitsLast30Days(BaseObject):
    pass

class OtherNames(BaseObject):
    pass

class OtherAddress(BaseObject):
    pass

class OtherRequirements(BaseObject):
    pass

class Person(BaseObject):
    pass

class PersonAddress(BaseObject):
    pass

class PersonHistorical(BaseObject):
    pass

class Phone(BaseObject):
    pass

class PhysicalDisability(BaseObject):
    pass

class PitCounts(BaseObject):
    pass

class PitCountSet(BaseObject):
    pass

class Pregnancy(BaseObject):
    pass

class PriorResidence(BaseObject):
    pass

class Races(BaseObject):
    pass

class ReasonsForLeaving(BaseObject):
    pass

class Region(BaseObject):
    pass

class ReleaseOfInformation(BaseObject):
    pass

class ReleaseOfInfo(BaseObject):
    pass

class ResidencyRequirements(BaseObject):
    pass

# SBB20100524 Adding object to manage dedup linking.
class DeduplicationLink(BaseObject):
    pass

class SourceExportLink(BaseObject):
    pass

class ResourceInfo(BaseObject):
    pass

class Seasonal(BaseObject):
    pass

class Service(BaseObject):
    pass

class ServiceEvent(BaseObject):
    pass

class ServiceEventNotes(BaseObject):
    pass

class ServiceGroup(BaseObject):
    pass

class Site(BaseObject):
    pass

class SiteService(BaseObject):
    pass

class SiteServiceParticipation(BaseObject):
    pass

class Source(BaseObject):
    pass

class SpatialLocation(BaseObject):
    pass

class SubstanceAbuseProblem(BaseObject):
    pass

class SystemConfiguration(BaseObject):
    pass

class Taxonomy(BaseObject):
    pass

class TimeOpen(BaseObject):
    pass

class TimeOpenDays(BaseObject):
    pass

class Url(BaseObject):
    pass

class Veteran(BaseObject):
    pass

class VeteranMilitaryBranches(BaseObject):
    pass

class VeteranMilitaryServiceDuration(BaseObject):
    pass

class VeteranServedInWarZone(BaseObject):
    pass

class VeteranServiceEra(BaseObject):
    pass

class VeteranVeteranStatus(BaseObject):
    pass

class VeteranWarzonesServed(BaseObject):
    pass

class VocationalTraining(BaseObject):    
    pass
  
def main(argv=None):  
    if argv is None:
        argv = sys.argv
    
    if settings.DB_PASSWD == "":
        settings.DB_PASSWD = raw_input("Please enter your password: ")
        
    #pg_db_engine = create_engine('postgres://%s:%s@localhost:5432/%s' % (settings.DB_USER, settings.DB_PASSWD, settings.DB_DATABASE), echo=settings.DEBUG_ALCHEMY)#, server_side_cursors=True)
    
    mappedObjects = DatabaseObjects()
    
    # Query Exports for Data
    print 'Export'
    for export in mappedObjects.queryDB(Export):
        print export.export_software_vendor
        dbo = export.fk_export_to_database
        dir(dbo)
    
    # Person records
    print 'All Persons'
    print '-----------------------------------'
    for field in mappedObjects.queryDB(Person):
        print "New Person"
        print '------'
        print field.person_date_of_birth_unhashed
        print field.person_legal_first_name_unhashed
        print field.person_legal_last_name_unhashed
        print '------'
        
    print 'Person: George Washington'
    print '-----------------------------------'
    for person in mappedObjects.queryDB(Person).filter(Person.person_legal_first_name_unhashed=='George'):
        print person.person_legal_first_name_unhashed
    print '-----------------------------------'
        
    # All Persons
    query = mappedObjects.queryDB(Person).filter("export_index_id='1'")
    print query.count()
    query = mappedObjects.queryDB(Person).filter("export_index_id='1'").first()
    print query
    
    # get their PersonHistorical records
    print 'Person: George Washington'
    print '-----------------------------------'
    for person in mappedObjects.queryDB(Person).filter(Person.person_legal_first_name_unhashed=='George'):
        print person.person_legal_first_name_unhashed
        person.reported = True
        person.person_legal_first_name_unhashed = "user"
        mappedObjects.session().commit()
        print 'Person: George Washington (user)'
        print '-----------------------------------'
        print person
        #print person.person_historical
        for ph in person.fk_person_to_person_historical:
            print '-------'
            print ph.employment_tenure
            print '-------'
            for ias in ph.fk_person_historical_to_income_and_sources:
                print "IAS:Amount: %s" % ias.amount
    print '-----------------------------------'

if __name__ == "__main__":
    sys.exit(main())             
            
            
