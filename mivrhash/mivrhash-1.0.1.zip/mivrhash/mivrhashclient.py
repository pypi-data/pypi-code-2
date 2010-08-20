"""
  The client side for Miv Remote Hash Table.
  Usage:
    rHash = MivRHash( "server_address", nPort )
    rHash[key] = value
    (all functions are similar to Python dict)
  (C) 2010 by Duc <duc at mi.ci.i.u-tokyo.ac.jp>
"""

import sys, os, socket, traceback, exceptions, urllib, cPickle
from operator import itemgetter

class RsHashClient:
    def __init__( self ):
        self.m_connected = False
        pass
    def connect( self, strHost, nPort ):
        """
        Connect to the server and create a new hash on it.
        """
        try:
            self.m_sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.m_sock.connect( ( strHost, nPort ) )
            self.m_fp = self.m_sock.makefile()
            strAck = self.m_fp.readline()
            strAck = strAck.replace( "RsHashService", "RsHashClient" )
            self.m_fp.write( strAck )
            self.m_fp.flush()
        except Exception:
            traceback.print_exc()
            return False
        self.m_connected = True
        return True

    def put( self, theKey, theVal ):
        if not self.m_connected:
            raise exceptions.IOError( 'Put', 'RsHashClient not connected' )
        objToSend = ( 'put', theKey, theVal )
        strToSend = cPickle.dumps( objToSend )
        strToSend = urllib.quote( strToSend ) + "\n"
        self.m_fp.write( strToSend )
        self.m_fp.flush()
        # self.m_fp.readline()

    def batch_put( self, pairLst ):
        """
        Put many (key, value) pair to the remote server.
        
        This is for reducing the time for write_back.
        """
        if not self.m_connected:
            raise exceptions.IOError( 'BatchPut', 'RsHashClient not connected' )
        objToSend = ( 'batchput', pairLst )
        strToSend = cPickle.dumps( objToSend )
        strToSend = urllib.quote( strToSend ) + "\n"
        self.m_fp.write( strToSend )
        self.m_fp.flush()
        
    def get( self, theKey ):
        if not self.m_connected:
            raise exceptions.IOError( 'Get', 'RsHashClient not connected' )
        objToSend = ( 'get', theKey )
        strToSend = cPickle.dumps( objToSend )
        strToSend = urllib.quote( strToSend ) + "\n"
        self.m_fp.write( strToSend )
        self.m_fp.flush()
        strRet = self.m_fp.readline().strip()
        objRecv = cPickle.loads( urllib.unquote( strRet ) )
        if not objRecv[0]:
            raise exceptions.KeyError( 'RsHashGet', theKey )
        theVal = objRecv[1]
        return theVal

    def get_size( self ):
        if not self.m_connected:
            raise exceptions.IOError( 'Size', 'RsHashClient not connected' )
        objToSend = ( 'size', )
        strToSend = cPickle.dumps( objToSend )
        strToSend = urllib.quote( strToSend ) + "\n"
        self.m_fp.write( strToSend )
        self.m_fp.flush()
        strRet = self.m_fp.readline().strip()
        objRecv = cPickle.loads( urllib.unquote( strRet ) )
        return objRecv
    
    def remove( self, theKey ):
        """
        Remove theKey from this hash.
        """
        if not self.m_connected:
            raise exceptions.IOError( 'Remove', "RsHashClient not connected" )
        objToSend = ( 'del', theKey )
        strToSend = cPickle.dumps( objToSend )
        strToSend = urllib.quote( strToSend ) + "\n"
        self.m_fp.write( strToSend )
        self.m_fp.flush()

    def clear( self ):
        """
        Clear all data in the hash.
        """
        if not self.m_connected:
            raise exceptions.IOError( 'Remove', "RsHashClient not connected" )
        objToSend = ( 'clear', )
        strToSend = cPickle.dumps( objToSend )
        strToSend = urllib.quote( strToSend ) + "\n"
        self.m_fp.write( strToSend )
        self.m_fp.flush()

    def get_iter( self, subj ):
        """
        Start an iterator on remote server.

        Many get_iter_chunk can be called after this call.
        """
        if not self.m_connected:
            raise exceptions.IOError( 'GetIter', 'RsHashClient not connected' )
        objToSend = ( 'init_iter', subj )
        strToSend = cPickle.dumps( objToSend )
        strToSend = urllib.quote( strToSend ) + "\n"
        self.m_fp.write( strToSend )
        self.m_fp.flush()
        self.m_bInIter = True

    def get_iter_chunk( self, nMaxLen ):
        """
        Get the next chunk of data for iterating the hash.
        """
        # a get_iter must be called before this
        objToSend = ( 'iter', nMaxLen )
        strToSend = cPickle.dumps( objToSend )
        strToSend = urllib.quote( strToSend ) + "\n"
        self.m_fp.write( strToSend )
        self.m_fp.flush()
        strRet = self.m_fp.readline().strip()
        objRecv = cPickle.loads( urllib.unquote( strRet ) )
        return objRecv
    
    def close( self ):
        """
        Free memory and close the connection to remote server.
        """
        if self.m_connected:
            objToSend = ( 'close', )
            strToSend = cPickle.dumps( objToSend )
            strToSend = urllib.quote( strToSend ) + "\n"
            self.m_fp.write( strToSend )
            self.m_fp.flush()
            self.m_fp.close()
            self.m_sock.close()
            self.m_connected = False
            
    def __del__( self ):
        if self.m_connected:
            import cPickle, urllib
            objToSend = ( 'close', )
            strToSend = cPickle.dumps( objToSend )
            strToSend = urllib.quote( strToSend ) + "\n"
            self.m_fp.write( strToSend )
            self.m_fp.flush()
            self.m_fp.close()
            self.m_sock.close()
            self.m_connected = False
    

