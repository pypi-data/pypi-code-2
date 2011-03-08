



import sys,os
import unittest

sys.path.insert(0,os.path.abspath('..'))

from matter import Lattice

class TestCase( unittest.TestCase ):
    

    def test_dsaworm(self):
        'Lattice: dsaw orm'
        lattice = Lattice(a=1,b=2,c=3,alpha=89,beta=91,gamma=92)

        orm = self.orm
        latticerecord = orm(lattice)
        
        orm.save(lattice)

        lattice_loaded = orm.load(Lattice, latticerecord.id)

        props = [d.name for d in Lattice.Inventory.getDescriptors()]
        for prop in props:
            self.assertEqual(getattr(lattice_loaded, prop), getattr(lattice, prop))
            continue
        return


    def setUp(self):
        self.orm = self._ormManager()
        self.orm2 = self._ormManager()


    def tearDown(self):
        del self.orm2
        
        db = self.orm.db
        db.destroyAllTables()
        return
        

    def _dbManager(self):
        from dsaw.db import connect
        db = connect(db ='postgres:///test')
        db.autocommit(True)
        return db


    def _ormManager(self):
        from dsaw.model.visitors.OrmManager import OrmManager
        return OrmManager(self._dbManager(), guid)



    pass # end of TestCase


# helpers
_id = 0
def guid():
    global _id
    _id += 1
    return str(_id)



#def main():
#    testsuite = unittest.makeSuite( TestCase )
#    unittest.TextTestRunner(verbosity=2).run(testsuite)
#    return 

if __name__ == "__main__": 
    unittest.main()

