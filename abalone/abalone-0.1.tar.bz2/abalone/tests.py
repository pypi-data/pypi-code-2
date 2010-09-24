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

import unittest

from abalone import Marble, Group, Game
class GameLogic(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_valid_groups(self):
        '''Assert that the groups of 1/2/3 marbles are valid.'''

        groups = (
                [(5,5)],
                [(5,5), (5,6)],
                [(5,5), (5,6), (5,7)],
                )
        for group in groups:
            self.game.start(group)
            group = Group(self.game.marbles.get_pos(group))
            self.assert_(group.is_valid())

    def test_group_ordering(self):
        '''Assert that the marbles of a group are ordered by their position'''

        group = [(2,2), (3,3), (1,1)]
        ordered = [(1,1), (2,2), (3,3)]

        group = Group([ Marble(pos, 1) for pos in group ])
        self.assert_(group.is_valid())
        self.assert_(group.positions == ordered)


    def test_invalid_groups(self):
        '''Assert that the groups with any of this characteristics
        is invalid:
            - Has not between 1 and 3 members.
            - Isn't in line.
            - Has invalid positions.
            - Has repeated positions.
            - There're enemys marbles in it.
        '''

        groups = (
                [], #no suficient members
                [(5,5), (5,6), (5,7), (5,8)], #too many members
                [(5,5), (5,7), (5,8)], #not inline
                [(10,10), (5,5)], #invalid positions
                [(5,5), (5,5), (6,6)], #repeated positions
                )

        groups_e = (
                [(5,5), (5,6)], #one team
                [(5,5), (5,7)], #the other (the enemy)
                )
        
        for group in groups:
            self.game.start(group)
            group = Group(self.game.marbles.get_pos(group))
            self.assert_(group.is_valid() == False)

        self.game.start(groups_e[0], groups_e[1])
        group = Group(self.game.marbles.get_pos(groups_e[0] + groups_e[1]))
        self.assert_(group.is_valid() == False)

    def test_free_move(self):
        '''Assert that a group of 1/2/3 marbles can move freelly
        in the center of the board in all directions, back to their
        initial position.'''

        groups = (
                [(5,5)],
                [(5,5), (5,6)],
                [(5,5), (5,6), (5,7)],
                )

        for group in groups:
            self.game.start(group)
            group = Group(self.game.marbles.get_pos(group))
            for direction in range(6):
                self.game.move(group, direction)
                self.assert_(group.is_valid())
            self.assert_(group.positions in groups)

    def test_out_of_matrix(self):
        '''Assert that a group can't move out of the matrix.'''

        groups = (
                [(1,1)],
                [(1,1), (1,2)],
                [(1,1), (1,2), (1,3)],
                )

        for group in groups:
            self.game.start(group)
            self.assertRaises(AssertionError, self.game.move, group, 2)
            self.assertRaises(AssertionError, self.game.move, group, 3)

    def test_is_pushable(self):
        '''Assert that a group can push an other with less members and
        that both are moved once.'''

        blacks = (
                [(1,1), (2,2)],
                [(1,1), (2,2), (3,3)],
                [(1,1), (2,2), (3,3)],
                )

        whites = (
                [(3,3)],
                [(4,4)],
                [(4,4), (5,5)],
                )

        black_results = (
                [(2,2), (3,3)],
                [(2,2), (3,3), (4,4)],
                [(2,2), (3,3), (4,4)],
                )

        white_results = (
                [(4,4)],
                [(5,5)],
                [(5,5), (6,6)],
                )

        for b, w, br, wr in zip(blacks, whites, black_results, white_results):
            self.game.start(b, w)
            black = Group(self.game.marbles.get_pos(b))
            white = Group(self.game.marbles.get_pos(w))
            self.game.move(black, 0)
            self.assert_(black.is_valid())
            self.assert_(white.is_valid())
            self.assert_(black.positions == br)
            self.assert_(white.positions == wr)

    def test_is_not_pushable(self):
        '''Assert that you can't push an enemy if:
            - Your group hasn't more marbles.
            - There's a marble that it's yours after the enemy.
            - Your movement is lateral.
        '''

        blacks = (
                [(1,1), (2,2), (3,3)],
                [(1,1), (2,2)],
                [(1,1)],
                [(1,1), (2,2), (3,3), (6,6)],
                [(1,1), (2,2), (3,3), (5,5)],
                [(1,1), (2,2), (4,4)],
                [(1,1), (1,2), (1,3)],
                [(1,1), (1,2)],
                )

        whites = (
                [(4,4), (5,5), (6,6)],
                [(3,3), (4,4)],
                [(2,2)],
                [(4,4), (5,5)],
                [(4,4)],
                [(3,3)],
                [(2,2), (2,3), (2,4)],
                [(2,2), (2,3)],
                )

        for black, white in zip(blacks, whites):
            self.game.start(black, white)
            self.assertRaises(AssertionError, self.game.move, black, 0)

    def test_killed(self):
        '''Assert that if you push the enemy out of the matrix,
        his marble gets killed.'''

        black = [(4,4), (4,5), (4,6)]
        white = [(4,7), (4,8)]

        black_result = [(4,5), (4,6), (4,7)]
        white_result = [(4,8)]

        self.game.start(black, white)
        black = Group(self.game.marbles.get_owner(1))
        white = Group(self.game.marbles.get_owner(-1))
        self.game.move(black, 1)
        black = Group(self.game.marbles.get_owner(1))
        white = Group(self.game.marbles.get_owner(-1))
        self.assert_(black.is_valid())
        self.assert_(white.is_valid())
        self.assert_(black.positions == black_result)
        self.assert_(white.positions == white_result)

    def test_game(self):
        '''Test a little game with only the blacks moving until the final.'''

        black = [(7,5), (5,3), (5,6), (5,7), (5,8), (5,9), (4,5),
                (4,6), (4,7), (4,8), (3,4), (3,5), (3,6), (3,7)]

        white = [(4,2), (3,1), (3,2), (2,1), (2,2), (2,3), (2,4),
                (2,5), (2,6), (1,1), (1,2), (1,3), (1,4), (1,5)]

        movements = (
                ([(5,9), (4,8), (3,7)], 3),
                ([(5,8), (4,7), (3,6)], 3),
                ([(5,7), (4,6), (3,5)], 3),
                ([(4,8), (3,7), (2,6)], 3),
                ([(4,7), (3,6), (2,5)], 3),
                ([(4,6), (3,5), (2,4)], 3),
                )

        self.game.start(black, white)
        for position, direction in movements:
            self.game.move(position, direction)
        self.assert_(self.game.get_looser() == -1)


import tk
class Tk(unittest.TestCase):

    def setUp(self):
        self.game = tk.Game()

if __name__ == '__main__':
    unittest.main()
