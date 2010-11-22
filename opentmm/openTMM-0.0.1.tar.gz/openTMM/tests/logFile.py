import scipy as sp
import time
import pickle
import os
import os.path 

class LogFile:
    def __init__(self, filename=None):
        # Create file if no filename is given.  If filename is given, read and save content.
        if filename is None:
            ct = time.localtime(time.time())
            date = str(ct.tm_mon) + '-' + str(ct.tm_mday) + '-' + str(ct.tm_year)
            t = str(ct.tm_hour) + ':' + str(ct.tm_min) + ':' + str(ct.tm_sec)
        
            self.filename = 'openTMMlog--' + date + '--' + t + '.pkl'
            self.saveFile = False
        elif filename is not None:
            self.filename = filename
            self.saveFile = False
            self.data = self.read()
#---------------------------------------------------------------------------------------------------
    def write(self, data, saveFile=True):
        # Using binary mode
        output = open(self.filename, 'ab')
        pickle.dump(data, output, protocol=2)
        output.close()
        self.saveFile = saveFile
#---------------------------------------------------------------------------------------------------
    def read(self):
        f = open(self.filename, 'rb')
        d = {}; i = 0

        cond = True
        while cond:
            try:
                d[str(i)] = pickle.load(f)
                i += 1
            except EOFError:
                f.close()
                cond = False
        return d
#---------------------------------------------------------------------------------------------------
    def cleanUp(self):
        if not self.saveFile and os.path.isfile(self.filename):
            try:
                os.remove(self.filename)
            except OSError:
                print "Could NOT delete layerStack log file, " + self.filename
#---------------------------------------------------------------------------------------------------
    def minDataSet(self, layerStack, layerDict, data, testName, msg=None):

        def criticalAngles(epsRel, muRel):
            ixIdeal = layerStack._ixIdealLHM | layerStack._ixIdealRHM
            angles = sp.arcsin( sp.sqrt(epsRel[ixIdeal].real * muRel[ixIdeal].real / 
                                        (epsRel[-1].real * muRel[-1].real)) )
            angles *= 180.0/sp.pi
            ix = sp.isreal(angles)
            criticalAngles = angles[ix].real
            return sp.sort(criticalAngles)

        ls = layerStack
        dataSet = {'h':ls.h, 'pol':ls.pol, 'patholMethod':ls._patholMethod, 
                   'data':data, 'testName': testName}

        ld = layerDict
        epsRel = sp.ones(ld['epsilonRelative'].size + 2, complex)
        muRel = sp.ones(ld['muRelative'].size + 2, complex)
        epsRel[1:ld['epsilonRelative'].size+1] = ld['epsilonRelative']
        muRel[1:ld['muRelative'].size+1] = ld['muRelative']
        if ld.has_key('hostMedia'):
            epsRel[0] = ld['hostMedia']['epsilonRelative'][0]
            epsRel[-1] = ld['hostMedia']['epsilonRelative'][1]
            muRel[0] = ld['hostMedia']['muRelative'][0]
            muRel[-1] = ld['hostMedia']['muRelative'][1]

        dataSet['epsRel'] = epsRel
        dataSet['muRel'] = muRel


        dataSet['criticalPhi'] = criticalAngles(ls.epsRel, ls.muRel)
        dataSet['msg'] = msg
        return dataSet
#----------------------------------------------------------------------------------------------------
