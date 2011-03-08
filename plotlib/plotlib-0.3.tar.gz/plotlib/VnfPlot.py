import os

class VnfPlot(object):
    """Wrapper to matplotlib and mayavi2 that allows us to plot analysis functions. 
    Supports text and netcdf files for now.
    """

    def __init__(self, filenames=None, sqe=None, base='pyplot', engineInstance=None, **kwds):
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
            
        # create plottables
        self.ncPlottables = []
        self.textPlottables = []
        for filename in filenames:
            path,ext = os.path.splitext(filename)
            if ext=='.nc':
                from NcPlottable import NcPlottable
                self.ncPlottables.append(NcPlottable(filename, base=base, 
                    engineInstance=engineInstance, **kwds))
            elif ext=='.plot':
                from TextPlottable import TextPlottable
                self.ncPlottables.append(NcPlottable(filename, base=base, 
                    engineInstance=engineInstance, **kwds))

    def plotType(self, **kwds):
#        self.show=True
#        if kwds.has_key('plt'): kwds.pop('plt')
#        if kwds.has_key('show'):
#            self.show = kwds.pop('show')        
        for ncPlottable in self.ncPlottables:
            ncPlottable.plotType(**kwds)
            
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