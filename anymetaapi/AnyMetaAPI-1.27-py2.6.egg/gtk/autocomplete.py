# Copyright (c) 2007-2009 Mediamatic Lab
# Released under the MIT License

import gtk

from twisted.internet import reactor

class AutocompleteWidget (gtk.HBox):
    """
    Widget which handles auto-completion for AnyMeta lookups.

    This widget contains a L{gtk.Entry} with autocompletion support,
    and has a small image next to it, which shows the current status
    of the lookup, e.g. whether a valid item has been selected or not.

    @ivar api: L{anymeta.api.AnyMetaAPI} instance which is used for the autocompletion.
    @ivar timeout: After what time to do the lookup (in seconds)
    @ivar kind: Filter Anymeta lookups on this kind.
    """
    
    api     = None
    timeout = 0.5
    kind    = None

    # Private variables
    store    = None
    compl    = None
    by_id    = None
    by_title = None
    _call    = None
    _oldtxt  = None
    
    def __init__(self, api, kind = None):
        gtk.HBox.__init__(self)

        self.api = api
        if kind:
            self.kind = kind
        
        self.store = gtk.TreeStore(int, str)

        self.by_id = {}
        self.by_title = {}

        self.compl = gtk.EntryCompletion()
        self.compl.set_model(self.store)
        self.compl.set_popup_completion(True)
        self.compl.set_inline_completion(True)
        self.compl.set_text_column(1)

        self.compl.connect("match-selected", self.matchSelected)

        self.combo = gtk.Entry()
        self.combo.set_completion(self.compl)
        self.combo.connect("changed", self.comboChanged)
        
        self.add(self.combo)
        
        self.img = gtk.Image()
        self.img.set_from_stock("gtk-no", gtk.ICON_SIZE_MENU)
        self.add(self.img)


    def get_value(self):
        """
        Return the currently selected ID, or None if there is no valid value.
        """
        return self.id


    def set_value(self, id):
        """
        Set the current value of this widget to the given id. It uses
        C{anymeta.predicates.get} to get a title for the given ID.
        """

        def res(r):
            self.id = id
            self._oldtxt = r['result']
            self.combo.set_text(r['result'])
            self.img.set_from_stock("gtk-yes", gtk.ICON_SIZE_MENU)

        self.id = None
        self.combo.set_text("")
        self.img.set_from_stock("gtk-no", gtk.ICON_SIZE_MENU)
        
        self.api.anymeta.predicates.get(id=id, field='text.title').addCallback(res)

        

    def matchSelected(self, compl, filter, iter):
        """
        Signal handler for the C{match-selected} signal, which is
        emitted by the completion popup after selecting an item.
        """
        self.id = filter.get_value(iter, 0)
        self.checkMatch()


    def checkMatch(self, *a):
        """
        Checks if the current text in the entry matches with an item
        that has been retrieved from the site.
        """
        
        ttl = self.combo.get_text()
        if not self.id and ttl in self.by_title:
            # It matches
            self.id = self.by_title[ttl]

        if self.id:
            self.img.set_from_stock("gtk-yes", gtk.ICON_SIZE_MENU)
        else:
            self.img.set_from_stock("gtk-no", gtk.ICON_SIZE_MENU)
            
        pass


    def comboChanged(self, *a):
        """
        Event is fired whenever the text in our entry box has
        changed. It first looks in the local cache for a match based
        on the current text (using C{checkMatch}), if this fails it
        will do a C{anymeta.search.live} call to the API, populating
        the completion model with the results.
        """
        self.id = None
        self.checkMatch()

        txt = self.combo.get_text()
        
        if len(txt) < 3 or txt == self._oldtxt:
            return

        self._oldtxt = txt
        
        def result(r):
            for res in r:
                if res['id'] in self.by_id:
                    continue
                self.store.append(None, [int(res['id']), res['title']])
                self.by_id[res['id']]    = res
                if res['title'] not in self.by_title:
                    self.by_title[res['title']] = res['id']
            self.checkMatch()
            if not self.id:
                # force popup if we have no direct match
                self.combo.emit("changed")

        if self._call and self._call.active():
            self._call.cancel()
            
        arg = {'search': txt}
        if self.kind:
            arg['kind'] = self.kind
        self._call = reactor.callLater(self.timeout, lambda : self.api.anymeta.search.live(**arg).addCallback(result))
