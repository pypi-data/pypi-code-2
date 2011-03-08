



import sys,os
import unittest

sys.path.insert(0,os.path.abspath('..'))

from matter import Structure, Atom, Lattice

class TestCase( unittest.TestCase ):
    

    def test_dsaworm(self):
        'Structure: dsaw orm'
        Fe57 = Atom( 'Fe', mass=57 )
        Al = Atom( 'Al' )
        atoms = [Fe57, Al]
        
        lattice = Lattice(a=1,b=2,c=3,alpha=89,beta=91,gamma=92)

        struct = Structure(atoms=atoms, lattice=lattice)

        orm = self.orm
        structrecord = orm(struct)
        
        orm.save(struct)

        struct_loaded = orm.load(Structure, structrecord.id)

        props = ['sg', 'description']
        for prop in props:
            self.assertEqual(getattr(struct_loaded, prop), getattr(struct, prop))
            continue

        props = ['a','b','c', 'alpha', 'beta', 'gamma']
        for prop in props:
            self.assertEqual(getattr(struct_loaded.lattice, prop), getattr(struct.lattice, prop))
            continue

        self.assertEqual( len(struct_loaded), 2 )
        for atom in struct_loaded:
            self.assertEqual(atom.__class__, Atom)
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

