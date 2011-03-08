import numpy as np
from Scientific.IO.NetCDF import NetCDFFile

class NcPlottable(object):
    """Wrapper to matplotlib that allows us to plot analysis functions (which are 
    usually netcdf format.
    """
    def __init__(self, netcdfFile=None, sqe=None, base='pyplot', engineInstance=None, 
                 **kwds):
        # assign engine
        global engine
        if engineInstance:
            engine = engineInstance
        elif base=='pyplot':
            from matplotlib import pyplot
            engine = pyplot
        elif base=='mlab':
            from enthought.mayavi import mlab
            engine = mlab
        #default attributes
        self.removeElasticLine = True
        self.elasticLineRows=1
        #matplotlib/mlab attributes
        for key,val in kwds.iteritems():
            setattr(self, key, val)
        if not self.removeElasticLine:
            self.elasticLineRows=0
        if netcdfFile!=None:
            self.processNcFile(netcdfFile)
        elif sqe!=None:
            self.processSqe(sqe)
        self.plotTypes= {'image':False, 'plotAll':False,
            'plotImage':False, 'plotImageCompare':False, 'pyplotSurface':False,
            'plotScatter':False, 'points3d':False, 
            'sumQs':False, 'surface':False, 'surfaceX':False}
            
    def processNcFile(self, netcdfFile):
        file = NetCDFFile(netcdfFile, 'r')
        allDimNames = file.dimensions.keys() 
        #print 'allDimNames', allDimNames
        self.vars = file.variables.keys()
        if file.variables.has_key('q'): #the file has grid data
            self.fileType = 'grid'
            self.q = file.variables['q'].getValue()[self.elasticLineRows:]
            #print 'q',self.q
            #print 'vars', self.vars
            if file.variables.has_key('dsf'):
                self.scatFunc = file.variables['dsf'].getValue()[self.elasticLineRows:, self.elasticLineRows:] # remove the elastic peak # do i really need to remove 0 energy?
            elif file.variables.has_key('sf'):
                self.scatFunc = file.variables['sf'].getValue()[self.elasticLineRows:, self.elasticLineRows:] # remove the elastic peak
            #print self.scatFunc
            #assume all files have the same data types, so overwrite each time
            if file.variables.has_key('energy'):
                self.yAxisType = 'energy'
                self.yAxis = file.variables['energy'].getValue()[self.elasticLineRows:] # remove the elastic peak
                self.yLabel = "E (meV)"
                self.sfLabel = "S(Q,E)"
            elif file.variables.has_key('frequency'):
                self.yAxisType = 'frequency'
                self.yAxis = file.variables['frequency'].getValue()[self.elasticLineRows:] # remove the elastic peak
                self.yLabel = "frequency (1/ps)"
                self.sfLabel = "S(Q,f)"
            elif file.variables.has_key('time'):
                self.yAxisType = 'time'
                self.yAxis = file.variables['time'].getValue()[self.elasticLineRows:] # remove the elastic peak
                self.yLabel = "time (ps)"
                self.sfLabel = "F(Q,t)"
            #print 'yAxis',self.yAxis
        if file.variables.has_key('points'): #the file has point data
            self.fileType = 'points'
            self.points = np.transpose(file.variables['points'].getValue())
            np.set_printoptions(threshold=100000)
