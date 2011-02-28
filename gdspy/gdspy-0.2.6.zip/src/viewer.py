########################################################################
##                                                                    ##
##  Copyright 2009-2010 Lucas Heitzmann Gabrielli                     ##
##                                                                    ##
##  This file is part of gdspy.                                       ##
##                                                                    ##
##  gdspy is free software: you can redistribute it and/or modify it  ##
##  under the terms of the GNU General Public License as published    ##
##  by the Free Software Foundation, either version 3 of the          ##
##  License, or any later version.                                    ##
##                                                                    ##
##  gdspy is distributed in the hope that it will be useful, but      ##
##  WITHOUT ANY WARRANTY; without even the implied warranty of        ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     ##
##  GNU General Public License for more details.                      ##
##                                                                    ##
##  You should have received a copy of the GNU General Public         ##
##  License along with gdspy.  If not, see                            ##
##  <http://www.gnu.org/licenses/>.                                   ##
##                                                                    ##
########################################################################

import numpy
import gdspy
import Tkinter, tkMessageBox, tkColorChooser, tkFileDialog
try:
    import Image, ImageDraw
    _pil_error = False
except:
    _pil_error = True
    print "gdspy - WARNING: the modules Image and ImageDraw were not found. Image output functions will be disabled."
#try:
#    from matplotlib import pyplot, patches
#    _matplotlib_error = False
#except:
#    _matplotlib_error = True
#    print "gdspy - WARNING: the module matplotlib was not found. Corresponding visualization functions will be disabled."

__version__ = '0.1.5'
__doc__ = """
Classes and functions for the visualization of layouts cerated with the
gdspy Python module.
"""

class Canvas:
    """
    Rasterize the GDSII elements onto an image buffer that can be saved
    or edited latter.

    Parameters
    ----------
    colors : array
        Colors (RGB tuple) for each GDSII layer.
    outlines : array
        Colors (RGB tuple) for each GDSII layer.
    resolution : number
        Geometry scaling in pixels per user units.
    bounding_box : array-like[4]
        Area of the geometry to be draw on the output file in the format
        (min_x, max_x, min_y, max_y). If ``None``, the whole extent of
        each cell will be used.
    """
    def __init__(self, colors, outlines, resolution=1, bounding_box=None):
        self._transform = []
        self._len_colors = len(colors)
        self._colors = colors
        self._len_outlines = len(outlines)
        self._outlines = outlines
        self.resolution = resolution
        self.bounding_box = bounding_box
        if self.bounding_box is None:
            self._origin = None
        else:
            self._origin = numpy.array([self.bounding_box[0], self.bounding_box[2]])
            self.width = int(numpy.ceil(self.resolution * (self.bounding_box[1] - bounding_box[0])))
            self.height = int(numpy.ceil(self.resolution * (self.bounding_box[3] - bounding_box[2])))
            self.image = Image.new('RGB', (self.width, self.height), (0,0,0))
            self.artist = ImageDraw.Draw(self.image)

#    def add_transform(self, translation=None, rotation=None, magnification=None, x_reflection=False):
#        """
#        Append a new transformation of coordinates to the canvas
#        (first in, last out).
#        
#        Parameters
#        ----------
#        translation : array-like[2]
#            Translation relative to the reference system.
#        rotation : number
#            Angle of rotation (in *degrees*).
#        magnification : number
#            Magnification factor.
#        x_reflection : bool
#            If ``True``, the coordinate system is reflected parallel to
#            the x direction before being rotated.
#        """
#        self._transform = [(translation, rotation, magnification, x_reflection)] + self._transform
    
#    def remove_transform(self):
#        """
#        Remove the last transformation of coordinates added to the
#        canvas (first in, last out).
#        """
#        self._transform = self._transform[1:]
    
#    def add_polygon(self, layer, points):
#        """
#        Add a new polygon to the canvas applying the existing coordinate
#        transformations.
#
#        Parameters
#        ----------
#        layer : integer
#            The GDSII layer number for this polygon.
#        points : array-like[N][2]
#            Coordinates of the polygon vertices.
#        """
#        for t in self._transform:
#            if t[3]:
#                points *= numpy.array([1, -1], dtype=int)
#            if t[2] is not None:
#                points *= numpy.array([t[2], t[2]])
#            if t[1] is not None:
#                ct = numpy.cos(t[1] * numpy.pi / 180.0)
#                st = numpy.sin(t[1] * numpy.pi / 180.0)
#                points = points * ct + points[:,::-1] * numpy.array([-st, st])
#            if t[0] is not None:
#                points = points + numpy.array(t[0])
#        if self.bounding_box is None:
#            self.bounding_box = (numpy.min(points[:,0]), numpy.max(points[:,0]), numpy.min(points[:,1]), numpy.max(points[:,1]))
#        elif self._origin is None:
#            self.bounding_box = (min(self.bounding_box[0], numpy.min(points[:,0])), max(self.bounding_box[1], numpy.max(points[:,0])), min(self.bounding_box[2], numpy.min(points[:,1])), max(self.bounding_box[3], numpy.max(points[:,1]))) 
#        else:
#            points = (points - self._origin) * self.resolution
#            points[:,1] = self.height - points[:,1]
#            self.artist.polygon(list(numpy.array(points, dtype=long).flatten()), fill=self._colors[layer % self._len_colors], outline=self._outlines[layer % self._len_outlines])

    def add_polygon(self, layer, points):
        """
        Add a new polygon to the canvas.

        Parameters
        ----------
        layer : integer
            The GDSII layer number for this polygon.
        points : array-like[N][2]
            Coordinates of the polygon vertices.
        """
        if self.bounding_box is None:
            self.bounding_box = (numpy.min(points[:,0]), numpy.max(points[:,0]), numpy.min(points[:,1]), numpy.max(points[:,1]))
        elif self._origin is None:
            self.bounding_box = (min(self.bounding_box[0], numpy.min(points[:,0])), max(self.bounding_box[1], numpy.max(points[:,0])), min(self.bounding_box[2], numpy.min(points[:,1])), max(self.bounding_box[3], numpy.max(points[:,1]))) 
        else:
            points = (points - self._origin) * self.resolution
            points[:,1] = self.height - points[:,1]
            self.artist.polygon(list(numpy.array(points, dtype=long).flatten()), fill=self._colors[layer % self._len_colors], outline=self._outlines[layer % self._len_outlines])

