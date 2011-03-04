import sys
if sys.version_info[:2] < (2, 4):
    raise ImportError("Python version 2.4 or later is required for NetworkX (%d.%d detected)." %  sys.version_info[:2])

del sys