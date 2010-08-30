from PyQt4.QtCore import *
from PyQt4 import QtGui

class Controller(object):

    def contextManager(self, value=None):
        if value is not None:
            self._contextManager = value
        if not hasattr(self, '_contextManager'):
            self._contextManager = None
        return self._contextManager

    def pomsetContext(self, value=None):
        if value is not None:
            self._pomsetContext = value
        if not hasattr(self, '_pomsetContext'):
            self._pomsetContext = None
        return self._pomsetContext

    def pomsetReference(self, value=None):
        if value is not None:
            self._pomsetReference = value
        if not hasattr(self, '_pomsetReference'):
            self._pomsetReference = None
        return self._pomsetReference

    def widget(self, value=None):
        if value is not None:
            self._widget = value
        if not hasattr(self, '_widget'):
            self._widget = None
        return self._widget

    def connectSignals(self):
        raise NotImplementedError('%s.connectSignals' % self.__class__)

    def notifyUserOfError(self, error,
                          text='Error',
                          icon=None):

        # show an error box to the user
        messageBox = QtGui.QMessageBox(self)
        messageBox.setText(text)
        messageBox.setInformativeText(str(error))

        if icon is None:
            icon = QtGui.QMessageBox.Critical
        messageBox.setIcon(icon)

        messageBox.setStandardButtons(
            QtGui.QMessageBox.Ok)
        ret = messageBox.exec_()
        return ret


    # END class Controller
    pass
