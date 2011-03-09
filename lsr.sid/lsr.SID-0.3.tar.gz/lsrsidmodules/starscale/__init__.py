#!/usr/bin/env python
# coding:utf-8

# StarScale2 - A star-rating-scale based on Markus Mruss StarHScale
# Copyright (C) 2010  Daniel Nögel
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
#
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

########################################################################
# Based on Mark Mruss' StarHScale:                                     #
# StarHScale a Horizontal slider that uses stars                       #
# Copyright (C) 2006 Mark Mruss <selsine@gmail.com>                    #
#                                                                      #
# This library is free software; you can redistribute it and/or        #
# modify it under the terms of the GNU Lesser General Public           #
# License as published by the Free Software Foundation; either         #
# version 2.1 of the License, or (at your option) any later version.   #
#                                                                      #
#           http://www.learningpython.com/2006/07                      #
#           /25/writing-a-custom-widget-using-pygtk/                   #
########################################################################

import gtk
import gobject
from gtk import gdk
import pygtk

import os

BORDER_WIDTH = 10

class StarScale(gtk.Widget):
    """A horizontal StarScale widget.
    
    Emits: 'rating-changed' and 'rating_changing'
    """
    
    def __init__(self, max_stars=5, stars=0, overlap=False, image_width=None, half=False):
        """Create a StarScale widget.
        
        max_stars is the maximum number of stars possible,
        stars are the stars checked at the beginning, 
        overlap allows the stars to overlap a bit - so more stars fit on the widgets space,
        image_width forces the given star-dimensions and prevents them from being resized,
        half determines if only full stars can be checked (excludes overlap)
        """
        
        if half:
            overlap = False
        
        gtk.Widget.__init__(self)
        
        if image_width is None:
            self.force_width = False
            self.image_width = 25
        else:
            self.image_width = image_width
            self.force_width = True
            
        self.overlap = overlap
        self.half = half
        self.max_stars = max_stars
        self.stars = stars
        
        self._calculate_values()
    
    def _calculate_values(self):
        """Collects some basic information"""
        
        ## Holds the x-position of each star
        self.x_positions = []
        if self.overlap:
            for count in range(0,self.max_stars):
                self.x_positions.append((count * (self.image_width/2)) + BORDER_WIDTH)
        else:
            for count in range(0,self.max_stars):
                self.x_positions.append((count * self.image_width) + BORDER_WIDTH)
        
        ## Holds the width of each star / just think of the overlapping 
        # of the half stars.  
        self.virtual_width = []
        if self.half:
            for count in range(0,self.max_stars*2):
                self.virtual_width.append((count * self.image_width/2) + BORDER_WIDTH)
        elif self.overlap:
            for count in range(0,self.max_stars):
                self.virtual_width.append((count * self.image_width/2) + BORDER_WIDTH)
        else:
            for count in range(0,self.max_stars):
                self.virtual_width.append((count * self.image_width) + BORDER_WIDTH)
            
            

    def redraw_stars(self, numstars):
        """ Clears the GC and draws all the stars"""
        
        y = (self.allocation.height-self.image_width)/2
        x = (self.allocation.width - (self.x_positions[-1] + self.image_width + BORDER_WIDTH)) / 2

        ## Clear 
        self.window.draw_rectangle(self.get_style().bg_gc[gtk.STATE_NORMAL], True, 0, 0, self.allocation.width, self.allocation.height)
        if not self.half:
            for count in range(0,numstars):
                self.window.draw_pixbuf(self.gc, self.pbRed, 0, 0
                                                    , x+self.x_positions[count] 
                                                    , y,-1, -1) 
            for count in range(numstars,self.max_stars):
                self.window.draw_pixbuf(self.gc, self.pbGrey, 0, 0
                                                    , x+self.x_positions[count] 
                                                    , y,-1, -1) 
        else:
            full = numstars // 2
            half = True if numstars % 2 > 0 else False
            empty = full if not half else full+1
            
            
            for count in range(0,full):
                self.window.draw_pixbuf(self.gc, self.pbRed, 0, 0
                                                    , x+self.x_positions[count] 
                                                    , y,-1, -1) 
            if half:
                self.window.draw_pixbuf(self.gc, self.pbRedHalf, 0, 0
                                                    , x+self.x_positions[full] 
                                                    , y,-1, -1) 
            for count in range(empty, self.max_stars):
                self.window.draw_pixbuf(self.gc, self.pbGrey, 0, 0
                                                    , x+self.x_positions[count] 
                                                    , y,-1, -1) 

    def check_for_new_stars(self, xPos, clicked=False, just_show=False):
        """Depending on the given x-coord this routine decides how many stars are 'checked' """
        
        ## Relative Position
        x = (self.allocation.width - (self.x_positions[-1] + self.image_width + BORDER_WIDTH)) / 2
        xPos -= x
        
        new_stars = len([l for l in self.virtual_width if l < xPos])
        
        if clicked:
            ## A special case is checked here: If a checked star was clicked,
            # it will become unchecked:
            if self.get_value() == new_stars:
                self.set_value(self.get_value()-1)
                return        
                
        if just_show:
            self.redraw_stars(new_stars)
        else:
            self.set_value(new_stars)
            
    def set_value(self, value):

        """Sets the current number of stars that will be 
        drawn.  If the number is different then the current
        number the widget will be redrawn"""
        if (value >= 0):
            if (self.stars != value):
                self.stars = value
                #check for the maximum
                if self.half and self.stars > self.max_stars*2:
                    self.stars = self.max_stars*2
                elif not self.half and self.stars > self.max_stars:
                    self.stars = self.max_stars
                # redraw the widget
                self.window.invalidate_rect(self.allocation, True)
                self.redraw_stars(self.stars)
                #~ self.window.process_updates(True)
         
                self.emit("rating-changing", self.stars)
            
    def get_value(self):
        """Get the current number of stars displayed"""
        
        return self.stars
        
    def set_max_value(self, max_value):
        """set the maximum number of stars"""
        
        if self.max_stars != max_value:
            if max_value > 0:
                self.max_stars = max_value
                self._calculate_values()        
                if (self.stars > self.max_stars):
                    self.set_value(self.max_stars)
    
    def get_max_value(self):
        """Get the maximum number of stars that can be shown"""
        
        return self.max_stars
    
    # http://faq.pygtk.org/index.py?req=edit&file=faq08.005.htp
    def load_files(self):
        yellow = os.path.join(os.path.dirname(__file__), "star.svg")
        red = os.path.join(os.path.dirname(__file__), "star_red.svg")
        red_half = os.path.join(os.path.dirname(__file__), "star_half_red.svg")
        grey  = os.path.join(os.path.dirname(__file__), "star_grey.svg")
        
        self.pbYellow = gtk.gdk.pixbuf_new_from_file_at_size(yellow, self.image_width, self.image_width)
        self.pbRed = gtk.gdk.pixbuf_new_from_file_at_size(red, self.image_width, self.image_width)
        self.pbRedHalf = gtk.gdk.pixbuf_new_from_file_at_size(red_half, self.image_width, self.image_width)
        self.pbGrey = gtk.gdk.pixbuf_new_from_file_at_size(grey, self.image_width, self.image_width)
    
    #
    # CALLBACKS
    #
        
    def do_realize(self):
        """Called when the widget should create all of its 
        windowing resources."""
        
        # First set an internal flag showing that we're realized
        self.set_flags(self.flags() | gtk.REALIZED)
        
        # Create a new gdk.Window which we can draw on.
        # Also say that we want to receive exposure events 
        # and button click and button press events
        self.window = gtk.gdk.Window(
            self.get_parent_window(),
            width=self.allocation.width,
            height=self.allocation.height,
            window_type=gdk.WINDOW_CHILD,
            wclass=gdk.INPUT_OUTPUT,
            event_mask=self.get_events() | gtk.gdk.EXPOSURE_MASK
                | gtk.gdk.BUTTON1_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK
                | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK
                | gtk.gdk.LEAVE_NOTIFY_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)
                
        # Associate the gdk.Window with ourselves, Gtk+ needs a reference
        # between the widget and the gdk window
        self.window.set_user_data(self)
        
        # Attach the style to the gdk.Window, a style contains colors and
        # GC contextes used for drawing
        self.style.attach(self.window)
        
        # The default color of the background should be what
        # the style (theme engine) tells us.
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)
        
        self.load_files()

        
        
        # self.style is a gtk.Style object, self.style.fg_gc is
        # an array or graphic contexts used for drawing the forground
        # colours   
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        #~ self.set_events(gtk.gdk.BUTTON_RELEASE)
        self.connect("motion_notify_event", self.motion_notify_event)
        #~ self.connect("button_release_event", self.do_button_release_event)
        
    def do_unrealize(self):
        """The do_unrealized method is responsible for freeing the GDK resources
        De-associate the window we created in do_realize with ourselves"""
        
        self.window.destroy()
        
    def do_size_request(self, requisition):
        """From Widget.py: The do_size_request method Gtk+ is calling
         on a widget to ask it the widget how large it wishes to be. 
         It's not guaranteed that gtk+ will actually give this size 
         to the widget.  So we will send gtk+ the size needed for
         the maximum amount of stars"""
        
        height = self.get_parent().allocation.height
        if height < self.image_width:
            height = self.image_width
        requisition.height = height
        requisition.width = self.x_positions[-1] + self.image_width + BORDER_WIDTH
        #(self.image_width * self.max_stars) + (BORDER_WIDTH * 2)
    
    
    def do_size_allocate(self, allocation):
        """The do_size_allocate is called by when the actual 
        size is known and the widget is told how much space 
        could actually be allocated Save the allocated space
        self.allocation = allocation."""
        
        ## Set the window to the given size
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

        ## calculate the size of the stars - only if size is not
        # set by the user
        if not self.force_width:
            m = self.max_stars/2 if self.overlap else self.max_stars
            
            w = (allocation.width - BORDER_WIDTH*2)/(m)
            h = allocation.height 
            #~ print allocation.width, allocation.height
            #~ print w, h , "wh"
            self.image_width = w if w < h else h
            self._calculate_values()

            self.load_files()
            if self.window:
                self.redraw_stars(self.stars)
        
        
    def do_expose_event(self, event):
        """Called when the widget needs to be redrawn."""
        self.redraw_stars(self.stars)

    def do_leave_notify_event(self, widget):
        """Called when the mouse leaves the widget region."""
        
        self.redraw_stars(self.stars)

    def motion_notify_event(self, widget, event):
        """Called when the mouse moves over the widget"""
        
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.state
        
        if (state & gtk.gdk.BUTTON1_MASK):
            self.check_for_new_stars(event.x)   
        else:
            self.check_for_new_stars(event.x, just_show=True)
            
    def do_button_press_event(self, event):
        """The button press event virtual method"""
        
        if event.button == 1:
            self.check_for_new_stars(event.x, clicked=True)          
        return True

    def do_button_release_event(self, event):
        """The button release event virtual method"""
        
        self.emit("rating-changed", self.stars)

## Register the class as a gtk object and also prepare some events
gobject.type_register(StarScale)
gobject.signal_new("rating-changed", StarScale, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,))
gobject.signal_new("rating-changing", StarScale, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,))

if __name__ == "__main__":        
    win = gtk.Window()
    win.resize(400,150)
    win.connect('delete-event', gtk.main_quit)
    
    
    vbox = gtk.VBox()
    win.add(vbox)
    
    vbox.pack_start(StarScale(10,5, image_width=32), False, True)
    vbox.pack_start(StarScale(5,5, half=True), False, True)
    vbox.pack_start(StarScale(10,5, overlap=True), True, True)
    
    win.show_all()    
    gtk.main()
