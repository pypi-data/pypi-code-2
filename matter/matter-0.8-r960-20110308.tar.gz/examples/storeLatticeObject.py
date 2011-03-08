from dsaw.db import connect
db = connect(db ='postgres:///test')
db.autocommit(True)
from dsaw.model.visitors.OrmManager import OrmManager
orm = OrmManager(db)

from matter.Lattice import Lattice
l1 = Lattice()
l1.id = 'l1'
orm.save(l1)

orm.destroyAllTables()