#            for dim in self.points:
#                print dim
            self.yLabel = "E (meV)"
            self.sfLabel = "S(Q,E)"
        
    def processSqe(self, sqe):
        self.scatFunc = sqe.sqe
        self.q = sqe.q
        self.yAxisType = 'energy'
        self.yAxis = sqe.e
        self.yLabel = "E (meV)"
        self.sfLabel = "S(Q,E)"
        self.fileType='grid'
            
    def sumQs(self):
        return [self.yAxis, np.add.reduce(self.scatFunc)]
            
    def createPoints(self):
        if self.fileType=='grid':
            dims = self.scatFunc.shape
            numPoints = dims[0]*dims[1]
            xs = np.zeros(numPoints)
            ys = np.zeros(numPoints)
            zs = np.zeros(numPoints)
            ind=0
            for i in range(dims[0]):#q
                for j in range(dims[1]):#energy, frequency
                    xs[ind] = self.q[i]
                    ys[ind] = self.yAxis[j]
                    zs[ind] = self.scatFunc[i,j]
                    ind += 1
            self.points = (xs,ys,zs)             
            return self.points
        elif self.fileType=='points':
            return self.points
        
    def __setattr__(self, attr, value):
        if hasattr(engine, attr):
            setattr(engine, attr, value)
        else:
            object.__setattr__(self, attr, value)

    def __getattr__(self, attr):
        if hasattr(engine, attr):
            return getattr(engine, attr)
        else:
            return object.__getattr__(self, attr)
        
    def plotType(self, **kwds):
        """need to pop general keywords here (with defaults in constructor) and
        pass rest to plotting function below"""
        defaults = {'figName':None,}
        for key,val in defaults.iteritems():
            setattr(self, key, val)
        plotKwds={}
        for key,val in kwds.iteritems():
            if defaults.has_key(key):
                setattr(self, key, val) #a general attribute
            elif self.plotTypes.has_key(key):
                self.plotTypes[key] = val # a plotting type keyword
            else:
                plotKwds[key] = val # a plotting keyword
        #create plot
        if self.plotTypes['sumQs']:
            #sum over the q's
            scatFuncData = self.sumQs()
            self.plot(*scatFuncData,**plotKwds)
            #self.axis([0, 60, 0, 0.001])
            #legend(('2.5 K','10 K','15 K','17.5 K','20 K','25 K','30 K','35 K','45 K','70 K','90 K'))
            self.xlabel('E (meV)')
            self.ylabel('S(E) (arbitrary units)')
        elif self.plotTypes['plotImage']:
            qGrid, yAxisGrid = np.meshgrid(self.q, self.yAxis)
            self.figure(1)
            #self.subplot(121)
            self.pcolor(qGrid, yAxisGrid, self.scatFunc.transpose(), 
                            vmin=0.0, vmax=0.01,**plotKwds)
            self.colorbar()
            self.title(self.sfLabel)
            self.xlabel("Q (1/Ang)")
            self.ylabel(self.yLabel)
        elif self.plotTypes['image']:
            #from scipy.interpolate import griddata
            from plotlib.types import image
            image(self, plotKwds=plotKwds)
        elif self.plotTypes['plotImageCompare']:
            from scipy import interpolate
            qGrid, yAxisGrid = np.meshgrid(self.q, self.yAxis)
            self.figure(1)
            self.subplot(221)
            self.pcolor(qGrid, yAxisGrid, self.scatFunc.transpose(),**plotKwds)
            self.colorbar()
            self.title(self.sfLabel)
            self.xlabel("Q (1/Ang)")
            self.ylabel(self.yLabel)
            self.subplot(222)
            self.pcolor(qGrid[1:,1:], yAxisGrid[1:,1:], 
                            self.scatFunc[1:,1:].transpose(), **plotKwds)
            self.colorbar()
            self.title(self.sfLabel)
            self.xlabel("Q (1/Ang)")
            self.ylabel(self.yLabel)
            def evenSpacing(q,numPoints=len(self.q)):
                return np.arange(q[0],q[-1],(q[-1]-q[0])/numPoints)
            #with elastic peaks
    #        qInterp,yAxisInterp = np.meshgrid(evenSpacextent=(0 ,10 , 0 ,10 , 0 ,10)ing(q), evenSpacing(yAxis))
    #        tck = interpolate.bisplrep(qGrid, yAxisGrid, scatFunc.transpose(), s=0)
    #        scatFuncInterp = interpolate.bisplev(qInterp[:,0],yAxisInterp[0,:],tck)
    #        #self.figure(1)
    #        self.subplot(223)
    #        self.pcolor(qInterp,yAxisInterp,scatFuncInterp)
    #        self.colorbar()
    #        self.title(sfLabel)
    #        self.xlabel("Q (1/Ang)")
    #        self.ylabel(yLabel)
            #without elastic peaks
            qInterp,yAxisInterp = np.meshgrid(evenSpacing(self.q[1:], numPoints=len(self.q[1:])), 
                                           evenSpacing(self.yAxis[1:], numPoints=len(self.yAxis[1:])))
            #fitpack
            m = len(qGrid[1:,1:].flatten())
            smoothing = m - np.sqrt(m)
            tck = interpolate.bisplrep(qGrid[1:,1:].flatten(), yAxisGrid[1:,1:].flatten(), 
                                       self.scatFunc[1:,1:].T.flatten(), s=0)#smoothing)
            scatFuncInterp = interpolate.bisplev(qInterp[0,:], yAxisInterp[:,0], tck)
            #print 'scatFuncInterp',scatFuncInterp
            #other way
            from scipy.interpolate.fitpack2 import LSQBivariateSpline, SmoothBivariateSpline
            spline = SmoothBivariateSpline(qGrid[1:,1:].flatten(), yAxisGrid[1:,1:].flatten(), 
                                       self.scatFunc[1:,1:].T.flatten())
            #splineArray = spline(qInterp.flatten(),yAxisInterp.flatten())#.reshape(len(q),len(yAxis))
            splineArray=np.zeros(qInterp.shape)
            splineArray=np.zeros((len(qInterp[0,:]),len(yAxisInterp[:,0])))
            for i,qVal in enumerate(qInterp[0,:]):
                for j,yVal in enumerate(yAxisInterp[:,0]):
                    #val = spline(qVal,yVal)
                    splineArray[i,j] = spline(qVal,yVal)#val
                    
            #splineArray = spline(qInterp,yAxisInterp)
            self.subplot(223)
            self.pcolor(qInterp, yAxisInterp, splineArray.T)
            #self.imshow(scatFuncInterp.T, cmap=cm.jet, interpolation='bilinear')
            self.colorbar()
            self.title(self.sfLabel)
            self.xlabel("Q (1/Ang)")
            self.ylabel(self.yLabel)       
            
            #self.figure(1)
            self.subplot(224)
            self.pcolor(qInterp,yAxisInterp,scatFuncInterp.transpose())
            #self.imshow(scatFuncInterp.T, cmap=cm.jet, interpolation='bilinear')
            self.colorbar()
            self.title(self.sfLabel)
            self.xlabel("Q (1/Ang)")
            self.ylabel(self.yLabel)            
            # first take all the data and interpolate since x and y spacing will be uneven
            #interpolate.interp2d(q, yAxis, scatFunc, kind='bilinear')
        elif self.plotTypes['plotScatter']:
            from mpl_toolkits.mplot3d import Axes3D
            #create the plotting data structures
            dims = self.scatFunc.shape
            numPoints = dims[0]*dims[1]
            xs = np.zeros(numPoints)
            ys = np.zeros(numPoints)
            zs = np.zeros(numPoints)
            ind=0
            for i in range(dims[0]):#q
                for j in range(dims[1]):#energy, frequency
                    xs[ind] = self.q[i]
                    ys[ind] = self.yAxis[j]
                    zs[ind] = self.scatFunc[i,j]
                    ind += 1
            # use the engine
            fig = self.figure()
            ax = Axes3D(fig)
            ax.scatter(xs, ys, zs)
            ax.set_xlabel("Q (1/Ang)")
            ax.set_ylabel(self.yLabel)
            ax.set_zlabel(self.sfLabel)
        elif self.plotTypes['points3d']:
            from plotlib.types import points3d
            points3d(self, plotKwds=plotKwds)
