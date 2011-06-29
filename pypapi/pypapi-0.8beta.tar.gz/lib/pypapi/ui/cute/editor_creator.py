# encoding: utf-8
# Copyright (c) 2011 AXIA Studio <info@pypapi.org>
# and Municipality of Riva del Garda TN (Italy).
#
# This file is part of PyPaPi Framework.
#
# This file may be used under the terms of the GNU General Public
# License versions 3.0 or later as published by the Free Software
# Foundation and appearing in the file LICENSE.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#


from PyQt4.QtGui import QItemEditorCreatorBase, QComboBox, \
     QItemEditorFactory, QSpinBox, QLineEdit
from PyQt4.QtCore import QVariant
from pypapi.ui.cute.model import LookupItem

# Registro due creazioni customizzate degli delle celle, la prima,
# quella veramente interessante, sostituisce il normale spinbox
# usato per gli interi con un QComboBox quando la colonna è di
# lookup, consentendo quindi di scegliere il valore con una comoda
# drop-down list. Lo StringEditorCreator c'è solo perché non è
# possibile sostituire un solo creatore nella factory di default,
# quindi serve per poter editare i campi di testo.
class LookupEditorCreator(QItemEditorCreatorBase):

    def createWidget(self, parent):

        # qui parent è in delegato, perciò parent.parent() è la
        # tabella
        view = parent.parent()
        index = view.currentIndex()
        item = index.internalPointer()
        if isinstance(item, LookupItem):
            widget = QComboBox(parent)
            widget.setModel(item.column.lookup_model)
        else:
            widget = QSpinBox(parent)
            # piccola fix per permettere valori > 99
            widget.setMaximum(10000)
        return widget

    def valuePropertyName(self):

        return 'currentIndex'

class StringEditorCreator(QItemEditorCreatorBase):

    def createWidget(self, parent):

        return QLineEdit(parent)

# configurazione e installazione della nuova factory. Questa
# operazione causa un Segmentation Fault in chiusura per problemi
# di ownership degli oggetti non sono ancora chiari.
edit_fac = QItemEditorFactory()
creator = LookupEditorCreator()
s_creator = StringEditorCreator()
edit_fac.registerEditor(QVariant.Int, creator)
edit_fac.registerEditor(QVariant.String, s_creator)
QItemEditorFactory.setDefaultFactory(edit_fac)
# Hack necessario per far si che il garbage collector non distrugga
# edit_fac, compito che dal momento dell'assegazione qui sopra viene
# svolto dalla libreria Qt
QItemEditorFactory._ef = edit_fac

