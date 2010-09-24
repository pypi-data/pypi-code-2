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

class Board:
    tag = 'board'
    fill = '#777777'

class Holes:
    tag = 'hole'
    fill = '#FFFFFF'
    outline = '#FFFFFF'

class Marbles:
    tag = 'marble'
    selected = '#555555'

class Players:
    class Black(int):
        fill = '#000000'
        vp = 0
        positions = [
                       (3,3), (3,4), (3,5),
             (2,1), (2,2), (2,3), (2,4), (2,5), (2,6),
                (1,1), (1,2), (1,3), (1,4), (1,5),
                ]

    class White(int):
        fill = '#FFFFFF'
        vp = 3
        positions = [
                (9,5), (9,6), (9,7), (9,8), (9,9),
            (8,4), (8,5), (8,6), (8,7), (8,8), (8,9),
                      (7,5), (7,6), (7,7),
                ]
