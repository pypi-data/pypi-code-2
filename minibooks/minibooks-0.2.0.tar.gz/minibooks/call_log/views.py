#postgres
import psycopg2
import psycopg2.extensions
#regular expressions
import re

from django.shortcuts import render_to_response
from call_log.models import *

#should I be using a manager?
def log(request):
    DSN = "dbname='asterisk' user='asterisk' host='localhost' password='ouFoo0yi'"
    conn = psycopg2.connect(DSN)
    cursor = conn.cursor(cursor_factory=LoggingCursor)
    #cursor = connection.cursor()
    cursor.execute('SELECT * FROM cdr LIMIT 20')
    result_set = []
    rows = cursor.fetchall()
    for row in rows:
        result = {}
        result['acctId'] = row[0]
        #format info: http://www.djangoproject.com/documentation/templates/#now
        result['calldate'] = row[1]
        result['callerid'] = row[2]
        result['src'] = row[3]
        result['dst'] = row[4]
        #dcontext 5
        #channel 6
        #dstchannel 7
        #lastapp 8
        #lastdata 9
        result['duration'] = row[10]
        #bellsec 11
        result['disposition'] = row[12]
        result['amaflags'] = row[13]
        #accountcode 14
        #uniqueid 15
        #userfield 16
        result['callerid_name']   = re.search("\".*\"",result['callerid']).group().strip("\"")
        result['callerid_number'] = re.search("<.*>",result['callerid']).group().strip("<>")
        result_set.append(result)

    context = {
        'calls' : result_set,
        'rows' : rows,
    }

    return render_to_response('call_log/log.html', context)
