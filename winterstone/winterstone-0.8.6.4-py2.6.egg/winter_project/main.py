#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from winterstone.snowflake import *
from winterstone.extraQt import WinterEditor

from PyQt4.QtGui import *
from PyQt4.QtCore import *

starttime = datetime.now()

from winterstone.baseQt import WinterQtApp, API

__author__ = 'author'

class UI(WinterQtApp):
    '''
        Main class
    '''
    def __init__(self):
        WinterQtApp.__init__(self, WinterEditor(self, CWD + 'main.py'))

    def _afterMWInit(self):
        pass

    def _afterAppInit(self):
        pass


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QMainWindow.close(self)

    def echo(self, *args, **kwargs):
        self.mainBrowser.append(args[0])


def main():
    qtapp = QApplication(sys.argv)
    ui = UI()

    ui.show()
    api = API()

    endtime = datetime.now()
    delta = endtime - starttime
    api.info('Initialization time: %s' % delta)
    qtapp.exec_()


if __name__ == '__main__':
    main()