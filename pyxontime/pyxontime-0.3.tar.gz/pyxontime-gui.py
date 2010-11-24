try:
    import pygtk
    pygtk.require('2.0')
except:
    print "PyGtk 2.0 is required for PyxonTime"

try:
    import gtk
    import gtk.glade
except:
    print "Gtk+ is required for PyxonTime"

from pyxontime import get_bus_stop_code, get_bus_stop_schedules
from pyxontime import persist

class Pyxontime:
    '''Graphical user interface and interactions for PyxonTime
    '''
    def __init__(self):
        self.widgets = gtk.glade.XML('pyxontime/gui/pyxontime.glade',"window1")
        self.favorites_textview = self.widgets.get_widget('favorites_textview').get_buffer()
        self.search_entry = self.widgets.get_widget('search_entry')
        self.search_textview = self.widgets.get_widget('search_textview').get_buffer()
        self.schedules_entry = self.widgets.get_widget('schedules_entry')
        self.schedules_textview = self.widgets.get_widget('schedules_textview').get_buffer()
        self.save_name_entry = self.widgets.get_widget('save_name_entry')
        self.save_code_entry = self.widgets.get_widget('save_code_entry')
        self.autoConnect()

    
    def autoConnect(self):
        '''Prefixes all signals functions by a 'gtk_'
        '''
        eventHandlers = {}
        for (itemName,value) in self.__class__.__dict__.items(): 
            if callable(value) and itemName.startswith('gtk_'):  
                eventHandlers[itemName[4:]] = getattr(self,itemName) 
        self.widgets.signal_autoconnect(eventHandlers)

    def gtk_delete(self, source=None, event=None):
        '''Closes the window
        '''
        gtk.main_quit()

    def do_favorite_button_action(self):
        '''Retrieve the stored bus stops names and codes
        '''
        result = ""
        bus_stops = persist.read()
        if bus_stops:
            for name, code in bus_stops:
                result = result + name.ljust(20) + " -> " + code + "\n"
        else:
            result = "No results found."

        self.favorites_textview.set_text(result)

    def gtk_on_favorites_button_clicked(self, source=None, event=None):
        '''Clic action to refresh the bus stops list
        '''
        self.do_favorite_button_action()
        return True

    def gtk_on_search_button_clicked(self, source=None, event=None):
        '''Searching bus stops
        '''
        bus_stops = get_bus_stop_code(self.search_entry.get_text())
        result = ""
        for stop_name, stop_code in bus_stops:
            result = result +  stop_name.ljust(20) + " -> " + stop_code + "\n"

        self.search_textview.set_text(result)

    def gtk_on_schedules_button_clicked(self, source=None, event=None):
        '''Searching schedules
        '''
        bus_code = self.schedules_entry.get_text()
        schedules = get_bus_stop_schedules(bus_code)
        result = ""
        if schedules:
            for service, destination, departure, null in schedules:
                result = result + "%s -> %s -> %s" % (service.ljust(10), destination, departure) + "\n"
        else:
            result = "No schedules..."

        self.schedules_textview.set_text(result)

    def gtk_on_save_button_clicked(self, source=None, event=None):
        '''Save a new favorite bus stop
        '''
        persist.save(self.save_code_entry.get_text(), self.save_name_entry.get_text())
        self.save_name_entry.set_text("")
        self.save_code_entry.set_text("")
        self.do_favorite_button_action()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = Pyxontime()
    app.main()

