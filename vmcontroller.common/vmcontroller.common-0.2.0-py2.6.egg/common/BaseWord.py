"""
BaseWord
"""

try:
    import time
    import pdb
    import stomper 
    import inject

    from vmcontroller.common import support
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

class BaseWord(object):
    """ Initializes the Frame object with the inheriting class' name """
    @inject.param('subject')
    def __init__(self, subject ):
        self.subject = subject

        self.frame = stomper.Frame()
        self.frame.cmd = 'SEND'    
        self.frame.body = self.name

        headers = {}
        headers['from'] = subject.descriptor.id
        headers['timestamp'] = str(time.time())

        self.frame.headers = headers

    @property
    def name(self):
        """ Get the word's name """
        return self.__class__.__name__

