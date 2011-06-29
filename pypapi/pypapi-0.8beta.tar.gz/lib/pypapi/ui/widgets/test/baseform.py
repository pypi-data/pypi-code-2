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


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication, QDialog
    from zope.component import getUtility, getMultiAdapter
    from pypapi.db.interfaces import IIterProcedurale, IDatabase
    from pypapi.db.model import IterProcedurale
    from pypapi.db.storage import SAListStore
    from pypapi.ui.cute.interfaces import IColumn, IDataContext, IForm
    from pypapi.ui.cute.form import StoreFormRegistration
    from pypapi.ui.cute.model import Column    
    app = QApplication([])

    db = getUtility(IDatabase)
    db.open('sqlite:///procedimenti.sqlite')

    # store
    ip_store = SAListStore(db.session.query(IterProcedurale))
    columns = [IColumn(IIterProcedurale.get('num'))]

    class MyDialog(QDialog):

        def __init__(self, store, parent):

            QDialog.__init__(self)
            self.initForm()
            self.store = store
            # da spostare prosssimamente in un binding
            ptv_dc = IDataContext(self.ptv)
            self.ptv.setSuperset(ptv_dc.lookup_model)

    register = StoreFormRegistration(MyDialog,
                                     IIterProcedurale,
                                     'baseform.ui',
                                     title='Dumb Demo')
    register.setModel(columns)
    columns = [Column('getCaption', 'Uffici'),]
    register.setModel(columns, '.ufficireferenti')

    form = getMultiAdapter((ip_store, None), IForm)
    form.edit(0)
    form.show()

    app.exec_()
    db.close(False) # per non eseguire il flush
