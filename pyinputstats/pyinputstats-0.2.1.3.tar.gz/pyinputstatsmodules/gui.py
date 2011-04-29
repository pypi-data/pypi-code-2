# coding:utf-8

# pyInputStats - An application for mouse and keyboard statistics
# Copyright (C) 2011  Daniel Nögel
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import time
import datetime

import gobject
import gtk

import database as db
from collector import DPC
import helpers

import pygtk_chart
from pygtk_chart import line_chart

import helpers
from pyinputstatsmodules import __VERSION__, __NAME__, __AUTHOR__

RED = gtk.gdk.color_parse("red")
GREEN = gtk.gdk.color_parse("green")
BLUE = gtk.gdk.color_parse("blue")

class TrayMenu(gtk.Menu):
    def __init__(self, parent):
        self.main = parent
        gtk.Menu.__init__(self)

        self.draw_menu_items()

    def draw_menu_items(self, play=None):
        self.mnuShow = gtk.ImageMenuItem("Show pyInputStats")
        w, h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        
        path = os.path.abspath(os.path.dirname(__file__))
        img = gtk.Image()
        image = os.path.join(path, "images", "ruler.png")
        if not os.path.exists(image):
            print ("Image not found")
        else:
            pix = gtk.gdk.pixbuf_new_from_file_at_size(image, w, h)
            img.set_from_pixbuf(pix)
            self.mnuShow.set_image(img)
        self.mnuShow.connect('activate', self.main.do_show)


        self.mnuQuit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.mnuQuit.connect('activate', self.main.main.quit)


        self.append(self.mnuShow)
        self.append(self.mnuQuit)
        
class TrayIcon(object):
    def __init__(self, parent, title = __NAME__, text = "{0} - v{1}".format(__NAME__, __VERSION__)):
        self.parent = parent
        self.menu = TrayMenu(parent)
        
        path = os.path.abspath(os.path.dirname(__file__))
        self.icon = gtk.status_icon_new_from_file(os.path.join(path, "images", "ruler.png"))
        self.icon.set_visible(False)
#        self.icon.connect('activate', self.parent.switch_window_state)
        self.icon.connect('activate', self.parent.do_show)
        self.icon.connect('popup-menu', self.cb_popup_menu, self.menu)
        self.icon.set_tooltip("%s\n%s" % (title, text))
        self.icon.set_visible(True)
        

    def cb_popup_menu(self, widget, button, time, event):
        event.show_all()
        event.popup(None, None, None, 3, time)

