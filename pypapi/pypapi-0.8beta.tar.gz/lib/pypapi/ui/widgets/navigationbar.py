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


import logging

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QAction, QIcon, QToolBar, QKeySequence

from zope.component import adapter, queryUtility
from zope.event import notify
from zope.interface import implementedBy
from pypapi.ui.cute.interfaces import IDataContext, IModelCursor, IModelCursorChangedEvent
from pypapi.ui.cute.event import local_event, ModelCursorChangedEvent, provideHandler
import pypapi.ui.resources
from pypapi.db.interfaces import IPermission, IEntitiesRegistry
from pypapi.cm.interfaces import IFolder


FIRST = ('nav_first_element',
         ':/icons/resultset_first.png',
         'Primo',
         "Spostati sul primo elemento (CTRL+F7)",
         QKeySequence(Qt.CTRL+Qt.Key_F7))
PREV = ('nav_prev_element',
        ':/icons/resultset_previous.png',
        'Prec (F7)',
        "Spostati sull'elemento precedente (F7)",
        QKeySequence(Qt.Key_F7))
NEXT = ('nav_next_element',
        ':/icons/resultset_next.png',
        'Succ (F8)',
        "Spostati sull'elemento successivo (F8)",
        QKeySequence(Qt.Key_F8))
LAST = ('nav_last_element',
        ':/icons/resultset_last.png',
        'Ultimo',
        "Spostati sull'ultimo elemento (CTRL+F8)",
        QKeySequence(Qt.CTRL+Qt.Key_F8))

EDIT = ('nav_edit_element',
        ':/icons/pencil.png',
        'Modifica',
        "Modifica l'elemento corrente (F3)",
        QKeySequence(Qt.Key_F3))
INSERT = ('nav_insert_element',
          ':/icons/add.png',
          'Nuovo (F4)',
          "Inserisci un nuovo elemento (F4)",
          QKeySequence(Qt.Key_F4))
DELETE = ('nav_delete_element',
          ':/icons/delete.png',
          'Cancella',
          "Cancella l'elemento corrente (CANC)",
          QKeySequence(Qt.Key_Delete))

CANCEL = ('nav_cancel_changes',
          ':/icons/cancel.png',
          'Annulla',
          "Annulla le modifiche effettuate (ESC)",
          QKeySequence(Qt.Key_Escape))
FLUSH = ('nav_flush_changes',
        ':/icons/disk.png',
        'Registra modifiche (F12)',
        "Registra le modifiche sul database (F12)",
        QKeySequence(Qt.Key_F12))
REFRESH = ('nav_refresh',
          ':/icons/arrow_refresh.png',
          'Aggiorna',
          "Aggiorna i dati presenti nella maschera",
          QKeySequence(Qt.Key_F2))

SEARCH = ('nav_search',
          ':/icons/find.png',
          'Cerca (F5)',
          u"Esegui una ricerca (F5)",
          QKeySequence(Qt.Key_F5))

CONTAINER = ('nav_container',
             ':/icons/folder.png',
             'Contenitore (F6)',
             "Mostra gli oggetti contenuti (F6)",
             QKeySequence(Qt.Key_F6))

SEARCH_COMMIT = 'Cerca'
SEARCH_COMMIT_TIP = "Effettua la ricerca utilizzando i valori inseriti"

INFO = ('nav_info',
        ':/icons/information.png',
        'Informazioni (F1)',
        u"Mostra le informazioni (F1)",
        QKeySequence(Qt.Key_F1))

ADMIN = ('nav_admin',
           ':/icons/application_osx_terminal.png',
          'Admin',
          u"Apertura sezione Admin (CTRL+F12)",
          QKeySequence(Qt.CTRL+Qt.Key_F12))

_mnemonics = {
    'A': CANCEL,
    'C': CONTAINER,
    'X': FLUSH,
    'D': DELETE,
    'E': EDIT,
    'F': FIRST,
    'I': INSERT,
    'L': LAST,
    'N': NEXT,
    'P': PREV,
    'R': REFRESH,
    'S': SEARCH,
    '?': INFO,
    '+': ADMIN,
    }

def addAdminToolBars(form):
    """Aggiunge una toolbar con gli strumenti amministrativi."""
    addNavigationToolBar(form, 'Admin', '+', actions_target=form)

def addStandardToolBars(form):
    """Aggiunge le toolbar standard alla form passata come parametro."""
    pdc = IDataContext(form)
    addNavigationToolBar(form, 'Navigation', 'FPNL', actions_target=pdc)
    addNavigationToolBar(form, 'Modification', 'REID', actions_target=pdc)
    addNavigationToolBar(form, 'Confirmation', 'AX', actions_target=pdc)
    addNavigationToolBar(form, 'Info', '-SC?', actions_target=pdc)
    notify(ModelCursorChangedEvent(pdc))

