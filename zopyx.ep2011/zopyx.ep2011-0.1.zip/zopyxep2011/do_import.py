
import os
import glob
import time
import pymongo
import vobject
import datetime
import random

DB = 'test'
COLL = 'addr'

cwd = os.path.dirname(__file__)
vcf_dir = os.path.join(cwd, 'vcf')

def main():

    print 'Starting import into MongoDB (database:% s, collection: %s)' % (DB, COLL)

    conn = pymongo.Connection()
    db = getattr(conn, DB)
    coll = getattr(db, COLL)
    coll.remove()

    for i, name in enumerate(os.listdir(vcf_dir)):
        if not name.endswith('.vcf'):
            continue
        print i, name
        data = file(os.path.join(vcf_dir, name)).read()
        vc = vobject.readOne(data)
        bday = vc.bday.value.strip().split('-')
        bday = map(int, bday)
        birthday = datetime.datetime(*bday)
        if birthday.year < 1973:
            birthday = None

        try:
            phone = vc.tel.value
        except: 
            phone = None
        d = dict(
            city=vc.adr.value.city,
            code=vc.adr.value.code,
            country=vc.adr.value.country,
            street=vc.adr.value.street,
            region=vc.adr.value.region,
            lastname=vc.n.value.family,
            firstname=vc.n.value.given,
            email=vc.email.value,
            phone=phone,
            birthday=birthday,
            age=random.randint(1,80),
            )
        coll.insert(d)
    
    print 'Import done'

if __name__ == '__main__':
    main()
