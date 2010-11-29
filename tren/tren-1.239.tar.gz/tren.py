#!/usr/bin/env python
# tren.py
# Copyright (c) 2010 TundraWare Inc.
# For Updates See:  http://www.tundraware.com/Software/tren

# Program Information

PROGNAME = "tren.py"
BASENAME = PROGNAME.split(".py")[0]
PROGENV  = BASENAME.upper()
INCLENV  = PROGENV + "INCL"
RCSID = "$Id: tren.py,v 1.239 2010/10/07 17:34:23 tundra Exp $"
VERSION = RCSID.split()[2]

# Copyright Information

CPRT         = "(c)"
DATE         = "2010"
OWNER        = "TundraWare Inc."
RIGHTS       = "All Rights Reserved."
COPYRIGHT    = "Copyright %s %s, %s  %s" % (CPRT, DATE, OWNER, RIGHTS)

PROGVER      = PROGNAME + " " + VERSION + (" - %s" % COPYRIGHT)
HOMEPAGE     = "http://www.tundraware.com/Software/%s\n" % BASENAME



#----------------------------------------------------------#
#            Variables User Might Change                   #
#----------------------------------------------------------#



#------------------- Nothing Below Here Should Need Changing ------------------#


#----------------------------------------------------------#
#                       Imports                            #
#----------------------------------------------------------#

import copy
import getopt
import glob
import os
import random
import re
import shlex
from   stat import *
import sys
import time

#####
# Imports conditional on OS
#####

# Set OS type - this allows us to trigger OS-specific code
# where needed.

OSNAME     = os.name
POSIX      = False
WINDOWS    = False

if OSNAME == 'nt':
    WINDOWS = True

elif OSNAME == 'posix':
    POSIX = True

# Set up Windows-specific stuff
    
if WINDOWS:

    # Try to load win32all stuff if it's available

    try:
        from win32api import GetFileAttributes, GetComputerName
        import win32con
        from win32file import GetDriveType
        from win32wnet import WNetGetUniversalName
        from win32security import *
        WIN32HOST = GetComputerName()
        WIN32ALL = True

    except:
        WIN32ALL = False

# Set up Unix-specific stuff

elif POSIX:

    # Get Unix password and group features

    import grp
    import pwd


# Uh oh, this is not an OS we know about

else:
    sys.stderr.write("Unsupported Operating System!  Aborting ...\n")
    sys.exit(1)
    

#----------------------------------------------------------#
#                 Aliases & Redefinitions                  #
#----------------------------------------------------------#



#----------------------------------------------------------#
#                Constants & Literals                      #
#----------------------------------------------------------#


#####
# General Program Constants
#####

MAXINCLUDES  =  1000        # Maximum number of includes allowed - used to catch circular references
MAXNAMELEN   =  255         # Maximum file or directory name length
MINNAMELEN   =  1           # Minimum file or directory name length

#####
# Message Formatting Constants
#####

# Make sure these make sense: ProgramOptions[MAXLINELEN] > PADWIDTH + WRAPINDENT
# because of the way line conditioning/wrap works.

PADCHAR      =  " "         # Padding character
PADWIDTH     =  30          # Column width
LSTPAD       =  13          # Padding to use when dumping lists
WRAPINDENT   =   8          # Extra indent on wrapped lines
MINLEN       =  PADWIDTH + WRAPINDENT + 1  # Minimum line length


#####
# Command Line Option Strings
#####

# List all legal command line options that will be processed by getopt() later.
# We exclude -I here because it is parsed manually before the getopt() call.

OPTIONSLIST  =  "A:abCcde:fhi:P:qR:r:S:T:tvw:Xx" # All legal command line options in getopt() format


#####
# Literals
#####

ARROW        =  "--->"          # Used for formatting renaming messages
ASKDOREST    =  "!"             # Do rest of renaming without asking
ASKNO        =  "N"             # Do not rename current file
ASKQUIT      =  "q"             # Quit renaming all further files
ASKYES       =  "y"             # Rename current file
COMMENT      =  "#"             # Comment character in include files
DEFINST      =  0               # Default replacement instance
DEFLEN       =  80              # Default output line length
DEFSEP       =  "="             # Default rename command separator: old=new
DEFSUFFIX    =  ".backup"       # String used to rename existing targets
DEFESC       =  "\\"            # Escape character
INCL         =  "I"             # Include file command line option
INDENT       =  "    "          # Indent string for nested messages
NULLESC      =  "Escape string"                   # Cannot be null
NULLRENSEP   =  "Old/New separator string"        # Cannot be null
NULLSUFFIX   =  "Forced renaming suffix string"   # Cannot be null
OPTINTRO     =  "-"             # Option introducer
PATHDELUNIX  =  ":"             # Separates include path elements on Unix systems
PATHDELWIN   =  ";"             # Separates include path elements on Windows systems
PATHSEP      =  os.path.sep     # File path separator character
RANGESEP     =  ":"             # Separator for instance ranges
SINGLEINST   =  "SINGLEINST"    # Indicates a single, not range, in a slice
WINDOWSGROUP =  "WindowsGroup"  # Returned on Windows w/o win32all
WINDOWSUSER  =  "WindowsUser"   # Reutrned on Windows w/o win32all
WINGROUPNOT  =  "GroupNotAvailable"    # Returned when win32all can't get a group name
WINUSERNOT   =  "UserNotAvailable"     # Returned when win32all can't get a user name

#####
# Replacement Token Literals
#####

# Sequence Alphabets

BINARY     =  "Binary"
DECIMAL    =  "Decimal"
OCTAL      =  "Octal"
HEXLOWER   =  "HexLower"
HEXUPPER   =  "HexUpper"
LOWER      =  "Lower"
LOWERUPPER =  "LowerUpper"
UPPER      =  "Upper"
UPPERLOWER =  "UpperLower"

# General Literals

ALPHADELIM =  ":"             # Delimits alphabet name in a Sequence renaming token
TOKDELIM   =  "/"             # Delimiter for all renaming tokens

# Shared File Attribute And Sequence Renaming Tokens

TOKFILADATE  =  "ADATE"
TOKFILATIME  =  "ATIME"
TOKFILCMD    =  "CMDLINE"
TOKFILCDATE  =  "CDATE"
TOKFILCTIME  =  "CTIME"
TOKFILDEV    =  "DEV"
TOKFILFNAME  =  "FNAME"
TOKFILGID    =  "GID"
TOKFILGROUP  =  "GROUP"
TOKFILINODE  =  "INODE"
TOKFILMODE   =  "MODE"
TOKFILMDATE  =  "MDATE"
TOKFILMTIME  =  "MTIME"
TOKFILNLINK  =  "NLINK"
TOKFILSIZE   =  "SIZE"
TOKFILUID    =  "UID"
TOKFILUSER   =  "USER"

# File Time Renaming Tokens

TOKADAY    =  "ADAY"          # mm replacement token
TOKAHOUR   =  "AHOUR"         # hh replacement token
TOKAMIN    =  "AMIN"          # mm replacement token
TOKAMON    =  "AMON"          # MM replacement token
TOKAMONTH  =  "AMONTH"        # Mmm replacement token
TOKASEC    =  "ASEC"          # ss replacement token
TOKAWDAY   =  "AWDAY"         # Ddd replacement token
TOKAYEAR   =  "AYEAR"         # yyyy replacement token

TOKCDAY    =  "CDAY"          # mm replacement token
TOKCHOUR   =  "CHOUR"         # hh replacement token
TOKCMIN    =  "CMIN"          # mm replacement token
TOKCMON    =  "CMON"          # MM replacement token
TOKCMONTH  =  "CMONTH"        # Mmm replacement token
TOKCSEC    =  "CSEC"          # ss replacement token
TOKCWDAY   =  "CWDAY"         # Ddd replacement token
TOKCYEAR   =  "CYEAR"         # yyyy replacement token

TOKMDAY    =  "MDAY"          # mm replacement token
TOKMHOUR   =  "MHOUR"         # hh replacement token
TOKMMIN    =  "MMIN"          # mm replacement token
TOKMMON    =  "MMON"          # MM replacement token
TOKMMONTH  =  "MMONTH"        # Mmm replacement token
TOKMSEC    =  "MSEC"          # ss replacement token
TOKMWDAY   =  "MWDAY"         # Ddd replacement token
TOKMYEAR   =  "MYEAR"         # yyyy replacement token

# System Renaming Tokens

