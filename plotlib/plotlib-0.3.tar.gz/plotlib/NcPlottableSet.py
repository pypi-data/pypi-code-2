import numpy as np
from NcPlottable import NcPlottable

class NcPlottableSet(object):
    """ To plot more than one ncplottable....initially we only support multiple S(E)s
    
    maybe: use the hold=True option available in most pyplot routines to overlay
    plots.
    """
    def __init__(self, netcdfFiles=None, base='pyplot', engineInstance=None, **kwds):
        global engine
        if engineInstance:
            engine = engineInstance
        elif base=='pyplot':
            from matplotlib import pyplot
            engine = pyplot
        elif base=='mlab':
            from enthought.mayavi import mlab
            engine = mlab
        self.ncPlottables = [NcPlottable(netcdfFile, base=base, 
                    engineInstance=engineInstance, **kwds) for netcdfFile in netcdfFiles]
        #assume all datasets are similar
        #take first dataset as representative
        set1 = self.ncPlottables[0]
        self.q = set1.q
        self.yAxis = set1.yAxis
        self.yAxisType = set1.yAxisType
        self.yLabel = set1.yLabel
        self.sfLabel = set1.sfLabel
        self.plotTypes= {'all':False, 'add':False,
                         'imageX':False,'points3d':False,}#these are directives for the ncplottablesSet object

    def add(self):
        #get data
        set1 = self.ncPlottables[0]
        sqeShape = set1.scatFunc.shape
        self.scatFunc = np.zeros(sqeShape)
        for ncItem in self.ncPlottables:
            self.scatFunc += ncItem.scatFunc

    def plotType(self, **kwds):
        plotKwds={} #these are details for the ncplottablesSet object
        kwdsCopy = kwds.copy()
        for key,val in kwdsCopy.iteritems():
            if self.plotTypes.has_key(key):
                self.plotTypes[key] = val # a plotting type keyword
                del kwds[key]
            else:
                plotKwds[key] = val # a plotting keyword
        #create plot
        if self.plotTypes['all']:  
            for ncPlottable in self.ncPlottables:
                ncPlottable.plotType(**kwds)
        elif self.plotTypes['add']:
            # define grid.
            qs=np.array([])
            ys=np.array([])
            scatFuncs=np.array([])
            for ncItem in self.ncPlottables:
                points = ncItem.createPoints()
                qs = np.append(qs, points[0])
                ys = np.append(ys, points[1])
                scatFuncs = np.append(scatFuncs, points[2])
            
            if self.plotTypes['imageX']:
                from matplotlib.mlab import griddata
                qi = np.linspace(min(qs), max(qs), plotKwds.get('xDivisions', 100))
                yi = np.linspace(min(ys), max(ys), plotKwds.get('yDivisions', 100))
                scatFunci = griddata(qs, ys, scatFuncs, qi, yi)
                if hasattr(self, 'clip'):
                    scatFunci = np.clip(scatFunci, self.clip[0], self.clip[1])
                # contour the gridded data, plotting dots at the randomly spaced data points.
                levels = plotKwds.get('levels', 15)
                
                CS = self.contourf(qi, yi, scatFunci, levels, 
                    cmap=self.cm.jet, **plotKwds)
                    #norm = norm, **plotKwds)
                self.title(self.sfLabel)
                self.xlabel("Q (1/Ang)")
                self.ylabel(self.yLabel)
                self.colorbar()
            elif self.plotTypes['points3d']:
                from plotlib.types import simplePoints3d
                simplePoints3d(self, qs, ys, scatFuncs, plotKwds)
                #CB = self.colorbar(CS, shrink=0.8, extend='both')
                #self.colorbar() # draw colorbar
                # plot data points.
                #self.scatter(qi, yAxisi, marker='o', c='b', s=5)
            
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