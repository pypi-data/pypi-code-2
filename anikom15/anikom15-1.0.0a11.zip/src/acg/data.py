# Copyright 2010 Westley Martinez
#
# This file is part of Anikom15's Computer Game (ACG).
# ACG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ACG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ACG.  If not, see <http://www.gnu.org/licenses/>.
"""Operations for storing and retrieving game data."""

import sys
import os
import getpass
import time
import csv

def new(name):
    """Checks if a csv file is empty."""
    scorereader = csv.reader(open(name, 'r'))
    if scorereader.line_num == 0:
        return True
    else:
        return False


def save(score, playtime):
    """Saves score and playtime to a file along with name and time."""
    if os.name == 'posix':
        try:
            filename = os.path.join(os.environ['XDG_DATA_HOME'],
                                    'anikom15.score')
        except:
            filename = os.path.expanduser(os.path.join('~', '.local', 'share',
                                                       'anikom15.score'))
    elif os.name == 'nt':
        filename = os.path.join(os.environ['APPDATA'], 'anikom15.score.txt')
    else:
        return None, None
    scorewriter = csv.writer(open(filename, 'w'))
    if new(filename):
        scorewriter.writerow(['Username', 'Date', 'Score', 'Time'])
    scorewriter.writerow([getpass.getuser(), time.time(), score, playtime])
    return getpass.getuser(), filename
