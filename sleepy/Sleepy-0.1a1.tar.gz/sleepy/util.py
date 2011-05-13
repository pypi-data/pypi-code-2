try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class MakoDef( object ):
    def __init__( self,
                  template,
                  deff,
                  kwargs ):
        self.template = template
        self.deff = deff
        self.kwargs = kwargs