TOKCMDEXEC =  "`"             # Delimiter for command execution renaming tokens
TOKENV     =  "$"             # Introducer for environment variable replacement tokens
TOKRAND    =  "RAND"          # Random replacement token
TOKNAMESOFAR = "NAMESOFAR"    # New name so far

# Sequence Renaming Tokens

TOKASCEND  =  "+"             # Ascending order flag
TOKDESCEND =  "-"             # Descending order flag


#####
# Internal program state literals
#####

ASK            =  "ASK"
BACKUPS        =  "BACKUPS"
DEBUG          =  "DEBUG"
CASECONV       =  "CASECONV"
CASESENSITIVE  =  "CASESENSITIVE"
ESCAPE         =  "ESCAPE"
EXISTSUFFIX    =  "EXISTSUFFIX"
FORCERENAME    =  "FORCERENAME"
INSTANCESTART  =  "INSTANCESTART"
INSTANCEEND    =  "INSTANCEEND"
MAXLINELEN     =  "MAXLINELEN"
QUIET          =  "QUIET"
REGEX          =  "REGEX"
RENSEP         =  "RENSEP"
TARGETSTART    =  "TARGETSTART"
TARGETEND      =  "TARGETEND"
TESTMODE       =  "TESTMODE"


#####
# Renaming Literals
#####

# Rename target keys

BASE           =  "BASENAME"
PATHNAME       =  "PATHNAME"          
STATS          =  "STATS"

# These literals serve two purposes:
#
#  1) They are used as the type indicator in a Sequence Renaming Token
#  2) They are keys to the SortViews and DateViews dictionaries that stores the prestorted views

ORDERBYADATE   =  TOKFILADATE
ORDERBYATIME   =  TOKFILATIME
ORDERBYCMDLINE =  TOKFILCMD
ORDERBYCDATE   =  TOKFILCDATE
ORDERBYCTIME   =  TOKFILCTIME
ORDERBYDEV     =  TOKFILDEV
ORDERBYFNAME   =  TOKFILFNAME
ORDERBYGID     =  TOKFILGID
ORDERBYGROUP   =  TOKFILGROUP
ORDERBYINODE   =  TOKFILINODE
ORDERBYMODE    =  TOKFILMODE
ORDERBYMDATE   =  TOKFILMDATE
ORDERBYMTIME   =  TOKFILMTIME
ORDERBYNLINK   =  TOKFILNLINK
ORDERBYSIZE    =  TOKFILSIZE
ORDERBYUID     =  TOKFILUID
ORDERBYUSER    =  TOKFILUSER

# Rename string keys

NEW            = "NEW"
OLD            = "OLD"


#----------------------------------------------------------#
#              Prompts, & Application Strings              #
#----------------------------------------------------------#


#####
# Debug Messages
#####

DEBUGFLAG          =   "-d"
dALPHABETS         =   "Alphabets"
dCMDLINE           =   "Command Line"
dCURSTATE          =   "Current State Of Program Options"
dDATEVIEW          =   "Date View:"
dDEBUG             =   "DEBUG"
dDUMPOBJ           =   "Dumping Object %s"
dINCLFILES         =   "Included Files:"
dPROGENV           =   "$" + PROGENV
dRENREQ            =   "Renaming Request:"
dRENSEQ            =   "Renaming Sequence: %s"
dRENTARGET         =   "Rename Target:"
dRESOLVEDOPTS      =   "Resolved Command Line"
dSEPCHAR           =   "-"     # Used for debug separator lines
dSORTVIEW          =   "Sort View:"


#####
# Error Messages
#####

eALPHABETEXIST     =  "Sequence renaming token '%s' specifies a non-existent alphabet!"
eALPHABETMISSING   =  "Sequence renaming token '%s' has a missing or incorrect alphabet specification!"
eALPHACMDBAD       =  "Alphabet specificaton '%s' malformed! Try \"Name:Alphabet\""
eALPHACMDLEN       =  "Alphabet '%s' too short!  Must contain at least 2 symbols."
eARGLENGTH         =  "%s must contain exactly %s character(s)!"
eBADARG            =  "Invalid command line: %s!"
eBADCASECONV       =  "Invalid case conversion argument: %s! Must be one of: %s"
eBADINCL           =  "option -%s requires argument" % INCL
eBADLEN            =  "Bad line length '%s'!"
eBADNEWOLD         =  "Bad -r argument '%s'!  Requires exactly one new, old string separator (Default: " + DEFSEP + ")"
eBADREGEX          =  "Invalid Regular Expression: %s"
eBADSLICE          =  "%s invalid slice format! Must be integer values in the form: n, :n, n:, start:end, or :"
eERROR             =  "ERROR"
eEXECFAIL          =  "Renaming token: '%s', command '%s' Failed To Execute!"
eFILEOPEN          =  "Cannot open file '%s': %s!"
eLINELEN           =  "Specified line length too short!  Must be at least %s" % MINLEN
eNAMELONG          =  "Renaming '%s' to new name '%s' too long! (Maximum length is %s.)"
eNAMESHORT         =  "Renaming '%s' to new name '%s' too short! (Minimum length is %s.)"
eNOROOTRENAME      =  "Cannot rename root of file tree!"
eNULLARG           =  "%s cannot be empty!"
eRENAMEFAIL        =  "Attempt to rename '%s' to '%s' failed : %s!"
eTOKBADSEQ         =  "Unknown sequence renaming token, '%s'!"
eTOKDELIM          =  "Renaming token '%s' missing delimiter!"
eTOKRANDIG         =  "Renaming token: '%s' has invalid random precision!  Must be integer > 0."
eTOKUNKNOWN        =  "Unknown renaming token, '%s'!"
eTOOMANYINC        =  "Too many includes! (Max is %d) Possible circular reference?" % MAXINCLUDES


#####
# Informational Messages
#####

iFORCEDNOBKU  =  "Forced renaming WITHOUT backups in effect!!! %s is overwriting %s."
iRENFORCED    =  "Target '%s' exists.  Creating backup."
iRENSKIPPED   =  "Target '%s' exists. Renaming '%s' skipped."
iRENAMING     =  "Renaming '%s' " + ARROW + " '%s'"
iSEQTOOLONG   =  "Sequence number %s, longer than format string %s, Rolling over!"


#####
# Usage Prompts
#####

uTable = [PROGVER,
          HOMEPAGE,
          "usage:  " + PROGNAME + " [[-abCcdfhqtvwXx] [-e type] [-I file] [-i instance] [-P escape] [ -R separator] [-r old=new] [-S suffix] [-T target] [-w width]] ... file|dir file|dir ...",
          "   where,",
          "         -A alphabet   Install \"alphabet\" for use by sequence renaming tokens",
          "         -a            Ask interactively before renaming (Default: Off)",
          "         -b            Turn off backups during forced renaming (Default: Do Backups)",
          "         -C            Do case-sensitive renaming (Default)",
          "         -c            Collapse case when doing string substitution (Default: False)",
          "         -d            Dump debugging information (Default: False)",
          "         -e type       Force case conversion (Default: None)",
          "         -f            Force renaming even if target file or directory name already exists (Default: False)",
          "         -h            Print help information (Default: False)",
          "         -I file       Include command line arguments from file",
          "         -i num|range  Specify which instance(s) to replace (Default: %s)" % DEFINST,
          "         -P char       Use 'char' as the escape sequence (Default: %s)" % DEFESC,
          "         -q            Quiet mode, do not show progress (Default: False)",
          "         -R char       Separator character for -r rename arguments (Default: %s)" % DEFSEP,
          "         -r old=new    Replace old with new in file or directory names",
          "         -S suffix     Suffix to use when renaming existing filenames (Default: %s)" % DEFSUFFIX,
          "         -t            Test mode, don't rename, just show what the program *would* do (Default: False)",
          "         -T num|range  Specify which characters in file name are targeted for renaming (Default: Whole Name)",
          "         -v            Print detailed program version information and continue (Default: False)",
          "         -w length     Line length of diagnostic and error output (Default: %s)" % DEFLEN,
          "         -X            Treat the renaming strings literally (Default)",
          "         -x            Treat the old replacement string as a Python regular expression (Default: False)",
         ]


#----------------------------------------------------------#
#                   Lookup Tables                          #
#----------------------------------------------------------#


# Case Conversion


# Notice use of *unbound* string function methods from the class definition

CASETBL = {'c' : str.capitalize,
           'l' : str.lower,
           's' : str.swapcase,
           't' : str.title,
           'u' : str.upper
          }

CASEOPS = CASETBL.keys()
CASEOPS.sort()


