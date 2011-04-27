from PyQt4.QtGui import *
from PyQt4.QtCore import *
from winterstone.baseQt import API

class Core(object):
    def _afterInit(self):
        self.api = API()

    def main(self):
        pass

    def test(self):
        self.api.info('Test success!')