class GUI(object):
    def __init__(self, main):
        self.main = main        
        
        self.timeout = None
        self.timeout_average = None
        #~ self.timeout_keys = None
        
        self.trayicon = TrayIcon(self)
        
        path = os.path.abspath(os.path.dirname(__file__))
        filename = os.path.join(path, "glade", "gui.glade")
        self.builder = gtk.Builder()
        self.builder.add_from_file(filename)
        
        self.window = self.builder.get_object("window1")
        #~ self.window.set_property("skip-taskbar-hint", True)
        self.calendar = self.builder.get_object("calendar1")
        self.lblDayInfos = self.builder.get_object("lblDayInfos")
        self.chkDistanceMonth = self.builder.get_object("chkDistanceMonth")
        self.chkClicksMonth = self.builder.get_object("chkClicksMonth")
        self.chkKeysMonth = self.builder.get_object("chkKeysMonth")
        self.chkDistance = self.builder.get_object("chkDistance")
        self.chkClicks = self.builder.get_object("chkClicks")
        self.chkKeys = self.builder.get_object("chkKeys")
        self.lblNoDay = gtk.Label("No day selected, yet")
        self.lblNoMonth = gtk.Label("No month selected, yet")
        self.frameDay = self.builder.get_object("frameDay")
        self.frameMonth = self.builder.get_object("frameMonth")
        
        self.frameMonth.add(self.lblNoMonth)
        
        self.tv_keys = self.builder.get_object("treeview1")
        self.setup_tv_keys()
        
        self.comboMonthSelect = gtk.combo_box_new_text()
        self.comboMonthSelect.connect("changed", self.comboMonthSelect_changed)
        self.builder.get_object("frmSelectMonth").add(self.comboMonthSelect)
        
        self.linechart = None
        
        self.set_image_from_file_at_size(self.builder.get_object("imgLogo"), os.path.join(path, "images", "ruler.png"), 64, 64)
        self.builder.get_object("lblName").set_markup("<span font-size='30000'>{0} - v{1}</span>".format(__NAME__, __VERSION__))
        
        for image in ("image1", "image6", "image10", "image4"):
            self.set_image_from_file_at_size(self.builder.get_object(image), os.path.join(path, "images", "1277530791.png"), 20, 20)
        for image in ("image2", "image7", "image11", "image5"):
            self.set_image_from_file_at_size(self.builder.get_object(image), os.path.join(path, "images", "Anonymous_keyboard_key.png"), 17, 17)
        for image in ("image3", "image8", "image12", "image9"):
            self.set_image_from_file_at_size(self.builder.get_object(image), os.path.join(path, "images", "babayasin_Hand_cursor.png"), 17, 17)
        
        self.window.set_title("{0} - {1}".format(__NAME__, __VERSION__))
        self.window.set_icon_from_file(os.path.join(path, "images", "ruler.png"))
        
        #~ self.do_show()
        
        self.update_alltime_average()
        
        ## BEFORE CONNECT
        self.mark_days()
        if helpers.get_autostart_entry():
            self.builder.get_object("chkAutostart").set_active(True)
        else:
            self.builder.get_object("chkAutostart").set_active(False)
        ## CONNECT
        self.builder.connect_signals(self)
        
        date = datetime.date.today()
        self.calendar.select_month(date.month-1, date.year)
        self.calendar.select_day(date.day)
        self.populate_comboMonthSelect()
        
        #~ self.draw_chart(datetime.date.today())
    
    def setup_tv_keys(self):
        liststore = gtk.ListStore(str, int, str)
        self.tv_keys.set_model(liststore)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Key", renderer, text=0)
        column.set_sort_column_id(0)
        self.tv_keys.append_column(column)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Count", renderer, text=1)
        column.set_sort_column_id(1)
        self.tv_keys.append_column(column)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("%", renderer, text=2)
        column.set_sort_column_id(2)
        self.tv_keys.append_column(column)
    
    def do_show(self, widget):
        if self.timeout is None:
            self.timeout = gobject.timeout_add(100, self.update)
        if self.timeout_average is None:
            self.timeout_average = gobject.timeout_add(2000, self.update_alltime_average)
        #~ if self.timeout_keys is None:
            #~ self.timeout_keys = gobject.timeout_add(10000, self.update_key_overview)
        self.window.show_all()
        self.window.present()
        self.show_day(datetime.date.today())
        
        
    def do_hide(self):
        gobject.source_remove(self.timeout)
        gobject.source_remove(self.timeout_average)
        #~ gobject.source_remove(self.timeout_keys)

        self.timeout = None
        self.timeout_average = None
        #~ self.timeout_keys = None
        self.window.hide()
        
    def set_image_from_file_at_size(self, image, path, width, height):
        pb = gtk.gdk.pixbuf_new_from_file_at_size(path, width, height)
        image.set_from_pixbuf(pb)
    
    def draw_chart_month(self, month):
        if not self.chkDistanceMonth.get_active() and not self.chkClicksMonth.get_active() and not self.chkKeysMonth.get_active():
            if self.frameMonth.get_child():
                self.frameMonth.remove(self.frameDay.get_child())
                self.frameMonth.add(self.lblNoMonth)
                self.frameMonth.set_markup("<b>Please select some data to show.</b>")
                self.lblNoMonth.show()
                return
                
        
        num_days = helpers.month_days(month)
        
        STEP = 10.0
        days = [(-1, -1, -1),] * int(STEP)
        with db.DatabaseConnector() as dh:
            for d in (x*(1.0/STEP) for x in range(0, int(num_days*STEP))):
                pix, clicks, keys =  dh.get_month_data(month, d, 1.0/STEP)[0]
                #~ if pix is None:
                    #~ pix = 0
                #~ if clicks is None:
                    #~ clicks = 0
                #~ if keys is None:
                    #~ keys = 0
                days.append((pix, clicks, keys))
        
        l = len(days)
        days = helpers.strip_data(days)
        assert len(days)  == l

        if self.frameMonth.get_child():
            self.frameMonth.remove(self.frameMonth.get_child())
        
        #~ if not self.linechart:
        linechart = line_chart.LineChart()
        linechart.legend.set_visible(True)
        linechart.legend.set_position(line_chart.POSITION_TOP_RIGHT)
        linechart.xaxis.set_property("label", "Day")
        #~ else:
            #~ self.linechart.remove_graph("distance")
            #~ self.linechart.remove_graph("clicks")
            #~ self.linechart.remove_graph("keys")
        y, m = month
        linechart.title.set_text("pyInputStats - {0}/{1}".format(y, m))
        
        linechart.hide()
        
        
        #~ linechart.yaxis.set_property("label", "Data")
        
        #~ numcheck = (num_days+1)*10
        
        if self.chkDistanceMonth.get_active():
            #~ line_pixels = line_chart.graph_new_from_function(lambda x: days[int(x)][0]/DPC/100, 0, num_days, "distance", numcheck)
            line_pixels = line_chart.Graph("distance", "", [(i/STEP, day[0]/DPC/100) for i, day in enumerate(days)])
            #~ line_pixels.set_property("show-values", True)
            line_pixels.set_property("color", RED)
            line_pixels.set_type(line_chart.GRAPH_BOTH)
            line_pixels.set_title("Mouse-distance in metres")
            line_pixels.set_property("show-title", False)
            linechart.add_graph(line_pixels)

        if self.chkClicksMonth.get_active():
            #~ line_clicks = line_chart.graph_new_from_function(lambda x: days[int(x)][1], 0, num_days, "clicks", numcheck)
            line_clicks = line_chart.Graph("clicks", "", [(i/STEP, day[1]) for i, day in enumerate(days)])
            #~ line_clicks.set_property("show-values", True)
            line_clicks.set_property("color", GREEN)
            line_clicks.set_type(line_chart.GRAPH_BOTH)
            line_clicks.set_title("Mouseclicks")
            line_clicks.set_property("show-title", False)
            linechart.add_graph(line_clicks)
        
        if self.chkKeysMonth.get_active():
            #~ line_keys = line_chart.graph_new_from_function(lambda x: days[int(x)][2], 0, num_days, "keys", numcheck)
            line_keys = line_chart.Graph("keys", "", [(i/STEP, day[2]) for i, day in enumerate(days)])
            #~ line_keys.set_property("show-values", True)
            line_keys.set_property("color", BLUE)
            line_keys.set_type(line_chart.GRAPH_BOTH)
            line_keys.set_title("Keystrokes")
            line_keys.set_property("show-title", False)
            linechart.add_graph(line_keys)
        
        self.frameMonth.add(linechart)
        linechart.show()

    #~ def find_nearest(iterable, item)

