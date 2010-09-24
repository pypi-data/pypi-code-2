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

'''Game logic of Abalone'''

from operator import add, sub
from gettext import gettext as _

from library import NoNegIndexList, Reductors

#representation of teams.
#NOTE: they can't be 0.
BLACK = 1
WHITE = -1

class Matrix(list):
    '''Matrix() -> list with all the positions of an abalone's board.'''

    def __init__(self):
        rows = range(1, 10)
        ranges = zip([1] * 5 + range(2, 6), range(6, 10) + [10] * 5)

        self.rows = NoNegIndexList(rows)
        self.columns = NoNegIndexList(rows)

        rows = iter(rows)
        for r in ranges:
            row = rows.next()
            self.extend([ (row, column) for column in range(*r) ])

class Marble(dict):
    '''Marble() -> dict with 'position' and 'owner' 
    keys that represents an abalone's marble.'''

    def __init__(self, position, owner):
        self['position'] = position
        self['owner'] = owner

class MarbleManager(list):
    '''MarbleManager(Marbles) -> list of Marble objects with special
    methods get_pos and get_owner.'''

    def get_pos(self, positions):
        '''get_pos(positions) -> get the Marble objects that have their
        position key in positions.
        
        positions -> list of (row, column) tuples.'''
        return [ marble for marble in self if marble['position'] in positions ]

    def get_owner(self, owner):
        '''get_owner(owner) -> get the Marble objects that have their
        owner key == owner.
        
        owner -> BLACK or WHITE'''
        return [ marble for marble in self if marble['owner'] == owner ]

class Group(list):
    '''Group(Marbles) -> list of Marble objects with special methods
    update and is_valid.'''

    def __init__(self, marbles=[]):
        assert all([ isinstance(marble, Marble) for marble in marbles ]), self.__doc__
        self.extend(sorted(marbles, key=lambda marble: marble['position']))

    def update(self, new):
        '''update(updated_marbles) -> update the position attribute of
        the marbles in the Group with the position attribute of others.
        
        updated_marbles -> updated marbles to get the position attr.'''
        for old_m, new_m in zip(self, new):
            old_m['position'] = new_m['position']

    def is_valid(self):
        '''is_valid() -> return bool saying if this Group is a valid one.
        If valid, set "owner" and "positions" attributes with the owner and
        the positions of the marbles.'''

        #must have between 1 and 3 members
        if not 1 <= len(self) <= 3:
            return False

        #the owner of all the marbles must be the same
        owners = [marble['owner'] for marble in self ]
        if not Reductors.equal(owners):
            return False
        self.owner = owners[0]

        #the position of the marbles must be in line
        positions = [ marble['position'] for marble in self ]
        if not len(positions) == 1:
            rows = [ pos[0] for pos in positions ]
            columns = [ pos[1] for pos in positions ]
            if not any((
                    Reductors.equal(rows) and Reductors.consec(columns),
                    Reductors.consec(rows) and Reductors.equal(columns),
                    Reductors.consec(rows) and Reductors.consec(columns))):
                return False
        self.positions = positions

        return True

