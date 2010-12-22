#~ pyaeso is a python package that makes access to the Alberta, Canada's
#~ Electric System Operator's (AESO) Energy Trading System (ETS) easier.

#~ Copyright (C) 2009 Keegan Callin

#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see
#~ <http://www.gnu.org/licenses/gpl-3.0.html>.

'''Prints market participants in alphabetical order according to AESO ETS.'''

# Standard library imports
import sys
from StringIO import StringIO
import datetime
from pprint import pprint

# 3rd Party Libraries
from pyaeso import ets

def  main():
    f = ets.urlopen_asset_list()
    assets = list(ets.parse_asset_list_file(f))
    f.close()

    # Remove duplicates from list and sort
    participants = list(set([a.participant_name for a in assets]))
    participants.sort()

    print '''Market Participants in Alphabetical Order According to AESO ETS'''
    for p in participants:
        print repr(p)

    return(0)


if __name__ == '__main__':
    sys.exit(main())