# Day And Month Conversion Tables


DAYS   = {0:"Mon", 1:"Tue", 2:"Wed", 3:"Thu", 4:"Fri", 5:"Sat", 6:"Sun"}
          
MONTHS = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun",
          7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}

# File Time Renaming Token Lookup Table

FILETIMETOKS = { TOKADAY   : ("%02d", "ST_ATIME", "tm_mday"),
                 TOKAHOUR  : ("%02d", "ST_ATIME", "tm_hour"),
                 TOKAMIN   : ("%02d", "ST_ATIME", "tm_min"),
                 TOKAMON   : ("%02d", "ST_ATIME", "tm_mon"),
                 TOKAMONTH : ("",     "ST_ATIME", "tm_mon"),
                 TOKASEC   : ("%02d", "ST_ATIME", "tm_sec"),
                 TOKAWDAY  : ("",     "ST_ATIME", "tm_wday"),
                 TOKAYEAR  : ("%04d", "ST_ATIME", "tm_year"),
                 TOKCDAY   : ("%02d", "ST_CTIME", "tm_mday"),
                 TOKCHOUR  : ("%02d", "ST_CTIME", "tm_hour"),
                 TOKCMIN   : ("%02d", "ST_CTIME", "tm_min"),
                 TOKCMON   : ("%02d", "ST_CTIME", "tm_mon"),
                 TOKCMONTH : ("",     "ST_CTIME", "tm_mon"),
                 TOKCSEC   : ("%02d", "ST_CTIME", "tm_sec"),
                 TOKCWDAY  : ("",     "ST_CTIME", "tm_wday"),
                 TOKCYEAR  : ("%04d", "ST_CTIME", "tm_year"),
                 TOKMDAY   : ("%02d", "ST_MTIME", "tm_mday"),
                 TOKMHOUR  : ("%02d", "ST_MTIME", "tm_hour"),
                 TOKMMIN   : ("%02d", "ST_MTIME", "tm_min"),
                 TOKMMON   : ("%02d", "ST_MTIME", "tm_mon"),
                 TOKMMONTH : ("",     "ST_MTIME", "tm_mon"),
                 TOKMSEC   : ("%02d", "ST_MTIME", "tm_sec"),
                 TOKMWDAY  : ("",     "ST_MTIME", "tm_wday"),
                 TOKMYEAR  : ("%04d", "ST_MTIME", "tm_year")
               }

# Alphabets - The user can add to these on the command line

ALPHABETS  =  {

               BINARY      : ["0", "1"],
    
               DECIMAL     : ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],

               HEXLOWER    : ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"],

               HEXUPPER    : ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"],

               LOWER       : ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                              "q", "r", "s", "t", "u", "v", "w", "x", "y", "z" ],

               LOWERUPPER  : ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                              "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F",
                              "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                              "W", "X", "Y", "Z"],

               OCTAL       : ["0", "1", "2", "3", "4", "5", "6", "7"],

               UPPER       : ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
                              "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z" ],

               UPPERLOWER  : ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
                              "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f",
                              "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
                              "w", "x", "y", "z"]
              }




#----------------------------------------------------------#
#          Global Variables & Data Structures              #
#----------------------------------------------------------#

# List of all the included files

IncludedFiles     = []


# Program toggle and option defaults

ProgramOptions    = {
                     ASK           : False,       # Interactively ask user before renaming each file
                     BACKUPS       : True,        # Do backups during forced renaming
                     DEBUG         : False,       # Debugging off
                     CASECONV      : None,        # Forced case conversions
                     CASESENSITIVE : True,        # Search is case-sensitive
                     ESCAPE        : DEFESC,      # Escape string
                     EXISTSUFFIX   : DEFSUFFIX,   # What to tack on when renaming existing targets
                     FORCERENAME   : False,       # Do not rename if target already exists
                     INSTANCESTART : DEFINST,     # Replace first, leftmost instance by default
                     INSTANCEEND   : SINGLEINST,
                     MAXLINELEN    : DEFLEN,      # Width of output messages
                     QUIET         : False,       # Display progress
                     REGEX         : False,       # Do not treat old string as a regex
                     RENSEP        : DEFSEP,      # Old, New string separator for -r
                     TARGETSTART   : False,       # Entire file name is renaming target by default
                     TARGETEND     : False, 
                     TESTMODE      : False        # Test mode off
                    }


# Used to track the sequence of name transformations as each renaming
# request is applied.  The -1th entry is thus also the "name so far"
# used for the /NAMESOFAR/ renaming token.

RenSequence       = []

#--------------------------- Code Begins Here ---------------------------------#


#----------------------------------------------------------#
#             Object Base Class Definitions                #
#----------------------------------------------------------#


#####
# Container For Holding Rename Targets And Renaming Requests
#####

