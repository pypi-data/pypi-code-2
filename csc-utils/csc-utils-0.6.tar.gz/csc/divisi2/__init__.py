import os
import divisi2
__path__ = [os.path.dirname(__file__), os.path.dirname(divisi2.__file__)]
mypath = __path__
globals().update(divisi2.__dict__)
__path__ = mypath
