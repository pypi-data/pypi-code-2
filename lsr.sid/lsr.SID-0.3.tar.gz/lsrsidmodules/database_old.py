#!/usr/bin/env python
# coding:utf-8

import os, sys
import time
import logging
try:
    from pysqlite2 import dbapi2 as sqlite3
except ImportError:
    import sqlite3
    

import helpers

class SID(object):
    def __init__(self, type, version, subsongs, startsong, title, artist, copyright, size, path, times , hash, basedir = None):
        self.type = type 
        self.version = version
        self.subsongs = subsongs
        self.startsong = startsong
        self.title = str(title)
        self.artist = str(artist)
        self.copyright = str(copyright)
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

        if not os.path.exists(self.db):
            self.open() 
            self.create_database()
            self._is_empty = True
        else:
            self.open() 
            self._is_empty = False

    @property
    def is_empty(self):
        sql = "SELECT COUNT(*) FROM 'sids' WHERE 1"
        try:
            ret = self.query(sql)
        except sqlite3.OperationalError:
            return True
        return ret[0][0] == 0
    @is_empty.setter
    def is_empty(self, value):
        self._is_empty = value

    def set_value(self, section, option, value, table="settings"):
        sql = "SELECT COUNT(*) FROM %s WHERE section='%s' and option='%s'" % (table, section, option)
        ret = self.query(sql)

        if ret[0][0] == 0:
            sql = "INSERT INTO %s (section, option, value) values('%s', '%s', '%s')" % (table, section, option, value)
        else:
            sql = "UPDATE %s SET value='%s' WHERE section='%s' and option='%s'" % (table, value, section, option)

        self.connection.execute(sql)
        self.connection.commit()

        self.query_counter += 1

    def increase_listen_counter(self, hash):
        sql = "SELECT counter FROM listencounter WHERE hash=?"
        ret = self.query(sql, (hash,))

        if ret == []:
            sql = "INSERT INTO listencounter (hash, counter) values(?, '1')"
        else:
            sql = "UPDATE listencounter SET counter=counter+1 WHERE hash=?"

        self.connection.execute(sql, (hash,))
        self.connection.commit()

        self.query_counter += 1

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
        self.connection.execute(sql)
        self.connection.commit()


        sql = """
        CREATE TABLE listencounter (
          uid INTEGER PRIMARY KEY,
          hash STRING,
          counter INT
        )
        """
        self.connection.execute(sql)
        self.connection.commit()
    
    def iter_sids(self, paths):
        results_per_iteration = 500
        
        for i in xrange(0, len(paths), results_per_iteration):
            path_string = "("
            for path in paths[i:i+results_per_iteration]:
                path_string += " path=? or" 
            path_string = path_string[:-3] + ")"
            sql = """
                SELECT
                    *
                FROM
                    sids
                WHERE 
                    %s
                """ % path_string
            
            basedir = self.main.basedir
            paths = [p.replace(basedir, "") for p in paths]
            results = self.query(sql, paths[i:i+results_per_iteration])
            
            yield  [SID(*result[1:], basedir=basedir) for result in results]
    
    ### DONT USE - CAN ONLY FETCH UP TO THOUSAND RESULTS
    def get_sids(self, paths):
        path_string = "("
        for path in paths:
            path_string += " path=? or" 
        path_string = path_string[:-3] + ")"
        sql = """
            SELECT
                *
            FROM
                sids
            WHERE 
                %s
            """ % path_string
        
        basedir = self.main.basedir
        paths = [p.replace(basedir, "") for p in paths]
        print sql
        results = self.query(sql, paths)
        
        return  [SID(*result[1:]) for result in results]
        
    
    def iter_sids_ordered(self, paths):
        for path in paths:
            yield self.get_sid(path)
    
    def get_sid(self, path):
        short_path = path.replace(self.main.basedir, "")
        
        query = "SELECT * FROM sids WHERE path=?;"
        values = [short_path]
        
        results = self.query(query, values)
        #~ type, version, subsongs, startsong, title, artist, copyright, size, time = *results
        #~ print results
        return SID(*results[0][1:], basedir=self.main.basedir)
        
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
        self.connection.executemany(sql, sids)
        self.connection.commit()
        logging.info("…done")
        
        logging.info("Indexing…")
        sql = "CREATE INDEX IDX_CUSTOMER_LAST_NAME on sids (path)"
        self.query(sql)
        logging.info("…done")
    
    def get_artists(self):
        sql = "SELECT DISTINCT artist FROM sids where 1"
        
        result = self.query(sql)
        return [l[0] for l in result]
    
    def get_artists_tracks(self, artist):
        sql = "SELECT * FROM sids WHERE artist=?;"
        results = self.query(sql, [artist])
        
        basedir = self.main.basedir
        return  [SID(*result[1:], basedir=basedir) for result in results]
    
    def search(self, text):
        sql = "SELECT * FROM sids WHERE title LIKE ? OR artist LIKE ? or path LIKE ?;"
        
        text = "%{0}%".format(text.replace(" ", "%"))
        
        results = self.query(sql, [text, text, text])
        basedir = self.main.basedir
        return  [SID(*result[1:], basedir=basedir) for result in results]

    def open(self):
        self.connection = sqlite3.connect(self.db)
        
    def close(self):
        self.connection.close()


    def query(self, query, values=None):
        
        try:
            cur = self.connection.cursor()
            if values:
                cur.execute(query, values)
            else:
                cur.execute(query)
            rows = cur.fetchall()
            return rows
        except Exception, inst:
            raise
