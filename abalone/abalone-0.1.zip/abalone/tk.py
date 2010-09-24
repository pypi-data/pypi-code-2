#Copyright (C) 2010 Unai Zalakain De Graeve
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''Tkinter interface for abalone.'''

import abalone
from library import C, circle, get_coord
import config

from Tkinter import Tk, Canvas, Frame, Button
from Tkinter import TOP, BOTTOM, X, BOTH
from math import pi, sqrt

from os.path import join, dirname
PATH = dirname(__file__)

class Group(abalone.Group):
    '''Nothing, for the moment.'''
    pass

#load the players conf
Players = {
        abalone.BLACK: config.Players.Black(abalone.BLACK),
        abalone.WHITE: config.Players.White(abalone.WHITE),
        }

class Board(Canvas):
    '''Board(*args, **kwargs) -> Abalone board in Tkinter Canvas.
    
    *args, **kwargs -> arguments for Tkinter.Canvas'''

    matrix = abalone.Matrix()
    vps = [ d * pi / 180 for d in range(360, 0, -60) ]
    selected = Group()

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.bind('<Button-1>', self.update_selection)

    def resize(self):
        '''resize() -> resize all the canvas elements and draw them.'''
        self.update_size()
        self.draw_board()
        self.draw_holes()
        self.draw_marbles()

    def update_size(self):
        '''update_size() -> update the size of the board.'''
        #get the canvas size and his center
        self.size = C(self.winfo_width(), self.winfo_height())
        self.center = C(*[ c/2.0 for c in self.size ])

        #if the canvas width is smaller that his height, the edge is the width/2
        if self.size.x < self.size.y:
            self.edge = self.size.x / 2.0
            #get the side from the edge
            self.side = sqrt(3/4.0 * self.edge ** 2) 
        #else, the side is height/2
        else:
            self.side = self.size.y / 2.0
            #get the edge from the size
            self.edge = sqrt(4/3.0 * self.side ** 2)

    def draw_board(self):
        '''draw_board() -> draw the board.'''
        #get the right coords and then make the simmetry with the left ones
        right = [(self.edge/2.0, self.side), (self.edge, 0), (self.edge/2.0, -self.side)]
        left = [ (-x, y) for (x, y) in right ]

        #center the coords, convert them to integers and unpack them
        coords = []
        [ (coords.append(int(self.center.x + x)), coords.append(int(self.center.y + y))) for (x,y) in right + left[::-1] ]

        #draw the polygon
        self.delete(config.Board.tag)
        self.create_polygon(
                *coords, 
                fill=config.Board.fill, 
                tags=config.Board.tag)
    
    def draw_holes(self):
        '''draw_holes() -> draw board holes.'''
        self.delete(config.Holes.tag)
        for pos in self.matrix:
            t, b = circle(self.get_coord(pos), self.edge / 9)
            self.create_oval(
                    t.x, t.y, b.x, b.y, 
                    fill=config.Holes.fill, 
                    outline=config.Holes.outline,
                    tags=config.Holes.tag)

    def draw_marbles(self):
        '''draw_marbles() -> draw the marbles.'''
        self.selected = Group()
        self.delete(config.Marbles.tag)
        for marble in self.master.marbles:
            t, b = circle(self.get_coord(marble['position']), self.edge / 8)
            marble.box = t, b
            marble.id = self.create_oval(
                    t.x, t.y, b.x, b.y, 
                    fill=Players[marble['owner']].fill, 
                    tags=config.Marbles.tag)

    def update_selection(self, e):
        '''update_selection(event) -> update self.selected with the marble
        on coordinates event.x and event.y, if any.'''
        def select(marble):
            self.itemconfigure(marble.id, fill=config.Marbles.selected)
            return marble
        def deselect(marble):
            self.itemconfigure(marble.id, fill=Players[marble['owner']].fill)
            return marble

        for marble in self.master.marbles:
            t, b = marble.box
            if t.x < e.x < b.x and t.y > e.y > b.y:
                if marble in self.selected:
                    self.selected.remove(deselect(marble))
                    if not self.selected.is_valid():
                        [ deselect(marble) for marble in self.selected ]
                        self.selected = Group([])
                else:
                    assert marble['owner'] == self.master.current
                    self.selected = Group(self.selected + [marble])
                    if self.selected.is_valid():
                        select(marble)
                    else:  
                        self.selected.remove(marble)
        
    def get_coord(self, pos):
        '''get_coord(position) -> get coordinates for the given position.'''
        return get_coord(self.center, self.edge, pos, self.vps[self.master.current.vp])
   

class Movement(Frame):
    '''Movement(*args, **kwargs) -> Frame with movement buttons for
    the marbles in the canvas.

    *args, **kwargs -> arguments for Tkinter.Frame.'''
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        Button(self, command=lambda: self.master.move(0), bitmap='@' + join(PATH, 'images/0.xbm')).grid(row=0, column=1)
        Button(self, command=lambda: self.master.move(1), bitmap='@' + join(PATH, 'images/1.xbm')).grid(row=1, column=1)
        Button(self, command=lambda: self.master.move(2), bitmap='@' + join(PATH, 'images/2.xbm')).grid(row=2, column=1)
        Button(self, command=lambda: self.master.move(3), bitmap='@' + join(PATH, 'images/3.xbm')).grid(row=2, column=0)
        Button(self, command=lambda: self.master.move(4), bitmap='@' + join(PATH, 'images/4.xbm')).grid(row=1, column=0)
        Button(self, command=lambda: self.master.move(5), bitmap='@' + join(PATH, 'images/5.xbm')).grid(row=0, column=0)

class ViewPoint(Frame):
    '''ViewPoint(*args, **kwargs) -> Frame with buttons for updating
    the viewpoint of the board for the current player.

    *args, **kwargs -> arguments for Tkinter.Frame.'''
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        def slc(d):
            self.master.current.vp = (self.master.current.vp + d) % 6

        Button(self,
                command=lambda: (slc(1), self.master.board.draw_marbles()),
                text='left',
                ).grid(row=0, column=0)

        Button(self,
                command=lambda: (slc(-1), self.master.board.draw_marbles()),
                text='right',
                ).grid(row=0, column=1)

class Game(abalone.Game, Tk):
    '''Game() -> new Tkinter interface for abalone.'''
    def __init__(self):
        super(Game, self).__init__()

        Tk.__init__(self)
        self.title = 'Abalone'
        self.bind('<Configure>', self.resize)
        self.minsize(400, 400)
        self.maxsize(1000, 1000)
        
    def resize(self, e):
        '''resize(event) -> update the board size
        and resize it with event.x and event.y.'''
        try:
            self.board.configure(width=self.winfo_width(), height=self.winfo_height())
            self.board.resize()
        except AttributeError:
            pass

    def start(self, *args, **kwargs):
        '''start(black=(), white=()) -> start a new abalone game.

        black -> positions for the black marbles.
        white -> positions for the white marbles.'''
        super(Game, self).start(*args, **kwargs)
        self.current = Players[self.current]

        self.board = Board(master=self, width=self.winfo_reqwidth(), height=self.winfo_reqheight())
        self.movement = Movement(master=self)
        self.viewpoint = ViewPoint(master=self)

        self.movement.pack(side=BOTTOM, fill=X)
        self.viewpoint.pack(side=BOTTOM, fill=X)
        self.board.pack(side=TOP, fill=BOTH)
        self.board.resize()

    def next(self):
        '''next() -> change the current player.'''
        if self.current == abalone.BLACK:
            self.current = Players[abalone.WHITE]
        else:
            self.current = Players[abalone.BLACK]

    def move(self, direction):
        '''move(direction) -> move the marbles selected in board in direction.
        
        direction -> direction of movement in range(6).'''
        direction = (direction + self.current.vp) % 6
        super(Game, self).move(self.board.selected, direction)

        self.next()
        looser = self.get_looser()
        if looser:
            print looser
            self.stop()
        self.board.draw_marbles()

    def stop(self):
        '''stop() -> destroy the current game.'''
        self.board.destroy()
        self.movement.destroy()
        self.viewpoint.destroy()

