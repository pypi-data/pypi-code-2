from PyQt4.QtGui import *
from PyQt4.QtCore import *
from winterstone.baseQt import API
from winterstone.winterBug import try_this


class Core(object):
    '''
        Store all your app logic here
    '''
    def _afterInit(self):
        '''
            when application totally init
        '''
        self.api = API()

    def main(self):
        '''
            dummy for main core method. no autorun
        '''
        pass

    def test(self):
        '''
            try execute in debug line "core.test"
        '''
        self.api.info('Test success!')