class RenameTargets:

    """ 
        This class is used to keep track of all the files and/or
        directories we're renaming.  After the class is constructed
        and the command line fully parsed, this will contain:

        self.RenNames    = { fullname : {BASE : basename, PATHNAME : pathtofile, STATS : stats}
                             ... (repeated for each rename target)
                           }

        self.SortViews   = {
                             ORDERBYATIME         : [fullnames in atimes order],
                             ORDERBYCMDLINE       : [fullnames in command line order],
                             ORDERBYCTIME         : [fullnames in ctimes order],
                             ORDERBYDEV           : [fullnames in devs order],
                             ORDERBYFNAME         : [fullnames in alphabetic order],
                             ORDERBYGID           : [fullnames in gids order],
                             ORDERBYGROUP         ; [fullnames in group name order],
                             ORDERBYINODE         : [fullnames in inode order],
                             ORDERBYMODE          : [fullnames in mode order],
                             ORDERBYMTIME         : [fullnames in mtimes order],
                             ORDERBYNLINK         : [fullnames in nlinks order],
                             ORDERBYSIZE          : [fullnames in size order],
                             ORDERBYUID           : [fullnames in uids order],
                             ORDERBYUSER          : [fullnames in user name order]
                            }

        self.DateViews   =  {
                             ORDERBYADATE-date... : [fullnames in  order by atime within same 'date'] ... (repeated for each date),
                             ORDERBYCDATE-date... : [fullnames in  order by ctime within same 'date'] ... (repeated for each date),
                             ORDERBYMDATE-date... : [fullnames in  order by mtime within same 'date'] ... (repeated for each date)
                            }
        
        self.RenRequests =  [
                             {
                               ASK           : interactive ask flag
                               BACKUPS       : do backups during forced renaming flag,
                               OLD           : old rename string,
                               NEW           : new rename string,
                               DEBUG         : debug flag,
                               CASECONV      : type of case conversion,
                               CASESENSITIVE : case sensitivity flag,
                               FORCERENAME   : force renaming flag,
                               INSTANCESTART : Replace first, leftmost instance by default,
                               INSTANCEEND   : ,
                               MAXLINELEN    : max output line length,
                               QUIET         : quiet output flag,
                               REGEX         : regular expression enable flag,
                               RENSEP        : old/new rename separator string,
                               TARGETSTART   : Entire file name target for renaming by default,
                               TARGETEND     : ,
                               TESTMODE      : testmode flag
                             } ... (repeated for each rename request)
                            ]

    """

    #####
    # Constructor
    #####

    def __init__(self, targs):

        # Keep track of all the new filenames we write (or would have)
        # so test mode can correctly report just what the the progam
        # *would* do.  Without this, backup generation is not properly
        # reported in test mode.

        self.RenamedFiles = []
        self.NewFiles     = []

        # Dictionary of all rename targets and their stat info

        self.RenNames   =   {}

        # Dictionary of all possible sort views
        # We can load the first two right away since they're based
        # only on the target names provided on the command line

        i=0
        while i < len(targs):
            targs[i] = os.path.abspath(targs[i])
            i += 1

        alpha = targs[:]
        alpha.sort()
        self.SortViews  =   {ORDERBYCMDLINE : targs, ORDERBYFNAME : alpha}
        del alpha

        # Dictionary to hold all possible date views - files sorted
        # by time *within* a common date.

        self.DateViews = {}

        # Dictionary of all the renaming requests - will be filled in
        # by -r command line parsing.

        self.RenRequests = []


        # This data structure is used to build various sort views
        # A null first field means the view requires special handling,
        # otherwise it's just a stat structure lookup.

        SeqTypes = [
                     [ST_ATIME,  {},  ORDERBYATIME],
                     [ST_CTIME,  {},  ORDERBYCTIME],
                     [ST_DEV,    {},  ORDERBYDEV],
                     [ST_GID,    {},  ORDERBYGID],
                     ["",        {},  ORDERBYGROUP],
                     [ST_INO,    {},  ORDERBYINODE],
                     [ST_MODE,   {},  ORDERBYMODE],
                     [ST_MTIME,  {},  ORDERBYMTIME],
                     [ST_NLINK,  {},  ORDERBYNLINK],
                     [ST_SIZE,   {},  ORDERBYSIZE],
                     [ST_UID,    {},  ORDERBYUID],
                     ["",        {},  ORDERBYUSER],                     
                   ]

        # Populate the data structures with each targets' stat information

        for fullname in targs:

            try:
                pathname, basename = os.path.split(fullname)
                stats    = os.stat(fullname)
            except (IOError, OSError) as e:
                ErrorMsg(eFILEOPEN % (fullname, e.args[1]))

            # Some operating systems (Windows) terminate the path with
            # a separator, some (Posix) do not.

            if pathname[-1] != os.sep:
                pathname += os.sep
            
            # Store fullname, basename, and stat info for this file
            
            if basename:
                self.RenNames[fullname] = {BASE : basename, PATHNAME : pathname, STATS : stats}

            # Catch the case where they're trying to rename the root of the directory tree

            else:
                ErrorMsg(eNOROOTRENAME)

            # Incrementally build lists of keys that will later be
            # used to create sequence renaming tokens

            for seqtype in SeqTypes:

                statflag, storage, order = seqtype

                # Handle os.stat() values

                if statflag:
                    sortkey = stats[statflag]

                # Handle group name values

                elif order == ORDERBYGROUP:
                    sortkey = self.__GetFileGroupname(fullname)

                # Handle user name values

                elif order == ORDERBYUSER:
                    sortkey = self.__GetFileUsername(fullname)

                # Save into storage
                    
                if sortkey in storage:
                    storage[sortkey].append(fullname)
                else:
                    storage[sortkey] = [fullname]


        # Create the various sorted views we may need for sequence
        # renaming tokens

        for seqtype in SeqTypes:

            statflag, storage, order = seqtype

            vieworder = storage.keys()
            vieworder.sort()            

            # Sort alphabetically when multiple filenames
            # map to the same key, creating overall
            # ordering as we go.

            t = []
            for i in vieworder:
                storage[i].sort()
                for j in storage[i]:
                    t.append(j)

            # Now store for future reference

            self.SortViews[order] = t

        # Release the working data structures

        del SeqTypes

        # Now build the special cases of ordering by time within date
        # for each of the timestamp types.

        for dateorder, timeorder, year, mon, day in ((ORDERBYADATE, ORDERBYATIME,
                                                      FILETIMETOKS[TOKAYEAR],
                                                      FILETIMETOKS[TOKAMON],
                                                      FILETIMETOKS[TOKADAY]),
                                               
                                                     (ORDERBYCDATE, ORDERBYCTIME,
                                                      FILETIMETOKS[TOKCYEAR],
                                                      FILETIMETOKS[TOKCMON],
                                                      FILETIMETOKS[TOKCDAY]),

                                                     (ORDERBYMDATE, ORDERBYMTIME,
                                                      FILETIMETOKS[TOKMYEAR],
                                                      FILETIMETOKS[TOKMMON],
                                                      FILETIMETOKS[TOKMDAY])):
                                               

            lastdate = ""
            for fullname in self.SortViews[timeorder]:

                targettime = eval("time.localtime(self.RenNames[fullname][STATS][%s])" % year[1])

                newdate = year[0] % eval("targettime.%s" % year[2]) + \
                          mon[0]  % eval("targettime.%s" % mon[2]) + \
                          day[0]  % eval("targettime.%s" % day[2])

                key = dateorder+newdate

                # New file date encountered

                if newdate != lastdate:

                    self.DateViews[key] = [fullname]
                    lastdate = newdate
                    
                # Add file to existing list of others sharing that date

                else:
                    self.DateViews[key].append(fullname)

    # End of '__init__()'


    #####
    # Debug Dump 
    #####

    def DumpObj(self):

        SEPARATOR = dSEPCHAR * ProgramOptions[MAXLINELEN]
        DebugMsg("\n")
        DebugMsg(SEPARATOR)
        DebugMsg(dDUMPOBJ % str(self))
        DebugMsg(SEPARATOR)


        # Dump the RenNames and SortView dictionaries

        for i, msg in ((self.RenNames, dRENTARGET), (self.SortViews, dSORTVIEW), (self.DateViews, dDATEVIEW)):

            for j in i:
                DumpList(msg, j, i[j])

        for rr in self.RenRequests:
            DumpList(dRENREQ, "", rr)

        DebugMsg(SEPARATOR + "\n\n")

    # End of 'DumpObj()'


    #####
    # Determine File's Group Name
    #####

    def __GetFileGroupname(self, fullname):
        
        if POSIX:
            return grp.getgrgid(self.RenNames[fullname][STATS][ST_GID])[0]

        else:
            retval = WINDOWSGROUP

            if WIN32ALL:

                try:
                    # Get the internal Win32 security group information for this file.

                    hg     = GetFileSecurity(fullname, GROUP_SECURITY_INFORMATION)
                    sidg   = hg.GetSecurityDescriptorGroup()

                    # We have to know who is hosting the filesystem for this file

                    drive = fullname[0:3]
                    if GetDriveType(drive) == win32con.DRIVE_REMOTE:
                        fnhost = WNetGetUniversalName(drive, 1).split('\\')[2]

                    else:
                        fnhost = WIN32HOST

                    # Now we can translate the sids into names

                    retval  = LookupAccountSid(fnhost, sidg)[0]

                # On any error, just act like win32all isn't there
                    
                except:
                    retval = WINGROUPNOT

            return retval

    # End of 'GetFileGroupname()'


    #####
    # Determine File's User Name
    #####

    def __GetFileUsername(self, fullname):

        if POSIX:
            return pwd.getpwuid(self.RenNames[fullname][STATS][ST_UID])[0]

        else:
            retval = WINDOWSUSER
 
            if WIN32ALL:

                try:

                    # Get the internal Win32 security information for this file.

                    ho     = GetFileSecurity(fullname, OWNER_SECURITY_INFORMATION)
                    sido   = ho.GetSecurityDescriptorOwner()

                    # We have to know who is hosting the filesystem for this file

                    drive = fullname[0:3]
                    if GetDriveType(drive) == win32con.DRIVE_REMOTE:
                        fnhost = WNetGetUniversalName(drive, 1).split('\\')[2]

                    else:
                        fnhost = WIN32HOST

                    # Now we can translate the sids into names

                    retval  = LookupAccountSid(fnhost, sido)[0]

                # On any error, just act like win32all isn't there
                    
                except:
                    retval = WINUSERNOT

            return retval

    # End of 'GetFileUsername()'


    #####
    # Go Do The Requested Renaming
    #####

    def ProcessRenameRequests(self):

        global RenSequence
        self.indentlevel = -1

        # Create a list of all renaming to be done.
        # This includes the renaming of any existing targets.

        for target in self.SortViews[ORDERBYCMDLINE]:

            oldname, pathname = self.RenNames[target][BASE], self.RenNames[target][PATHNAME]
            newname = oldname

            # Keep track of incremental renaming for use by debug
            RenSequence = [oldname]
            
            for renrequest in self.RenRequests:
                
                # Select portion of name targeted for renaming

                lname = ""
                rname = ""
                tstart = renrequest[TARGETSTART]
                tend   = renrequest[TARGETEND]

                # Condition values so that range slicing works properly below.
                # This couldn't be done at the time the target range was
                # saved intially, because the length of the name being processed
                # isn't known until here.
                
                if tstart == None:
                    tstart = 0

                if tend == None:
                    tend = len(newname)
                    
                if tstart or tend:

                    bound = len(newname)
                        
                    # Normalize negative refs so we can use consistent
                    # logic below

                    if tstart < 0:
                        tstart = bound + tstart

                    if (tend != SINGLEINST and tend < 0):
                        tend = bound + tend

                    # Condition and bounds check the target range as needed

                    # Handle single position references
                    if (tend == SINGLEINST):

                        # Select the desired position.  Notice that
                        # out-of-bounds references are ignored and the
                        # name is left untouched.  This is so the user
                        # can specify renaming operations on file
                        # names of varying lengths and have them apply
                        # only to those files long enough to
                        # accommodate the request without blowing up
                        # on the ones that are not long enough.

                        if 0 <= tstart < bound:
                            lname, newname, rname = newname[:tstart], newname[tstart], newname[tstart+1:]

                        # Reference is out of bounds - leave name untouched

                        else:
                            lname, newname, rname = newname, "", ""

                    # Handle slice range requests

                    else:

                        # Out-Of-Bounds or invalid slice ranges will
                        # cause renaming request to be ignored as above

                        if newname[tstart:tend]:
                            lname, newname, rname = newname[:tstart], newname[tstart:tend], newname[tend:]

                        else:
                            lname, newname, rname = newname, "", ""                            
                    

                # Handle conventional string replacement renaming requests
                # An empty newname here means that the -T argument processing
                # selected a new string and/or was out of bounds -> we ignore the request.

                if newname and (renrequest[OLD] or renrequest[NEW]):

                    # Resolve any embedded renaming tokens

                    old = self.__ResolveRenameTokens(target, renrequest[OLD])
                    new = self.__ResolveRenameTokens(target, renrequest[NEW])

                    oldstrings = []

                    # Build a list of indexes to every occurence of the old string,
                    # taking case sensitivity into account

                    # Handle the case when old = "".  This means to
                    # *replace the entire* old name with new.  More
                    # specifically, replace the entire old name *as
                    # modified so far by preceding rename commands*.

                    if not old:
                        old = newname

                    # Find every instance of the 'old' string in the
                    # current filename.  'Find' in this case can be either
                    # a regular expression pattern match or a literal
                    # string match.  
                    #
                    # Either way, each 'hit' is recorded as a tuple:
                    #
                    #    (index to beginning of hit, beginning of next non-hit text)
                    #
                    # This is so subsequent replacement logic knows:
                    #
                    #    1) Where the replacement begins
                    #    2) Where the replacement ends
                    #
                    # These two values are used during actual string
                    # replacement to properly replace the 'new' string
                    # into the requested locations.


                    # Handle regular expression pattern matching

                    if renrequest[REGEX]:

                        try:
                            # Do the match either case-insentitive or not

                            if renrequest[CASESENSITIVE]:
                                rematches = re.finditer(old, newname)

                            else:
                                rematches = re.finditer(old, newname, re.I)

                            # And save off the results

                            for match in rematches:
                                oldstrings.append(match.span())

                        except:
                            ErrorMsg(eBADREGEX % old)

                    # Handle literal string replacement

                    else:

                        searchtarget = newname
                        
                        # Collapse case if requested
                        
                        if not renrequest[CASESENSITIVE]:

                            searchtarget = searchtarget.lower()
                            old  = old.lower()

                        oldlen = len(old)
                        i = searchtarget.find(old)
                        while i >= 0:

                            nextloc = i + oldlen
                            oldstrings.append((i, nextloc))
                            i = searchtarget.find(old, nextloc)

                    # If we found any matching strings, replace them

                    if oldstrings:

                        # But only process the instances the user asked for

                        todo = []

                        # Handle single instance requests doing bounds checking as we go

                        start = renrequest[INSTANCESTART]
                        end   = renrequest[INSTANCEEND]

                        if (end == SINGLEINST):

                            # Compute bounds for positive and negative indicies.
                            # This is necessary because positive indicies are 0-based,
                            # but negative indicies start at -1.

                            bound = len(oldstrings)

                            if start < 0:
                                bound += 1

                            # Now go get that entry

                            if abs(start) < bound:
                                todo.append(oldstrings[start])

                        # Handle instance range requests

                        else:
                            todo = oldstrings[start:end]


                        # Replace selected substring(s).  Substitute from
                        # R->L in original string so as not to mess up the
                        # replacement indicies.

                        todo.reverse()
                        for i in todo:
                            newname = newname[:i[0]] + new + newname[i[1]:]


                # Handle case conversion renaming requests
                    
                elif renrequest[CASECONV]:
                    newname = CASETBL[renrequest[CASECONV]](newname)

                # Any subsequent replacements operate on the modified name
                # which is reconstructed by combining what we've renamed
                # with anything that was excluded from the rename operation.

                newname = lname + newname + rname

                # Keep track of incremental renaming for use by debug
                RenSequence.append(newname)
                                
            # Show the incremental renaming steps if debug is on

            if ProgramOptions[DEBUG]:
                DebugMsg(dRENSEQ % ARROW.join(RenSequence))

            # Nothing to do, if old- and new names are the same

            if newname != oldname:
                self.__RenameIt(pathname, oldname, newname)
            
    # End of 'ProcessRenameRequests()'


    #####
    # Actually Rename A File
    #####

    def __RenameIt(self, pathname, oldname, newname):

        self.indentlevel += 1
        indent = self.indentlevel * INDENT
        newlen = len(newname)
        
        # First make sure the new name meets length constraints

        if newlen < MINNAMELEN:
            ErrorMsg(indent + eNAMESHORT% (oldname, newname, MINNAMELEN))
            return

        if newlen > MAXNAMELEN:
            ErrorMsg(indent + eNAMELONG % (oldname, newname, MAXNAMELEN))
            return

        # Get names into absolute path form

        fullold = pathname + oldname
        fullnew = pathname + newname

        # See if our proposed renaming is about to stomp on an
        # existing file, and create a backup if forced renaming
        # requested.  We do such backups with a recursive call to
        # ourselves so that filename length limits are observed and
        # backups-of-backups are preserved.

        doit = True
        newexists = os.path.exists(fullnew)

        if (not ProgramOptions[TESTMODE] and newexists) or \
           (ProgramOptions[TESTMODE] and fullnew not in self.RenamedFiles and (newexists or fullnew in self.NewFiles)):

            if ProgramOptions[FORCERENAME]:

                # Create the backup unless we've been told not to

                if ProgramOptions[BACKUPS]:

                    bkuname = newname + ProgramOptions[EXISTSUFFIX]
                    InfoMsg(indent + iRENFORCED % fullnew)
                    self.__RenameIt(pathname, newname, bkuname)

                else:
                    InfoMsg(iFORCEDNOBKU % (fullold, fullnew))
                
            else:
                InfoMsg(indent + iRENSKIPPED % (fullnew, fullold))
                doit = False

        if doit:

            if ProgramOptions[ASK]:

                answer = ""
                while answer.lower() not in [ASKNO.lower(), ASKYES.lower(), ASKDOREST.lower(), ASKQUIT.lower()]:

                    PrintStdout("Rename %s to %s? [%s]: " % (fullold, fullnew, ASKNO+ASKYES+ASKDOREST+ASKQUIT), TRAILING="")

                    answer = sys.stdin.readline().lower().strip()

                    # A blank line means take the default - do nothing.

                    if not answer:
                        answer = ASKNO.lower()
                        
                if answer == ASKNO.lower():
                    doit = False

                if answer == ASKYES.lower():
                    doit = True

                if answer == ASKDOREST.lower():
                    doit = True
                    ProgramOptions[ASK] = False

                if answer == ASKQUIT.lower():
                    sys.exit(1)

            if doit:
                
                # In test mode, track file names that would be produced.
                
                if ProgramOptions[TESTMODE]:

                    self.NewFiles.append(fullnew)
                    self.RenamedFiles.append(fullold)
                    
                    if fullold in self.NewFiles:
                        self.NewFiles.remove(fullold)
                    
                    if fullnew in self.RenamedFiles:
                        self.RenamedFiles.remove(fullnew)

                InfoMsg(indent + iRENAMING % (fullold, fullnew))

                if not ProgramOptions[TESTMODE]:

                    try:
                        os.rename(fullold, fullnew)
                    except OSError as e:
                        ErrorMsg(eRENAMEFAIL % (fullold, fullnew, e.args[1]))

        self.indentlevel -= 1

    # End of '__RenameIt()'

    
    #####
    # Resolve Rename Tokens
    #####

    """ This replaces all renaming token references in 'renstring'
        with the appropriate content and returns the resolved string.
        'target' is the name of the current file being renamed.  We
        need that as well because some renaming tokens refer to file
        stat attributes or even the file name itself.
    """

    def __ResolveRenameTokens(self, target, renstring):

        # Find all token delimiters but ignore any that might appear
        # inside a command execution replacement token string.

        rentokens = []
        odd = True
        incmdexec = False

        i=0
        while i < len(renstring):

            if renstring[i] == TOKCMDEXEC:
                incmdexec = not incmdexec

            elif renstring[i] == TOKDELIM:

                if incmdexec:
                    pass

                elif odd:

                    rentokens.append([i])
                    odd = not odd

                else:

                    rentokens[-1].append(i)
                    odd = not odd


            i += 1

        # There must be an even number of token delimiters
        # or the renaming token is malformed

        if rentokens and  len(rentokens[-1]) != 2:
            ErrorMsg(eTOKDELIM % renstring)

        # Now add the renaming token contents.  This will be used to
        # figure out what the replacement text should be.

        i = 0
        while i < len(rentokens):

            rentokens[i].append(renstring[rentokens[i][0]+1 : rentokens[i][1]])
            i += 1

        # Process each token.  Work left to right so as not to mess up
        # the previously stored indexes.

        rentokens.reverse()

        for r in rentokens:

            fullrentoken = "%s%s%s" % (TOKDELIM, r[2], TOKDELIM)  # Need this for error messages.
        
            ###
            # File Attribute Renaming Tokens
            ###

            if r[2] == TOKFILDEV:
                r[2] = str(self.RenNames[target][STATS][ST_DEV])
                
            elif r[2] == TOKFILFNAME:
                r[2] = os.path.basename(target)

            elif r[2] == TOKFILGID:
                r[2] = str(self.RenNames[target][STATS][ST_GID])

            elif r[2] == TOKFILGROUP:
                r[2] = self.__GetFileGroupname(target)

            elif r[2] == TOKFILINODE:
                r[2] = str(self.RenNames[target][STATS][ST_INO])

            elif r[2] == TOKFILMODE:
                r[2] = str(self.RenNames[target][STATS][ST_MODE])

            elif r[2] == TOKFILNLINK:
                r[2] = str(self.RenNames[target][STATS][ST_NLINK])

            elif r[2] == TOKFILSIZE:
                r[2] = str(self.RenNames[target][STATS][ST_SIZE])

            elif r[2] == TOKFILUID:
                r[2] = str(self.RenNames[target][STATS][ST_UID])

            elif r[2] == TOKFILUSER:
                r[2] = self.__GetFileUsername(target)
                

            ###
            # File Time Renaming Tokens
            ###

            elif r[2] in FILETIMETOKS:

                parms = FILETIMETOKS[r[2]]
                val   = eval("time.localtime(self.RenNames[target][STATS][%s]).%s" % (parms[1], parms[2]))

                # The first value of FILETIMETOKS table entry
                # indicates the formatting string to use (if the entry
                # is non null), or that we're doing a lookup for the
                # name of a month (if the entry is null)

                if parms[0]:
                    r[2] = parms[0] % val

                elif parms[2] == "tm_mon":
                    r[2] = MONTHS[val]

                elif parms[2] == "tm_wday":
                    r[2] = DAYS[val]
                
            ###
            # System Renaming Tokens
            ###
            
            # Environment Variable replacement token
            
            elif r[2].startswith(TOKENV):

                r[2] = os.getenv(r[2][1:])
 
                # Handle case for nonexistent environment variable
                
                if not r[2]:
                    r[2] = ""
               
            
            # Command Run replacement token

            elif r[2].startswith(TOKCMDEXEC) and r[2].endswith(TOKCMDEXEC):

                command = r[2][1:-1]

                # Handle Windows variants - they act differently

                if not POSIX:
                    pipe = os.popen(command, 'r')

                # Handle Unix variants

                else: 
                    pipe = os.popen('{ ' + command + '; } 2>&1', 'r')

                output = pipe.read()
                status = pipe.close()

                if status == None:
                    status = 0

                # Nonzero status means error attempting to execute the command
                    
                if status:
                    ErrorMsg(eEXECFAIL % (fullrentoken, command))

                # Otherwise swap the command with its results, stripping newlines
                    
                else:
                    r[2] = output.replace("\n", "")


            # Random Number Replacement token
                    
            elif r[2].startswith(TOKRAND):

                random.seed()

                # Figure out how many digits of randomness the user want

                try:
                    precision = r[2].split(TOKRAND)[1]
                    precision = int(precision)

                except:
                    ErrorMsg(eTOKRANDIG % fullrentoken)

                if precision < 1:
                    ErrorMsg(eTOKRANDIG % fullrentoken)
                    
                fmt =  '"%0' + str(precision) + 'd" % random.randint(0, pow(10, precision)-1)'
                r[2] = eval(fmt)

            # Name So Far Replacement Token

            elif r[2] == (TOKNAMESOFAR):
                r[2] = RenSequence[-1]

            ###
            # Sequence Renaming Tokens
            ###
                    
            elif r[2] and (r[2][0] == TOKASCEND or r[2][0] == TOKDESCEND):

                # Parse the Sequence Renaming Token into the token itself
                # and its corresponding formatting field.

                # Note that the a legal Sequence Renaming Token will either
                # be one of the keys of the SortViews dictionary or one
                # of the "ORDERBYnDATE" orderings.

                token = r[2][1:]

                found = False
                for seqtoken in self.SortViews.keys() + [ORDERBYADATE, ORDERBYCDATE, ORDERBYMDATE]:

                    if token.split(ALPHADELIM)[0] == (seqtoken):

                        token, field = token[:len(seqtoken)], token[len(seqtoken):]
                        found = True
                        break

                if not found:
                    ErrorMsg(eTOKBADSEQ % fullrentoken)

                # Now derive the name of the alphabet to use

                if not field.startswith(ALPHADELIM):
                    ErrorMsg(eALPHABETMISSING % fullrentoken)

                field = field[1:]

                alphabet, alphadelim, field = field.partition(ALPHADELIM)

                if not alphadelim:
                    ErrorMsg(eALPHABETMISSING % fullrentoken)

                # Empty alphabet string means default to decimal counting
                    
                if not alphabet:
                    alphabet = DECIMAL
                    
                if alphabet not in ALPHABETS:
                    ErrorMsg(eALPHABETEXIST % fullrentoken)


                # Retrieve the ordered list of the requested type,
                # adjust for descending order, and plug in the
                # sequence number for the current renaming target
                # (which is just the index of that filename in the
                # list).

                # One of the standard sorted views requested
                    
                if token in self.SortViews:
                    orderedlist = self.SortViews[token][:]

                # One of the views sorted within dates requested

                else:


                    if token == ORDERBYADATE:
                        year, mon, day = FILETIMETOKS[TOKAYEAR], FILETIMETOKS[TOKAMON], FILETIMETOKS[TOKADAY]

                    elif token == ORDERBYCDATE:
                        year, mon, day = FILETIMETOKS[TOKCYEAR], FILETIMETOKS[TOKCMON], FILETIMETOKS[TOKCDAY]

                    elif token == ORDERBYMDATE:
                        year, mon, day = FILETIMETOKS[TOKMYEAR], FILETIMETOKS[TOKMMON], FILETIMETOKS[TOKMDAY]

                    targettime = eval("time.localtime(self.RenNames[target][STATS][%s])" % year[1])

                    key = token + \
                          year[0] % eval("targettime.%s" % year[2]) + \
                          mon[0]  % eval("targettime.%s" % mon[2]) + \
                          day[0]  % eval("targettime.%s" % day[2])

                    orderedlist = self.DateViews[key][:]

                if r[2][0] == TOKDESCEND:
                    orderedlist.reverse()

                r[2] = ComputeSeqString(field, orderedlist.index(target), ALPHABETS[alphabet])

            ###
            # Unrecognized Renaming Token
            ###
                    
            else:
                ErrorMsg(eTOKUNKNOWN % fullrentoken)
                    
            ###
            # Successful Lookup, Do the actual replacement
            ###

            renstring = renstring[:r[0]] + r[2] + renstring[r[1]+1:]
            
        return renstring

    # End of '__ResolveRenameTokens()'


