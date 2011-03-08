import sys
print sys.path

from dsaw.db import connect
db = connect(db ='postgres:///test', echo = True)
db.autocommit(True)

# we have to create system tables because we're using a reference
db.createSystemTables()

#create Lattice
from matter.orm.Lattice import Lattice
db.createTable(Lattice)
l1 = Lattice()
l1.id = 'l1'
db.insertRow(l1)

# create Atom
from matter.orm.Atom import Atom

db.createTable(Atom)
a1 = Atom()
a1.id = 'a1'
a1.lattice = l1

db.insertRow(a1)

print a1
print a1.lattice
print a1.lattice.dereference(db)
#H    0.000000 0.000000 0.000000 1.0000
#lattice###l1
#Lattice()

db.dropTable(Atom)
db.dropTable(Lattice)
db.destroySystemTables()

    


