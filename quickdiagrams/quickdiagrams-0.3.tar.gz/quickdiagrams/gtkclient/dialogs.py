import gtk
import sys

class SaveDialog:

    def __init__(self, parent, pattern, save_callback):
        self.parent = parent
        self._create_dialog(pattern)
        self.save_callback = save_callback

    def _create_dialog(self, pattern):
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE, gtk.RESPONSE_OK)
        action = gtk.FILE_CHOOSER_ACTION_SAVE

        dialog = gtk.FileChooserDialog(action=action,
                buttons=buttons,
                parent=self.parent)
        dialog.set_do_overwrite_confirmation(True)

        # Custom filter
        filter = gtk.FileFilter()
        label, mask = pattern
        filter.set_name(label)
        filter.add_pattern(mask)
        dialog.add_filter(filter)

        # All files filter (*)
        filter = gtk.FileFilter()
        filter.set_name("All Files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        self.dialog = dialog

    def run(self):
        response = self.dialog.run()
        self.dialog.hide()

        if response == gtk.RESPONSE_OK:
            filename = self.dialog.get_filename()
            self.save_callback(filename)
        else:
            return False

class OpenDialog:

    def __init__(self, parent, pattern, callback, extra_pattern=None):
        self.parent = parent
        self._create_dialog(pattern, extra_pattern)
        self.callback = callback

    def _create_dialog(self, pattern, extra_pattern=None):
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        action = gtk.FILE_CHOOSER_ACTION_SAVE

        dialog = gtk.FileChooserDialog(action=action,
                buttons=buttons,
                parent=self.parent)

        # Custom filter
        filter = gtk.FileFilter()
        label, mask = pattern
        filter.set_name(label)
        filter.add_pattern(mask)
        dialog.add_filter(filter)

        if extra_pattern:
            filter = gtk.FileFilter()
            label, mask = extra_pattern
            filter.set_name(label)
            filter.add_pattern(mask)
            dialog.add_filter(filter)

        # All files filter (*)
        filter = gtk.FileFilter()
        filter.set_name("All Files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        self.dialog = dialog

    def run(self):
        response = self.dialog.run()
        self.dialog.hide()

        if response == gtk.RESPONSE_OK:
            filename = self.dialog.get_filename()
            self.callback(filename)
        else:
            return False