# End of class 'RenameTargets'
    

#----------------------------------------------------------#
#             Supporting Function Definitions              #
#----------------------------------------------------------#


#####
# Check For Correct Slice Syntax
#####

def CheckSlice(val):

    try:

        # Process ranges

        if val.count(RANGESEP):

            lhs, rhs = val.split(RANGESEP)

            if not lhs:
                lhs = None

            else:
                lhs = int(lhs)

            if not rhs:
                rhs = None

            else:
                rhs = int(rhs)

        # Process single indexes

        else:

            lhs = int(val)
            rhs = SINGLEINST

    # Something about the argument was bogus

    except:
        ErrorMsg(eBADSLICE % val)

    return (lhs, rhs)

# End Of 'CheckSlice()'


#####
# Turn A List Into Columns With Space Padding
#####

def ColumnPad(list, PAD=PADCHAR, WIDTH=PADWIDTH):

    retval = ""
    for l in list:
        l = str(l)
        retval += l + ((WIDTH - len(l)) * PAD)

    return retval

# End of 'ColumnPad()'


def ComputeSeqString(fmt, incr, alphabet):

    """ 
        fmt      = A literal "format field" string
        incr     = A integer to be "added" to the field
        alphabet = The alphabet of characters to use, in ascending order

        Add 'incr' to 'fmt' in base(len(alphabet)).  Characters in
        'fmt' that are not in 'alphabet' are ignored in this addition.

        The final result is limited to be no longer than 'fmt'.  Any
        result longer than fmt has MSD dropped, thereby effectively
        rolling over the count.  If 'fmt' is null on entry, the final
        result length is unlimited.
    """
       
    base     = len(alphabet)

    # Do position-wise "addition" via symbol substitution moving from
    # right-to-left adjusting for the fact that not all symbols in the
    # format string will be in the alphabet.
    

    # First convert the increment into a string in the base of the
    # alphabet

    idigits = []
    while incr >  base-1:

        incr, digit = incr/base, incr % base
        idigits.append(alphabet[digit])

    idigits.append(alphabet[incr])
    idigits.reverse()
    incr = "".join(idigits)

    # Now do right-to-left digit addition with the format
    # field.

    # Do position-wise "addition" via symbol substitution moving from
    # right-to-left.  Take into account that the format pattern string
    # may be a different length than the increment string and that not
    # all characters in the format pattern are guaranteed to exist in
    # the alphabet.

    newval   = ""
    carry    = None
    fmtlen   = len(fmt)
    incrlen  = len(incr)
    calcsize = max(fmtlen, incrlen)

    i = -1
    done = False
    while abs(i) <= calcsize and not done:

        sum = 0

        if carry:
            sum += carry

        if fmt and (abs(i) <= fmtlen) and fmt[i] in alphabet:
            sum +=  alphabet.index(fmt[i])

        if abs(i) <= incrlen:
            sum += alphabet.index(incr[i])

        # Do arithmetic modulo alphabet length
            
        carry, digit = sum/base, sum % base

        if not carry:
            carry = None

            # We're completely done if we're out of digits in incr and
            # there's no carry to propagate.  This prevents us from
            # tacking on leading 0th characters which could overwrite
            # out-of-alphabet characters in the format field.

            if abs(i-1) > incrlen:
                done =True

        newval = alphabet[digit] + newval

        i -= 1

    if carry:
        newval = alphabet[carry] + newval

    # Constrain the results to the length of the original format
    # string, rolling over and warning the user as necessary.  The one
    # exception to this is when a null format string is passed.  This
    # is understood to mean that sequences of any length are
    # permitted.

    # Result length constrained by format string

    if fmtlen:
        
        if len(newval) > fmtlen:
            InfoMsg(iSEQTOOLONG % (newval,fmt))
            newval = newval[-fmtlen:]

        return  fmt[:-len(newval)] + newval

    # Any length result permitted

    else:
        return newval

