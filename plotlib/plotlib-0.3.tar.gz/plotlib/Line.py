# -*- Python -*-
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                      California Institute of Technology
#                        (C) 2008  All Rights Reserved
#
# {LicenseText}
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

import os
from numpy import zeros
#from dsaw.model.Inventory import Inventory as InvBase

#hbar=6.57e-16*10e12*10e3#eV-s*ps/s*meV/eV 
THzToMeV=4.136
#E=hbar*omega

class Line:



    y = [0.0]
    x = [0.0]
    filePath = ''
    
    # dsaw model orm
    
#    class Inventory(InvBase):
#        dosList = InvBase.d.array(name='dosList', elementtype='float',shape=-1)
#        enList = InvBase.d.array(name='enList', elementtype='float',shape=-1)
#        dosFilePath = InvBase.d.str(name='dosFilePath', max_length=1024)
    
    def __init__(self, **kwds):
        for k, v in kwds.iteritems():
            setattr(self, k, v)
    
    def getXY(self):
        if len(self.y)==1:
            self.x, self.y = self.readLine()
        return self.x, self.y
    
    def readLine(self):
        path, extension = os.path.splitext(self.filePath)
        if extension is '.pkl':
            import pickle
            return pickle.load(file(self.filePath,'rb'))   
        elif extension in ['.plot']:
            fileObj = open(self.filePath)
            lines = fileObj.readlines()
            xList=[];yList=[]
            for line in lines:
                if line[0]=='#':
                    continue
                else:
                    x,y = map(float, line.split())
                    xList.append(x);yList.append(y)
            return xList, yList
        elif extension in ['.nc']:
            from Scientific.IO.NetCDF import NetCDFFile
            file = NetCDFFile(self.filePath, 'r')
            allDimNames = file.dimensions.keys() 
            print 'allDimNames', allDimNames
            vars = file.variables.keys()
            print 'vars', vars
            if 'sf' in vars:
                isf = file.variables['sf'].getValue() #numpy array
                q = file.variables['q'].getValue()
                time = file.variables['time'].getValue()
                #print time
                #sum over the q's
                isfQSum = zeros(time.shape[0])
                for qind in range(q.shape[0]):
                    isfQSum += isf[qind,:]
                return time, isfQSum
            elif 'dsf' in vars:
                dsf = file.variables['dsf'].getValue() #numpy array
                q = file.variables['q'].getValue()
                omega = file.variables['frequency'].getValue()
                #print omega
                #sum over the q's
                dsfQSum = zeros(omega.shape[0])
                for qind in range(q.shape[0]):
                    dsfQSum += dsf[qind,:]
                E = omega*THzToMeV
                return E, dsfQSum
            elif 'isf' in vars:
                isf = file.variables['isf'].getValue() #numpy array
                q = file.variables['q'].getValue()
                omega = file.variables['omega'].getValue()
                #print omega
                #sum over the q's
                isfQSum = zeros(omega.shape[0])
                for qind in range(q.shape[0]):
                    isfQSum += isf[qind,:]
                E = omega*THzToMeV
                return E, isfQSum
        elif extension in ['.xyz', '.his']:
            return 
        
    


# version
__id__ = "$Id$"

# End of file 
