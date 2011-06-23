from Products.Five.browser import BrowserView
import sys
import pdb

class PDB(BrowserView):
    """ Drop to PDB fast """

    def drop(self):
        if sys.stdout.isatty():
            pdb.set_trace()