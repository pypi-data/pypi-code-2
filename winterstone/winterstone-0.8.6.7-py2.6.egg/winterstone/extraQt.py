# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from snowflake import getFileContent
from base import WinterObject
import re

try:
    from PyQt4.Qsci import *
    QSCI_SUPPORT = True
except ImportError:
    QSCI_SUPPORT = False
    print 'WARNING: QSCI_SUPPORT disabled'

class WinterLine(QLineEdit):
    def __init__(self):
        QLineEdit.__init__(self)
        self.connect(self, SIGNAL("textChanged(QString)"), self._newchar)
        self.connect(self, SIGNAL("returnPressed()"), self._command)

        self.hist_a = []
        self.hist_b = []


    def setComplete(self, array):
        self.completerList = QStringList()
        for line in array:
            self.completerList.append(QString(line))
        self.lineEditCompleter = QCompleter(self.completerList)
        self.lineEditCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.lineEditCompleter)

    def _command(self):
        pass

    def _newchar(self):
        ln = re.findall('[^ ]*', str(self.text().toUtf8()))[0]
        if self.checkLine():
            self.color = QColor(0, 150, 0)
            self.decor = 'underline'
            self.dlock = False
        else:
            self.color = QColor(140, 0, 0)
            self.decor = 'none'
            self.dlock = True
        self.setStyleSheet(
            "QWidget { font: bold; color: %s; text-decoration: %s;}" % (self.color.name(), self.decor))
        self.onChange()

    def checkLine(self):
        return True

    def onChange(self):
        pass

    def keyPressEvent(self, event):
        if event.key() == 16777216:
            self.clear()
        elif event.key() in [16777235]:
            if str(self.text()):
                self.hist_b.append(str(self.text()))
                self.hist_b = list(set(self.hist_b))
            if self.hist_a:
                self.setText(str(self.hist_a.pop()))
        elif event.key() in [16777237]:
            if str(self.text()):
                self.hist_a.append(str(self.text()))
                self.hist_a = list(set(self.hist_a))
            if self.hist_b:
                self.setText(str(self.hist_b.pop()))
        else:
            QLineEdit.keyPressEvent(self, event)


class WinterSearch(WinterLine):
    def __init__(self, container):
        WinterLine.__init__(self)
        self.container = container

    def checkLine(self):
        return self.container.findFirst(self.text(), False, False, False, True)

    def _command(self):
        self.container.findNext()


class WinterEditor(QWidget,WinterObject):
    def __init__(self, parent, filename='', lexer='Python'):
        QWidget.__init__(self)
        WinterObject.__init__(self)
        self.QSCI_SUPPORT=QSCI_SUPPORT
        self.parent = parent
        try:
            self.api = parent.API()
        except AttributeError:
            from baseQt import API

            self.api = API()
        self.filename = filename
        lay = QVBoxLayout()
        self.tb = QToolBar(self)
        lay.addWidget(self.tb)

        self.tb_save = QToolButton()
        self.tb_save.setIcon(QIcon.fromTheme('document-save', QIcon(self.api.icons['filesave'])))
        self.connect(self.tb_save, SIGNAL("clicked()"), self.save)
        self.tb.addWidget(self.tb_save)

        if QSCI_SUPPORT:
            editor = QsciScintilla(self)
            self.lexers = {'Bash': QsciLexerBash, 'Batch': QsciLexerBatch, 'CMake': QsciLexerCMake, 'CPP': QsciLexerCPP,\
                           'CSS': QsciLexerCSS, 'D': QsciLexerD, 'Diff': QsciLexerDiff, 'Fortran': QsciLexerFortran77,\
                           'HTML': QsciLexerHTML, 'Lua': QsciLexerLua, 'Make': QsciLexerMakefile,
                           'Pascal': QsciLexerPascal,\
                           'Perl': QsciLexerPerl, 'PostScript': QsciLexerPostScript, 'POV': QsciLexerPOV,\
                           'Properties': QsciLexerProperties, 'Python': QsciLexerPython, 'Ruby': QsciLexerRuby,\
                           'SQL': QsciLexerSQL, 'TCL': QsciLexerTCL, 'TeX': QsciLexerTeX,\
                           'VHDL': QsciLexerVHDL, 'YAML': QsciLexerYAML, 'Plain': QsciLexerPython}

            editor.setLexer(self.lexers[lexer]())

            self.tb_undo = QToolButton()
            self.tb_undo.setIcon(QIcon.fromTheme('edit-undo', QIcon(self.api.icons['edit-undo'])))
            self.connect(self.tb_undo, SIGNAL("clicked()"), editor.undo)
            self.tb.addWidget(self.tb_undo)

            self.tb_redo = QToolButton()
            self.tb_redo.setIcon(QIcon.fromTheme('edit-redo', QIcon(self.api.icons['edit-redo'])))
            self.connect(self.tb_redo, SIGNAL("clicked()"), editor.redo)
            self.tb.addWidget(self.tb_redo)


        else:
            editor = QTextEdit(self)

        self.editor = editor
        lay.addWidget(editor)
        if filename:
            editor.setText(getFileContent(filename))

        self.tb.addWidget(QWidget().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.tb.addWidget(QLabel('Search:  '))
        self.tb.addWidget(WinterSearch(self.editor))

        self.setLayout(lay)

    def save(self):
        try:
            f = open(self.filename, 'w')
            f.write(self.editor.text())
            f.close()
            self.parent.statusBar.showMessage('Saved')
        except Exception, e:
            self.api.error(e)
            self.parent.statusBar.showMessage('Saving unseccessfull')

