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

class CppCommentStripper(object):
    def __init__(self):
        def q(c):
            """Returns a regular expression that matches a region
               delimited by c, inside which c may be escaped with
               a backslash.
            """
            return r"%s(\\.|[^%s])*%s" % (c, c, c)

        self.single_quoted_string_pattern = q('"')
        self.double_quoted_string_pattern = q("'")
        self.c_comment_pattern = r"/\*.*?\*/"
        self.cpp_comment_pattern = r"//[^\n]*"

        self.rx = re.compile("|".join([self.single_quoted_string_pattern,
                                       self.double_quoted_string_pattern,
                                       self.c_comment_pattern,
                                       self.cpp_comment_pattern]),
                             re.DOTALL)

    def replace(self, x):
        """
        replaces a comment with an empty string
        """
        y = x.group(0)
        if y.startswith("/"):
            return ""
        return y

    def strip_comments(self, from_string):
        """
        find the comments in from_string and replace them with an empty string
        """
        return self.rx.sub(self.replace, from_string)

if __name__ == "__main__":
    code = r"""
#include "Cad_int.h"
#include <io.h> // this is the rups pardief pardaf
#include "..\env\ParamFile.h"
//#include "DontFindMe.h"

/************************************************************************************************************/

            /*
#include "orme.h"  // should work correctly!
*/

#include "..\env\linkedcontrol.h"

/* TEXT CONSTANT FOR ENUMERATION */
const WORD TxtCompType[]        = { TXT_CMP_MODL_FOURSIDED, TXT_CMP_MODL_TWOSIDED, TXT_CMP_MODL_IRREGULAR, TXT_CMP_MODL_BGA, TXT_CMP_MODL_LEADLESS, TXT_CMP_MODL_PGA, TXT_CMP_MODL_LGA, NULL };
""" 
    code2 = r"""
// constants for Enumeration parameters (Write/Read model files )
#include "..\mmi\mmi2.h"
    """
    stripper = CppCommentStripper()
    print "BEFORE:"
    print code
    print "AFTER:"
    print stripper.strip_comments(code)

    print "BEFORE:"
    print code2
    print "AFTER:"
    print stripper.strip_comments(code2)