# End of 'ComputeSeqString()'


#####
# Condition Line Length With Fancy Wrap And Formatting
#####

def ConditionLine(msg, 
                  PAD=PADCHAR, \
                  WIDTH=PADWIDTH, \
                  wrapindent=WRAPINDENT ):

    retval = []
    retval.append(msg[:ProgramOptions[MAXLINELEN]])
    msg = msg[ProgramOptions[MAXLINELEN]:]

    while msg:
        msg = PAD * (WIDTH + wrapindent) + msg
        retval.append(msg[:ProgramOptions[MAXLINELEN]])
        msg = msg[ProgramOptions[MAXLINELEN]:]

    return retval

# End of 'ConditionLine()'


#####
# Print A Debug Message
#####

def DebugMsg(msg):
 
   l = ConditionLine(msg)
   for msg in l:
        PrintStderr(PROGNAME + " " + dDEBUG + ": " + msg)

# End of 'DebugMsg()'


#####
# Debug Dump Of A List
#####

def DumpList(msg, listname, content):

    DebugMsg(msg)
    itemarrow = ColumnPad([listname, " "], WIDTH=LSTPAD)
    DebugMsg(ColumnPad([" ", " %s %s" % (itemarrow, content)]))

# End of 'DumpList()'


#####
# Dump The State Of The Program
#####

