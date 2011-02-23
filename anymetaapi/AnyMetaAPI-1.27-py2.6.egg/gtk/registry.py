# Copyright (c) 2007-2009 Mediamatic Lab
# Released under the MIT License

"""
Registry dialog based on GTK.
"""

import re

import gtk

from anymeta.api.oauth.oauth import OAuthError
from anymeta.api.registry import AnyMetaRegistry



def sibpath(frm, to):
    """
    Clone from Twisted's sibpath.
    """
    import os
    return os.path.join(os.path.dirname(frm), to)



class GladeDialog (gtk.Dialog):
    """
    A generic class for dialogs based on glade.
    """

    gladefile = None
    top_widget = None
    builder = None

    registry = None

    def __init__(self, registry = None):
        gtk.Dialog.__init__(self)

        self.set_modal(True)

        if not registry:
            self.registry = AnyMetaRegistry.getInstance()
        else:
            self.registry = registry


        self.builder = gtk.Builder()
        self.builder.add_from_file(sibpath(__file__, self.gladefile))
        self.builder.connect_signals(self)
        w = self.builder.get_object(self.top_widget)
        w.reparent(self.vbox)
        w.show()

        self.connect("destroy", self.stop)
        self.connect("delete_event", self.stop)


    def stop(self, *args):
        self.emit("response", 0)
        self.destroy()



class RegistryDialog (GladeDialog):
    """
    Dialog which shows a list of APIs from the AnyMeta registry. It
    has the possibility to select an API, add a new one, or edit an
    existing one.
    """

    gladefile = "registry.glade"
    top_widget = "top_widget"

    current_id = None
    _run_as_main = False

    def __init__(self, *args, **kwargs):
        GladeDialog.__init__(self, *args, **kwargs)

        self.set_title("AnyMeta sites")

        self.set_size_request(640, 400)

        self.site_store = gtk.ListStore(str, str) # self.builder.get_object("site_store")
        self.site_view  = self.builder.get_object("site_view")
        self.site_view.set_model(self.site_store)

        col = gtk.TreeViewColumn("Site")
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.set_min_width(120)
        col.add_attribute(cell, "text", 0)
        self.site_view.append_column(col)

        col = gtk.TreeViewColumn("Base URL")
        cell = gtk.CellRendererText()
        col.pack_start(cell, True)
        col.add_attribute(cell, "text", 1)
        col.set_expand(True)
        self.site_view.append_column(col)

        sel = self.site_view.get_selection()
        sel.connect("changed", self.selection_changed)

        self._refresh_sites()
        self.selection_changed()


    def selection_changed(self, sel = None):
        if sel:
            store, iter = sel.get_selected()

        if not sel or not iter:
            self.current_id = None
            self.builder.get_object("edit_button").set_sensitive(False)
            self.builder.get_object("remove_button").set_sensitive(False)
            if not self._run_as_main:
                self.builder.get_object("use_button").set_sensitive(False)
        else:
            self.current_id = store.get_value(iter, 0)
            self.builder.get_object("edit_button").set_sensitive(True)
            self.builder.get_object("remove_button").set_sensitive(True)
            self.builder.get_object("use_button").set_sensitive(True)


    def run_as_main(self):
        self._run_as_main = True
        self.builder.get_object("use_button").set_label("Quit")
        self.builder.get_object("use_button").set_sensitive(True)
        self.run()


    def _refresh_sites(self):

        self.site_store.clear()

        entries = self.registry.getAll()
        for entry in entries:
            site = entries[entry]
            self.site_store.append([entry, site["entrypoint"]])


    def quit(self, *args):
        self.hide()
        self.destroy()


    def on_use_button_clicked(self, w):
        self.emit("response", 1)
        self.id = self.current_id
        self.destroy()


    def on_add_button_clicked (self, w):
        d = SiteDialog(self.registry)
        d.set_title("Add site")
        if not d.run():
            return
        self._refresh_sites()


    def on_edit_button_clicked (self, w):
        d = SiteDialog(self.registry)
        d.set_title("Edit site")
        d.edit(self.current_id, self.registry.get(self.current_id))
        self._refresh_sites()


    def on_remove_button_clicked (self, w):
        msg = "Are you sure you want to remove site '%s'?" % self.current_id
        d = gtk.MessageDialog(self, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        d.set_title("Confirm removal")
        if d.run() == gtk.RESPONSE_YES:
            self.registry.delete(self.current_id)
        d.destroy()
        self._refresh_sites()


    def on_site_view_row_activated(self, *args):
        self.emit("response", 1)
        self.id = self.current_id
        self.destroy()



class SiteDialog (GladeDialog):
    """
    Dialog for editing/adding a single API entry.
    """

    gladefile = "registry.glade"
    top_widget = "site_dialog_root"

    id = None


    def on_save_button_clicked (self, w):

        self._sanify_url_box()

        new_id   = self.builder.get_object("site_id").get_text()
        self.url = self.builder.get_object("url").get_text()

        if self.id:
            # editing

            if self.id != new_id:
                # rename old id to new id
                cfg = self.registry.get(self.id)
                self.registry.set(new_id, cfg['entrypoint'], cfg['oauth'], cfg['comment'])
                self.registry.delete(self.id)
                self.registry.save()
                self.id = new_id

        else:
            def wait_open_url(url):
                d = URLDialog(url)
                d.run()
                d.destroy()

            # adding
            try:
                self.registry.register_interactive(new_id, self.url, "", None, None, wait_open_url)

            except OAuthError, e:
                gtk.MessageDialog(self, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, e.message).run()
                return

            self.id = new_id

        self.emit("response", 1)
        self.hide()


    def edit(self, id, site):
        self.id = id
        self.builder.get_object("site_id").set_text(id)
        self.builder.get_object("url").set_text(site["entrypoint"])
        self.builder.get_object("url").set_sensitive(False)
        return self.run()


    def _sanify_url_box(self):
        """
        Sanify the URL to conform to the REST API entry point.

        Very AnyMeta specific - should be replaced with proper
        discovery, some day.
        """

        url = self.builder.get_object("url").get_text()

        if not re.match(r'^https?://', url):
            url = "http://" + url

        if url[-1:] != "/":
            url += "/"

        if not re.match(r'^.*services/rest/', url):
            url += "services/rest/"
        self.builder.get_object("url").set_text(url)


    def __init__(self, *args, **kwargs):
        GladeDialog.__init__(self, *args, **kwargs)
        self.set_size_request(400, 130)



class URLDialog (GladeDialog):
    """
    The dialog for the OAuth authorization.
    """

    gladefile = "registry.glade"
    top_widget = "url_dialog_root"

    def __init__(self, url):
        GladeDialog.__init__(self)
        self.builder.get_object("urlbutton").set_uri(url)
        self.set_title("Authorization required")


    def on_auth_button_clicked(self, b):
        self.emit("response", 1)
        self.hide()



__all__ = ["RegistryDialog", "SiteDialog", "URLDialog"]
