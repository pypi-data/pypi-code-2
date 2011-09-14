"""!
@file errors.py

This file contains custom exception error objects
for use in reporting errors in nmc.
"""


#*************************** Begin NoOutputFilenameError ************************

class NoOutputFilenameError(Exception):
    def __init__(self, errormsg):

        self.errormsg = errormsg

    def __str__(self):

        return self.errormsg
    
#*************************** End NoOutputFilenameError **************************

class ParameterError(Exception):
    def __init__(self, errormsg):

        self.errormsg = errormsg

    def __str__(self):

        return self.errormsg
        
class ImportChildError(Exception):

    def __init__(self, errormsg):

        self.errormsg = "Symbol Import Child Error: %s" % errormsg

    def __str__(self):

        return self.errormsg


class SymbolError(Exception):

    def __init__(self, errormsg):

        self.errormsg = "Symbol Error: %s" % errormsg

    def __str__(self):

        return self.errormsg


class LibraryPathError(Exception):

    def __init__(self, errormsg=""):

        self.errormsg = """Can't find a suitable model library path, please set one
        of the following variables to point to the appropriate directory (absolute path)
        that contains your ndf library: NEUROSPACES_NMC_USER_MODELS, NEUROSPACES_NMC_PROJECT_MODELS,
        NEUROSPACES_NMC_SYSTEM_MODELS or NEUROSPACES_NMC_MODELS
        """

    def __str__(self):

        return self.errormsg