#class Viewport:
#    """
#    Handles transformations between different coordinate systems to
#    interface the GDS elements with a *matplotlib* ``AxesSubplot``
#    object.
#
#    Parameters
#    ----------
#    axes : ``AxesSubplot``
#        A *matplotlib* ``AxesSubplot`` object to contain the plot.
#    style : array-like
#        Drawing style for all layers. Each element is a dictionary
#        composed of ``**kwargs`` for a ``matplotlib.patches.Polygon``
#        object creation. Please see the **matplotlib** documentation for
#        all options.
#    """
#    def __init__(self, axes, style):
#        self._axes = axes
#        self._transform = []
#        self._format = style
#        self._format_len = len(style)
#
#    
#    def add_transform(self, translation=None, rotation=None, magnification=None, x_reflection=False):
#        """
#        Append a new transformation of coordinates to the view port
#        (first in, last out).
#        
#        Parameters
#        ----------
#        translation : array-like[2]
#            Translation relative to the reference system.
#        rotation : number
#            Angle of rotation (in *degrees*).
#        magnification : number
#            Magnification factor.
#        x_reflection : bool
#            If ``True``, the coordinate system is reflected parallel to
#            the x direction before being rotated.
#        """
#        self._transform = [(translation, rotation, magnification, x_reflection)] + self._transform
#    
#    def remove_transform(self):
#        """
#        Remove the last transformation of coordinates added to the
#        view port (first in, last out).
#        """
#        self._transform = self._transform[1:]
#    
#    def add_polygon(self, layer, points):
#        """
#        Add a new polygon to the axes represented by the view port after
#        applying the existing coordinate transformations.
#
#        Parameters
#        ----------
#        layer : integer
#            The GDSII layer number for this polygon.
#        points : array-like[N][2]
#            Coordinates of the polygon vertices.
#        """
#        for t in self._transform:
#            if t[3]:
#                points = points * numpy.array([1, -1], dtype=int)
#            if t[2] is not None:
#                points = points * numpy.array([t[2], t[2]])
#            if t[1] is not None:
#                ct = numpy.cos(t[1] * numpy.pi / 180.0)
#                st = numpy.sin(t[1] * numpy.pi / 180.0)
#                points = points * ct + points[:,::-1] * numpy.array([-st, st])
#            if t[0] is not None:
#                points = points + numpy.array(t[0])
#        self._axes.add_patch(patches.Polygon(points, **(self._format[layer % self._format_len])))


