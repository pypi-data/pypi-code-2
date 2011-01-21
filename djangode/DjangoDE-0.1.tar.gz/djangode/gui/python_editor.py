# DjangoDE, a integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from PyQt4 import QtCore, QtGui

from djangode import global_objects

from djangode.data.autocomplete import AutoCompleter
from djangode.gui.highlighters import PythonHighlighter

class PythonEditor(QtGui.QPlainTextEdit):
    def __init__(self, file_name):
        QtGui.QPlainTextEdit.__init__(self)

        self.highlighter = PythonHighlighter(self.document())

        self.file_name = file_name
        self.document().addResource(100, QtCore.QUrl("info://file_name"), file_name)

        self.drop_down = None

        if file_name is not None:
            self.document().setPlainText(open(self.file_name).read())

        self.completer = QtGui.QCompleter(QtCore.QStringList(), self)

        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

        self.breakpoints = []
        self.debug_line = None

        self.line_numbers = LineNumbers(self)

        self.blockCountChanged.connect(self.line_numbers.block_count_changed)
        self.updateRequest.connect(self.line_numbers.update_area)

    def scroll_to_line(self, line):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
        cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, line-1)
        self.setTextCursor(cursor)

    def scroll_to_top(self):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
        self.setTextCursor(cursor)

    def scroll_to_first_instance(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
        cursor = self.document().find(text, cursor)
        self.setTextCursor(cursor)

    def create_autocomplete_box(self, attrs):
        cursor_rect = self.cursorRect()

        self.completer.complete()
        self.completer.popup().move(cursor_rect.right(), cursor_rect.bottom())

    def setup_completion(self):
        tc = self.textCursor()
        text = self.document().toPlainText()

        line_no = len(text[:tc.position()].split("\n")) - 1
        char_no = len(text[:tc.position()].split("\n")[-1]) - 1

        autocompleter = AutoCompleter()
        module = autocompleter.process(str(text))
        var = module.get_at_text_pos(line_no, char_no)

        if var is not None:
            string_list = QtCore.QStringList()
            for attr in var.get_attributes():
                print attr.name
                string_list.append(attr.name)
            self.completer.setModel(QtGui.QStringListModel(string_list, self.completer))

            return True
        else:
            return False

    def insert_completion(self, completion):
        tc = self.textCursor()

        extra = (completion.length() - self.completer.completionPrefix().length())

        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion.right(extra))

        self.setTextCursor(tc)

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            if event.key() in [
                    QtCore.Qt.Key_Enter,
                    QtCore.Qt.Key_Return,
                    QtCore.Qt.Key_Escape,
                    QtCore.Qt.Key_Tab,
                    QtCore.Qt.Key_Backtab]:
                event.ignore()
                return

        # Has ctrl-tab been pressed??
        is_shortcut = event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Tab

        if not self.completer.popup().isVisible() and not (is_shortcut or event.text() == "."):
            QtGui.QPlainTextEdit.keyPressEvent(self, event)
            return

        if event.text() != ".":
            completion_prefix = self.text_under_cursor()
        else:
            completion_prefix = ""

        if completion_prefix != self.completer.completionPrefix() or not self.completer.popup().isVisible():
            if not self.completer.popup().isVisible():
                if not self.setup_completion():
                    QtGui.QPlainTextEdit.keyPressEvent(self, event)
                    return

            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0,0))

        if not is_shortcut:
            QtGui.QPlainTextEdit.keyPressEvent(self, event)

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    def resizeEvent(self, e):
        QtGui.QPlainTextEdit.resizeEvent(self, e)

        cr = self.contentsRect()
        self.line_numbers.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_numbers.area_width(), cr.height()))

    def set_debug_line(self, line_no):
        self.debug_line = line_no

        self.update_extra_selections()

    def update_extra_selections(self):
        selections = []

        for break_line in self.breakpoints:
            selection = QtGui.QTextEdit.ExtraSelection()

            selection.format.setBackground(QtGui.QColor("lightskyblue"))
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

            cursor = QtGui.QTextCursor(self.document())
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor) # move to start
            cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, break_line-1) # move down line_no times
            selection.cursor = cursor
            selection.cursor.clearSelection()

            selections.append(selection)

        if self.debug_line > 0:
            selection = QtGui.QTextEdit.ExtraSelection()

            selection.format.setBackground(QtGui.QColor("yellow"))
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            cursor = QtGui.QTextCursor(self.document())
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor) # move to start
            cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, self.debug_line-1) # move down line_no times
            selection.cursor = cursor
            selection.cursor.clearSelection()

            selections.append(selection)

        self.setExtraSelections(selections)

    def save(self):
        text = self.document().toPlainText()

        fp = open(self.file_name, "w")
        fp.write(text)
        fp.close()

        window.reload_project()

    def close(self):
        return True

    def toggle_breakpoint(self):
        current_line = self.textCursor().blockNumber()

        if current_line in self.breakpoints:
            del self.breakpoints[self.breakpoints.indexOf(current_line)]
        else:
            self.breakpoints.append(current_line+1)

        self.update_extra_selections()

        global_objects.project.set_breakpoints()

class LineNumbers(QtGui.QWidget):
    def __init__(self, editor):
        QtGui.QWidget.__init__(self, editor)

        self.editor = editor

        self.block_count_changed(0)

    def sizeHint(self):
        return QtCore.QSize(self.area_width(), 0)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), QtCore.Qt.lightGray)

        block = self.editor.firstVisibleBlock()
        blockNumber = block.blockNumber() + 1
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0, top, self.width(), self.editor.fontMetrics().height(), QtCore.Qt.AlignRight, str(blockNumber))

            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            blockNumber += 1

    def area_width(self):
        digits = len(str(self.editor.blockCount()))

        return 3 + self.editor.fontMetrics().width('9') * digits

    def block_count_changed(self, block_count):
        self.editor.setViewportMargins(self.area_width(), 0, 0, 0)

    def update_area(self, rect, dy):
        if dy > 0:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height());

        if rect.contains(self.editor.viewport().rect()):
            self.block_count_changed(0)