#    def mycallback(self, date, data, keys, i, num):
#        #~ rest = i - abs(i)
#        t = time.mktime(date.timetuple()) + i*60*60 #(abs(i)*60*60) + (rest*60*60)
#        #~ key = min(data.keys(), key=lambda date : abs(date-t))
#        for key in keys:
#            if key-t <= 30 and key-t > 0:
#                return data[key][num]
#        return 0
#        #~ if abs(key-t) > 30:
#            #~ return 0
#        #~ print data[key]
#        #~ return  data[key][num]/DPC
        


    def draw_chart(self, date):
        if not self.chkDistance.get_active() and not self.chkClicks.get_active() and not self.chkKeys.get_active():
            if self.frameDay.get_child():
                self.frameDay.remove(self.frameDay.get_child())
                self.frameDay.add(self.lblNoDay)
                self.lblNoDay.set_markup("<b>Please select some data to show.</b>")
                self.lblNoDay.show()
                return
                
        STEP = 4.0
        hours = []
        #~ data_x = []
        #~ data_y = []
        with db.DatabaseConnector() as dh:
            for h in (x*(1.0/STEP) for x in range(0, int(25*STEP))):
                pix, clicks, keys =  dh.get_day_data(date, h, 1.0/STEP)[0]
                #~ if pix is None:
                    #~ pix = None
                #~ else:
                    #~ pix = pix/DPC/100
                #~ if clicks is None:
                    #~ clicks = 0
                #~ if keys is None:
                    #~ keys = 0
                hours.append((pix, clicks, keys))
                #~ data_x.append(h)
                #~ data_y.append((pix, clicks, keys))
                
            #~ data = {}
            #~ for p, c, k, t in dh.test(date):
                #~ data[t] = (p, c, k)
            #~ keys = sorted(data.keys())
            #~ print self.compat(d)
        
        l = len(hours)
        hours = helpers.strip_data(hours)
        assert len(hours)  == l
        
        if self.frameDay.get_child():
            self.frameDay.remove(self.frameDay.get_child())
        
        #~ if not self.linechart:
        linechart = line_chart.LineChart()
        linechart.legend.set_visible(True)
        linechart.legend.set_position(line_chart.POSITION_TOP_RIGHT)
        linechart.xaxis.set_property("label", "Time")
        #~ else:
            #~ self.linechart.remove_graph("distance")
            #~ self.linechart.remove_graph("clicks")
            #~ self.linechart.remove_graph("keys")
        y, m, d = date.year, date.month, date.day
        linechart.title.set_text("pyInputStats - {0}/{1}/{2}".format(y, m, d))
        linechart.hide()
        
        
        #~ linechart.yaxis.set_property("label", "Data")
        
        #~ numcheck = 24*4
        
        #~ import matplotlib.pyplot as plt
        #~ plt.plot(data_x, [y[0] for y in data_y], 'ro-', label="Mousemeter")
        #~ plt.plot(data_x, [y[1] for y in data_y], 'bs-', label="Mouseclicks")
        #~ plt.plot(data_x, [y[2] for y in data_y], 'gd-', label="Keystrokes")
        #~ plt.axis([0, 24, 0, max([y[2] for y in data_y])])
        #~ plt.legend()
        #~ plt.show()
        
        if self.chkDistance.get_active():
            #~ line_pixels = line_chart.graph_new_from_function(lambda x: hours[int(x)][0]/DPC/100, 0, 24, "distance", numcheck)
            #~ print [(i, hour[0]/DPC/100) for i, hour in enumerate(hours)]
            line_pixels = line_chart.Graph("distance", "", [(i/STEP, hour[0]/DPC/100) for i, hour in enumerate(hours)])
            #~ line_pixels = line_chart.graph_new_from_function(lambda x:self.mycallback(date, data, keys, x, 0)/DPC/100, 0, 24, "distance", numcheck)
            #line_pixels.set_property("show-values", True)
            line_pixels.set_property("color", RED)
            line_pixels.set_type(line_chart.GRAPH_BOTH)
            line_pixels.set_title("Mouse-distance in metres")
            line_pixels.set_property("show-title", False)
            linechart.add_graph(line_pixels)

        if self.chkClicks.get_active():
            #~ line_clicks = line_chart.graph_new_from_function(lambda x: hours[int(x)][1], 0, 24, "clicks", numcheck)
            #~ line_clicks = line_chart.graph_new_from_function(lambda x:self.mycallback(date, data, keys, x, 1), 0, 24, "clicks", numcheck)
            line_clicks = line_chart.Graph("clicks", "", [(i/STEP, hour[1]) for i, hour in enumerate(hours)])
            line_clicks.set_property("color", GREEN)
            line_clicks.set_type(line_chart.GRAPH_BOTH)
            line_clicks.set_title("Mouseclicks")
            line_clicks.set_property("show-title", False)
            linechart.add_graph(line_clicks)
        
        if self.chkKeys.get_active():
            #~ line_keys = line_chart.graph_new_from_function(lambda x: hours[int(x)][2], 0, 24, "keys", numcheck)
            #~ line_keys = line_chart.graph_new_from_function(lambda x:self.mycallback(date, data, keys, x, 2), 0, 24, "keys", numcheck)
            line_keys = line_chart.Graph("keys", "", [(i/STEP, hour[2]) for i, hour in enumerate(hours)])
            line_keys.set_property("color", BLUE)
            line_keys.set_type(line_chart.GRAPH_BOTH)
            line_keys.set_title("Keystrokes")
            line_keys.set_property("show-title", False)
            linechart.add_graph(line_keys)
        
        self.frameDay.add(linechart)
        linechart.show()
    
    def show_month(self, month):
        year = int(month[0])
        month = int(month[1])
        self.last_seen_month = (year, month)
        with db.DatabaseConnector() as dh:
            pixels, clicks, keys = dh.get_stats((year, month))
            if pixels is None:
                pixels = 0
            if clicks is None:
                clicks = 0
            if keys is None:
                keys = 0
            self.builder.get_object("lblDistanceMonth").set_text("{0:.2f}".format(pixels/DPC/100))
            self.builder.get_object("lblKeysMonth").set_text(str(keys))
            self.builder.get_object("lblButtonsMonth").set_text(str(clicks))
            self.draw_chart_month((year, month))
    
    def show_day(self, date):
        self.last_seen_date = date
        with db.DatabaseConnector() as dh:
            pixels, clicks, keys = dh.get_stats(date)
            if pixels is None:
                pixels = 0
            if clicks is None:
                clicks = 0
            if keys is None:
                keys = 0
            self.builder.get_object("lblDistanceDay").set_text("{0:.2f}".format(pixels/DPC/100))
            self.builder.get_object("lblKeysDay").set_text(str(keys))
            self.builder.get_object("lblButtonsDay").set_text(str(clicks))
            self.draw_chart(date)
    
    def populate_comboMonthSelect(self):
        with db.DatabaseConnector() as dh:
            for month in dh.get_months()[::-1]:
                self.comboMonthSelect.append_text("{0}-{1}".format(*month))
            try:
                self.comboMonthSelect.set_active(0)
            except AttributeError:
                pass
    
    def mark_days(self):
        self.calendar.clear_marks()
        
        with db.DatabaseConnector() as dh:
            for date in dh.get_days():
                #~ self.calendar.select_month(date.month, date.year)
                if self.calendar.get_date()[0:2] == (date.year, date.month-1):
                    self.calendar.mark_day(date.day)

    def update_key_overview(self):
        model = self.tv_keys.get_model()
        model.clear()
                
        with db.DatabaseConnector() as dh:
            stats = dh.get_char_stats()
            keys = sum((s[1]) for s in stats)
            for key, count in stats:
                #~ print key, helpers.get_char(key)
                try:
                    char = str(helpers.get_char(key)).decode("utf-8")
                except UnicodeDecodeError:
                    char = "???"
                    
                percentage = round(float(count)/keys*100.0,2)
                model.append((char, count, percentage))
        

    def update_alltime_average(self):
        with db.DatabaseConnector() as dh:
            num = dh.get_num_days()#float(len(dh.get_days()))
            #~ print num
            pixels, clicks, keys = self.main.get_data_fast()
            
            pd = pixels / num
            cd = clicks / num
            kd = keys / num
            
            self.builder.get_object("lblDistanceAverage").set_text("{0:.2f}".format(pd/DPC/100))
            self.builder.get_object("lblKeysAverage").set_text("{0:.2f}".format(kd))
            self.builder.get_object("lblButtonsAverage").set_text("{0:.2f}".format(cd))
            
        return True

    def update(self):
        pixels, clicks, keys = self.main.get_data_fast()
        
        self.builder.get_object("lblDistance").set_text("{0:.2f}".format(pixels/DPC/100))
        self.builder.get_object("lblKeys").set_text(str(keys))
        self.builder.get_object("lblButtons").set_text(str(clicks))
        
        return True

    #
    # Callbacks
    #
    def chkAutostart_toggled_cb(self, widget):
        if widget.get_active():
            helpers.enable_autostart()
        else:
            helpers.disable_autostart()
        
    def comboMonthSelect_changed(self, widget):
        active = widget.get_active_text()
        if active:
            self.show_month(active.split("-"))
        
    def btnRefresh_clicked_cb(self, widget):
        self.main.update()
        self.update()
        self.update_alltime_average()
        self.update_key_overview()
        if self.builder.get_object("notebook1").get_current_page() == 1:
            y, m, d = self.calendar.get_date()
            date = datetime.date(y, m+1, d)
            self.show_day(date)
        if self.builder.get_object("notebook1").get_current_page() == 2:
            self.show_month(self.last_seen_month)
        
    def notebook1_switch_page_cb(self, widget, page, pagenum):
        if pagenum == 0:
            self.update_alltime_average()
        elif pagenum == 2:
            self.show_month(self.last_seen_month)
        elif pagenum == 3:
            self.update_key_overview()
        
    def btnClose_clicked_cb(self, widget):
        self.do_hide()
    
    def checkboxMonth_toggled_cb(self, checkbox):
        self.show_month(self.last_seen_month)
    
    def checkbox_toggled_cb(self, checkbox):
        self.show_day(self.last_seen_date)
        
    def calendar1_day_selected_cb(self, calendar):
        y, m, d = calendar.get_date()
        date = datetime.date(y, m+1, d)
        if date == datetime.date.today():
            self.main.update()
        self.show_day(date)

    def calendar1_month_changed_cb(self, calendar):
        self.mark_days()
        
    def window1_destroy_cb(self, window):
        return
        #~ self.do_hide()

    def window1_delete_event_cb(self, window, event):
        self.do_hide()
        return True
