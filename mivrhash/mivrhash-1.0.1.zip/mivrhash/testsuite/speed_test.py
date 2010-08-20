import random, time
if __name__ == '__main__':
    import os, sys
    sys.path.append( os.path.dirname( 
            os.path.dirname( os.path.abspath( __file__ ) ) ) )


from mivrhashclient import MivRHash


class MivRHashTest:
    def __init__( self ):
        self.m_h = MivRHash( "localhost", 10080, 2000 )

    def test_seq_insert( self ):
        print "Inserting 1000000 items ..."
        i = 0
        startTime = time.time()
        while i < 1000000:
            self.m_h[i] = i + 1
            i += 1
        finTime = time.time()
        elapsedTime = finTime - startTime
        print "Insert 1000000 items in %f [s]" % elapsedTime
        print "Hash size = %d" % len( self.m_h )
        
    def test_seq_access( self ):
        print "Accessing 1000000 items ..."
        i = 0
        startTime = time.time()
        while i < 1000000:
            j = self.m_h[i]
            if j != ( i + 1 ):
                raise Exception( "Invalid value at i = " % i )
            i += 1
        finTime = time.time()
        eTime = finTime - startTime
        print "Seq. accessed 1000000 items in %f [s]" % eTime

    def test_local_insert( self ):
        print "Local inserting 1000000 items ..."
        self.m_h.clear()
        i = 0
        startTime = time.time()
        while i < 1000000:
            k = i / 100000
            j = random.randint( k * 1000, k * 1000 + 999 )
            self.m_h[j] = j + 1
            i += 1
        finTime = time.time()
        eTime = finTime - startTime
        print "Local inserted 1000000 items in %f [s]" % eTime
        nSize = len( self.m_h )
        print "Hash size = %d" % nSize

    def test_local_access( self ):
        i = 0
        print "Local accessing 1000000 items ..."
        startTime = time.time()
        while i < 1000000:
            k = i / 100000
            j = random.randint( k * 1000, k * 1000 + 999 )
            if self.m_h.has_key( j ):
                if self.m_h[j] != ( j + 1 ):
                    raise Exception( "Invalid value at j = " % j )
            i += 1
        finTime = time.time()
        eTime = finTime - startTime
        print "Local accessed 1000000 items in %f [s]" % eTime
        
    def test_random_insert( self ):
        print "Random inserting 1000000 items ..."
        self.m_h.clear()
        i = 0
        startTime = time.time()
        while i < 1000000:
            # randomly insert with conflict keys
            j = random.randint( 0, 500000 )
            self.m_h[j] = j + 1
            i += 1
        finTime = time.time()
        eTime = finTime - startTime
        print "Random inserted 1000000 items in %f [s]" % eTime
        print "Hash size = %d" % len( self.m_h )

    def test_random_access( self ):
        print "Random accessing 1000000 items ..."
        i = 0
        startTime = time.time()
        while i < 1000000:
            j = random.randint( 0, 50000)
            if self.m_h.has_key( j ):
                if self.m_h[j] != ( j + 1 ):
                    raise Exception( "Invalid value at j = %d" % j )
            i += 1
            if i % 30000 == 0:
                print "i = %d" % i
        finTime = time.time()
        eTime = finTime - startTime
        print "Random accessed 1000000 items in %f [s]" % eTime

    def test_iterkeys( self ):
        print "Testing iterkeys"
        nCount = 0
        nSum = 0
        startTime = time.time()
        for i in self.m_h.iterkeys():
            nCount += 1
            nSum += i
            #assert( self.m_h[i] == ( i + 1 ) )
        finTime = time.time()
        eTime = finTime - startTime
        assert( nCount == 1000000 )
        assert( nSum == ( 1000000 / 2 ) * ( 1000000 - 1 ) )
        print "Iterkeys in %f [s]" % eTime

    def test_itervalues( self ):
        print "Testing itervalues"
        nCount = 0
        nSum = 0
        startTime = time.time()
        for i in self.m_h.itervalues():
            nCount += 1
            nSum += i
        finTime = time.time()
        eTime = finTime - startTime
        assert( nCount == 1000000 )
        assert( nSum == ( ( 1000000 / 2 ) * ( 1000000 + 1 ) ) )
        print "Itervalues in %f [s]" % eTime

    def test_iteritems( self ):
        print "Testing iteritems ..."
        nCount = 0
        nSum = 0
        startTime = time.time()
        for k, v in self.m_h.iteritems():
            nCount += 1
            nSum += k
            assert( v == ( k + 1 ) )
        finTime = time.time()
        eTime = finTime - startTime
        assert( nCount == 1000000 )
        assert( nSum == ( ( 1000000 / 2 ) * ( 1000000 - 1 ) ) )
        print "Iteritems in %f [s]" % eTime
        
    def run_test( self ):
        self.test_seq_insert()
        #self.test_seq_access()
        self.test_iterkeys()
        self.test_itervalues()
        self.test_iteritems()
        # self.test_local_insert()
        # self.test_local_access()
        # self.test_random_insert()
        # self.test_random_access()

if __name__ == '__main__':
    def speed_test_main():
        tCls = MivRHashTest()
        tCls.run_test()
        tCls.m_h = None

    speed_test_main()