class Logic(Matrix):
    '''Logic() -> group of methods with the game logic of abalone.'''
    marbles = []

    def is_in_matrix(self, group):
        '''is_in_matrix(group) -> return True if group is in Matrix,
        False otherways.
        
        group -> Group instance.'''
        return all([ marble['position'] in self for marble in group ])

    def get_moved(self, group, direction):
        '''get_moved(group, direction) -> return the group moved in direction.
        
        group -> Group instance.
        direction -> direction of movement, in range(6)'''
        diffs = 1, 1, 0, -1, -1, 0
        try:
            row_diff = diffs[direction + 1]
        except IndexError:
            row_diff = diffs[0]
        column_diff = diffs[direction]

        l = []
        for marble in group:
            try:
                row = self.rows[self.rows.index(marble['position'][0]) + row_diff]
                column = self.columns[self.columns.index(marble['position'][1]) + column_diff]
            except IndexError:
                pass
            else:
                if (row, column) in self:
                    l.append(Marble((row, column), marble['owner']))
        return Group(l)

    def get_obstacles(self, group, direction):
        '''get_obstacles(group, direction) -> return the obstacles when trying to move
        group in direction.
        
        group -> Group instance.
        direction -> direction of movement, in range(6).'''
        moved_group = self.get_moved(group, direction)
        diff = [ marble['position'] for marble in moved_group if marble not in group ]
        return Group([ marble for marble in self.marbles if marble['position'] in diff ])

    def is_lateral_move(self, group, direction):
        '''is_lateral_move(group, direction) -> return True if the movement
        of group in direction is a lateral move, False otherways.
        
        group -> Group instance.
        direction -> direction of movement, in range(6).'''
        moved_group = self.get_moved(group, direction)
        return all([ marble not in group for marble in moved_group ])

    def get_mirror_obstacles(self, group, direction):
        '''get_mirror_obstacles(group, direction) -> return the obstacles when
        trying to move group in direction len(group) times.
        
        group -> Group instance.
        direction -> direction of movement, in range(6).'''
        obstacles = []
        for movement in range(len(group)):
            obstacle = self.get_obstacles(group, direction)
            if not obstacle:
                break
            obstacles.extend(obstacle)
            group = self.get_moved(group, direction)
        return Group(obstacles)

    def is_pushable(self, group, mirror_obstacles):
        '''is_pushable(group, mirror_obstacles) -> return True if group
        can push the mirror_obstacles, False otherways.
        
        group -> Group instance
        mirror_obstacles -> obstacles returned by Logic.get_mirror_obstacles'''
        return all((
                mirror_obstacles.is_valid(),
                self.is_in_matrix(mirror_obstacles),
                len(group) > len(mirror_obstacles),
                ))

class Game(object):
    '''Game() -> An abalone game.'''

    logic = Logic()

    def start(self, black=(), white=()):
        '''start(black=(), white=()) -> start a new game. 
        
        black -> positions of the marbles of the black team.
        white -> positions of the marbles of the white team.'''
        self.marbles = MarbleManager(
                [ Marble(position, BLACK) for position in black ] + \
                [ Marble(position, WHITE) for position in white ]
                )
        self.current = BLACK
        self.initial = len(black), len(white)

    def get_looser(self):
        '''get_looser() -> get the looser team, False if no one.'''
        for team, initial in zip((BLACK, WHITE), self.initial):
            if initial - len(self.marbles.get_owner(team)) >= initial / (14/6.0):
                return team
        return False

    def next(self):
        '''next() -> switch the actual player.'''
        if self.current == BLACK:
            self.current = WHITE
        else:
            self.current = BLACK

    def move(self, positions_or_group, direction):
        '''move(positions_or_group, direction) -> move the positions_or_group
        in direction. raises AssertionError if the move isn't possible.

        positions_or_group -> position of the marbles of a Group instance with
        them.

        direction -> direction of the movement, in range(6).'''

        if isinstance(positions_or_group, Group):
            group = positions_or_group
        else:
            group = Group(self.marbles.get_pos(positions_or_group))

        self.logic.marbles = self.marbles

        assert group.is_valid() and self.logic.is_in_matrix(group), _('The group of marbles isn\'t valid.')
        assert group.owner == self.current, _('The marbles aren\'t yours.')

        obstacles = self.logic.get_obstacles(group, direction)

        if not obstacles:
            moved_group = self.logic.get_moved(group, direction)

        else: 
            assert not self.logic.is_lateral_move(group, direction), _('You can\'t push an enemy in a lateral move.')
            assert obstacles.is_valid()
            assert obstacles.owner is not self.current, _('You can\'t push your own marbles.')

            enemy = self.logic.get_mirror_obstacles(group, direction)
            assert self.logic.is_pushable(group, enemy), _('You can\'t push the enemy.')

            moved_enemy = self.logic.get_moved(enemy, direction)
            if len(enemy) > len(moved_enemy):
                self.marbles.remove(enemy[-1])
                enemy.pop(-1)
            enemy.update(moved_enemy)

            moved_group = self.logic.get_moved(group, direction)

        assert len(group) == len(moved_group) and moved_group.is_valid() and self.logic.is_in_matrix(moved_group), _('You can\'t move there.')
        group.update(moved_group)