class MivRHashIter:
    """
    Iterator for MivRHash
    """
    def __init__( self, iterType, theHash ):
        self.m_iterType = iterType
        self.m_nCacheStartIndex = -1
        self.m_nStartIndex = 0
        self.m_cachedItems = None
        self.m_h = theHash
        self.m_bWillStop = False

    def __iter__( self ):
        return self

    def next( self ):
        iterType = self.m_iterType
        if self.m_iterType != 'values':
            iterType = 'items'
        if self.m_nCacheStartIndex < 0:
            self.m_h.m_rsHashClient.get_iter( iterType )
        if ( not self.m_cachedItems ) or (
            ( self.m_nCacheStartIndex + len( self.m_cachedItems
                                             ) <= self.m_nStartIndex ) and (
                 not self.m_bWillStop
               ) ):
            retObj = self.m_h.m_rsHashClient.get_iter_chunk(
                self.m_h.m_nCacheSize / 2 )
            self.m_cachedItems = retObj[1]
            self.m_bWillStop = retObj[0]
            self.m_nCacheStartIndex = self.m_nStartIndex
            if iterType == 'items':
                self.m_h.batch_set_item( self.m_cachedItems )
        if self.m_nStartIndex >= self.m_nCacheStartIndex + len( self.m_cachedItems ):
            raise StopIteration()
        theIndex = self.m_nStartIndex - self.m_nCacheStartIndex
        self.m_nStartIndex += 1
        if self.m_iterType == 'keys':
            return self.m_cachedItems[theIndex][0]
        else:
            return self.m_cachedItems[theIndex]
        
                 
        
