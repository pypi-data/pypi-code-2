# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/task output dialog.ui'
#
# Created: Sat Mar  6 10:52:07 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(602, 486)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(230, 440, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setGeometry(QtCore.QRect(21, 20, 561, 411))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.treeTasks = QtGui.QTreeWidget(self.splitter)
        self.treeTasks.setMinimumSize(QtCore.QSize(0, 0))
        self.treeTasks.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeTasks.setObjectName("treeTasks")
        self.treeTasks.headerItem().setText(0, "1")
        self.treeTasks.header().setVisible(True)
        self.textEditOutput = QtGui.QTextEdit(self.splitter)
        self.textEditOutput.setMinimumSize(QtCore.QSize(0, 0))
        self.textEditOutput.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.textEditOutput.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.textEditOutput.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        self.textEditOutput.setReadOnly(True)
        self.textEditOutput.setObjectName("textEditOutput")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Task message outputs", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

