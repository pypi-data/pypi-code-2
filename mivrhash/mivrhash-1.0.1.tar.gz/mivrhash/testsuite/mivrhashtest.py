import unittest, random
if __name__ == '__main__':
    import os, sys
    sys.path.append( os.path.dirname( 
            os.path.dirname( os.path.abspath( __file__ ) ) ) )

from mivrhashclient import MivRHash


class TestRHash( unittest.TestCase ):
    def setUp( self ):
        self.m_h = MivRHash( "localhost", 10080 )

    def tearDown( self ):
        self.m_h = None
    
    def test_insert( self ):
        i = 0
        while i < 10000:
            self.m_h[i] = i + 1
            i += 1
        i = 0
        while i < 10000:
            j = self.m_h[i]
            self.assertEqual( j, i + 1 )
            i += 1

    def test_delete( self ):
        i = 0
        while i < 10000:
            self.m_h[i] = random.random()
            i += 1
        print "Inserted 10000 entries"
        i = 0
        while i < 1000:
            self.assertTrue( self.m_h.has_key( i ) )
            del self.m_h[i]
            self.assertFalse( self.m_h.has_key( i ) )
            i += 1
            if i % 100 == 0:
                print "Deleted %d entries" % i 

    def test_clear( self ):
        i = 0
        while i < 10000:
            self.m_h[ random.random() ] = random.random()
            i += 1
        self.assertTrue( len( self.m_h ) > 0 )
        self.m_h.clear()
        self.assertEqual( len( self.m_h ),  0 )

    def test_random_access( self ):
        i = 0
        while i < 10000:
            self.m_h[i] = i + 1
            i += 1
        indexLst = range( 0, 10000 )
        random.shuffle( indexLst )
        count = 0
        for i in indexLst:
            count += 1
            self.assertEqual( self.m_h[i], ( i + 1 ) )
            if count % 1000 == 0:
                print "Accessed %d/10000 entries" % count

    def test_random_delete( self ):
        i = 0
        while i < 2500:
            self.m_h[i] = i + 1
            i += 1
        indexLst = range( 0, 2500 )
        random.shuffle( indexLst )
        count = 0
        for i in indexLst:
            count += 1
            self.assertTrue( self.m_h.has_key( i ) )
            del self.m_h[i]
            self.assertFalse( self.m_h.has_key( i ) )
            if count % 100 == 0:
                print "Deleted %d/2500 entries" % count

    def test_random_hash( self ):
        i = 0
        while i < 10000:
            self.m_h[i] = i + 1
            i += 1
        indexLst = range( 0, 10000 )
        random.shuffle( indexLst )
        for i in range( 0, 200 ):
            j = random.randint( 0, 9999 )
            # this is slightly different from dict: nothing raises!
            del self.m_h[j]
            self.assertFalse( self.m_h.has_key( j ) )
        for i in range( 0, 2000 ):
            j = random.randint( 0, 99999 )
            self.m_h[j] = j - 1
        i = 0
        while i < 10000:
            if self.m_h.has_key( i ):
                v = self.m_h[i]
                self.assertTrue( ( ( v == i + 1 ) or ( v == i - 1 ) ) )
            i += 1
            if i % 1000 == 0:
                print "Accessed %d/10000 entries" % i
        
if __name__ == '__main__':
    unittest.main()

        
    
