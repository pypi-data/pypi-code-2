import sys
print sys.path

from dsaw.db import connect
db = connect(db ='postgres:///test', echo = True)
db.autocommit(True)

from matter.orm.Atom import Atom
from matter.orm.Lattice import Lattice
from matter.orm.Structure import Structure


tables = [
    Lattice,
    Atom,
    Structure
    ]
for table in tables:
    db.registerTable(table)

db.createAllTables()


at1 = Atom('C', [0.333333333333333, 0.666666666666667, 0])
at1.id = 'at1'
db.insertRow(at1)
db.commit()

at2 = Atom('C', [0.666666666666667, 0.333333333333333, 0])
at2.id = 'at2'
db.insertRow(at2)
db.commit()

hexag = Lattice(1, 1, 1, 90, 90, 120)
hexag.id = 'hexag'
db.insertRow(hexag)
db.commit()

graphite = Structure( [ at1, at2], lattice = hexag)
graphite.id = 'graphite'
db.insertRow(graphite)
db.commit()

graphite.atomStore.add(at1, db)
graphite.atomStore.add(at2, db)
    
db.destroyAllTables()
    



    


