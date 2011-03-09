#!/usr/bin/env python
# coding:utf-8

# lsrSID - Python HVSC browser and sidplay2 GUI.
# Copyright (C) 2010  Daniel Nögel
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys
import time
import logging
import datetime
try:
    from pysqlite2 import dbapi2 as sqlite3
except ImportError:
    import sqlite3
    

import Queue, thread
from threading import Thread
import truncate

import helpers

class Query(object):
    def __init__(self, cmd=None, params=[]):
        if cmd is None: cmd = SqlCmd
        self.cmd = cmd
        self.params = params

ReconnectCmd = "reconnect"
ConnectCmd = "connect"
SqlCmd = "SQL"
SqlMany = "sqlmany"
StopCmd = "stop"

(
 FIELD_UID,
 FIELD_TYPE,
 FIELD_VERSION,
 FIELD_SUBTUNES,
 FIELD_STARTTUNE,
 FIELD_TITLE,
 FIELD_ARTIST,
 FIELD_COPYRIGHT,
 FIELD_SIZE,
 FIELD_PATH,
 FIELD_TIMES,
 FIELD_HASH
) = range(12)
 

class DBThread(Thread):
    def __init__(self, path, queue, thread_lock, thread_counter):
        Thread.__init__(self)
        self.path = path
        self.nr = thread_counter
        self.started = time.time()
        
        self.queue = queue
        self.thread_lock = thread_lock
        self.thread_counter = thread_counter
    
    def reconnect(self):
        self.con.close()
        self.con = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cur = self.con.cursor()
            
    def run(self):
        self.con = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cur = self.con.cursor()
        while True:
            s = self.queue.get()
            #~ if "print-queries" in sys.argv:
                #~ print "Conn %d -> %s -> %s" % (self.nr, s.cmd, s.params)
            if s.cmd == SqlCmd:
                #~ print self.started
                commitneeded = False
                res = []
#               s.params is a list to bundle statements into a "transaction"
                for sql in s.params:
                    try:
                        if len(sql) == 1:
                            self.cur.execute(sql[0])
                        else:
                            self.cur.execute(sql[0],sql[1])
                    except Exception, inst:
                        logging.error(sql)
                        raise
                    if not sql[0].upper().startswith("SELECT"): 
                        commitneeded = True
                    for row in self.cur.fetchall(): res.append(row)
                if commitneeded:
                    self.con.commit()
                s.resultqueue.put(res)
            elif s.cmd == SqlMany:
                self.con.executemany(s.params[0], s.params[1])
                self.con.commit()
            elif s.cmd == ReconnectCmd:
                self.reconnect()
            else:
                self.con.close()
                self.thread_lock.acquire()
                self.thread_counter -= 1
                self.thread_lock.release()
#               allow other threads to stop
                self.queue.put(s)
                s.resultqueue.put(None)
                break

class SID(object):
    def __init__(self, type, version, subsongs, startsong, title, artist, copyright, size, path, times, hash, basedir = None):
        self.type = unicode(type )
        self.version = version
        self.subsongs = subsongs
        self.startsong = startsong
        self.title = unicode(title)
        self.artist = unicode(artist)
        self.copyright = unicode(copyright)
        self.size = size
        self.hash = hash
        if basedir:
            self.path = os.path.join(basedir, path.lstrip("/"))
        else:
            self.path = path
        self.times = [int(t) for t in str(times).split(",")]
    
    def get_songlength(self, song):
        return self.times[song-1]

