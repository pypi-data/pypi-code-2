# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: stefaan.himpe@gmail.com

import re
import CppCommentStripper
from IncludeFile import IncludeFile

ANGULAR_INCLUDEFILE_PATTERN = re.compile('^#include\s+<(?P<includefile>[^>"]+)>')
QUOTED_INCLUDEFILE_PATTERN = re.compile('^#include\s+"(?P<includefile>[^"]+)"')

class IncludeFileFinder(object):
    """
    Parses a file or a code fragment to extract all includes.
    """
    def __init__(self, code=""):
        """
        IncludeFileFinder expects to be initialized 
        with a string containing the complete code
        inside the header file
        """
        self.code = code
        self.include_files = []
        self.loc = 0

    def parse(self):
        """
        parse first strips the comments and strings
        from the code (to avoid false positives), 
        then extracts the header files

        #ifdef and friends are ignored
        """
        s = CppCommentStripper.CppCommentStripper()
        c = s.strip_comments(self.code)
        self.loc = c.count(";")
        for line in c.splitlines():
            self.parse_line(line)

    def parse_line(self, line):
        """
        parse a single line of text to extract the
        #include directive if one is present
        """
        m = ANGULAR_INCLUDEFILE_PATTERN.match(line)
        if m:
            self.include_files.append(IncludeFile(m.group('includefile'), 'Angular'))
        m = QUOTED_INCLUDEFILE_PATTERN.match(line)
        if m:
            self.include_files.append(IncludeFile(m.group('includefile'), 'Quoted'))

    def get_raw_parse_result(self):
        """
        return the data structure created by the parser
        """
        return self.include_files

    def get_no_of_statements(self):
        """
        return how many ";" were found in the file
        """
        return self.loc

if __name__ == '__main__' :
    code = r"""
#include "Cad_int.h"
#include "CadBgaData.h"
#include "RegularPadGroup.h"
#include "CornerPadGroup.h"
#include "CenterPadGroup.h"
#include "SidePadGroup.h" // and some comment
#include "SaveImageInfo.h"
#include <io.h>
#include "..\env\ParamFile.h"
//#include "DontFindMe.h"

/*
#include "orme.h"  // doesn't work correctly!
*/

#include "..\env\linkedcontrol.h"

/* TEXT CONSTANT FOR ENUMERATION */
const WORD TxtCompType[]        = { TXT_CMP_MODL_FOURSIDED, TXT_CMP_MODL_TWOSIDED, TXT_CMP_MODL_IRREGULAR, TXT_CMP_MODL_BGA, TXT_CMP_MODL_LEADLESS, TXT_CMP_MODL_PGA, TXT_CMP_MODL_LGA, NULL };
const WORD TxtScanDir[]         = {TXT_MMI2_VERTICAL, TXT_MMI2_HORIZONTAL, TXT_MMI2_CLOCKWISE, TXT_MMI2_COUNTERCLOCKWISE, NULL};
const WORD TxtPadGroupType[]    = {TXT_CMP_MODL_FOURSIDED, TXT_CMP_MODL_FOURSIDED, TXT_CMP_MODL_FOURSIDED, TXT_CMP_MODL_CORNER, TXT_CMP_MODL_CENTER, TXT_CMP_MODL_IRREGULAR, TXT_CMP_MODL_SIDEPAD, NULL};
const WORD TxtCornerLayout[]    = {TXT_CMP_MODL_4CORNERS, TXT_CMP_MODL_4CORNERS_1PIN1,TXT_CMP_MODL_1PIN1, TXT_CMP_MODL_3CORNERS, NULL};
const WORD TxtCornerPadOrient[] = {TXT_CMP_MODL_45DEGREES, TXT_CMP_MODL_0DEGREES, NULL};
const WORD TxtComponentSide[]   = {TXT_CMP_MODL_COMPSIDE_LEFT, TXT_CMP_MODL_COMPSIDE_BOTTOM, TXT_CMP_MODL_COMPSIDE_RIGHT, TXT_CMP_MODL_COMPSIDE_TOP, NULL}; 
const WORD TxtBumpedComponent[] = {TXT_MMI2_NO, TXT_MMI2_YES, NULL}; 
"""    
    Ifinder = IncludeFileFinder(code)
    Ifinder.parse()
    include_files = Ifinder.get_raw_parse_result()
    print include_files
