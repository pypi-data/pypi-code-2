#!/usr/bin/python

####################################################################################
#                                                                                  #
# Copyright (c) 2003 Dr. Conan C. Albrecht <conan_albrechtATbyuDOTedu>             #
#                                                                                  #
# This file is part of Picalo.                                                     #
#                                                                                  #
# Picalo is free software; you can redistribute it and/or modify                   #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation; either version 2 of the License, or                # 
# (at your option) any later version.                                              #
#                                                                                  #
# Picalo is distributed in the hope that it will be useful,                        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################
#                                                                                  
# The modules in the base/ directory are globally imported into the Python namespace
# when you run "from picalo import *".  They are separated here into different files
# for convenience (rather than putting it all in __init__.py).  See picalo/__init__.py
# for how they are globally imported into Picalo.
#                                                                                  
####################################################################################


# this code imports that basic functions and data types of Picalo.
# in each of these modules, the items listed __all__ variables are
# accessible globally to Picalo.  It is expected that the user runs
# "from picalo import *" to make this happen

# the order here is important!
from base.Boolean    import *
from base.Number     import *
from base.Currency   import *
from base.Error      import *
from base.Global     import *
from base.Calendar   import *
from base.Filer      import *
from base.Table      import *
from base.TableArray import *
from base.TableList  import *
from base.Project    import *
global_variables =         \
  base.Boolean.__all__    +\
  base.Number.__all__     +\
  base.Currency.__all__   +\
  base.Error.__all__      +\
  base.Global.__all__     +\
  base.Calendar.__all__   +\
  base.Filer.__all__      +\
  base.Table.__all__      +\
  base.TableArray.__all__ +\
  base.TableList.__all__  +\
  base.Project.__all__      
  
# modules that load with picalo.  these modules must be used with
# their names, as in "Simple.describe" rather than simply "describe".
global_modules = [
  'Benfords',
  'Crosstable',
  'Database',
  'Financial',
  'Grouping',
  'Simple',
  'Trending',
]

# built-in python modules that picalo ensures are loaded whenever
# the user runs "from picalo import *"
# yes, I arbitrarily decided which ones most users would want always
# included based on my experience with quite a few users using Picalo
python_modules = [
  'string',
  'sys',
  're',
  'random',
  'os',
  'os.path',
  'urllib',
  'xml.etree.ElementTree',
]
import xml.etree.ElementTree  # for some reason this has to be here or py2app/py2exe won't pick it up, even if listed in setup.py


# export the variables and modules in the __all__ variable
__all__ = global_variables + global_modules

# now that we're done setting up, show progress indicators for user code 
import base.Global
base.Global.use_progress_indicators(True)





