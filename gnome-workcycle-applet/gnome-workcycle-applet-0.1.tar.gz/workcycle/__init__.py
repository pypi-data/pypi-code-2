#!/usr/bin/env python

import gtk
import gnomeapplet
import gobject
import datetime
import time
import pynotify
import gconf

global GCONF_DIR
GCONF_DIR =  '/apps/gnome-workcycle-applet'

def gconf_client():
    client = gconf.client_get_default()
    client.add_dir(GCONF_DIR, gconf.CLIENT_PRELOAD_NONE)
    return client

class WorkcycleApplet(gnomeapplet.Applet): 
    
    start_time = None
    stop_time = None
    is_worktime = False
    
    def __init__(self, applet, iid):
        self.applet = applet
        self._init_widgets()
        self._connect_events()
        self._init_notify()
        self._init_gconf()
        self.applet.show_all()        
        
    def _init_widgets(self):
        self.applet.set_background_widget(self.applet)
        self._create_menu()
        display_hbox = gtk.HBox(False, 5)
        self.display_icon = gtk.Image()
        self.display_icon.set_from_stock(gtk.STOCK_MEDIA_RECORD, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.display_label = gtk.Label("Click to start")
        self.display_time = gtk.Label("")
        display_hbox.pack_start(self.display_icon, True)
        display_hbox.pack_start(self.display_label, True)
        display_hbox.pack_start(self.display_time, True)
        self.applet.add(display_hbox)
        
    def _connect_events(self):
        self.applet.connect("destroy", self.destroy)
        self.applet.connect("button_press_event", self.toggle_timer)
    
    def _init_notify(self):
        pynotify.init("gnome-workcycle-applet")
        self.wt_notify = pynotify.Notification("Worktime", "Start working now", "notification-audio-play")
        self.ft_notify = pynotify.Notification("Funtime", "Have some fun","notification-device-eject")
    
    def _init_gconf(self):
        global GCONF_DIR
        client = gconf_client()
        client.notify_add(GCONF_DIR + '/worktime', self.update_worktime)
        client.notify_add(GCONF_DIR + '/funtime', self.update_funtime)
        self.update_worktime(client)
        self.update_funtime(client)
    
    def update_worktime(self, client, *args):
        global GCONF_DIR
        self.worktime = client.get_int(GCONF_DIR + '/worktime')
        
    def update_funtime(self, client, *args):
        global GCONF_DIR
        self.funtime = client.get_int(GCONF_DIR + '/funtime')
        
    def destroy(self, event):
        del self.applet
        
    def update_state(self):
        if not (self.start_time is None and self.stop_time is None):
            current_time = datetime.datetime.now()
            if (current_time < self.stop_time):
                if(self.is_worktime):
                    total = datetime.timedelta(minutes = self.worktime) # GCONF
                else:
                    total = datetime.timedelta(minutes = self.funtime) # GCONF
                elapsed = (current_time - self.start_time)
                timer_now = ((total.seconds - elapsed.seconds) / 60)
                self.display_time.set_text("~" + str(timer_now) + "min")
                return True
            else:
                self.toggle_timer(None, None)
                return False
    
    def _create_menu(self):
        xml="""<popup name="button3">
                    <menuitem name="ItemStop"
                              verb="Stop"
                              label="_Stop timer"
                              pixtype="stock"
                              pixname="gtk-media-stop"/>
                    <menuitem name="ItemPreferences" 
                              verb="Preferences" 
                              label="_Preferences" 
                              pixtype="stock" 
                              pixname="gtk-preferences"/>
                    <separator/>
                    <menuitem name="ItemAbout" 
                              verb="About" 
                              label="_About" 
                              pixtype="stock" 
                              pixname="gtk-about"/>
                </popup>"""

        verbs = [('About', self.show_about), ('Preferences', self.show_preferences), ('Stop', self.stop_timer)]
        self.applet.setup_menu(xml, verbs, None)
    
    def show_about(self, *args):
        pass
   
    def show_preferences(self, *args):
        WorkcycleSettings()
        
    def start_timer(self):
        if(self.start_time is None and self.stop_time is None):
            gobject.timeout_add(50, self.update_state)
        self.start_time = datetime.datetime.now()
        if(self.is_worktime):
            self.display_icon.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_SMALL_TOOLBAR)
            self.display_label.set_text("Worktime:")
            self.stop_time = self.start_time + datetime.timedelta(minutes = self.worktime) # GCONF_WORKTIME
            self.wt_notify.show()
        else:
            self.display_icon.set_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_SMALL_TOOLBAR)
            self.display_label.set_text("Funtime:")
            self.stop_time = self.start_time + datetime.timedelta(minutes = self.funtime) # GCONF_FUNTIME
            self.ft_notify.show()
    
    def stop_timer(self, *args):
        self.display_icon.set_from_stock(gtk.STOCK_MEDIA_RECORD, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.display_label.set_text("Click to start")
        self.display_time.set_text("")
        self.start_time = None
        self.stop_time = None
        self.is_worktime = not self.is_worktime
    
    def toggle_timer(self, *args):
        if args[1] is not None and args[1].button == 3:
            pass
        else:
            self.start_time = None
            self.stop_time = None
            self.is_worktime = not self.is_worktime
            self.start_timer()
            
            
class WorkcycleSettings():
    
    def __init__(self):
        self._init_widgets()
        self._connect_events()
        
        self.dialog.show_all()
    
    def _init_widgets(self):
        global GCONF_DIR
        
        self.dialog = gtk.Dialog()
        self.dialog.set_title('Workcycle Applet Preferences')
        
        content = self.dialog.get_content_area()
        
        worktime_hbox = gtk.HBox(True)
        worktime_label = gtk.Label('Worktime:')
        self.worktime_input = gtk.Entry()
        self.worktime_input.set_text(str(gconf_client().get_int(GCONF_DIR + '/worktime')))
        worktime_hbox.pack_start(worktime_label, True)
        worktime_hbox.pack_start(self.worktime_input)
        worktime_hbox.pack_start(gtk.Label(" minutes"))
        
        content.pack_start(worktime_hbox, False)
            
        funtime_hbox = gtk.HBox(True)
        funtime_label = gtk.Label('Funtime:')
        self.funtime_input = gtk.Entry()
        self.funtime_input.set_text(str(gconf_client().get_int(GCONF_DIR + '/funtime')))
        funtime_hbox.pack_start(funtime_label, True)
        funtime_hbox.pack_start(self.funtime_input)
        funtime_hbox.pack_start(gtk.Label(" minutes"))
        
        content.pack_end(funtime_hbox, False)
        
        self.dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
    
    def _connect_events(self):
        self.dialog.connect('response', self.cb_close_dialog)
        
    def cb_close_dialog(self, *args):
        global GCONF_DIR
        client = gconf_client()
        client.set_int(GCONF_DIR + '/worktime', int(self.worktime_input.get_text()))
        client.set_int(GCONF_DIR + '/funtime', int(self.funtime_input.get_text()))
        self.dialog.destroy()
        


