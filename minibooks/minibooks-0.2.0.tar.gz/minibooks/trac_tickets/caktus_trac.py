import psycopg2
import psycopg2.extensions

from caktus.decorators import requires_kwarg

class CaktusCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        print sql
        psycopg2.extensions.cursor.execute(self, sql, args)

class CaktusTrac(object):
    dsn = None
    client_encoding = 'UTF8'
    dbname, user, password, host = None, None, None, None
    
    @requires_kwarg('dbname')
    def __init__(self, *args, **kwargs):
        self.dbname = kwargs.pop('dbname')
        self.user = kwargs.pop('user', None)
        self.password = kwargs.pop('password', None)
        self.host = kwargs.pop('host', None)
        
        self._connect()
    
    def _connect(self):
        """
        Establish a connection to trac database
        """
        
        # create DSN string
        dsn_options = []
        for option in ('dbname', 'user', 'password', 'host'):
            value = getattr(self, option, None)
            if value is not None:
                dsn_options.append("%s='%s'" % (option, value))
        
        self.dsn = " ".join(dsn_options)
        self.connection = psycopg2.connect(self.dsn)
        self.connection.set_client_encoding(self.client_encoding)
        self.cursor = self.connection.cursor(cursor_factory=CaktusCursor)
    
    def _install_views(self):
        """
        Create views to simplify access to trac database model
        """
        
        # get a list of trac schemas (one for each trac project)
        self.cursor.execute(
        """
        SELECT
            DISTINCT(table_schema)
        FROM 
            information_schema.tables
        WHERE
            table_schema NOT IN ('information_schema', 'pg_catalog', 'public')
        """)
        
        for schema in self.cursor.fetchall():
            schema_name = schema[0]
            
            try:
                self.cursor.execute("DROP VIEW _%s_totalhours CASCADE" % schema_name)
            except psycopg2.ProgrammingError:
                # view does not exist
                self.connection.rollback()
            
            self.cursor.execute("""
            CREATE VIEW _%s_totalhours AS
            SELECT
                change.ticket,
                ticket.milestone,
                change.author,
                ROUND(CASE 
                        WHEN newvalue = '' OR newvalue is NULL THEN 0
                        ELSE newvalue::float 
                    END::numeric, 2) AS value,
                value as billable
            FROM %s.ticket_change change, %s.ticket_custom custom, %s.ticket ticket
            WHERE change.ticket = custom.ticket AND
                change.ticket = ticket.id AND
                custom.name = 'billable' AND
                change.field = 'totalhours' AND
                change.time = (SELECT max(change2.time) 
                        FROM %s.ticket_change change2 
                        WHERE change2.ticket = change.ticket AND 
                            change2.field='totalhours')
            GROUP BY change.author, change.ticket, ticket.milestone, custom.value, change.newvalue
            ORDER BY change.ticket;
            """ % (schema_name, schema_name, schema_name, schema_name, schema_name))
            
            try:
                self.cursor.execute("DROP VIEW _%s_hours_with_time CASCADE" % schema_name)
            except psycopg2.ProgrammingError:
                self.connection.rollback()
            
            self.cursor.execute("""
            CREATE VIEW _%s_hours_with_time AS
            SELECT     
                change.ticket,
                to_timestamp(change.time) AS time,
                ticket.milestone,
                change.author,
                ROUND(CASE 
                    WHEN newvalue = '' OR newvalue is NULL THEN 0
                    ELSE newvalue::float 
                    END::numeric, 2) AS value,
                value as billable
            FROM %s.ticket_change change, %s.ticket_custom custom, %s.ticket ticket
            WHERE change.ticket = custom.ticket AND
                change.ticket = ticket.id AND
                custom.name = 'billable' AND
                change.field = 'hours'
            GROUP BY change.author, change.ticket, ticket.milestone, custom.value, change.time, change.newvalue
            ORDER BY change.ticket;
            """ % (schema_name, schema_name, schema_name, schema_name))
            
            try:
                self.cursor.execute("DROP VIEW _%s_hours CASCADE" % schema_name)
            except psycopg2.ProgrammingError:
                self.connection.rollback()
            
            return
            
            self.cursor.execute("""
            CREATE VIEW _%s_hours AS
            SELECT
                ticket,
                milestone,
                author,
                SUM(value) AS value,
                billable
            FROM _%s_hours_with_time
            GROUP BY value, ticket, milestone, author, billable;
            """ % (schema_name, schema_name))
            
            combined_view_sql.append("""
            SELECT '%s' as project,
                hours.ticket, 
                hours.milestone,
                hours.author,
                hours.value AS hours,
                totalhours.value AS totalhours,
                hours.billable
            FROM _%s_totalhours totalhours, _%s_hours hours
            WHERE totalhours.ticket = hours.ticket
            """ % (schema_name, schema_name, schema_name))
            
            combined_view_sql_with_time.append("""
            SELECT
                '%s' as project,
                ticket, 
                time,
                milestone,
                author,
                value AS hours,
                billable
            FROM
                _%s_hours_with_time
            """ % (schema_name, schema_name))
            
        self.cursor.execute("""
        CREATE VIEW public.combined_hours AS
        %s;
        """ % '\nUNION ALL\n'.join(combined_view_sql))
        
        self.cursor.execute("""
        CREATE VIEW public.combined_hours_with_time AS
        %s;
        """ % '\nUNION ALL\n'.join(combined_view_sql_with_time))
    