def addNavigationToolBar(parent, title='Navigation', buttons=None, actions_target=None):
    """Aggiungi una toolbar di navigazione alla window specificata.

    parent
      la window a cui aggiungere la toolbar

    name
      nome della toolbar

    buttons : None
      Sequenza dei pulsanti da attivare.

      Se non specificato diversamente, viene utilizzata l'intera sequenza
      di pulsanti, nell'ordine canonico.

      Può essere specificata sia come sequenza di pulsanti, e in
      questo caso ogni elemeno ``None`` indica un **break** nella
      disposizione dei pulsanti, piuttosto che mnemonicamente,
      utilizzando una stringa dove ogni carattere rappresenta
      l'iniziale del pulsante desiderato (con l'eccezione di
      `cancel`, indicato dalla lettera ``A``). Eventuali caratteri
      non riconosciuti verranno interpretati come **break**:
      specificando ad esempio ``"FP-NL"`` si otterrà una barra
      con i pulsanti `FIRST` e `PREV` sulla prima "riga", e
      `NEXT` e `LAST` nella seconda.

    actions_target: None
      Delegato a cui connettere le azioni. Deve implementare l'interfaccia
      IModelCursor.

    Ritorna la nuova toolbar.
    """

    if buttons is None:
        buttons = (FIRST, PREV, NEXT, LAST, EDIT, INSERT, DELETE, CANCEL, FLUSH, REFRESH, SEARCH, INFO, ADMIN)
    elif isinstance(buttons, basestring):
        buttons = [_mnemonics.get(m) for m in buttons]
    nav_toolbar = NavigationToolBar(parent, title, buttons, actions_target)
    nav_toolbar.setMovable(False)
    parent.addToolBar(nav_toolbar)
    return nav_toolbar

class NavigationToolBar(QToolBar):
    """Crea una toolbar di azioni a partire da una list di descrizione dei pulsanti"""
    def __init__(self, parent, title, buttons, actions_target=None):

        QToolBar.__init__(self, title, parent)

        for button in buttons:
            if button is None:
                self.addSeparator()
            else:
                aname, aicon, atext, atip, ashortcut = button
                action = QAction(aname, parent)
                setattr(self, aname, action)
                action.setToolTip(atip)
                action.setText(atext)
                if ashortcut is not None:
                    action.setShortcut(ashortcut)
                if aicon:
                    action.setIcon(QIcon(aicon))
                self.addAction(action)
        provideHandler(self.updateActions)
        self.buttons_specs = buttons
        if actions_target is not None:
            self.setActionsTarget(actions_target, parent)
        #self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    def setActionsTarget(self, obj, form):
        "Imposta il target delle azioni"
        # XXX da implementare in una disconnessione dal vecchio target
        # prima di connettere il nuovo

        for button in self.buttons_specs:
            if button is None:
                continue
            aname, aicon, atext, atip, _ = button
            action = getattr(self, aname)
            chunks = aname.split('_')
            chunks.pop(0)
            handler = chunks.pop(0)
            while chunks:
                handler += chunks.pop(0).capitalize()
            try:
                if hasattr(form, handler):
                    obj.connect(action, SIGNAL('triggered()'), getattr(form, handler))
                else:
                    obj.connect(action, SIGNAL('triggered()'), getattr(obj, handler))
            except AttributeError:
                logging.error("Il delegato specificato non implementa il metodo %r "
                              "per il pulsante %r", handler, aname)
                action.setVisible(False)


    @adapter(IModelCursor, IModelCursorChangedEvent)
    @local_event
    def updateActions(self, model_cursor, event):
        "Aggiorna lo stato delle azioni"

        notb = not model_cursor.at_bof
        note = not model_cursor.at_eof
        dirty = model_cursor.is_dirty
        ndirty = not dirty

        per = queryUtility(IPermission)
        form = self.parent()
        can_select, can_insert, can_update, can_delete = per.resolvePermissions(form.interface)

        reg = queryUtility(IEntitiesRegistry)
        klass = reg.getEntityClassFor(form.interface)
        is_folder = IFolder in implementedBy(klass)

        if hasattr(self, 'nav_first_element'):
            self.nav_first_element.setEnabled(can_select and ndirty and notb)
        if hasattr(self, 'nav_prev_element'):
            self.nav_prev_element.setEnabled(can_select and ndirty and notb)
        if hasattr(self, 'nav_next_element'):
            self.nav_next_element.setEnabled(can_select and ndirty and note)
        if hasattr(self, 'nav_last_element'):
            self.nav_last_element.setEnabled(can_select and ndirty and note)

        if hasattr(self, 'nav_edit_element'):
            self.nav_edit_element.setEnabled(can_update and ndirty and (notb or note))
        if hasattr(self, 'nav_insert_element'):
            self.nav_insert_element.setEnabled(can_insert and ndirty)
        if hasattr(self, 'nav_delete_element'):
            self.nav_delete_element.setEnabled(can_delete and ndirty and (notb or note))

        if hasattr(self, 'nav_cancel_changes'): self.nav_cancel_changes.setEnabled(dirty)
        if hasattr(self, 'nav_commit_changes'): self.nav_commit_changes.setEnabled(dirty)
        if hasattr(self, 'nav_flush_changes'): self.nav_flush_changes.setEnabled(dirty)

        if hasattr(self, 'nav_search'): 
            self.nav_search.setEnabled(can_select and ndirty)
        if hasattr(self, 'nav_info'): self.nav_info.setEnabled(ndirty)

        if hasattr(self, 'nav_container'):
            self.nav_container.setEnabled(is_folder)
