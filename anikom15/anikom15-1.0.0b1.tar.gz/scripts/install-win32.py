# Copyright 2010, 2011 Westley Martinez
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
"""Post-installation script for win32.  Used by distutils."""

import sys
import os

if sys.argv[1] == '-install':
    # Append .py to scripts
    os.rename(os.path.join(sys.prefix, 'Scripts', 'anikom15'),
              os.path.join(sys.prefix, 'Scripts', 'anikom15.py'))
    file_created(os.path.join(sys.prefix, 'Scripts', 'anikom15.py'))
    # Create desktop and start menu shortcuts
    desktop = get_special_folder_path("CSIDL_COMMON_DESKTOPDIRECTORY")
    startmenu = get_special_folder_path("CSIDL_COMMON_STARTMENU")
    create_shortcut(os.path.join(sys.prefix, 'Scripts', 'anikom15.py'),
                    "Launch Anikom15's Computer Game",
                    os.path.join(desktop, 'Anikom15.lnk'),
                    '', '',
                    os.path.join(sys.prefix, 'Icons', 'anikom15.ico'))
    file_created(os.path.join(desktop, 'Anikom15.lnk'))
    create_shortcut(os.path.join(sys.prefix, 'Scripts', 'anikom15.py'),
                    "Anikom15's Computer Game",
                    os.path.join(startmenu, 'Anikom15.lnk'),
                    '', '',
                    os.path.join(sys.prefix, 'Icons', 'anikom15.ico'))
    file_created(os.path.join(startmenu, 'Anikom15.lnk'))
elif sys.argv[1] == '-remove':
    pass
