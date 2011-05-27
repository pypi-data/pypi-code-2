import os.path
try:
    os.path.exists(os.path.dirname(__file__)+"RFIDIOtconfig.py")
except ImportError:
    import os
    #FIXME Hide command output and provide pretty waiting message
    os.system("cd {0} && make".format(os.path.dirname(__file__)))