def DumpState():

    SEPARATOR = dSEPCHAR * ProgramOptions[MAXLINELEN]
    DebugMsg(SEPARATOR)
    DebugMsg(dCURSTATE)
    DebugMsg(SEPARATOR)

    opts = ProgramOptions.keys()
    opts.sort()
    for o in opts:
        DebugMsg(ColumnPad([o, ProgramOptions[o]]))

    DumpList(dALPHABETS, "", ALPHABETS)

    DebugMsg(SEPARATOR)


# End of 'DumpState()'


#####
# Print An Error Message And Exit
#####

def ErrorMsg(emsg):

    l = ConditionLine(emsg)

    for emsg in l:
        PrintStderr(PROGNAME + " " + eERROR + ": " + emsg)

    sys.exit(1)

# End of 'ErrorMsg()'


#####
# Split -r Argument Into Separate Old And New Strings
#####

def GetOldNew(arg):


    escaping = False
    numseps  = 0 
    sepindex = 0
    oldnewsep = ProgramOptions[RENSEP]

    i = 0
    while i < len(arg):

        # Scan string ignoring escaped separators

        if arg[i:].startswith(oldnewsep):

            if (i > 0 and (arg[i-1] != ProgramOptions[ESCAPE])) or i == 0:
                sepindex = i
                numseps += 1
            
            i += len(oldnewsep)

        else:
            i += 1


    if numseps != 1:
        ErrorMsg(eBADNEWOLD % arg)

    else:
        old, new = arg[:sepindex], arg[sepindex + len(oldnewsep):]
        old = old.replace(ProgramOptions[ESCAPE] + oldnewsep, oldnewsep)
        new = new.replace(ProgramOptions[ESCAPE] + oldnewsep, oldnewsep)
        return [old, new]

# End of 'GetOldNew()'


#####
# Print An Informational Message
#####

def InfoMsg(imsg):

    l = ConditionLine(imsg)

    msgtype = ""
    if ProgramOptions[TESTMODE]:
        msgtype = TESTMODE

    if not ProgramOptions[QUIET]:
        for msg in l:
            PrintStdout(PROGNAME + " " + msgtype + ": " + msg)

# End of 'InfoMsg()'


#####
# Print To stderr
#####

def PrintStderr(msg, TRAILING="\n"):
    sys.stderr.write(msg + TRAILING)

# End of 'PrintStderr()'


#####
# Print To stdout
#####

def PrintStdout(msg, TRAILING="\n"):
    sys.stdout.write(msg + TRAILING)

# End of 'PrintStdout()'


#####
# Process Include Files On The Command Line
#####

