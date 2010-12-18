"""
An entry with an arrow. Similar to comboBoxEdit but with possibility to
connect to click on the arrow

"""
import gobject
import gtk

class FkEdit(gtk.HBox):
    __gtype_name__ = 'FkEntry'

    def __init__(self):
        gtk.HBox.__init__(self)
        self.entry = gtk.Entry()
        
        # the date button
        self.button = gtk.Button()

        self._align_entry = gtk.Alignment(1,0,1,0)
        self._align_arrow = gtk.Alignment(0,0,0,0)

        self._align_entry.add(self.entry)
        self._align_arrow.add(self.button)

        self.add(self._align_entry)
        self.add(self._align_arrow)
        # the down arrow
        arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
        self.button.add(arrow)
        arrow.show()
        # finally show the button
        self._align_entry.show_all()
        self._align_arrow.show_all()
        
        
        self.connect('realize', self.set_packing)

    def modify_base(self, state, color):
        self.entry.modify_base(state, color)
        
    def set_packing(self, other):
        parent = self.get_parent()
        props = [prop.name for prop in parent.list_child_properties()]
        if 'y-options' in props:
            parent.child_set_property(self, 'y-options', 0)

    def _on_entry_clicked(self, *args):
        print "entry clicked", args

    def _on_button_clicked(self, *args):
        print "button clicked", args

