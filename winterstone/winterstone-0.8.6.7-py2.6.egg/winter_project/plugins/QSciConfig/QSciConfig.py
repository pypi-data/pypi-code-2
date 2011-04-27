from PyQt4.QtGui import *
from winterstone.base import WinterPlugin
from winterstone.extraQt import WinterEditor

try:
    from PyQt4.Qsci import *
    QSCI_SUPPORT = True
except ImportError:
    QSCI_SUPPORT = False

class QSciConfig(WinterPlugin):
    def activate(self):
        if QSCI_SUPPORT:
            for we in WinterEditor.objects.all():
                we.editor.setCaretLineBackgroundColor(QColor(self.config.options.caretline_color))
                we.editor.setMarginsBackgroundColor(QColor(self.config.options.margins_bg_color))
                we.editor.setMarginsForegroundColor(QColor(self.config.options.margins_fg_color))
                we.editor.setFoldMarginColors(QColor(self.config.options.foldmargin_prim_color), QColor(self.config.options.foldmargin_sec_color))
                we.editor.setSelectionBackgroundColor(QColor(self.config.options.selection_bg_color))
                we.editor.setSelectionForegroundColor(QColor(self.config.options.selection_fg_color))
                we.editor.setFolding(self.config.options.folding)

                font = QFont()
                font.setFamily(self.config.options.font)
                font.setFixedPitch(True)
                font.setPointSize(self.config.options.font_size)
                fm = QFontMetrics(font)
                we.editor.setFont(font)
                if self.config.options.linenumbers:
                    we.editor.setMarginsFont(font)
                    we.editor.setMarginWidth(0, fm.width("000") + 5)
                    we.editor.setMarginLineNumbers(0, True)
                if self.config.options.folding:
                    we.editor.setFolding(QsciScintilla.BoxedTreeFoldStyle)
                we.editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)
                we.editor.setCaretLineVisible(self.config.options.caretline)

        else:
            raise Exception('QSCI_SUPPORT required')
        self.api.info('%s: start' % self.name)
        return WinterPlugin.activate(self)

    def deactivate(self):
        if QSCI_SUPPORT:
            pass
        self.api.info('%s: stop' % self.name)
        return WinterPlugin.deactivate(self)