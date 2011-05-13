import struct
import sys

import Numeric


# Class for loading mfccfiles in the C_SDK format. Supports byteswapping.
# Questions: Tor Andre Myrvoll, myrvoll@research.bell-labs.com

class MFCCFile:
    # This class loads a mfcc file in LASR format and gives access to
    # mfcc vectors indexed by file and position
    def __init__(self,filename,DEBUG = 0,BYTEORDER='@'):
        self.DEBUG = DEBUG
        self.BYTEORDER = BYTEORDER
        self.FileName = filename
        long_s = 4
        float_s = 4 

        # See if we should byteswap
        if not struct.pack('%sL' % (self.BYTEORDER),1) == struct.pack('L',1):
            BYTESWAP = 1
        else:
            BYTESWAP = 0

        fp = open(filename,'r')
        if DEBUG:
            sys.stderr.write("Opening file %s\n" % (filename))
            


        # Store the number of sentences in this file
        str = fp.read(long_s)
        self.numSent = struct.unpack('%sL' % (self.BYTEORDER),str)[0]
        if DEBUG:
            sys.stderr.write("    Number of sentences: %d\n" % (self.numSent))

        # Store the feature vector dimension
        str = fp.read(long_s)
        self.vecSize = struct.unpack('%sL' % (self.BYTEORDER),str)[0]
        if DEBUG:
            sys.stderr.write("    Vector size: %d\n" % (self.vecSize))
            

        # Load an array of sentence lengths into a list
        self.sentLength = []
        for sent in range(self.numSent):
            str = fp.read(long_s)
            length = struct.unpack('%sL' % (self.BYTEORDER),str)[0]
            self.sentLength.append(length)
        if DEBUG:
            sys.stderr.write("\n")
            

        # Now load the entire file and store the vectors in lists
        self.sentList = []
        sentnum = 0
        index = 0
        veclength = self.vecSize*float_s
        if DEBUG:
            sys.stderr.write("    Loading sentences:")
            

        str = fp.read()
        for sent in range(self.numSent):
            if DEBUG:
                sys.stderr.write(" %d" % (sent))
            sentdata = []
            for vec in range(self.sentLength[sent]):
                mfccvec = Numeric.fromstring(str[index:index+veclength],'f')
                if BYTESWAP:
                    mfccvec = mfccvec.byteswapped()
                sentdata.append(mfccvec)
                index += veclength
                
            self.sentList.append(sentdata)

        # We're done. Close the file
        fp.close()
        if DEBUG:
            sys.stderr.write("\n")

    def Save(self,filename):
        fh = open(filename,'w')
        # First we write the header
        str = struct.pack('LL',self.numSent,self.vecSize)
        fh.write(str)

        # Now the array of sentence lengths
        for length in self.sentLength:
            str = struct.pack('L',length)
            fh.write(str)

        # Finally, we save the cepstral vectors themselves
        for utt in self.sentList:
            for vec in utt:
                str = vec.tostring()
                fh.write(str)

        fh.close()
            
    def ReturnSent(self,sentnum):
        # Returns a list containing the entire sentence
        return self.sentList[sentnum]
    

    def ReturnVector(self,sentnum,vecnum):
        # Returns vector i of utterance j
        return self.sentList[sentnum][vecnum]
    