class LayoutViewer(Tkinter.Frame):              
    """
    Provide a GUI where the layout can be viewed.

    The view can be scrolled vertically with the mouse wheel, and
    horizontally by holding the shift key and using the mouse wheel.
    Dragging the 2nd mouse button also scrolls the view, and if control
    is held down, it scrolls 10 times faster.

    You can zoom in or out using control plus the mouse wheel, or drag a
    rectangle on the window with the 1st mouse button to zoom into that
    area.

    A ruler is available by clicking the 1st mouse button anywhere on
    the view and moving the mouse around.  The distance is shown in the
    status area.

    Double-clicking on any polygon gives some information about it.

    Layer colors can be changed by double-clicking on the layer list or
    clicking the 3rd mouse button on any polygon.  On the color chooser,
    clicking cancel will make the selected layer transparent.  To change
    the outline color, use shift + double click on the layer list, or
    shift + click with the 3rd button on any polygon.
    
    The background color can be changed by clicking on the background
    with the 3rd mouse button.

    Parameters
    ----------
    cells : array-like
        The array of cells to be included in the view. If ``None``, all
        cells listed in ``Cell.cell_list`` are used.
    exclude_layers : array-like
        The array of layers to be excluded from the view.
    width : integer
        Horizontal size of the viewer window.
    height : integer
        Vertical size of the viewer window.
    colors : array-like
        Colors (RGB tuple) for each GDSII layer, with components from 0
        to 255. Any colors set to ``None`` will set that layer to
        transparent.
    outlines : array-like
        Colors (RGB tuple) for each GDSII layer, with components from 0
        to 255. Any colors set to ``None`` will set that layer to
        transparent.

    Examples
    --------
    All layers filled (in red, green, and blue) and with light outlines:

    >>> LayoutViewer(colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
    ...              outlines=[(192, 192, 192)])

    No filling, colored outlines:

    >>> LayoutViewer(colors=[None] * 64)
    """
    def __init__(self, cells=None, exclude_layers=[], width=800, height=600, colors=None, outlines=None):
        Tkinter.Frame.__init__(self, None)   

        if cells is None:
            cells = gdspy.Cell.cell_list
        self.cells = dict([(c.name, c) for c in cells])
        self.cell_bb = dict([(c.name, None) for c in cells])
        self.current_cell = Tkinter.StringVar()
        self.current_cell.set(cells[0].name)

        self.exclude_layers = exclude_layers

        if colors is None:
            self.colors = ['', '#e50000', '#41e500', '#0083e5', '#e500c4', '#c4e500', '#00e5c4', '#8300e5', '#e58300', '#00e541', '#0000e5', '#e50041', '#e5c400', '#00e583', '#4100e5', '#e54100', '#00e500', '#0041e5', '#e50083', '#83e500', '#00c4e5', '#c400e5', '#d2543f', '#54d23f', '#3f7ed2', '#d23fa8', '#a8d23f', '#3fd2d2', '#a83fd2', '#d2a83f', '#3fd27e', '#543fd2', '#d23f54', '#d2d23f', '#3fd2a8', '#7e3fd2', '#d27e3f', '#3fd254', '#3f54d2', '#d23f7e', '#7ed23f', '#3fa8d2', '#d23fd2', '#bf7272', '#88bf72', '#729ebf', '#bf72b4', '#b4bf72', '#72bfb4', '#9e72bf', '#bf9e72', '#72bf88', '#7272bf', '#bf7288', '#bfb472', '#72bf9e', '#8872bf', '#bf8872', '#72bf72', '#7288bf', '#bf729e', '#9ebf72', '#72b4bf', '#b472bf']
        else:
            self.colors = [('' if c is None else '#%02x%02x%02x' % tuple(c)) for c in colors]
        if outlines is None:
            outlines = ['#808080', '#e50000', '#41e500', '#0083e5', '#e500c4', '#c4e500', '#00e5c4', '#8300e5', '#e58300', '#00e541', '#0000e5', '#e50041', '#e5c400', '#00e583', '#4100e5', '#e54100', '#00e500', '#0041e5', '#e50083', '#83e500', '#00c4e5', '#c400e5', '#d2543f', '#54d23f', '#3f7ed2', '#d23fa8', '#a8d23f', '#3fd2d2', '#a83fd2', '#d2a83f', '#3fd27e', '#543fd2', '#d23f54', '#d2d23f', '#3fd2a8', '#7e3fd2', '#d27e3f', '#3fd254', '#3f54d2', '#d23f7e', '#7ed23f', '#3fa8d2', '#d23fd2', '#bf7272', '#88bf72', '#729ebf', '#bf72b4', '#b4bf72', '#72bfb4', '#9e72bf', '#bf9e72', '#72bf88', '#7272bf', '#bf7288', '#bfb472', '#72bf9e', '#8872bf', '#bf8872', '#72bf72', '#7288bf', '#bf729e', '#9ebf72', '#72b4bf', '#b472bf']
            l = len(outlines)
            self.outlines = [(outlines[i % l] if len(self.colors[i]) == 0 else '') for i in range(len(self.colors))]
        else:
            self.outlines = [('' if c is None else '#%02x%02x%02x' % tuple(c)) for c in outlines]

        ## Setup resizable window
        self.grid(sticky='nsew')
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        ## Setup toolbar
        self.frame = Tkinter.Frame(self)
        self.frame.columnconfigure(2, weight=1)
        self.frame.grid(row=2, column=0, padx=2, pady=2, sticky='ew')

        ## Setup canvas
        self.canvas = Tkinter.Canvas(self, width=width, height=height, background='#000', xscrollincrement=0, yscrollincrement=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        ## Setup scrollbars
        self.xscroll = Tkinter.Scrollbar(self, orient=Tkinter.HORIZONTAL, command=self.canvas.xview)
        self.xscroll.grid(row=1, column=0, sticky='ew')
        self.yscroll = Tkinter.Scrollbar(self, orient=Tkinter.VERTICAL, command=self.canvas.yview)
        self.yscroll.grid(row=0, column=1, sticky='ns')

        self.canvas['xscrollcommand'] = self.xscroll.set
        self.canvas['yscrollcommand'] = self.yscroll.set

        ## Setup buttons
        self.screenshot = Tkinter.Button(self.frame, text="Screenshot", command=self._save_screenshot)
        self.cell_menu = Tkinter.OptionMenu(self.frame, self.current_cell, *self.cells.keys())
        self.home = Tkinter.Button(self.frame, text="Extents", command=self._update_current_cell)
        self.screenshot.grid(row=0, column=0, sticky='w')
        self.cell_menu.grid(row=0, column=1, sticky='w')
        self.home.grid(row=0, column=2, sticky='w')
        self.bind_all("<KeyPress-Home>", self._update_current_cell)
        self.bind_all("<KeyPress-A>", self._update_current_cell)
        self.bind_all("<KeyPress-a>", self._update_current_cell)

        ## Setup coordinates box
        self.coords = Tkinter.Label(self.frame, text="0, 0")
        self.coords.grid(row=0, column=3, sticky='e')

        ## Layers
        self.layer_list = Tkinter.StringVar()
        self.layer_list_c = Tkinter.StringVar()

        self.l_frame = Tkinter.LabelFrame(self, text='Layers')
        self.l_frame.rowconfigure(0, weight=1)
        self.l_frame.columnconfigure(1, weight=1)
        self.l_frame.grid(row=0, column=2, rowspan=2, ipadx=6, padx=6, pady=3, sticky='nsew') 
        self.b_frame = Tkinter.Frame(self)
        self.b_frame.columnconfigure(0, weight=1)
        self.b_frame.columnconfigure(1, weight=1)
        self.b_frame.grid(row=2, column=2, padx=6, sticky='nsew')
        
        self.listbox = Tkinter.Listbox(self.l_frame, listvariable=self.layer_list, relief=Tkinter.FLAT, selectmode=Tkinter.EXTENDED, width=4)
        self.listbox_c = Tkinter.Listbox(self.l_frame, listvariable=self.layer_list_c, relief=Tkinter.FLAT, width=2)
        self.listbox.grid(row=0, column=1, pady=6, sticky='nsew')
        self.listbox_c.grid(row=0, column=0, pady=6, sticky='nsew')
        
        self.l_scroll = Tkinter.Scrollbar(self.l_frame, orient=Tkinter.VERTICAL, command=self._scrollboth)
        self.l_scroll.grid(row=0, column=2, pady=6, sticky='ns')
        
        self.listbox['yscrollcommand'] = self._scroll_the_other
        self.listbox_c['yscrollcommand'] = self._scroll_the_other

        self.btn_raise = Tkinter.Button(self.b_frame, text=u'\u2191', command=self._raise)
        self.btn_raise.grid(row=0, column=0, sticky='ew')
        self.btn_lower = Tkinter.Button(self.b_frame, text=u'\u2193', command=self._lower)
        self.btn_lower.grid(row=0, column=1, sticky='ew')

        ## Change current cell
        self.current_cell.trace_variable('w', self._update_current_cell)

        ## Double click to change layer color
        self.listbox.bind('<Double-Button-1>', self._change_layer_color)
        self.listbox_c.bind('<Double-Button-1>', self._change_layer_color)
        self.listbox.bind('<Shift-Double-Button-1>', self._change_layer_outline)
        self.listbox_c.bind('<Shift-Double-Button-1>', self._change_layer_outline)
        
        ## Change color: button 3
        self.canvas.bind('<ButtonRelease-3>', self._change_canvas_color)
        self.canvas.bind('<Shift-ButtonRelease-3>', self._change_canvas_outline)

        ## Drag-scroll: button 2
        self.canvas.bind('<Button-2>', lambda(evt): self.canvas.scan_mark(evt.x, evt.y))
        self.canvas.bind('<Motion>', self._mouse_move)

        ## Y scroll: scroll wheel
        self.bind_all('<MouseWheel>', lambda(evt): self.canvas.yview(Tkinter.SCROLL, 1 if evt.delta < 0 else -1, Tkinter.UNITS))
        self.canvas.bind('<Button-4>', lambda(evt): self.canvas.yview(Tkinter.SCROLL, -1, Tkinter.UNITS))
        self.canvas.bind('<Button-5>', lambda(evt): self.canvas.yview(Tkinter.SCROLL, 1, Tkinter.UNITS))

        ## X scroll: shift + scroll wheel
        self.bind_all('<Shift-MouseWheel>', lambda(evt): self.canvas.xview(Tkinter.SCROLL, 1 if evt.delta < 0 else -1, Tkinter.UNITS))
        self.canvas.bind('<Shift-Button-4>', lambda(evt): self.canvas.xview(Tkinter.SCROLL, -1, Tkinter.UNITS))
        self.canvas.bind('<Shift-Button-5>', lambda(evt): self.canvas.xview(Tkinter.SCROLL, 1, Tkinter.UNITS))

        ## Object properties: double button 1
        ## Zoom rectangle: drag button 1
        ## Measure tool: button 1 (click + click, no drag)
        self.canvas.bind('<Button-1>', self._zoom_rect_mark)
        self.canvas.bind('<ButtonRelease-1>', self._mouse_btn_1)
        self.canvas.bind('<Double-Button-1>', self._properties)

        ## Zoom: control + scroll wheel
        self.bind_all('<Control-MouseWheel>', self._zoom)
        self.canvas.bind('<Control-Button-4>', self._zoom)
        self.canvas.bind('<Control-Button-5>', self._zoom)

        ## Update the viewer
        self.shown_cell = None
        self.canvas_margins = None
        self._update_current_cell()
        self.master.title('gdspy - Layout Viewer')
        self.mainloop()


    def _update_current_cell(self, *args):
        self.canvas.delete(Tkinter.ALL)
        self.canvas.ruler = None
        self.canvas.x_rl = 0
        self.canvas.y_rl = 0
        pol_dict = self.cells[self.current_cell.get()].get_polygons(by_layer=True)
        if (self.shown_cell is None) or (self.current_cell.get() != self.shown_cell):
            layers = pol_dict.keys()
            layers.sort()
            if self.shown_cell is None:
                width = float(self.canvas.cget('width'))
                height = float(self.canvas.cget('height'))
            else:
                width = float(self.canvas.winfo_width()) - self.canvas_margins[0]
                height = float(self.canvas.winfo_height()) - self.canvas_margins[1]
            self.shown_cell = self.current_cell.get()
        else:
            layers = [int(i) for i in self.listbox.get(0, Tkinter.END)]
            width = float(self.canvas.winfo_width()) - self.canvas_margins[0]
            height = float(self.canvas.winfo_height()) - self.canvas_margins[1]
        layers.reverse()
        self.layer_list.set('')
        self.layer_list_c.set('')
        if len(layers) > 0:
            if len(self.colors) < max(layers):
                self.colors = [c for c in (self.colors * (max(layers) // len(self.colors) + 1))]
            if len(self.outlines) < max(layers):
                self.outlines = [c for c in (self.outlines * (max(layers) // len(self.outlines) + 1))]
        if self.cell_bb[self.current_cell.get()] is None:
            bb = [1e300, 1e300, -1e300, -1e300]
            for i in layers:
                if i not in self.exclude_layers:
                    for pol in pol_dict[i]:
                        if bb[0] > numpy.min(pol[:,0]):
                            bb[0] = numpy.min(pol[:,0])
                        if bb[1] > -numpy.max(pol[:,1]):
                            bb[1] = -numpy.max(pol[:,1])
                        if bb[2] < numpy.max(pol[:,0]):
                            bb[2] = numpy.max(pol[:,0])
                        if bb[3] < -numpy.min(pol[:,1]):
                            bb[3] = -numpy.min(pol[:,1])
            self.cell_bb[self.current_cell.get()] = tuple(bb)
        else:
            bb = list(self.cell_bb[self.current_cell.get()])
        if bb[2] < bb[0]:
            tkMessageBox.showwarning('Warning', 'The selected cell is empty.')
            bb = [-1, -1, 1, 1]
        self.scale = ((bb[3] - bb[1]) / height, (bb[2] - bb[0]) / width)
        if self.scale[0] > self.scale[1]:
            self.scale = self.scale[0] * 1.05
            add = (width * self.scale - bb[2] + bb[0]) * 0.5
            bb[0] -= add
            bb[2] += add
            add = (bb[3] - bb[1]) * 0.025
            bb[1] -= add
            bb[3] += add
        else:
            self.scale = self.scale[1] * 1.05
            add = (height * self.scale - bb[3] + bb[1]) * 0.5
            bb[1] -= add
            bb[3] += add
            add = (bb[2] - bb[0]) * 0.025
            bb[0] -= add
            bb[2] += add
        for i in layers:
            if i not in self.exclude_layers:
                self.listbox.insert(0, str(i))
                self.listbox_c.insert(0, ' ')
                self.listbox_c.itemconfig(0, background=self.colors[i])
                for pol in pol_dict[i]:
                    self.canvas.create_polygon(*list((numpy.array((1, -1)) * pol / self.scale).flatten()), fill=self.colors[i], outline=self.outlines[i], activeoutline='#FFF', activewidth=2, tag=('L' + str(i), 'V%d' % (pol.shape[0],)))
        self.canvas['scrollregion'] = tuple([x / self.scale for x in bb])
        self.canvas.zoom_rect = None
        if self.canvas_margins is None:
            self.update()
            self.canvas_margins = (int(self.canvas.winfo_width()) - width, int(self.canvas.winfo_height()) - height)

    def _raise(self):
        for i in self.listbox.curselection():
            i = int(i)
            if i > 0:
                layer = self.listbox.get(i)
                layer_above = self.listbox.get(i - 1)
                self.listbox.delete(i - 1)
                self.listbox.insert(i, layer_above)
                self.listbox_c.itemconfigure(i, background=self.colors[int(layer_above)])
                self.listbox_c.itemconfigure(i - 1, background=self.colors[int(layer)])
                self.canvas.tag_raise('L' + layer, 'L' + layer_above)

    def _lower(self):
        idx = list(self.listbox.curselection())
        idx.reverse()
        for i in idx:
            i = int(i)
            if i + 1 < self.listbox.size():
                layer = self.listbox.get(i)
                layer_under = self.listbox.get(i + 1)
                self.listbox.delete(i + 1)
                self.listbox.insert(i, layer_under)
                self.listbox_c.itemconfigure(i, background=self.colors[int(layer_under)])
                self.listbox_c.itemconfigure(i + 1, background=self.colors[int(layer)])
                self.canvas.tag_lower('L' + layer, 'L' + layer_under)

    def _change_layer_color(self, evt):
        i = self.listbox.nearest(evt.y)
        layer = self.listbox.get(i)
        ilayer = int(layer)
        rgb, color = tkColorChooser.askcolor(self.colors[ilayer], title='Select color for layer %s' % (layer,))
        if color is None:
            color = ''
            if len(self.outlines[ilayer]) == 0:
                self.outlines[ilayer] = '#808080' if len(self.colors[ilayer]) == 0 else self.colors[ilayer]
        self.colors[ilayer] = color
        self.listbox_c.itemconfig(i, background=color)
        for i in self.canvas.find_withtag('L' + layer):
            self.canvas.itemconfigure(i, fill=color, outline=self.outlines[ilayer])

    def _change_layer_outline(self, evt):
        i = self.listbox.nearest(evt.y)
        layer = self.listbox.get(i)
        ilayer = int(layer)
        rgb, color = tkColorChooser.askcolor(self.outlines[ilayer], title='Select outline for layer %s' % (layer,))
        if color is None:
            color = ''
            if len(self.colors[ilayer]) == 0:
                self.colors[ilayer] = '#808080' if len(self.outlines[ilayer]) == 0 else self.outlines[ilayer]
                self.listbox_c.itemconfig(i, background=self.colors[ilayer])
        self.outlines[ilayer] = color
        for i in self.canvas.find_withtag('L' + layer):
            self.canvas.itemconfigure(i, fill=self.colors[ilayer], outline=color)

    def _change_canvas_color(self, evt):
        if self.canvas.ruler is None:
            i = self.canvas.find_withtag(Tkinter.CURRENT)
            if len(i) == 0:
                rgb, color = tkColorChooser.askcolor(self.canvas.cget('bg'), title='Select background color')
                if color is not None:
                    self.canvas['bg'] = color
            else:
                layer = self.canvas.gettags(i[0])[0][1:]
                ilayer = int(layer)
                i = self.listbox.get(0, Tkinter.END).index(layer)
                rgb, color = tkColorChooser.askcolor(self.colors[ilayer], title='Select color for layer %s' % (layer,))
                if color is None:
                    color = ''
                    if len(self.outlines[ilayer]) == 0:
                        self.outlines[ilayer] = '#808080' if len(self.colors[ilayer]) == 0 else self.colors[ilayer]
                self.colors[ilayer] = color
                self.listbox_c.itemconfig(i, background=color)
                for i in self.canvas.find_withtag('L' + layer):
                    self.canvas.itemconfigure(i, fill=color, outline=self.outlines[ilayer])

    def _change_canvas_outline(self, evt):
        if self.canvas.ruler is None:
            i = self.canvas.find_withtag(Tkinter.CURRENT)
            if len(i) != 0:
                layer = self.canvas.gettags(i[0])[0][1:]
                ilayer = int(layer)
                i = self.listbox.get(0, Tkinter.END).index(layer)
                rgb, color = tkColorChooser.askcolor(self.outlines[ilayer], title='Select outline for layer %s' % (layer,))
                if color is None:
                    color = ''
                    if len(self.colors[ilayer]) == 0:
                        self.colors[ilayer] = '#808080' if len(self.outlines[ilayer]) == 0 else self.outlines[ilayer]
                        self.listbox_c.itemconfig(i, background=self.colors[ilayer])
                self.outlines[ilayer] = color
                for i in self.canvas.find_withtag('L' + layer):
                    self.canvas.itemconfigure(i, fill=self.colors[ilayer], outline=color)

    def _scroll_the_other(self, *args):
        self.l_scroll.set(*args)
        self.listbox.yview(Tkinter.MOVETO, args[0])
        self.listbox_c.yview(Tkinter.MOVETO, args[0])

    def _scrollboth(self, *args):
        self.listbox.yview(*args)
        self.listbox_c.yview(*args)

    def _mouse_move(self, evt):
        x = self.canvas.canvasx(evt.x)
        y = self.canvas.canvasy(evt.y)
        if self.canvas.ruler is None:
            self.coords['text'] = '%g, %g' % (x * self.scale, -y * self.scale)
        else:
            self.canvas.coords(self.canvas.ruler, self.canvas.x_rl, self.canvas.y_rl, x, y)
            dx = (x - self.canvas.x_rl) * self.scale
            dy = (self.canvas.y_rl - y) * self.scale
            self.coords['text'] = 'Distance: %g | dx = %g | dy = %g' % ((dx**2 + dy**2)**0.5, dx, dy)
        if evt.state & 0x0200:
            if evt.state & 0x0004:
                self.canvas.scan_dragto(evt.x, evt.y, 10)
            else:
                self.canvas.scan_dragto(evt.x, evt.y, 1)
        elif evt.state & 0x0100:
            if self.canvas.zoom_rect is None:
                self.canvas.zoom_rect = self.canvas.create_rectangle(self.canvas.x_zr, self.canvas.y_zr, self.canvas.x_zr, self.canvas.y_zr, outline='#DDD')
            self.canvas.coords(self.canvas.zoom_rect, self.canvas.x_zr, self.canvas.y_zr, x, y)

    def _zoom(self, evt):
        if evt.num==4:
            evt.delta = 1
        elif evt.num==5:
            evt.delta = -1
        s = 1.5 if evt.delta > 0 else 1/1.5
        self.scale /= s
        x0 = s * self.canvas.canvasx(evt.x) - evt.x# + self.canvas_margins[0]
        y0 = s * self.canvas.canvasy(evt.y) - evt.y# + self.canvas_margins[1]
        self.canvas.scale(Tkinter.ALL, 0, 0, s, s)
        self.canvas.x_rl *= s
        self.canvas.y_rl *= s
        bb = self.canvas.bbox(Tkinter.ALL)
        w = (bb[2] - bb[0]) * 1.5
        h = (bb[3] - bb[1]) * 1.5
        bb = (bb[0] - w, bb[1] - h, bb[2] + w, bb[3] + h)
        self.canvas['scrollregion'] = bb
        self.canvas.xview(Tkinter.MOVETO, (x0 - bb[0]) / (bb[2] - bb[0]))
        self.canvas.yview(Tkinter.MOVETO, (y0 - bb[1]) / (bb[3] - bb[1]))

    def _zoom_rect_mark(self, evt):
        self.canvas.x_zr = float(self.canvas.canvasx(evt.x))
        self.canvas.y_zr = float(self.canvas.canvasy(evt.y))

    def _mouse_btn_1(self, evt):
        if self.canvas.zoom_rect is None:
            if self.canvas.ruler is None:
                x0 = self.canvas.canvasx(evt.x)
                y0 = self.canvas.canvasy(evt.y)
                self.canvas.ruler = self.canvas.create_line(x0, y0, x0, y0, arrow=Tkinter.BOTH, fill='#FFF')
                self.canvas.x_rl = x0
                self.canvas.y_rl = y0
            else:
                self.canvas.delete(self.canvas.ruler)
                self.canvas.ruler = None
        else:
            x1 = float(self.canvas.winfo_width()) - self.canvas_margins[0]
            sx = float(self.canvas.canvasx(evt.x))
            dx = abs(self.canvas.x_zr - sx)
            sx += self.canvas.x_zr
            y1 = float(self.canvas.winfo_height()) - self.canvas_margins[1]
            sy = float(self.canvas.canvasy(evt.y))
            dy = abs(self.canvas.y_zr - sy)
            sy += self.canvas.y_zr
            self.canvas.delete(self.canvas.zoom_rect)
            self.canvas.zoom_rect = None
            if abs(dx * dy) > 1.0e-12:
                s = (x1 / dx, y1 / dy)
                if s[0] < s[1]:
                    s = s[0]
                    y0 = 0.5 * (s * sy - y1)
                    x0 = 0.5 * s * (sx - dx)
                else:
                    s = s[1]
                    x0 = 0.5 * (s * sx - x1)
                    y0 = 0.5 * s * (sy - dy)
                self.scale /= s
                self.canvas.scale(Tkinter.ALL, 0, 0, s, s)
                self.canvas.x_rl *= s
                self.canvas.y_rl *= s
                bb = self.canvas.bbox(Tkinter.ALL)
                w = (bb[2] - bb[0]) * 1.5
                h = (bb[3] - bb[1]) * 1.5
                bb = (bb[0] - w, bb[1] - h, bb[2] + w, bb[3] + h)
                self.canvas['scrollregion'] = bb
                self.canvas.xview(Tkinter.MOVETO, (x0 - bb[0]) / (bb[2] - bb[0]))
                self.canvas.yview(Tkinter.MOVETO, (y0 - bb[1]) / (bb[3] - bb[1]))

    def _properties(self, evt):
        if self.canvas.ruler is not None:
            self.canvas.delete(self.canvas.ruler)
            self.canvas.ruler = -1
        i = self.canvas.find_closest(self.canvas.canvasx(evt.x), self.canvas.canvasy(evt.y))
        bb = self.canvas.bbox(i)
        bb = (bb[0] * self.scale, -bb[3] * self.scale, bb[2] * self.scale, -bb[1] * self.scale)
        tags = self.canvas.gettags(i)
        tkMessageBox.showinfo('Element information', 'Layer %s\nVertices: %s\nApproximate bounding box:\n(%g, %g) - (%g, %g)' % ((tags[0][1:], tags[1][1:]) + bb), parent=self.canvas)

    def _save_screenshot(self, *args):
        name = tkFileDialog.asksaveasfilename(filetypes=[('PNG', '*.png'), ('BMP', '*.bmp'), ('GIF', '*.gif'), ('JPEG', '*.jpg, *.jpeg'), ('TIFF', '*.tif, *.tiff')], initialfile=self.current_cell.get(), parent=self, title='Save screenshot as...')
        if len(name) > 0:
            i = name.rfind('.')
            if i < 0:
                fmt = 'png'
            else:
                fmt = name[i + 1:]
                name = name[:i]
            colors = [(None if x == '' else x) for x in self.colors]
            outlines = [(None if x == '' else x) for x in self.outlines]
            bb = (self.scale * self.canvas.canvasx(self.canvas_margins[0]), self.scale * self.canvas.canvasx(float(self.canvas.winfo_width())), -self.scale * self.canvas.canvasy(float(self.canvas.winfo_height())), -self.scale * self.canvas.canvasy(self.canvas_margins[1]))
            gds_image(self.cells[self.current_cell.get()], self.exclude_layers, name, fmt, colors, outlines, 1 / self.scale, bb, 2)


#def gds_view(cells=None, exclude_layers=[], style=None, show=True):
#    """
#    Plot the cells using the *matplotlib* module.
#
#    This function should be called only once, preferably at the end of
#    the file.
#    
#    Parameters
#    ----------
#    cells : array-like
#        The array of cells to be included in the plot. If ``None``, all
#        cells listed in ``Cell.cell_list`` are used.
#    exclude_layers : array-like
#        The array of layers to be excluded from the plot.
#    style : array-like
#        Drawing style for all layers. Each element is a dictionary
#        composed of ``**kwargs`` for a ``matplotlib.patches.Polygon``
#        object creation. Please see the **matplotlib** documentation for
#        all options. If ``None``, a default style set will be used.
#    show : bool
#        If false, matplotlib.pyplot.show() is not called, so that
#        the plot can be edited or new plots can be made before the
#        figure(s) are shown.
#
#    Examples
#    --------
#    >>> style = [{'fill': False}, {'fc': (1,0,0), 'hatch': '/'},
#    ...          {'fc': (0.7,0.7,0.7), 'alpha': 0.5}]
#    >>> gds_view(style=style)
#    """
#    if _matplotlib_error:
#        print "gdspy - ERROR: this function is disabled because the module matplotlib was not found."
#    else:
#        if cells == None:
#            cells = gdspy.Cell.cell_list
#        if style is None:
#            colors = [(0.90000000000000002, 0.0, 0.0), (0.25714285714285706, 0.90000000000000002, 0.0), (0.0, 0.51428571428571412, 0.90000000000000002), (0.90000000000000002, 0.0, 0.77142857142857191), (0.77142857142857146, 0.90000000000000002, 0.0), (0.0, 0.90000000000000002, 0.77142857142857113), (0.51428571428571412, 0.0, 0.90000000000000002), (0.90000000000000002, 0.51428571428571423, 0.0), (0.0, 0.90000000000000002, 0.25714285714285706), (0.0, 0.0, 0.90000000000000002), (0.90000000000000002, 0.0, 0.25714285714285784), (0.90000000000000002, 0.77142857142857146, 0.0), (0.0, 0.90000000000000002, 0.51428571428571412), (0.25714285714285706, 0.0, 0.90000000000000002), (0.90000000000000002, 0.25714285714285712, 0.0), (0.0, 0.90000000000000002, 0.0), (0.0, 0.25714285714285706, 0.90000000000000002), (0.90000000000000002, 0.0, 0.51428571428571412), (0.51428571428571446, 0.90000000000000002, 0.0), (0.0, 0.77142857142857146, 0.90000000000000002), (0.77142857142857191, 0.0, 0.90000000000000002), (0.82499999999999996, 0.33000000000000002, 0.24750000000000003), (0.33000000000000002, 0.82499999999999996, 0.24750000000000003), (0.24750000000000003, 0.49499999999999988, 0.82499999999999996), (0.82499999999999996, 0.24750000000000003, 0.66000000000000003), (0.66000000000000003, 0.82499999999999996, 0.24750000000000003), (0.24750000000000003, 0.82499999999999996, 0.82499999999999996), (0.65999999999999959, 0.24750000000000003, 0.82499999999999996), (0.82499999999999996, 0.65999999999999992, 0.24750000000000003), (0.24750000000000003, 0.82499999999999996, 0.49500000000000016), (0.33000000000000029, 0.24750000000000003, 0.82499999999999996), (0.82499999999999996, 0.24750000000000003, 0.33000000000000029), (0.82499999999999996, 0.82499999999999996, 0.24750000000000003), (0.24750000000000003, 0.82499999999999996, 0.66000000000000003), (0.49499999999999966, 0.24750000000000003, 0.82499999999999996), (0.82499999999999996, 0.49500000000000005, 0.24750000000000003), (0.24750000000000003, 0.82499999999999996, 0.33000000000000029), (0.24750000000000003, 0.33000000000000002, 0.82499999999999996), (0.82499999999999996, 0.24750000000000003, 0.49500000000000016), (0.49500000000000005, 0.82499999999999996, 0.24750000000000003), (0.24750000000000003, 0.66000000000000003, 0.82499999999999996), (0.82499999999999996, 0.24750000000000003, 0.82499999999999996), (0.75, 0.44999999999999996, 0.44999999999999996), (0.53571428571428559, 0.75, 0.44999999999999996), (0.44999999999999996, 0.62142857142857144, 0.75), (0.75, 0.44999999999999996, 0.7071428571428573), (0.70714285714285707, 0.75, 0.44999999999999996), (0.44999999999999996, 0.75, 0.70714285714285707), (0.62142857142857144, 0.44999999999999996, 0.75), (0.75, 0.62142857142857144, 0.44999999999999996), (0.44999999999999996, 0.75, 0.53571428571428559), (0.44999999999999996, 0.44999999999999996, 0.75), (0.75, 0.44999999999999996, 0.53571428571428603), (0.75, 0.70714285714285707, 0.44999999999999996), (0.44999999999999996, 0.75, 0.62142857142857144), (0.53571428571428559, 0.44999999999999996, 0.75), (0.75, 0.53571428571428559, 0.44999999999999996), (0.44999999999999996, 0.75, 0.44999999999999996), (0.44999999999999996, 0.53571428571428559, 0.75), (0.75, 0.44999999999999996, 0.62142857142857144), (0.62142857142857144, 0.75, 0.44999999999999996), (0.44999999999999996, 0.70714285714285707, 0.75), (0.7071428571428573, 0.44999999999999996, 0.75)]
#            hatches = ['/', '\\', 'x', '|', '-', '+']
#            style = [{'fill': False}] + [{'fc': color} for color in colors]
#            for hatch in hatches:
#                style += [{'fc': color, 'hatch': hatch} for color in colors]
#        for cell in cells:
#            pyplot.figure()
#            view = Viewport(pyplot.gca(), style)
#            for element in cell.elements:
#                element.draw(view, exclude_layers)
#            pyplot.axis('equal')
#            pyplot.title(cell.name)
#        if show:
#            pyplot.show()


def gds_image(cells=None, exclude_layers=[], image_name=None, image_format='png', colors=None, outlines=None, resolution=1, bounding_box=None, antialias=0):
    """
    Generates an image from each cell and saves them to files.
    
    Parameters
    ----------
    cells : gdspy.Cell or list
        Cell or list of cells to be included in the plot. If ``None``, all
        cells listed in ``Cell.cell_list`` are used.
    exclude_layers : array-like
        The array of layers to be excluded from the plot.
    image_name : string
        Name of the output image without extension. If ``None``, the cell
        names will be used. If ``cells`` contains more than 1 element, the
        name of the output file will be the corresponding cell name with
        ``image_name`` as a prefix.
    image_format : string
        The supported image formats are bmp, gif, jpg, pcx, png, ppm, and
        tiff.
    colors : array-like
        Colors (RGB tuple) for each layer.
    outlines : array-like
        Outline colors (RGB tuple) for each layer.
    resolution : number
        Geometry scaling in pixels per user units.
    bounding_box : array-like[4]
        Area of the geometry to be draw on the output file in the format
        (min_x, max_x, min_y, max_y). If ``None``, the whole extent of
        each cell will be used.
    antialias : non-negative integer
        Level of anti-aliasing to be used when drawing the image.

    Examples
    --------
    >>> colors = [(255,0,0), (0,255,0), (0,0,255)]
    >>> gds_image(image_name='/output_folder/layout', colors=colors)
    """
    if _pil_error:
        print "gdspy - ERROR: this function is disabled because the modules Image and ImageDraw were not found."
    else:
        if colors is None:
            colors = [None, (229, 0, 0), (65, 229, 0), (0, 131, 229), (229, 0, 196), (196, 229, 0), (0, 229, 196), (131, 0, 229), (229, 131, 0), (0, 229, 65), (0, 0, 229), (229, 0, 65), (229, 196, 0), (0, 229, 131), (65, 0, 229), (229, 65, 0), (0, 229, 0), (0, 65, 229), (229, 0, 131), (131, 229, 0), (0, 196, 229), (196, 0, 229), (210, 84, 63), (84, 210, 63), (63, 126, 210), (210, 63, 168), (168, 210, 63), (63, 210, 210), (168, 63, 210), (210, 168, 63), (63, 210, 126), (84, 63, 210), (210, 63, 84), (210, 210, 63), (63, 210, 168), (126, 63, 210), (210, 126, 63), (63, 210, 84), (63, 84, 210), (210, 63, 126), (126, 210, 63), (63, 168, 210), (210, 63, 210), (191, 114, 114), (136, 191, 114), (114, 158, 191), (191, 114, 180), (180, 191, 114), (114, 191, 180), (158, 114, 191), (191, 158, 114), (114, 191, 136), (114, 114, 191), (191, 114, 136), (191, 180, 114), (114, 191, 158), (136, 114, 191), (191, 136, 114), (114, 191, 114), (114, 136, 191), (191, 114, 158), (158, 191, 114), (114, 180, 191), (180, 114, 191)]
        if outlines is None:
            outlines = [((255, 255, 255) if x is None else None) for x in colors]
        if cells == None:
            cells = Cell.cell_list
        elif cells.__class__ != [].__class__:
            cells = [cells]
        if antialias > 0:
            resolution = resolution * (antialias + 1)
        for cell in cells:
            pol_dict = cell.get_polygons(by_layer=True)
            if bounding_box is None:
                canvas = Canvas(colors, outlines, resolution)
                #for element in cell.elements:
                #    element.draw(canvas, exclude_layers)
                for layer in pol_dict.iterkeys():
                    if layer not in exclude_layers:
                        for polygon in pol_dict[layer]:
                            canvas.add_polygon(layer, polygon)
                bb = numpy.array(canvas.bounding_box)
                margin = numpy.sqrt(0.01 * (bb[1] - bb[0]) * (bb[3] - bb[2]))
                bb += numpy.array([-margin, margin, -margin, margin])
            else:
                bb = bounding_box
            canvas = Canvas(colors, outlines, resolution, bb)
            #for element in cell.elements:
            #    element.draw(canvas, exclude_layers)
            for layer in pol_dict.iterkeys():
                if layer not in exclude_layers:
                    for polygon in pol_dict[layer]:
                        canvas.add_polygon(layer, polygon)
            if image_name is None:
                name = cell.name + '.' + image_format
            elif len(cells) > 1:
                name = image_name + cell.name + '.' + image_format
            else:
                name = image_name + '.' + image_format
            if antialias > 0:
                canvas.image.resize((canvas.width // (antialias + 1), canvas.height // (antialias + 1)), Image.ANTIALIAS).save(name)
            else:
                canvas.image.save(name)
