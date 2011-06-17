
import os
import time
import json
import pymongo
import datetime
import random
import csv

DB = 'test'
COLL = 'addr'

cwd = os.path.dirname(__file__)
country_data = json.load(file(os.path.join(cwd, 'countrys.json')))

class MyDialect(csv.excel):
    delimiter = ','
    lineterminator = '\n'

def main():

    print 'Starting import into MongoDB (database:% s, collection: %s)' % (DB, COLL)

    conn = pymongo.Connection()
    db = getattr(conn, DB)
    coll = getattr(db, COLL)
    coll.remove()

    csv_file = os.path.join(cwd, 'data.csv')
    map = dict()
    addresses = list()
    for i, line in enumerate(csv.reader(file(csv_file), dialect=MyDialect)):
        if i % 1000 == 0:
            print i
        if i == 0:
            for k, name in enumerate(line):
                map[k] = name
        else:
            d = dict()
            for k, name in enumerate(line):
                if k in map:
                    d[map[k].lower()] = name
            addresses.append(d)

    for i, d in enumerate(addresses):
        birthday = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365*40))
        d['age'] = random.randint(0, 100)
        d['birthday'] = birthday
        d['country2'] = random.choice(country_data)['name-en']
        d['centimeters'] = float(d['kilograms'])
        try:
            d['pounds'] = float(d['pounds'])
        except:
            pass
        coll.insert(d)
    
    print 'Import done'

if __name__ == '__main__':
    main()
