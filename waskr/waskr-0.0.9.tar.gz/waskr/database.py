import os
from pymongo import Connection, DESCENDING
import sqlite3
from time import time, strftime, gmtime
from waskr.config import options
import log

# Fixes Database Absolute Location
FILE_CWD =  os.path.abspath(__file__)
FILE_DIR = os.path.dirname(FILE_CWD)
DB_FILE = FILE_DIR+'/waskr.db'


class conf_db(object):

    def __init__(self,
            db = DB_FILE):
        self.db = db 
        if os.path.isfile(self.db):
            self.conn = sqlite3.connect(self.db)
            self.c = self.conn.cursor()
        else:
            self.conn = sqlite3.connect(self.db)
            table = """CREATE TABLE config(path TEXT)"""
            self.c = self.conn.cursor()
            self.c.execute(table)
            self.conn.commit()


    def closedb(self):
        """Make sure the db is closed"""
        self.conn.close()


    def add_config(self, path):
        """Adds a MASTER config for waskr"""
        values = (path,path)
        delete = 'DELETE FROM config'
        command = 'INSERT INTO config(path) select ? WHERE NOT EXISTS(SELECT 1 FROM config WHERE path=?)' 
        self.c.execute(delete)
        self.c.execute(command, values)
        self.conn.commit()


    def get_config_path(self):
        """Returns the first entry for the config path"""
        command = "SELECT * FROM config limit 1"
        return self.c.execute(command)


class Stats(object):

    def __init__(self, config=None, test=False):
        config = options(config)
        try:
            self.connection = Connection(
                    config['db_host'], 
                    int(config['db_port']))
        except Exception, error:
            log.database.critical("Could not connect to MongoDB: %s" % error)
        self.waskr = self.connection['waskr']
        self.stats = self.waskr['stats']
        self.users = self.waskr['user']
        log.database.debug("database connection initialized")
        if test:
            self.waskr = self.connection['test_waskr']
            self.stats = self.waskr['stats']
            self.users = self.waskr['user']

    def insert(self, stats):
        # Stats should come as a list of dictionaries
        for stat in stats:
            self.stats.insert(stat)
        log.database.debug("inserted stats to database")

    def last_insert(self):
        last = self.stats.find().sort('time', DESCENDING).limit(1)
        for entry in last:
            unix_time =  entry['time']
            struct = gmtime(unix_time)
            formatted = strftime('%Y-%m-%d %H:%M:%S', struct)
            return formatted
        log.model.debug("returned formatted last insert from database")

    def apps_nodes(self):
        apps = []
        for application in self.stats.distinct('application'):
            c = self.stats.find({'application':application})
            for record in c:
                match = (record['application']), record['server_id']
                if match not in apps:
                    apps.append(match)
        return apps
        log.model.debug("returned all application nodes present")

    def response_time(self, minutes):
        """Get the last N minutes of response stats"""
        time_response = []
        mins = int(minutes) * 60
        start = time() - int(mins)
        records = self.stats.find({"time": {"$gte": start, "$lt": time()}})
        for stat in records:
            data = []
            miliseconds = int(stat['time']) * 1000
            data.append(miliseconds)
            data.append(stat['response'])
            time_response.append(data)
        log.model.debug("returned the last N minutes of response stats")
        return time_response

    def response_bundle(self, minutes):
        """Get the last N minutes of response stats in a bundle"""
        time_response = []
        total = 0
        mins = int(minutes) * 60
        start = time() - int(mins)
        records = self.stats.find({"time": {"$gte": start, "$lt": time()}})
        for stat in records:
            total = total + stat['response']
            time_response.append(stat['response'])
        divide_by = len(time_response)
        try:
            average = total /divide_by
        except ZeroDivisionError:
            average = 0
        return average

    def request_bundle(self, minutes):
        """Get the last N minutes of request stats in a bundle"""
        mins = int(minutes) * 60
        start = time() - int(mins)
        hits = self.stats.find({"time": {"$gte": start, "$lt": time()}}).count()
        return hits
        log.model.debug("returned requests per second")
 
    def request_time(self, minutes):
        """Get the last N minutes of request stats"""
        requests_second = []
        mins = int(minutes) * 60
        start = time() - int(mins)
        records = self.stats.find({"time": {"$gte": start, "$lt": time()}})
        for stat in records:
            data = []
            hits = self.stats.find({'time':stat['time']}).count()
            miliseconds = int(stat['time']) * 1000
            data.append(miliseconds)
            data.append(hits)
            requests_second.append(data)
        return requests_second
        log.model.debug("returned requests per second")
    

