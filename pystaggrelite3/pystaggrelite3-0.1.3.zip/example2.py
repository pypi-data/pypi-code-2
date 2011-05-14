import random
import sqlite3
import pystaggrelite3

con = sqlite3.connect(":memory:")

for (name,arity,func) in pystaggrelite3.getaggregators():
    con.create_aggregate(name,arity,func)

cur = con.cursor()
cur.execute("create table test(f)")

for i in xrange(100):
    cur.execute("insert into test(f) values (?)",
                (random.uniform(0.,2.),))


for (name,arity,func) in pystaggrelite3.getaggregators():
    
    cur.execute("select %s(f) from test"%name)
    print('%s\t\t\t%f'%(name,cur.fetchone()[0]))
