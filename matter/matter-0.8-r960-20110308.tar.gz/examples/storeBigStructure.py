from dsaw.db import connect
db = connect(db ='postgres:///test', echo = True)
db.autocommit(True)
from dsaw.model.visitors.OrmManager import OrmManager
orm = OrmManager(db)

from matter.Atom import Atom
from matter.Lattice import Lattice
from matter.orm.BigStructure import Structure

at1 = Atom('C', [0.333333333333333, 0.666666666666667, 0])
at2 = Atom('C', [0.666666666666667, 0.333333333333333, 0])
hexag = Lattice(2.456, 2.456, 6.696, 90, 90, 120)

graphite = Structure( [ at1, at2], lattice = hexag, sgid = 194)
graphite.id = 'graphite'
print graphite
#lattice=Lattice(a=2.456, b=2.456, c=6.696, alpha=90, beta=90, gamma=120)
#C    0.333333 0.666667 0.000000 1.0000
#C    0.666667 0.333333 0.000000 1.0000

from matter.expansion import supercell
graphite_sheet = supercell(graphite, (10,10,1))
graphite_sheet.id = 'sheet'
print graphite_sheet.getChemicalFormula()
#C200

orm.save(graphite_sheet)

#orm.destroyAllTables()
    



    


