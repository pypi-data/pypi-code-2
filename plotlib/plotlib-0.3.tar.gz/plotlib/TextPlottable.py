from matplotlib import pyplot

class TextPlottable(object):
    """A thin wrapper over matplotlib.pyplot...any pyplot command can be used on TextPlottable
    as if it were pyplot."""

    def __init__(self, filename, base='pyplot', engineInstance=None, **kwds):
        '''plots two column ascii'''
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
            
        # process file
        self.x=[];self.y=[]
        fp = file(filename)
        lines=fp.readlines()
        for line in lines:
            if line[0]=='#': continue
            xT,yT=map(float, line.split())
            self.x.append(xT);self.y.append(yT)
        
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
        engine.plot(self.x, self.y, **kwds)
        #axis([0, 60, 0, 0.001])
        if kwds.has_key('legend'):
            engine.legend(kwds['legend'])
        if kwds.has_key('xlabel'):
            engine.xlabel(kwds['xlabel'])
        if kwds.has_key('ylabel'):
            engine.ylabel(kwds['ylabel'])
        if kwds.has_key('title'):
            engine.title(kwds['title'])
        