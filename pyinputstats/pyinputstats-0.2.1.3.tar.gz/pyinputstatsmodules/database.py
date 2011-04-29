# coding:utf-8

# pyInputStats - An application for mouse and keyboard statistics
# Copyright (C) 2011  Daniel Nögel
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

import os
import helpers
import sqlite3

import time
import datetime

class Cursor(object):
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, type, value, traceback):
        self.cursor.close()


class DatabaseConnector(object):
    def __enter__(self):
        path = helpers.get_data_dir()
        self.db_path = os.path.join(path, "data.db")
        if not os.path.exists(self.db_path):
            self.create_database()
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self

    def __exit__(self, type, value, traceback):
        self.connection.close()

    def create_database(self):
        sql = u"""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY,
                pixels INT,
                clicks INT,
                keys INT,
                time INT
            )"""
        sql2 = u"""CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY,
                key STRING UNIQUE,
                count INT)"""
        connection = sqlite3.connect(self.db_path)
        with Cursor(connection) as cursor:
            cursor.execute(sql)
            cursor.execute(sql2)
        connection.close()

    def get_char_stats(self):
        sql = u"""SELECT key, count FROM keys ORDER BY count DESC"""
        with Cursor(self.connection) as cursor:
            return cursor.execute(sql).fetchall()

    def get_stats(self, date=None):
        if not date:
            sql = u"""SELECT sum(pixels), sum(clicks), sum(keys) FROM data"""
            with Cursor(self.connection) as cursor:
                return cursor.execute(sql).fetchone()
        elif date == "today":
            today = datetime.date.today() #date.(fromtimestamp(time.time())
            timestamp = time.mktime(today.timetuple())
            sql = u"""
            SELECT sum(pixels), sum(clicks), sum(keys) 
            FROM data
            WHERE time > ?
            """
            with Cursor(self.connection) as cursor:
                return cursor.execute(sql, (timestamp,)).fetchone()
        elif isinstance(date, datetime.date):
            timestamp_start = time.mktime(date.timetuple())
            timestamp_end = timestamp_start + 24*60*60
            sql = u"""
            SELECT sum(pixels), sum(clicks), sum(keys) 
            FROM data
            WHERE time > ? AND time < ?
            """
            with Cursor(self.connection) as cursor:
                return cursor.execute(sql, (timestamp_start, timestamp_end)).fetchone()
        else:
            year, month = date
            timestamp_start = time.mktime(datetime.date(year, month, 1).timetuple())
            if month < 12:
                timestamp_end = time.mktime(datetime.date(year, month+1, 1).timetuple())
            else:
                timestamp_end = time.mktime(datetime.date(year+1, 1, 1).timetuple())
            sql = u"""
            SELECT sum(pixels), sum(clicks), sum(keys) 
            FROM data
            WHERE time > ? AND time < ?
            """
            with Cursor(self.connection) as cursor:
                return cursor.execute(sql, (timestamp_start, timestamp_end)).fetchone()

    def get_month_data(self, date, day, step=1):
            year, month = date
            timestamp_start = time.mktime(datetime.date(year, month, 1).timetuple()) + day*60*60*24
            timestamp_end = timestamp_start + step*60*60*24
            sql = u"""
            SELECT sum(pixels), sum(clicks), sum(keys)
            FROM data
            WHERE time > ? AND time < ?
            """
            with Cursor(self.connection) as cursor:
                return cursor.execute(sql, (timestamp_start, timestamp_end)).fetchall()

    #~ def test(self, date):
            #~ timestamp_start = time.mktime(date.timetuple()) 
            #~ timestamp_end = timestamp_start + 24*60*60
            #~ sql = u"""
            #~ SELECT pixels, clicks, keys, time
            #~ FROM data
            #~ WHERE time > ? AND time < ?
            #~ """
            #~ with Cursor(self.connection) as cursor:
                #~ return cursor.execute(sql, (timestamp_start, timestamp_end)).fetchall()

    def get_day_data(self, date, hour, step=1):
            timestamp_start = time.mktime(date.timetuple()) + hour*60*60
            timestamp_end = timestamp_start + step*60*60
            sql = u"""
            SELECT sum(pixels), sum(clicks), sum(keys)
            FROM data
            WHERE time > ? AND time < ?
            """
            with Cursor(self.connection) as cursor:
                return cursor.execute(sql, (timestamp_start, timestamp_end)).fetchall()

    def insert(self, data):
        sql = u"""INSERT OR IGNORE INTO data (
            pixels,
            clicks,
            keys,
            time
        ) VALUES (?, ?, ?, ?)"""
        
        #~ sql2 = u"""INSERT OR IGNORE INTO keys (
            #~ key,
            #~ count
        #~ ) VALUES (?, ?)"""
        
        sql2 = u"""INSERT OR IGNORE INTO keys (
            key,
            count
        ) VALUES (?, 0)"""
        
        sql3 = u""" UPDATE keys SET count = count+? WHERE key=?"""
        
        with Cursor(self.connection) as cursor:
            cursor.execute(sql, (data["distance"], data["buttons"], data["keys"], data["time"]))
            cursor.executemany(sql2, (((i[0], ) for i in data["keys_pressed"])))
            cursor.executemany(sql3, ((i[::-1] for i in data["keys_pressed"])))
        self.connection.commit()

    def get_num_days(self):
        sql = u"""SELECT time FROM data ORDER BY time ASC"""
        with Cursor(self.connection) as cursor:
            first = cursor.execute(sql).fetchone()
            if first:
                first = first[0]
                last = time.time()
                s = last-first
                d, s = divmod(s, 3600*24)
                h, s = divmod(s, 3600)
                res = d + h/24.0
                if res == 0:
                    return 1
                return d + h/24.0
                #~ return datetime.timedelta(seconds=last-first).days +1
            else:
                return 1

    def get_months(self):
        months = []
        
        sql = u"""SELECT time FROM data"""
        with Cursor(self.connection) as cursor:
            timestamps = cursor.execute(sql).fetchall()
            for timestamp in timestamps:
                d = datetime.date.fromtimestamp(timestamp[0])
                t = (d.year, d.month)
                if not t in months:
                    months.append(t)
            today = datetime.date.today()
            if not (today.year, today.month) in months:
                months.append((today.year, today.month))
            months.sort()
            return months

    def get_days(self):
        days = []
        
        sql = u"""SELECT time FROM data"""
        with Cursor(self.connection) as cursor:
            timestamps = cursor.execute(sql).fetchall()
            for timestamp in timestamps:
                d = datetime.date.fromtimestamp(timestamp[0])
                if not d in days:
                    days.append(d)
            return days
        