#        elif self.plotTypes['simplePoints3d']:
#            from plotlib.types import simplePoints3d
#            simplePoints3d(self, self.points[0], self.points[1], self.points[2], plotKwds=plotKwds)
        elif self.plotTypes['surface']:
            #create the plotting data structures
            dims = self.scatFunc.shape
            numPoints = dims[0]*dims[1]
            xs = np.zeros(numPoints)
            ys = np.zeros(numPoints)
            zs = np.zeros(numPoints)
            ind=0
            for i in range(dims[0]):#q
                for j in range(dims[1]):#energy, frequency
                    xs[ind] = self.q[i]
                    ys[ind] = self.yAxis[j]
                    zs[ind] = self.scatFunc[i,j]
                    ind+=1
            # use the engine
            qGrid2, yAxisGrid2 = np.meshgrid(self.q, self.yAxis)
            qGrid, yAxisGrid = np.mgrid[0:len(self.q), 0:len(self.yAxis)]
            
            #find the largest peak and set that as the upper limit on z
            #highestPeak = scatFunc[1:,1:].max()
            #lowestPoint = scatFunc.min()
            extentTuplet = (0 ,1 , 0 ,1 , 0 ,1)
            pic = self.surf(qGrid, yAxisGrid, self.scatFunc, 
                                extent=extentTuplet)
            #pic = self.surf(xs, ys, zs)
            self.outline(pic, extent=extentTuplet)
            self.axes(pic, xlabel="Q (1/Ang)", ylabel=self.yLabel, 
                          zlabel=self.sfLabel, extent=extentTuplet,
                          range=[self.q[0], self.q[-1], self.yAxis[0], self.yAxis[-1],
                                 np.min(self.scatFunc), np.max(self.scatFunc)])
        elif self.plotTypes['surfaceX']:
            #create the plotting data structures
            dims = self.scatFunc.shape
            numPoints = dims[0]*dims[1]
            xs = np.zeros(numPoints)
            ys = np.zeros(numPoints)
            zs = np.zeros(numPoints)
            ind=0
            for i in range(dims[0]):#q
                for j in range(dims[1]):#energy, frequency
                    xs[ind] = self.q[i]
                    ys[ind] = self.yAxis[j]
                    zs[ind] = self.scatFunc[i,j]
                    ind+=1
            # use the engine
            extentTuplet = (0 , 1, 0, 1, 0, 1)
            pic = self.pipeline.scalar_scatter(xs, ys, zs)#, extent=extentTuplet)

            #self.outline(pic, extent=extentTuplet)
            #self.axes(pic, extent=extentTuplet)
#            self.axes(pic, xlabel="Q (1/Ang)", ylabel=self.yLabel, 
#                          zlabel=self.sfLabel, extent=extentTuplet)
        elif self.plotTypes['pyplotSurface']:
            from mpl_toolkits.mplot3d import Axes3D
            fig = self.figure()
            ax = Axes3D(fig)
            qGrid, yAxisGrid = np.meshgrid(self.q, self.yAxis)
            #find the largest peak and set that as the upper limit on z
            #highestPeak = scatFunc[1:,1:].max()
            #lowestPoint = scatFunc.min()
            surf = ax.plot_surface(qGrid[1:], yAxisGrid[1:], self.scatFunc[1:,1:].transpose(), 
                        rstride=1, cstride=1, cmap=cm.jet,
                        linewidth=0, antialiased=False)
            ax.set_ylabel("Q (1/Ang)")
            ax.set_xlabel("E (meV)")
            ax.set_zlabel("S(Q,E) (a.u.)")
            #ax.set_zlim3d(lowestPoint, highestPeak)
            fig.colorbar(surf, shrink=0.5, aspect=5)      





if __name__ == '__main__':
    #plotTwoColumnTxt('first.txt','second.txt','second-b.txt')
    pass
    
