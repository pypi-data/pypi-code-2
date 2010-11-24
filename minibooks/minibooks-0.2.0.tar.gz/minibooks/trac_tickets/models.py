from django.db import models
from django.conf import settings

import logging
import psycopg2
import psycopg2.extensions
import psycopg2.extras
from datetime import datetime, timedelta
#from trac.config import *

import os
import pyparsing
import pprint

from crm.models import Project

class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        logger.info(self.mogrify(sql, args))
        
        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception, exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise

class TracConnection:
    def __init__(self):
        # make single connection to trac database
        DSN = "dbname='%s' user='%s' password='%s' host='%s'" % ( settings.TRAC_BASE, settings.TRAC_USER, settings.TRAC_PASS, settings.TRAC_HOST )
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
        
        self.connection = psycopg2.connect(DSN)
        self.connection.set_client_encoding('UTF8')

    def get_project_hours_sql(self, projects, min_date, max_date):
        select = ""
        for project in projects:
            if project.trac_environment == None or project.trac_environment == '':
                continue
            project_hours_select = str("""
                SELECT 
                             author,
                       SUM( CASE 
                                                WHEN newvalue = '' OR newvalue is NULL THEN 0 
                                                ELSE newvalue::float 
                                        END ), 
                             value AS billable,
                             '%s' AS project
                       FROM (
                                    SELECT * 
                                    FROM %s.ticket_change, %s.ticket_custom
                                    WHERE %s.ticket_change.ticket = %s.ticket_custom.ticket AND
                                          %s.ticket_custom.name = 'billable'
                             ) AS combined
                             WHERE 
                                      field='hours' AND 
                                      time >= EXTRACT(EPOCH FROM TIMESTAMP '%s') AND 
                                      time <= EXTRACT(EPOCH FROM TIMESTAMP '%s')
                             GROUP BY author, billable\n
            """ % (
                      project.trac_environment, #project column value
                  project.trac_environment, #FROM FROM
                  project.trac_environment, #FROM FROM
                  project.trac_environment, #FROM WHERE
                  project.trac_environment, #FROM WHERE
                  project.trac_environment, #FROM WHERE
                        min_date, 
                        max_date,
                        )
            )
            select += project_hours_select
            if project != list(projects)[-1]:
                select += '\nUNION ALL\n'
        print select
        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        return select


    def getUserTotalHours(self, projects, min_date, max_date, hash_prefix):
        cursor = self.connection.cursor(cursor_factory=LoggingCursor)
        select = self.get_project_hours_sql(projects, min_date=min_date, max_date=max_date)
        select = "SELECT author, SUM(sum), billable FROM ( %s ) AS total GROUP BY author, billable ORDER BY author;" % select
        try:
            cursor.execute(select)
        except Exception, e:
            print 'getTotalHours: select failed: %s' % e
            #print select
            return
        rows = cursor.fetchall()
        checks = {}
        for row in rows:
            if row[2] == '1':
                hash = { hash_prefix + "_billable" : row[1] }
            elif row[2] == '0':
                hash = { hash_prefix + "_not_billable" : row[1] }
            else:
                raise Exception('Unknown billable status', row[2])
            if checks.has_key(row[0]):
                checks[row[0]].update(hash)
            else:
                checks[row[0]] = hash
        return checks


    def getTickets(self, projects, username):
    
        columns = ( 'id', 'cc', 'owner', 'summary', 'changetime' )
        columns_select = ', '.join( column for column in columns )
        
        result = []
        for project in projects:
            if project.trac_environment == None or project.trac_environment == '':
                result.append((project,()))
                continue
            
            try:
                cursor = self.connection.cursor(cursor_factory=LoggingCursor)
                cursor.execute( str("SELECT %s FROM %s.ticket WHERE ( owner ILIKE '%s' OR cc ILIKE '%s' ) AND status!='closed'" % (columns_select.__str__(), project.trac_environment, username.__str__(), username.__str__() ) ) )
            except Exception, e:
                print "getTickets: select failed: %s" % e
                continue
            
            rows = cursor.fetchall()
            
            tickets = []
            for row in rows:
                ticket = {}
                for i in range( len(columns) ):
                    if 'time' in columns[i]:
                        ticket.update( { columns[i] : datetime.fromtimestamp(row[i]) } )
                    else:
                        ticket.update( { columns[i] : row[i] } )
                if ticket['id']:
                    ticket.update( { 'url' : '%sticket/%s' % ( project.trac_url(), ticket['id'] ) } )
                tickets.append(ticket)
            result.append( (project, tickets ) )
    
        return result