def ProcessIncludes(OPTIONS):

    """ Resolve include file references allowing for nested includes.
        This has to be done here separate from the command line
        options so that normal getopt() processing below will "see"
        the included statements.

        This is a bit tricky because we have to handle every possible
        legal command line syntax for option specification:

          -I filename
          -Ifilename
          -....I filename
          -....Ifilename
    """

    # Build a list of all the options that take arguments.  This is
    # needed to determine whether the include symbol is an include
    # option or part of an argument to a preceding option.

    OPTIONSWITHARGS = ""
    for i in re.finditer(":", OPTIONSLIST):
        OPTIONSWITHARGS += OPTIONSLIST[i.start() - 1]

    NUMINCLUDES = 0
    FoundNewInclude = True

    while FoundNewInclude:

        FoundNewInclude = False
        i = 0
        while i < len(OPTIONS):

            # Detect all possible command line include constructs,
            # isolating the requested filename and replaciing its
            # contents at that position in the command line.

            field = OPTIONS[i]
            position = field.find(INCL)
            
            if field.startswith(OPTINTRO) and (position > -1):

                
                lhs = field[:position]
                rhs = field[position+1:]

                # Make sure the include symbol isn't part of some
                # previous option argument

                previousopt = False
                for c in OPTIONSWITHARGS:

                    if c in lhs:

                        previousopt = True
                        break
                    
                # If the include symbol appears in the context of a
                # previous option, skip this field, otherwise process
                # it as an include.


                if not previousopt:
                    
                    FoundNewInclude = True
                    if lhs == OPTINTRO:
                        lhs = ""

                    if rhs == "":

                        if i < len(OPTIONS)-1:

                            inclfile = OPTIONS[i+1]
                            OPTIONS = OPTIONS[:i+1] + OPTIONS[i+2:]

                        # We have an include without a filename at the end
                        # of the command line which is bogus.
                        else:
                            ErrorMsg(eBADARG % eBADINCL)

                    else:
                        inclfile = rhs

                    # Before actually doing the include, make sure we've
                    # not exceeded the limit.  This is here mostly to make
                    # sure we stop recursive/circular includes.

                    NUMINCLUDES += 1
                    if NUMINCLUDES > MAXINCLUDES:
                        ErrorMsg(eTOOMANYINC)

                    # Read the included file, stripping out comments

                    # Use include path if one was provided

                    inclpath = os.getenv(INCLENV)
                    if inclpath:

                        found = searchpath(inclfile, inclpath, PATHDEL)
                        if found:
                            inclfile = found[0]

                    try:
                        n = []
                        f = open(inclfile)
                        for line in f.readlines():
                            line = line.split(COMMENT)[0]
                            n += shlex.split(line)
                        f.close()

                        # Keep track of the filenames being included for debug output

                        IncludedFiles.append(os.path.abspath(inclfile))

                        # Insert content of included file at current
                        # command line position

                        # A non-null left hand side means that there were
                        # options before the include we need to preserve

                        if lhs:
                            n = [lhs] + n

                        OPTIONS = OPTIONS[:i] + n + OPTIONS[i+1:]

                    except IOError as e:
                        ErrorMsg(eFILEOPEN % (inclfile, e.args[1]))
        
            i += 1

    return OPTIONS

# End of 'ProcessIncludes()'


#####
# Search Path Looking For Include File
#####

def searchpath(filename, pathlist, pathdelim):

    # What we'll return if we find nothing
    
    retval = []

    # Find all instances of filename in specified paths

    paths = pathlist.split(pathdelim)

    for path in paths:

        if path and path[-1] != PATHSEP:
            path += PATHSEP

        path += filename

        if os.path.exists(path):
            retval.append(os.path.realpath(path))

    return retval

# End of 'searchpath()'


#####
# Print Usage Information
#####

def Usage():
    for line in uTable:
        PrintStdout(line)

# End of 'Usage()'


#----------------------------------------------------------#
#                    Program Entry Point                   #
#----------------------------------------------------------#

# Set up proper include path delimiter
    

if WINDOWS:
    PATHDEL = PATHDELWIN

else:
    PATHDEL = PATHDELUNIX


#####
# Command Line Preprocessing
# 
# Some things have to be done *before* the command line
# options can actually be processed.  This includes:
#
#  1) Prepending any options specified in the environment variable.
#
#  2) Resolving any include file references
#
#  3) Building the data structures that depend on the file/dir names
#     specified for renaming.  We have to do this first, because
#     -r renaming operations specified on the command line will
#     need this information if they make use of renaming tokens.
#
#####

# Process any options set in the environment first, and then those
# given on the command line


OPTIONS = sys.argv[1:]

envopt = os.getenv(PROGENV)
if envopt:
    OPTIONS = shlex.split(envopt) + OPTIONS

# Deal with include files

OPTIONS = ProcessIncludes(OPTIONS)

# And parse the command line

try:
    opts, args = getopt.getopt(OPTIONS, OPTIONSLIST)
except getopt.GetoptError as e:
    ErrorMsg(eBADARG % e.args[0])

# Create and populate an object with rename targets.  This must be
# done here because this object also stores the -r renaming requests
# we may find in the options processing below.  Also, this object must
# be fully populated before any actual renaming can take place since
# many of the renaming tokens derive information about the file being
# renamed.


# Do wildcard expansion on the rename targets because they may
# have come from an include file (where they are not expanded)
# or from a Windows shell that doesn't know how to handle globbing
# properly.

# If the glob expands to nothing, then supply the original string.
# That way an error will be thrown if either an explicitly named file
# does not exist, or if a wildcard expands to nothing.

expandedlist = []
for arg in args:

    wc = glob.glob(arg)
    if wc:
        expandedlist += wc
    else:
        expandedlist.append(arg)

targs = RenameTargets(expandedlist)

# Now process the options

for opt, val in opts:

    # Install new alphabet

    if opt == "-A":

        alphaname, delim, alpha = val.partition(ALPHADELIM)

        if not delim:
            ErrorMsg(eALPHACMDBAD % val)

        if not alphaname:
            ErrorMsg(eALPHACMDBAD % val)

        if len(alpha) < 2:
            ErrorMsg(eALPHACMDLEN % val)

        a = []
        for c in alpha:
            a.append(c)

        ALPHABETS[alphaname] = a

    if opt == "-a":
        ProgramOptions[ASK] = True

    # Turn off backups during forced renaming

    if opt == "-b":
        ProgramOptions[BACKUPS] = False

    # Select case-sensitivity for replacements (or not)
    
    if opt == "-C":
        ProgramOptions[CASESENSITIVE] = True

    if opt == "-c":
        ProgramOptions[CASESENSITIVE] = False

    # Turn on debugging

    if opt == "-d":
        ProgramOptions[DEBUG] = True
        DumpState()

    # Force case conversion
        
    if opt == "-e":

        # Make sure we support the requested case conversion
        if val in CASEOPS:

            ProgramOptions[CASECONV] = val

            # Construct a renaming request
            
            req = {}
            req[OLD], req[NEW] = None, None
            for opt in ProgramOptions:
                req[opt] = ProgramOptions[opt]

            targs.RenRequests.append(req)

        # Error out if we don't recognize it
        else:
            ErrorMsg(eBADCASECONV % (val, ", ".join(CASEOPS)))
        

    # Force renaming of existing targets

    if opt == "-f":
        ProgramOptions[FORCERENAME] = True

    # Output usage information

    if opt == "-h":
        Usage()
        sys.exit(0)

    # Specify which instances to replace

    if opt == "-i":

        ProgramOptions[INSTANCESTART], ProgramOptions[INSTANCEEND] = CheckSlice(val)

    # Set the escape character

    if opt == "-P":
        if len(val) == 1:
            ProgramOptions[ESCAPE] = val
        else:
            ErrorMsg(eARGLENGTH % (NULLESC, 1))

    # Set quiet mode
            
    if opt == "-q":
        ProgramOptions[QUIET] = True

    # Set the separator character for replacement specifications

    if opt == '-R':
        if len(val) == 1:
            ProgramOptions[RENSEP] = val
        else:
            ErrorMsg(eARGLENGTH % (NULLRENSEP, 1))

    # Specify a replacement command

    if opt == "-r":
        req = {}
        req[OLD], req[NEW] = GetOldNew(val)
        ProgramOptions[CASECONV] = None
        for opt in ProgramOptions:
            req[opt] = ProgramOptions[opt]
        targs.RenRequests.append(req)

    # Specify a renaming suffix

    if opt == "-S":
        if val:
            ProgramOptions[EXISTSUFFIX] = val
        else:
            ErrorMsg(eNULLARG % NULLSUFFIX)

    # Set substring targeted for renaming

    if opt == "-T":
        ProgramOptions[TARGETSTART], ProgramOptions[TARGETEND] = CheckSlice(val)

    # Request test mode

    if opt == "-t":
        ProgramOptions[TESTMODE] = True


    # Output program version info

    if opt == "-v":
        PrintStdout(RCSID)

    # Set output width

    if opt == "-w":
        try:
            l = int(val)
        except:
            ErrorMsg(eBADLEN % val)
        if l < MINLEN:
            ErrorMsg(eLINELEN)
        ProgramOptions[MAXLINELEN] = l

    # Select whether 'old' replacement string is a regex or not

    if opt == "-X":
        ProgramOptions[REGEX] = False

    if opt == "-x":
        ProgramOptions[REGEX] = True


# At this point, the command line has been fully processed and the
# container fully populated.  Provide debug info about both if
# requested.

if ProgramOptions[DEBUG]:

    # Dump what we know about the command line

    DumpList(dCMDLINE, "", sys.argv)
    DumpList(dPROGENV, "", envopt)
    DumpList(dRESOLVEDOPTS, "", OPTIONS)

    # Dump what we know about included files

    DumpList(dINCLFILES, "", IncludedFiles)

    # Dump what we know about the container

    targs.DumpObj()


# Perform reqested renamings

targs.ProcessRenameRequests()


# Release the target container if we created one

del targs

