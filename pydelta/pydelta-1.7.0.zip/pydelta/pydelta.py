# -*- coding: utf-8 -*-
#===========================================================================#
#                             PyDELTA                                       #
#                                                                           #
#                A General-Purpose Python Library for                       #
#        Reading Text Files in DELTA (DEscription Language for              #
#                          TAxonomy) Format                                 #
#                                                                           #
#                  Copyright 2008 Mauro J. Cavalcanti                       #
#                         maurobio@gmail.com                                #
#                                                                           #                  
#          Copyright 2010 Mauro J. Cavalcanti & Thomas Kluyver              #
#                  maurobio@gmail.com, takowl@gmail.com                     # 
#                                                                           #
#   This program is free software: you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published by    #
#   the Free Software Foundation, either version 3 of the License, or       #
#   (at your option) any later version.                                     #
#                                                                           #
#   This program is distributed in the hope that it will be useful,         #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#   GNU General Public License for more details.                            #
#                                                                           #
#   You should have received a copy of the GNU General Public License       #
#   along with this program. If not, see <http://www.gnu.org/licenses/>.    # 
#                                                                           #
#   REVISION HISTORY:                                                       #
#    Version 1.00, 04 Aug 2008 - Initial implementation (Mauro Cavalcanti)  #
#    Version 1.50, 09 Feb 2010 - Substantial reworking (Thomas Kluyver)     #
#    Version 1.51. 21 Feb 2010 - Minor bug fixes (Thomas Kluyver)           # 
#    Version 1.52, 23 Feb 2010 - Improved split function (Thomas Kluyver)   #
#    Version 1.53, 24 Feb 2010 - Changes to demo program (Mauro Cavalcanti) #
#    Version 1.60, 03 Jun 2010 - Load Intkey binary files (Thomas Kluyver)  #
#    Version 1.70, 21 Nov 2010 - Reworking internals (Thomas Kluyver)       #
#===========================================================================#
"""
This module reads and manipulates descriptive biological data stored
in the DELTA (DEscription Language for TAxonomy) format. For more details,
see:
http://www.delta-intkey.com/www/programs.htm

This is part of the FreeDELTA project:
http://freedelta.sourceforge.net/

===============
Usage example (uses grass genera example files):
from pydelta import deltafiles

Example = deltafiles.load("grass/chars", "grass/items", "grass/specs")
# One multistate character (char_type==CT['UM']), one numeric (CT['RN'])
print Example.chars[4].feature, Example.chars[4].states
print Example.chars[26].feature, Example.chars[26].unit

#Print their values out for each item that has them
for i, item in enumerate(Example.items):
    print ""
    print item.name
    if 4 in item.attributes:
        culm_state = item.attributes[4]
        if culm_state.isdigit(): # Some of them are "1/2", i.e. mixed.
            print " Culms:", culm_state, "(" + Example.chars[4].states[int(culm_state)-1] + ")"
        else:
            print " Culms:", culm_state
    if 26 in item.attributes:
        print " Spikelets", item.attributes[26], Example.chars[26].unit
"""
from __future__ import absolute_import
from . import structxt

#----- Character types
CT= {'UM':2, 'OM':3, 'IN':4, 'RN':5, 'TE':8}
CTNames = {2: "Multistate",
3: "Multistate (ordered)",
4: "Number (integer)",
5: "Number (decimal)",
8: "Text"}

pseudovalues = {"V":"Variable",
"U": "Unknown",
"-": "Not applicable"}

#---- Extreme character values
EXTRVAL_LOW  = 1  # extreme low value
EXTRVAL_HIGH = 2  # extreme high value

#---- Special character values
VARIABLE = -999999
UNKNOWN  = -999998
NOTAPPLI = -999997

#----- Delta character description class
class CharDescr(object):
    "The description of a single character, including its unit or possible states."
    def __init__(self):
        self.feature = ""
        self.unit = ""
        self.states = DeltaList()
        self.char_type = CT['UM']
        self.notes = ""
        self.images = []
        self.implicit = None # Will be replaced when an implicit value is read.
        
    def __repr__(self):
        return "<%s character: %s>" % (CTNames[self.char_type], self.feature)
        