class MivRHash:
    """
    Remote hash table, provide the same interface with the Python dict
    
    The actual data of the hash table may be stored in a remote host
    """
    def __init__( self, strHost, nPort, nCacheSize = 1000 ):
        """
        Create a new MivRHash, store data on host strHost
        """
        self.m_nCacheSize = nCacheSize
        self.m_cachedItems = {}
        self.m_nMaxCacheId = 0
        # cacheUpdateTime update threshold: history is saved in 28 bits
        self.m_nCacheUpdateThreshold = self.m_nCacheSize / 28
        # bit index starts from 0
        # bit 30: Not put yet, bit 29: Dirty, bit 28: Reference 
        # bit 27-0: reference history
        self.m_cacheUpdateTime = {}
        self.m_rsHashClient = RsHashClient()
        self.m_rsHashClient.connect( strHost, nPort )

    def update_cache_info( self ):
        # update the cacheUpdateTime table by aging the bits
        for cacheId in self.m_cacheUpdateTime.iterkeys():
            theTime = self.m_cacheUpdateTime[cacheId]
            nU = ( theTime & 0x0FFFFFFF )  # least 28 bits
            nRD = ( ( theTime >> 28 ) & 0x01 )  # Reference bit
            nU = ( ( nU >> 1 ) | ( nRD << 27 ) )  # new value for nU
            theTime = ( ( theTime & 0x60000000 ) | nU )
            self.m_cacheUpdateTime[cacheId] = theTime
        self.m_nCacheUpdateThreshold = self.m_nCacheSize / 28

    def insert_item( self, theKey, theVal, bDirty ):
        # insert an item into the cache
        if self.m_nMaxCacheId >= ( 1 << 30 ):
            self.refresh_cache_id()
        self.m_nMaxCacheId += 1
        cacheId = self.m_nMaxCacheId
        self.m_cachedItems[theKey] = ( cacheId, theVal )
        theTime = ( 1 << 28 )
        if bDirty:
            # set the NotPut bit and the Dirty bit
            theTime |= ( ( 1 << 30 ) | ( 1 << 29 ) )
        self.m_cacheUpdateTime[cacheId] = theTime
        
    def do_write_back( self ):
        # write dirty items back to the server
        pairList = []
        for theKey, thePair in self.m_cachedItems.iteritems():
            cacheId, theVal = thePair
            theTime = self.m_cacheUpdateTime[cacheId]
            if ( ( theTime >> 29 ) & 0x01 ) > 0:  # if dirty
                # self.m_rsHashClient.put( theKey, theVal )
                pairList.append( ( theKey, theVal ) )
                # clear the NotPut bit and Dirty bit
                theTime &= 0x1FFFFFFF
                self.m_cacheUpdateTime[cacheId] = theTime
        self.m_rsHashClient.batch_put( pairList )
        
    def do_swap_out( self ):
        # swap out the LRU (NRU) items
        self.do_write_back()
        sortedCacheIdList = sorted( self.m_cacheUpdateTime.items(),
                                    key = itemgetter( 1 ) )
        nToSwapOut = len( sortedCacheIdList ) / 2
        swapOutSet = set()
        for itm in sortedCacheIdList:
            cacheId, theTime = itm
            swapOutSet.add( cacheId )
            nToSwapOut -= 1
            if nToSwapOut <= 0:
                break
        swapOutKeySet = set()
        for theKey, thePair in self.m_cachedItems.iteritems():
            cacheId, theVal = thePair
            if cacheId in swapOutSet:
                swapOutKeySet.add( theKey )
                del self.m_cacheUpdateTime[cacheId]
        for theKey in swapOutKeySet:
            del self.m_cachedItems[theKey]
                
    def refresh_cache_id( self ):
        # refresh the cache id when the nMaxCacheId becomes too large.
        newCacheId = 0
        newCacheItems = {}
        newCacheUpdateTime = {}
        for theKey, thePair in self.m_cachedItems.itervalues():
            newCacheId += 1
            cacheId, theVal = thePair
            newCacheItems[theKey] = (newCacheId, theVal)
            newCacheUpdateTime[newCacheId] = self.m_cacheUpdateTime[cacheId]
        self.m_cachedItems = newCacheItems
        self.m_cacheUpdateTime = newCacheUpdateTime
        self.m_nMaxCacheId = newCacheId
        
    def __getitem__( self, theKey ):
        theVal = None
        if self.m_cachedItems.has_key( theKey ):
            self.m_nCacheUpdateThreshold -= 1
            cacheId, theVal = self.m_cachedItems[theKey]
            # update the UpdateTime
            theTime = self.m_cacheUpdateTime[cacheId]
            # bit 28 of theTime is the Reference bit
            theTime |= ( 1 << 28 )
            self.m_cacheUpdateTime[cacheId] = theTime
            if self.m_nCacheUpdateThreshold < 0:
                # update the cacheUpdateTime
                self.update_cache_info()
        else:  # cache miss
            # get the remote value
            theVal = self.m_rsHashClient.get( theKey )
            # check if we need to swap out
            if len( self.m_cachedItems ) >= self.m_nCacheSize:
                # write back and swap out
                self.do_swap_out()
            self.insert_item( theKey, theVal, False )
        return theVal

    def __setitem__( self, theKey, theVal ):
        if self.m_cachedItems.has_key( theKey ):
            cacheId, cacheVal = self.m_cachedItems[theKey]
            self.m_cachedItems[theKey] = ( cacheId, theVal )
            cacheVal = None
            theTime = self.m_cacheUpdateTime[cacheId]
            theTime |= ( 1 << 29 )  # update the Dirty bit
            theTime |= ( 1 << 28 )  # and the Reference bit
            self.m_cacheUpdateTime[cacheId] = theTime
            self.m_nCacheUpdateThreshold -= 1
        else: # the item is not in cache
            # swap out if need
            if len( self.m_cachedItems ) >= self.m_nCacheSize:
                self.do_swap_out()
            # insert it into the cache
            self.insert_item( theKey, theVal, True )

    def batch_set_item( self, itmList ):
        # this is for iterkeys and iteritems in iterator
        # When iterkeys is called, we also get the item itself because
        # there is a high probility that h[key] will be accessed
        for anItem in itmList:
            self.__setitem__( anItem[0], anItem[1] )
        
    def __delitem__( self, theKey ):
        bLocalItem = False
        if self.m_cachedItems.has_key( theKey ):
            cacheId, theVal = self.m_cachedItems[theKey]
            theTime = self.m_cacheUpdateTime[cacheId]
            bLocalItem = ( theTime & 0x40000000 ) 
            del self.m_cacheUpdateTime[cacheId]
            del self.m_cachedItems[theKey]
        if not bLocalItem:
            self.m_rsHashClient.remove( theKey )

    def has_key( self, theKey ):
        """
        Check if theKey is in this hash.

        Similar to dict.has_key
        """
        if self.m_cachedItems.has_key( theKey ):
            cacheId, theVal = self.m_cachedItems[theKey]
            theTime = self.m_cacheUpdateTime[cacheId]
            theTime |= ( 1 << 28 )
            self.m_cacheUpdateTime[cacheId] = theTime
            self.m_nCacheUpdateThreshold -= 1
            return True
        else:
            try:
                itm = self.__getitem__( theKey )
            except KeyError:
                return False
        return True

    def __len__( self ):
        remoteSize = self.m_rsHashClient.get_size()
        localSize = 0
        for aTime in self.m_cacheUpdateTime.itervalues():
            if (  aTime & 0x40000000  ):
                localSize += 1
        return ( remoteSize + localSize )

    def clear( self ):
        """
        Clear the hash.
        
        Similar to dict.clear()
        """
        self.m_rsHashClient.clear()
        self.m_cachedItems.clear()
        self.m_cacheUpdateTime.clear()
        self.m_nMaxCacheId = 0
        self.m_nCacheUpdateThreshold = self.m_nCacheSize / 28

    def iterkeys( self ):
        """
        Return the key iterator. This requires only a small amount of memory.

        The iterator is optimized with cache.
        """
        self.do_write_back()
        return MivRHashIter( 'keys', self )
    
    def itervalues( self ):
        """
        Return the value iterator. This requires only a small amount of memory.

        The iterator is optimized with cache.
        """
        self.do_write_back()
        return MivRHashIter( 'values', self )

    def iteritems( self ):
        """
        Return the item iterator. This requires only a small amount of memory.

        The iterator is optimized with cache.
        """
        self.do_write_back()
        return MivRHashIter( 'items', self )

    def __iter__( self ):
        self.do_write_back()
        return MivRHashIter( 'keys', self )

    def close( self ):
        """
        Free all memory on remote host and close the connection.
        """
        self.m_rsHashClient.close()

if __name__ == "__main__":
    print "MivRHash client testing ..."
    def rshashclient_main():
        hClient = RsHashClient()
        hClient.connect( "localhost", 10080 )
        i = 0
        while i < 1000000:
            hClient.put( i , i + 1 )
            if i % 10000 == 0:
                print i
            i += 1
        i = 0
        while i < 1000000:
            j = hClient.get( i )
            if i % 10000 == 0:
                print i
            if j != ( i + 1 ):
                raise Exception( "RsHashClient", "Invalid value", i )
            i += 1
        hClient = None
    rshashclient_main()
