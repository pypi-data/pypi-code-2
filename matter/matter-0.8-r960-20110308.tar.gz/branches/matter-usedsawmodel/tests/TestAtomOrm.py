



import sys,os
import unittest

sys.path.insert(0,os.path.abspath('..'))
print sys.path

from matter import Atom

class TestCase( unittest.TestCase ):
    

    def test_dsaworm(self):
        'Atom: dsaw orm'
        Fe57 = Atom( 'Fe', mass=57 )

        orm = self.orm
        Fe57record = orm(Fe57)
        
        orm.save(Fe57)

        Fe57_loaded = orm.load(Atom, Fe57record.id)

        props = ['symbol', 'label', 'occupancy']
        for prop in props:
            self.assertEqual(getattr(Fe57_loaded, prop), getattr(Fe57, prop))
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