#----- Delta item description class
class ItemDescr(object):
    "The description of a single item, including its attributes (character states)."
    def __init__(self):
        self.name = ""
        self.comment = ""
        self.attributes = {}
        self.images = []
        self.charlist = None
            
    def __repr__(self):
        return "<Item: %s>" % self.name
        
    def get_val_or_implicit(self, char):
        """
        Returns the value associated with this item for a given character
        number, or if this cannot be found, the implicit value. This will only
        work if the item has been linked to a DeltaCharList (this occurs
        automatically when a suitable specifications file is parsed).
        """
        if char in self.attributes:
            return self.attributes[char]
        return self.charlist[char].implicit


class DeltaList(list):
    """A list which uses the 1-based indexing of DELTA, rather than Python's
    0-based indexing. Negative indexing still works as is normal in Python, 
    (counting backwards from the end of the list)."""
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.insert(0, None)
    
    def __len__(self):
        return list.__len__(self) - 1
        
    def __iter__(self):
        temp = list.__iter__(self)
        next(temp)  # Throw away first item (blank)
        return temp
    
    def __repr__(self):
        return repr(self[1:])

#===== DeltaCharList ====================================================

class DeltaCharList(DeltaList):
    """
    A list of available characters, and possible states for each.
    Items can be retrieved using DELTA's 1-based indexing, so the first
    character is charlist[1], not charlist[0]. Negative indices work as
    normal, so charlist[-1] is the last item.
    
    Instantiate by passing in the filename. If a separate file of
    character notes is present, its name can be passed in to the argument
    cnotes_fname.
    
    If you don't want to parse the file when instantiating it, use the argument
    parse=False. The parse_characters (and parse_cnotes) method can then be
    called later.
    """
    #----- Constructor
    def __init__(self, fname): 
        super(DeltaCharList, self).__init__()
        self.fname = fname # name of Delta character list file
        self.cnotes_fname = None
        self.directives = []
        self.title = ""
        
    def __repr__(self):
        return "<DeltaCharList: %i characters>" % len(self)

#===== DeltaItemList ========================================================

class DeltaItemList(DeltaList):
    """
    A list of items (e.g. species). Individual items can be retrieved using
    DELTA's 1-based indexing (i.e. the first item is itemlist[1], not itemlist[0]).
    
    Instantiate simply by passing it the filename to use. If you don't want
    it to parse the file straight away, use the argument parse=False. The
    parse_items method can then be used later.
    """
    #----- Constructor
    def __init__(self, fname): 
        super(DeltaItemList, self).__init__()
        self.fname = fname # name of Delta items file
        self.directives = []
        self.title = ""
        
    def __repr__(self):
        return "<DeltaItemList: %i items>" % len(self)

#===== Delta ============================================================
class Delta(object):
    """
    An entire DELTA database, consisting of a list of characters (pass as
    chars_fname), a list of items (typically species or other taxa; pass as
    items_fname), and two optional files: a set of specifications for the
    database (pass as specs_fname) and a list of notes for specific characters
    (pass as cnotes_fname).
    
    Once set up, the data is accessible in .items and .chars
    """
    #----- Constructor
    def __init__(self, chars, items):
        self.chars = chars
        self.items = items
        # Link items to the character list so that they can look up implicit
        # values. This creates references, not copies!
        for item in items:
            item.charlist = chars
        self.specs = None
        
    def __repr__(self):
        return "<Delta: %i items × %i characters>" % (len(self.items), len(self.chars))

#===== Miscellaneous =====================================================

#----- Remove comments (delimited by < >) from a string
def remove_comments(src):
    "Cuts out any DELTA style <comments> in a string."
    return structxt.removechunks(src, "<", ">")

#----- Extracts comments from src string
def extract_comment(src):
    "Returns only the (first) <comment> from a DELTA file source line."
    left = src.find('<')+1
    right = src.find('>')
    return src[left:right]

#----- Expands a character range and returs a list of character numbers
def expand_range(src):
    "Turns a range '4-7' into a list [4,5,6,7]; used in parsing DELTA files."
    nchar = []
    if len(src) > 0:
        pos = src.find('-')
        if pos != -1:
            first = int(src[:pos])
            last  = int(src[pos+1:])
        else:
            return [int(src)]  # Only one number
        for j in range (first, last+1): 
            nchar.append(j)
        return nchar
