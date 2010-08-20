"""
  The server side for Miv Remote Hash Table
  Usage: python mivrhashserver.py [nPort]
  Default port is 10080
  (C) 2010, Duc <duc at mi.ci.i.u-tokyo.ac.jp>
"""

import sys, os, socket, threading, thread, urllib, cPickle

class RsHashService:
    """
    Remote Hash service: listen to connection from clients and create hashes.

    Each client is served in a separated thread.
    """
    def __init__( self ):
        self.m_childrenList = {}
        self.m_childrenListLock = threading.Lock()
        pass
    def serve_client( self, conn, addr ):
        self.m_childrenListLock.acquire()
        self.m_childrenList[ thread.get_ident() ] = threading.currentThread()
        self.m_childrenListLock.release()
        print "Accepted: %s:%d" % addr
        fp = conn.makefile()
        fp.write( "RsHashService %d\n" % addr[1] )
        fp.flush()
        strLine = fp.readline().strip()
        if strLine != ( "RsHashClient %d" % addr[1] ):
            fp.write( "Invalid Protocol" )
            fp.flush()
            fp.close()
            conn.close()
        else:
            myHash = {}
            myIter = None  # iterator for the hash
            print "Created a new hash for %s:%d" % addr
            while True:
                strLine = fp.readline().strip()
                strLine = urllib.unquote( strLine )
                argLst = cPickle.loads( strLine )
                if len( argLst ) <= 0:
                    continue
                cmd = argLst[0]
                if ( cmd == 'get' ) or ( cmd == 'has_key' ):
                    if len( argLst ) <= 1:
                        continue
                    theKey = argLst[1]
                    if myHash.has_key( theKey ):
                        responseObj = ( True, myHash[theKey] )
                    else:
                        responseObj = ( False, None )
                    strResponse = cPickle.dumps( responseObj )
                    strResponse = urllib.quote( strResponse ) + "\n"
                    fp.write( strResponse )
                    fp.flush()
                elif cmd == 'put':
                    if len( argLst ) <= 2:
                        continue
                    theKey = argLst[1]
                    theVal = argLst[2]
                    myHash[theKey] = theVal
                elif cmd == 'batchput':
                    if len( argLst ) <= 1:
                        continue
                    putPairs = argLst[1]
                    for aPair in putPairs:
                        myHash[aPair[0]] = aPair[1]
                elif cmd == 'size':
                    strResponse = cPickle.dumps( len( myHash ) )
                    strResponse = urllib.quote( strResponse ) + "\n"
                    fp.write( strResponse )
                    fp.flush()
                elif cmd == 'init_iter':
                    if len( argLst ) <= 1:
                        continue
                    iterSubject = argLst[1]
                    if iterSubject == 'keys':
                        myIter = myHash.iterkeys()
                    elif iterSubject == 'values':
                        myIter = myHash.itervalues()
                    elif iterSubject == 'items':
                        myIter = myHash.iteritems()
                elif cmd == 'iter':
                    if len( argLst ) <= 1:
                        continue
                    chunkLen = argLst[1]
                    nIterCount = 0
                    retLst = []
                    bStopIter = False
                    while nIterCount < chunkLen:
                        try:
                            theItem = myIter.next()
                            retLst.append( theItem )
                            nIterCount += 1
                        except StopIteration:
                            bStopIter = True
                            myIter = None
                            break
                    retObj = ( bStopIter, retLst )
                    strResponse = cPickle.dumps( retObj )
                    strResponse = urllib.quote( strResponse ) + "\n"
                    fp.write( strResponse )
                    fp.flush()
                elif cmd == 'clear':
                    myHash = {}
                elif cmd == 'del':
                    if len( argLst ) <= 1:
                        continue
                    theKey = argLst[1]
                    if myHash.has_key( theKey ):
                        del myHash[theKey]
                elif cmd == 'close':
                    myHash = None
                    fp.close()
                    break
        conn.close()
        self.m_childrenListLock.acquire()
        if self.m_childrenList.has_key( thread.get_ident() ):
            del self.m_childrenList[ thread.get_ident() ]
        self.m_childrenListLock.release()
        print "%s:%d disconnected" % addr
        
    def start( self, port ):
        """
        Start listen on port port.
        """
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        s.bind( ( '', port ) )
        s.listen( 5 )
        print "Server listening on port %d" % port
        while True:
            conn, addr = s.accept()
            newTh = threading.Thread( group = None, target = self.serve_client,
                                      name = None,
                                      args = ( conn, addr ),
                                      kwargs = {} )
            newTh.start()

    def start_service( self, port = 10080 ):
        try:
            self.start( port )
        except KeyboardInterrupt:
            # wait for all children to exit
            self.m_childrenListLock.acquire()
            for aTh in self.m_childrenList.itervalues():
                try:
                    aTh.join()
                except:
                    pass
            self.m_childrenListLock.release()
        print "Server terminated"

if __name__ == "__main__":
    def rs_hash_main():
        if len( sys.argv ) > 1:
            try:
                nPort = int( sys.argv[1] )
            except:
                print "Usage: python mivrhashservice.py [nPort]"
                print "Default port number is 10080"
                return
        else:
            nPort = 10080
        svr = RsHashService()
        svr.start_service( nPort )
    # invoke the main
    rs_hash_main()

            
    
            