class DB(object):
    def __init__(self, main):
        self.main = main
        
        self.db = os.path.join(helpers.get_data_dir(), "lsrsid.db")
        self.connection = None

        self.query_counter = 0

        self.open() 
        self.create_database()

    @property
    def is_empty(self):
        if not os.path.exists(self.db):
            return True
        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        try:
            ret = self.query(sql)
        except OperationalError:
            return True
        if not ("sids", ) in ret:
            self.create_database()
            return True
        else:
            sql = "SELECT COUNT(*) FROM sids WHERE 1"
            ret = self.query(sql)
            if ret[0][0] == 0:
                return True
            return False
    #~ @is_empty.setter
    #~ def is_empty(self, value):
        #~ self._is_empty = value

    def rate_track(self, hash, rating):
        sql = "SELECT rating FROM listencounter WHERE hash=?"
        ret = self.query(sql, (hash,))

        if ret == []:
            sql = "INSERT INTO listencounter (hash, rating) values(?, ?)"
            data = (hash, rating)
        else:
            sql = "UPDATE listencounter SET rating=? WHERE hash=?"
            data = (rating, hash)

        self.query(sql, data)
        
    def get_track_rating(self, hash):
        sql = "SELECT rating FROM listencounter WHERE hash=?"
        ret = self.query(sql, (hash, ))
        if ret == [] or ret == -1: 
            return 0
        else:
            if ret[0][0] is None:
                return 0
            else:
                return ret[0][0]

    def increase_listen_counter(self, hash):
        sql = "SELECT counter FROM listencounter WHERE hash=?"
        ret = self.query(sql, (hash,))

        if ret == []:
            sql = "INSERT INTO listencounter (hash, counter, time) values(?, '1', ?)"
            data = (hash, time.time())
        else:
            sql = "UPDATE listencounter SET counter=counter+1, time=? WHERE hash=?"
            data = (time.time(), hash)

        self.query(sql, data)
        
        #~ self.connection.execute()
        #~ print type(self.query('select current_timestamp as "time [timestamp]"')[0][0])
        
    def get_random_sids(self, num):
        sql = "SELECT * FROM sids ORDER BY RANDOM() LIMIT ?"

        results = self.query(sql, [str(num)])
        
        return  [SID(*result[1:], basedir=self.main.basedir) for result in results]

    def get_most_played(self, num=None):
        if not num:
            sql = "SELECT sids.* from sids, listencounter WHERE sids.hash=listencounter.hash AND listencounter.counter > 0 ORDER BY listencounter.counter DESC"
            results = self.query(sql)
        else:
            sql = "SELECT sids.* from sids, listencounter WHERE sids.hash=listencounter.hash AND listencounter.counter > 0 ORDER BY listencounter.counter DESC LIMIT ?"
            results = self.query(sql, [str(num)])
        return  [SID(*result[1:], basedir=self.main.basedir) for result in results]

    def get_best_rated(self, num=None):
        if not num:
            sql = "SELECT sids.* from sids, listencounter WHERE sids.hash=listencounter.hash AND listencounter.rating > 0 ORDER BY listencounter.rating DESC"
            results = self.query(sql)
        else:
            sql = "SELECT sids.* from sids, listencounter WHERE sids.hash=listencounter.hash AND listencounter.rating > 0 ORDER BY listencounter.rating DESC LIMIT ?"
            results = self.query(sql, [str(num)])
        return  [SID(*result[1:], basedir=self.main.basedir) for result in results]

    def get_listen_counter(self, hash):
        sql = "SELECT counter FROM listencounter WHERE hash=?"
        ret = self.query(sql, (hash, ))
        if ret == [] or ret == -1: 
            return 0
        else:
            if len(ret[0]) == 1: 
                return ret[0][0]
            else:
                return ret[0]

    def create_database(self):
        #type, version, subtunes, startsong, title, artist, copyright, size, time,
        
        logging.info("Creating Tables")

        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        result = self.query(sql)
        if not ("sids", ) in result:

            logging.info("Creating table 'sids'")

            sql = """
            CREATE TABLE sids (
              uid INTEGER PRIMARY KEY,
              type STRING,
              version STRING,
              subsongs INT,
              startsong STRING,
              title STRING,
              artist STRING,
              copyright STRING,
              size INT,
              path STRING,
              times STRING,
              hash STRING
            )
            """
            #~ self.connection.execute(sql)
            #~ self.connection.commit()
            self.query(sql)

        if not ("listencounter", ) in result:
    
            logging.info("Creating table 'listencounter'")
    
            sql = """
            CREATE TABLE listencounter (
              uid INTEGER PRIMARY KEY,
              hash STRING,
              time int,
              rating int,
              counter INT
            )
            """ # TIMESTAMP
            #~ self.connection.execute(sql)
            #~ self.connection.commit()
            self.query(sql)
        
    def get_sid_rating(self, hashes):
        basedir = self.main.basedir
        hashes = ["'{0}'".format(h) for h in hashes]
        
        hash_string = ", ".join(hashes)
        hash_string = "listencounter.hash IN ({0})".format(hash_string)

        sql = """
            SELECT
                hash, rating, counter
            FROM
                listencounter
            WHERE
                %s
            """ % hash_string
        
        results = self.query(sql)
        return  results
    
    def iter_sids(self, paths, results_per_iteration=500, sort=False):
        
        basedir = self.main.basedir
        paths = [p.replace(basedir, "") for p in paths]
        new_paths = ["'{0}'".format(p) for p in paths]
        
        for i in xrange(0, len(paths), results_per_iteration):
            #~ path_string = "("
            #~ for path in paths[i:i+results_per_iteration]:
                #~ path_string += " (path=? and sids.hash=listencounter.hash) or"                 
            #~ path_string = path_string[:-3] + ")"
            path_string = ", ".join(new_paths[i:i+results_per_iteration])
            path_string = "sids.path IN ({0})".format(path_string)
                
            
            
            sql = """
                SELECT
                    *
                FROM
                    sids
                WHERE
                    %s
                """ % path_string
            
            #~ basedir = self.main.basedir
            #~ paths = [p.replace(basedir, "") for p in paths]
            results = self.query(sql)#, paths[i:i+results_per_iteration])
            #~ print results

            if sort:
                logging.debug("Sorting results...")
                results = [k for k in results for j in paths[i:i+results_per_iteration] if k[FIELD_PATH] == j]
                logging.debug("... done")
            
            yield  [SID(*result[1:], basedir=basedir) for result in results]
    
    def get_sids(self, paths, sort=False):
        basedir = self.main.basedir
        paths = [p.replace(basedir, "") for p in paths]
        new_paths = ["'{0}'".format(p) for p in paths]
        
        path_string = ", ".join(new_paths)
        path_string = "sids.path IN ({0})".format(path_string)

        sql = """
            SELECT
                *
            FROM
                sids
            WHERE
                %s
            """ % path_string
        
        results = self.query(sql)
        #~ print len(results)
        
        if sort:
            results = [i for i in results for j in paths if i[FIELD_PATH] == j]
            #~ for result in results:
                
        
        return  [SID(*result[1:]) for result in results]
        
    
    #~ def iter_sids_ordered(self, paths):
        #~ for path in paths:
            #~ yield self.get_sid(path)
    
    def get_sid(self, path):
        short_path = path.replace(self.main.basedir, "")
        
        query = "SELECT * FROM sids WHERE path=?;"
        values = [short_path]
        
        results = self.query(query, values)
        #~ type, version, subsongs, startsong, title, artist, copyright, size, time = *results
        #~ print results
        try:
            return SID(*results[0][1:], basedir=self.main.basedir)
        except IndexError, msg:
            print query, path
            print results
            raise
        
    def insert_sids(self, sids):
       
        sql = u"""INSERT INTO sids (
            type,
            version,
            subsongs,
            startsong,
            title,
            artist,
            copyright,
            size,
            path,
            times,
            hash
        ) VALUES (
            :type,
            :version,
            :subsongs,
            :startsong,
            :title,
            :artist,
            :copyright,
            :size,
            :path,
            :times,
            :hash
        )
            """
        logging.info("Inserting data…")
        self.execute_many(sql, sids)
        logging.info("…done")
    
    def drop_table_sids(self):
        sql = "DROP TABLE IF EXISTS 'sids'"
        self.query(sql)
        s = Query(ReconnectCmd, None)
        self.queue.put(s)

    
    def create_index(self):
        sql = "DROP INDEX IF EXISTS 'IDX_PATH_HASH'"
        self.query(sql)

        sql = "DROP INDEX IF EXISTS 'IDX_LISTENCOUNTER_HASH'"
        self.query(sql)

        logging.info("Indexing sids…")
        sql = "CREATE INDEX IDX_PATH_HASH on sids (path, hash)"
        self.query(sql)
        logging.info("…done")

        logging.info("Indexing listencounter…")
        sql = "CREATE INDEX IDX_LISTENCOUNTER_HASH on listencounter (hash)"
        self.query(sql)
        logging.info("…done")

    
    def get_number_of_songs(self):
        sql = "SELECT COUNT(*) FROM sids where 1"
        
        return self.query(sql)[0][0]
    
    def get_date(self):
        sql = "SELECT DISTINCT substr(copyright, 0, 5) FROM sids WHERE 1 ORDER BY copyright"
        
        result = self.query(sql)
        return [l[0] for l in result]
    
    def get_artists(self):
        sql = "SELECT DISTINCT artist FROM sids where 1 ORDER BY artist"
        
        result = self.query(sql)
        return [l[0] for l in result]
    
    def get_tracks_by_year(self, year):
        sql = "SELECT * FROM sids WHERE copyright LIKE ? ORDER BY artist;"
        results = self.query(sql, ["{0}%".format(year)])
        
        basedir = self.main.basedir
        return  [SID(*result[1:], basedir=basedir) for result in results]
    
    #~ def get_multiple_artists_tracks(self, artists):
        #~ artists_string = ", ".join(["?" for a in artists])
        #~ sql = "SELECT * FROM sids WHERE artist IN ({0}) ORDER BY artist, title".format(artists_string)
        #~ 
        #~ results = self.query(sql, artists)
        #~ basedir = self.main.basedir
        #~ return  [SID(*result[1:], basedir=basedir) for result in results]
    
    def get_artists_tracks(self, artist):
        sql = "SELECT * FROM sids WHERE artist=? ORDER BY title;"
        results = self.query(sql, [artist])
        
        basedir = self.main.basedir
        return  [SID(*result[1:], basedir=basedir) for result in results]
    
    def get_artist_playstats(self, artist):
        sql = "SELECT sum(listencounter.counter) FROM sids, listencounter WHERE sids.hash=listencounter.hash and sids.artist=?;"
        
        ret = self.query(sql, (artist,))[0][0]
        if ret is None:
            return 0
        else:
            return ret
    
    def search(self, text):
        sql = "SELECT * FROM sids WHERE title LIKE ? OR artist LIKE ? or path LIKE ?;"
        
        text = "%{0}%".format(text.replace(" ", "%"))
        
        results = self.query(sql, [text, text, text])
        basedir = self.main.basedir
        return  [SID(*result[1:], basedir=basedir) for result in results]

    def open(self):
        self.connection = sqlite3.connect(self.db, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.thread_lock = thread.allocate_lock()
        self.thread_counter = 0
        self.queue = Queue.Queue()
        
        self.thread_lock.acquire()
        self.thread_counter += 1
        self.thread_lock.release()
        wrap = DBThread(self.db, self.queue, self.thread_lock, self.thread_counter)
        wrap.start()
        
    def close(self):
        self.connection.close()

    def quit(self):
        logging.info("Shutting down database…")
        s = Query(StopCmd)
        s.resultqueue = Queue.Queue()
        self.queue.put(s)
        #~ self.close()
        #~ while self.thread_counter > 0:
            #~ time.sleep(0.1)
        logging.info("…done")

    def execute_many(self, sql, data):
        s = Query(SqlMany, (sql, data))
        self.queue.put(s)
        self.query_counter += 1
        


    def query(self, query, values=None):
        logging.debug("Query #{0:4}: {1}".format(self.query_counter, truncate.trunc(query, max_pos=80, trim=True)))
        if not values:
            s = Query(None, [(query, )])
        else:
            s = Query(None, [(query, values)])
        s.resultqueue = Queue.Queue()
        self.queue.put(s)
        ret = s.resultqueue.get()
        
        self.query_counter += 1
        #~ logging.debug("Query #{0:4}: {1}, {2}".format(self.query_counter, query, values))
        return ret
        
        #~ try:
            #~ cur = self.connection.cursor()
            #~ if values:
                #~ cur.execute(query, values)
            #~ else:
                #~ cur.execute(query)
            #~ rows = cur.fetchall()
            #~ return rows
        #~ except Exception, inst:
            #~ raise
