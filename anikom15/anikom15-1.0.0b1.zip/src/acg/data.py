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
import platform
import getpass
import time
import csv

def supported():
    """Returns true if saving is supported."""
    if os.name == 'posix' or os.name == 'nt':
        return True


def get_filename():
    """Get specific filename for platform."""
    if os.name == 'posix':
        try:
            return os.path.join(os.environ['XDG_DATA_HOME'],
                                    'anikom15-scores.csv')
        except:
            # XDG_DATA_HOME is not defined.
            return os.path.expanduser(os.path.join('~', '.local', 'share',
                                                   'anikom15-scores.csv'))
    elif os.name == 'nt':
        return os.path.join(os.environ['APPDATA'], 'anikom15-scores.csv')


def read():
    """Read scores and other data from file."""
    filename = get_filename()
    return csv.reader(open(filename, newline=''))


def save(score, playtime, version):
    """Saves score and playtime to a file along with name and time.
    
    Keyword arguments:
    score -- player's score
    playtime -- length of time the player played the game
    version -- acg's version

    """
    filename = get_filename()
    if filename is None:
        return None, None
    scorewriter = csv.writer(open(filename, 'a'))
    scorewriter.writerow([time.time(),
                          platform.system() + ' ' + platform.release(),
                          getpass.getuser(),
                          'Python ' + platform.python_version(),
                          'ACG ' + version, score, playtime / 1000])
    return getpass.getuser(), filename
