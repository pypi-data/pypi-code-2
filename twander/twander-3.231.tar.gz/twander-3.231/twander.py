#!/usr/bin/env python
# twander - Wander around the file system
# Copyright (c) 2002-2009 TundraWare Inc.  All Rights Reserved.
# For Updates See:  http://www.tundraware.com/Software/twander

# Program Information

PROGNAME = "twander"
RCSID    = "$Id: twander.py,v 3.231 2009/07/01 07:29:20 tundra Exp $"
VERSION  = RCSID.split()[2]

# Copyright Information

DATE         = "2002-2009"
CPRT         = "(c)"
OWNER        = "TundraWare Inc."
RIGHTS       = "All Rights Reserved."
COPYRIGHT    = "Copyright %s %s %s  %s" % (CPRT, DATE, OWNER, RIGHTS)


#----------------------------------------------------------#
#                     Imports                              #
#----------------------------------------------------------#

from socket import getfqdn
from stat import *
import getopt
from fnmatch import fnmatch
import mutex
import os
import re
import sys
import thread
import time

from Tkinter import *
from tkMessageBox import askyesno, showerror, showinfo, showwarning
from tkSimpleDialog import askinteger, askstring

#####
# Imports conditional on OS
#####

# Set OS type - this allows us to trigger OS-specific code
# where needed.

OSNAME     = os.name
OSPLATFORM = sys.platform

# If we're on Win32, try to load win32all stuff if possible

WIN32ALL = False
if OSPLATFORM == 'win32':
    try:
        from win32api import GetLogicalDriveStrings as GetDrives
        from win32api import GetUserName, GetFileAttributes, GetComputerName, GetDiskFreeSpace, GetVolumeInformation
        from win32file import GetDriveType
        from win32wnet import WNetGetUniversalName
        import win32con
        from win32security import *
        WIN32HOST = GetComputerName()
        WIN32ALL = True
    except:
        WIN32ALL = False


# Get unix password and group features

if OSNAME == 'posix':
    import grp
    import pwd


#----------------------------------------------------------#
#          Variables User Might Change                     #
#----------------------------------------------------------#

#####
# Default Key Assignments
#####

# General Program Commands

CLRHIST       = '<Control-y>'              # Clear Command History
FONTDECR      = '<Control-bracketleft>'    # Decrease Font Size
FONTINCR      = '<Control-bracketright>'   # Increase Font Size
MOUSECTX      = '<ButtonRelease-3>'        # Pop-up Command Menu
MOUSEDIR      = '<Shift-ButtonRelease-3>'  # Pop-up Directory Menu
MOUSEHIST     = '<Shift-Control-ButtonRelease-3>' # Pop-up History Menu
MOUSESC       = '<Alt-Control-ButtonRelease-1>'    # Pop-up Shortcut Menu
MOUSESORT     = '<Alt-Shift-ButtonRelease-3>'     # Pop-up Sort Menu
KEYPRESS      = '<KeyPress>'               # Any keypress (for commands)
QUITPROG      = '<Control-q>'              # Quit the program
READCONF      = '<Control-r>'              # Re-read the configuration file
REFRESH       = '<Control-l>'              # Refresh screen
TOGAUTO       = '<Control-o>'              # Toggle autorefreshing
TOGDETAIL     = '<Control-t>'              # Toggle detail view
TOGLENGTH     = '<Control-0>'              # Toggle length display between actual and normalized
TOGSYMDIR     = '<Control-asciitilde>'     # Toggle sorting of symbolic links pointing to directories
TOGSYMEXPAND  = '<Control-exclam>'         # Toggle symbolic link expansion
TOGSYMRESOLV  = '<Control-at>'             # Toggle absolute symbolic link resolution
TOGWIN32ALL   = '<Control-w>'              # Toggle win32all features, if available

# Directory Navigation

CHANGEDIR   = '<Control-x>'              # Enter a new path
DIRHOME     = '<Control-h>'              # Goto $HOME
DIRBACK     = '<Control-b>'              # Goto previous directory
DIRROOT     = '<Control-j>'              # Goto root directory
DIRSTART    = '<Control-s>'              # Goto starting directory
DIRUP       = '<Control-u>'              # Go up one directory level
DRIVELIST   = '<Control-k>'              # On Win32, display Drive List View if possible
MOUSEBACK   = '<Control-Double-ButtonRelease-1>'  # Go back one directory with mouse
MOUSEUP     = '<Control-Double-ButtonRelease-3>'  # Go up one directory with mouse

# Selection Keys

SELALL      = '<Control-comma>'          # Select all items
SELINV      = '<Control-i>'              # Invert the current selection
SELNONE     = '<Control-period>'         # Unselect all items
SELNEXT     = '<Control-n>'              # Select next item
SELPREV     = '<Control-p>'              # Select previous item
SELEND      = '<Control-e>'              # Select bottom item
SELTOP      = '<Control-a>'              # Select top item

# Scrolling Commands

PGDN        = '<Control-v>'              # Move page down
PGUP        = '<Control-c>'              # Move page up
PGRT        = '<Control-g>'              # Move page right
PGLFT       = '<Control-f>'              # Move page left


# Execute Commands

RUNCMD      = '<Control-z>'              # Run arbitrary user command
SELKEY      = '<Return>'                 # Select item w/keyboard
MOUSESEL    = '<Double-ButtonRelease-1>' # Select item w/mouse

# Directory Shortcuts

KDIRSC1     = '<F1>'
KDIRSC2     = '<F2>'
KDIRSC3     = '<F3>'
KDIRSC4     = '<F4>'
KDIRSC5     = '<F5>'
KDIRSC6     = '<F6>'
KDIRSC7     = '<F7>'
KDIRSC8     = '<F8>'
KDIRSC9     = '<F9>'
KDIRSC10    = '<F10>'
KDIRSC11    = '<F11>'
KDIRSC12    = '<F12>'
KDIRSCSET   = "<Control-8>"

# Program Memories

MEMCLR1     = '<Control-F1>'
MEMCLR2     = '<Control-F2>'
MEMCLR3     = '<Control-F3>'
MEMCLR4     = '<Control-F4>'
MEMCLR5     = '<Control-F5>'
MEMCLR6     = '<Control-F6>'
MEMCLR7     = '<Control-F7>'
MEMCLR8     = '<Control-F8>'
MEMCLR9     = '<Control-F9>'
MEMCLR10    = '<Control-F10>'
MEMCLR11    = '<Control-F11>'
MEMCLR12    = '<Control-F12>'

MEMCLRALL   = '<Control-m>'              # Clear all memories

MEMSET1     = '<Alt-F1>'                 # Set program memories
MEMSET2     = '<Alt-F2>'
MEMSET3     = '<Alt-F3>'
MEMSET4     = '<Alt-F4>'
MEMSET5     = '<Alt-F5>'
MEMSET6     = '<Alt-F6>'
MEMSET7     = '<Alt-F7>'
MEMSET8     = '<Alt-F8>'
MEMSET9     = '<Alt-F9>'
MEMSET10    = '<Alt-F10>'
MEMSET11    = '<Alt-F11>'
MEMSET12    = '<Alt-F12>'

# Sorting Keys

SORTBYNONE   = '<Shift-F10>'             # Select sorting parameters
SORTBYPERMS  = '<Shift-F1>'
SORTBYLINKS  = '<Shift-F2>'
SORTBYOWNER  = '<Shift-F3>'
SORTBYGROUP  = '<Shift-F4>'
SORTBYLENGTH = '<Shift-F5>'
SORTBYTIME   = '<Shift-F6>'
SORTBYNAME   = '<Shift-F7>'
SORTREV      = '<Shift-F11>'
SORTSEP      = '<Shift-F12>'

# Wildcard Features

MOUSEWILDFILTER = '<Alt-Control-ButtonRelease-2>'   # Pop-up Filter Wildcard Menu
MOUSEWILDSEL    = '<Alt-Control-ButtonRelease-3>'   # Pop-up Selection Wildcard Menu
FILTERWILD      = '<Control-equal>'          # Filter file list with wildcard
SELWILD         = '<Control-backslash>'      # Select using wildcards
TOGFILT         = '<Control-minus>'          # Invert the filter wildcard logic
TOGHIDEDOT      = '<Control-9>'              # Toggle display of dotfiles

#####
# GUI Defaults
#####

#####
# Initial Size And Postition In Pixels
#####

HEIGHT   = 600
WIDTH    = 800
STARTX   = 0
STARTY   = 0

#####
# Default Colors
#####

# Main Display Colors

BCOLOR  = "black"
FCOLOR  = "green"

# Menu Colors

MBARCOL = "beige"
MBCOLOR = "beige"
MFCOLOR = "black"

# Help Screen Colors

HBCOLOR = "lightgreen"
HFCOLOR = "black"

#####
# Default Display Fonts
#####

# Main Display Font

FNAME = "Courier"
FSZ   = 12
FWT   = "bold"

# Menu Font

MFNAME = "Courier"
MFSZ   = 12
MFWT   = "bold"

# Help Screen Font

HFNAME = "Courier"
HFSZ   = 10
HFWT   = "italic"


#------------------- Nothing Below Here Should Need Changing ------------------#


#----------------------------------------------------------#
#              Constants & Literals                        #
#----------------------------------------------------------#



#####
# Booleans
#####

# Don't need to define True & False - they are defined in the Tkinter module


#####
# Symbolic Constants Needed Below
#####

#####
# Defaults
#####

ACTUALLENGTH    = False           # Show actual file lengths
ADAPTREFRESH    = True            # Dynamically adjust refresh intervals
AFTERCLEAR      = True            # Clear all selections following REFRESHAFTER
AFTERWAIT       = 1               # Seconds to wait before REFRESHAFTER
AUTOREFRESH     = True            # Automatically refresh the directory display?
CMDMENUSORT     = False           # Sort the command menu?
CMDSHELL        = ""              # No CMDSHELL processing
DEBUGLEVEL      = 0               # No debug output
DEFAULTSEP      = "==>"           # Default separator in PROMPT and YES definitions
DOTFILE         = '.'             # Leading string of files suppressed by HIDEDOTFILES
FORCEUNIXPATH   = False           # Force Unix path separators regardless of OS
HIDEDOTFILES    = False           # Suppress display of files begining with DOTFILE
INVERTFILTER    = False           # Invert wildcard filtering logic
ISODATE         = False           # Display date/time in ISO 8601 Format
MAXMENU         = 32              # Maximum length of displayed menu
MAXMENUBUF      = 250             # Maximum size of internal menu buffer
MAXNESTING      = 32              # Maximum depth of nested variable definitions
NODETAILS       = False           # True means details can never be displayed
NONAVIGATE      = False           # True means that all directory navigation is prevented
QUOTECHAR       = '\"'            # Character to use when quoting Built-In Variables
REFRESHINT      = 5000            # Interval (ms) for automatic refresh
SCALEPRECISION  = 1               # Precision of scaled length representation
SORTBYFIELD     = "Name"          # Field to use as sort key
SORTREVERSE     = False           # Reverse specified sort order?
SORTSEPARATE    = True            # Separate Directories and Files in sorted displays?
SYMDIR          = True            # Sort symlinks pointing to directories as directories
SYMEXPAND       = True            # Expand symlink to show its target
SYMRESOLV       = False           # Show absolute path of symlink target
USETHREADS      = False           # Use threads on Unix?
USEWIN32ALL     = True            # Use win32all features if available?
WARN            = True            # Warnings on?
WILDNOCASE      = False           # Turns on case-insensitive wildcard matching
WIN32ALLON      = True            # Flag for toggling win32all features while running

# Wildcards are case-insensitive on Win32 by default

if OSPLATFORM == 'win32':
    WILDNOCASE = True

#####
# Constants
#####

# General Constants


CMDESCAPE     = '"'             # Character to force literal dialog processing
CMDSHELLESC   = CMDESCAPE       # Disable CMDSHELL processing for a  manual command entry
KB            = 1024            # 1 KB constant
MB            = KB * KB         # 1 MB constant
GB            = MB * KB         # 1 GB constant
HOMEDIRMARKER = '~'             # Shortcut string used to indicate home directory
NUMFUNCKEY    = 12              # Number of function keys
NUMPROGMEM    = 12              # Number of program memories
POLLINT       = 250             # Interval (ms) the poll routine should run
PSEP          = os.sep          # Character separating path components
REFRESHINDI   = "*"             # Titlebar character used to indicate refresh underway
REFRESHAFTER  = '+'             # Indicate we want a refresh after a command runs
SHOWDRIVES    = '\\\\'          # Logical directory name for Win32 Drive Lists
STRICTMATCH   = CMDESCAPE       # Tells wildcard system to enforce strict matching
STRIPNL       = '-'             # Tells variable execution to replace newlines with spaces
TTLMAXDIR     = 60              # Maximum length of current directory path to show in titlebar
TTLDIR2LONG   = "..."           # String to place at front of long dir paths in titlebar

# Sort Field Names In Normal View

fNONE        = "No Sort"
fPERMISSIONS = "Permissions"
fLINKS       = "Links"
fOWNER       = "Owner"
fGROUP       = "Group"
fLENGTH      = "Length"
fDATE        = "Time"
fNAME        = "Name"

# Sort Field Names In Drive List View

dlvNONE      = "No Sort"
dlvLABEL     = "Label/Share"
dlvTYPE      = "Drive Type"
dlvFREE      = "Free Space"
dlvTOTAL     = "Total Space"
dlvLETTER    = "Drive Letter"

# 'Fake' sorting field used to set SORTREVERSE and SORTSEPARATE

fREVERSE     = "Reverse"
fSEPARATE    = "Separate"

# Build a dictionary whose keys are the names of all the legal sort fields
# and whose entries are tuples in the form:
#
#   (field #,
#    Name Of Sort Option In Normal View,
#    Name Of Sort Option In Drive List View)
#
# When preparing to actually sort, BuildDirList() gets information on
# each file from FileDetails() in the form of a set of fields in a
# list.  The field # entered loaded here, tells BuildDirList() just
# *which* of the fields (list position) is relevant to each of the
# sort types.
#
# Placing a None value in either of the last two tuple entries causes the
# keystroke combination associated with that sort option to be ignored AND
# prevents that option from appearing in the Sort Menu.
#
# Note that fNONE indicates that no sorting is to be done, so there
# is no real associated sortkey field.

Name2Key = {}
index = -1

for x, y in [(fNONE, dlvNONE), (fPERMISSIONS, dlvLABEL), (fLINKS, dlvTYPE), (fOWNER, dlvFREE),
             (fGROUP, dlvTOTAL), (fLENGTH, dlvLETTER), (fDATE, None), (fNAME, None),
             (fREVERSE, fREVERSE), (fSEPARATE, None)]:
    Name2Key[x.lower()] = (index, x, y)
    index += 1

# Highest key index needed by Drive List View

MAXDLVKEY = 4


#####
# System-Related Defaults
#####

# Default startup directory
STARTDIR = os.path.abspath("." + os.sep)

# Home directory


ENVHOME = os.getenv("HOME")
HOME = ENVHOME or STARTDIR

# Get hostname

# Try the local environment first when looking for the
# hostname.  Only use the socket call as a last
# resort because a misconfigured or malfunctioning
# network will cause this call to be *very* slow
# and 'twander' will take forever to start-up.

HOSTNAME = os.getenv("HOSTNAME") or getfqdn()

# Get the user name

if OSPLATFORM == 'win32':
    if WIN32ALL and USEWIN32ALL and WIN32ALLON:
        USERNAME = GetUserName()
    else:
        USERNAME = os.getenv("LOGNAME")
    

elif OSNAME == 'posix':
    USERNAME = os.getenv("USER")

else:
    USERNAME = ""

# Concatenate them if we got a user name

if USERNAME:
    FULLNAME = "%s@%s" % (USERNAME, HOSTNAME)
else:
    FULLNAME = HOSTNAME



#####
# GUI-Related Stuff
#####

# Constants

CMDMENU_WIDTH = 16


ROOTBORDER    =  1
MENUBORDER    =  2
MENUPADX      =  2
MENUOFFSET    = ROOTBORDER + MENUBORDER + MENUPADX

# Key & Button Event Masks

ShiftMask     = (1<<0)
LockMask      = (1<<1)
ControlMask   = (1<<2)
Mod1Mask      = (1<<3)
Mod2Mask      = (1<<4)
Mod3Mask      = (1<<5)
Mod4Mask      = (1<<6)
Mod5Mask      = (1<<7)
Button1Mask   = (1<<8)
Button2Mask   = (1<<9)
Button3Mask   = (1<<10)
Button4Mask   = (1<<11)
Button5Mask   = (1<<12)

# There are some event bits we don't care about -
# We'll use the following constant to mask them out
# later in the keyboard and mouse handlers.

DontCareMask  = LockMask | Mod2Mask | Mod3Mask | Mod4Mask | Mod5Mask

# Some things are OS-dependent

if OSPLATFORM == 'win32':
    AltMask = (1<<17)
    DontCareMask |= Mod1Mask   # Some versions of Win32 set this when Alt is pressed
else:
    AltMask = Mod1Mask


# Name The Key/Mouse Assignments Which We Do Not Allow To Be Rebound In The Config File

NOREBIND =  ["MOUSECTX", "MOUSEDIR", "MOUSEHIST", "MOUSESC", "MOUSESORT", "MOUSEWILDFILTER", "MOUSEWILDSEL", "MOUSEBACK","MOUSEUP", "MOUSESEL"]


#####
# Stat-Related Stuff
#####

# Misc. Stat-Related Strings

FILEGROUP     = "group"
FILEOWNER     = "owner"
NODRIVE       = "<Drive Empty>"
NOLABEL       = "<No Label>"
SYMPTR        = " -> "
UNAVAILABLE   = "Unavailable"
WIN32GROUP    = "win32" + FILEGROUP
WIN32OWNER    = "win32" + FILEOWNER
WIN32FREE     = "free"
WIN32TOTAL    = "total  "        # Leave trailing space - drive letter follows

MAX_SZ_CHARS      = 17    # Number of digits needed to display max drive/file size - including commas
SZ_TRAILING_SPACE = 2     # Number of trailing spaces to add after a drive/file size field.

MAX_SZ_FIELD  =  MAX_SZ_CHARS + SZ_TRAILING_SPACE  # Biggest a drive/file size string can be


if WIN32ALL:
    
    # Used with win32all-based permissions logic.
    # Format for each entry is: (mask to test, symbol if true).
    # Position in tuple determines position in display.

    win32all_mode = ((win32con.FILE_ATTRIBUTE_DIRECTORY,  'd'),
                     (win32con.FILE_ATTRIBUTE_ARCHIVE,    'A'),
                     (win32con.FILE_ATTRIBUTE_COMPRESSED, 'C'),
                     (win32con.FILE_ATTRIBUTE_HIDDEN,     'H'),
                     (win32con.FILE_ATTRIBUTE_NORMAL,     'N'),
                     (win32con.FILE_ATTRIBUTE_READONLY,   'R'),
                     (win32con.FILE_ATTRIBUTE_SYSTEM,     'S'))

    win32all_type = ((win32con.DRIVE_CDROM,     'CD/DVD'),
                     (win32con.DRIVE_FIXED,     'Fixed'),
                     (win32con.DRIVE_RAMDISK,   'Ramdisk'),
                     (win32con.DRIVE_REMOTE,    'Remote'),
                     (win32con.DRIVE_REMOVABLE, 'Removable'))

    # Size of each of the drive detail fields, including room for trailing space.
    

    SZ_DRIVE_SHARE  = 24   # Can be label or share string - leave plenty of room
    SZ_DRIVE_TYPE   = 20
    SZ_DRIVE_FREE   = MAX_SZ_FIELD
    SZ_DRIVE_TTL    = MAX_SZ_FIELD

    SZ_DRIVE_TOTAL = SZ_DRIVE_SHARE + SZ_DRIVE_TYPE + SZ_DRIVE_FREE + len(WIN32FREE) + \
                     SZ_DRIVE_TTL + len(WIN32TOTAL)

# Constants used with the more usual Unix-style details
# Used both by Unix and Win32 when win32all is not present or disabled.


# Month Name -> Number Conversion Needed For ISO Representation

ST_MONTHS     = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04",
                 "May":"05", "Jun":"06", "Jul":"07", "Aug":"08",
                 "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"
                }


# Permissions

ST_PERMIT     = ["---", "--x", "-w-", "-wx",
                 "r--", "r-x", "rw-", "rwx"]

# Special file type lookup

ST_SPECIALS   = {"01":"p", "02":"c", "04":"d", "06":"b",
                 "10":"-", "12":"l", "14":"s"}

# Size of each status display field including trailing space
# These are sized for the worst-case: Win32 with win32all features

ST_SZMODE     = 12
ST_SZNLINK    = 5
ST_SZUNAME    = 18
ST_SZGNAME    = 18
ST_SZLEN      = MAX_SZ_FIELD
ST_SZMTIME    = 18

ST_SZTOTAL    = ST_SZMODE + ST_SZNLINK + ST_SZUNAME + ST_SZGNAME + \
                ST_SZLEN + ST_SZMTIME


# Special Bit Masks

STICKY_MASK   = 1
SETGID_MASK   = 2
SETUID_MASK   = 4


#####
# Configuration File-Related Constants & Globals
#####

ASSIGN      = "="               # Assignment for variable definitions
ASSOCBLANK  = "RESETASSOC"      # Internally used to indicate a blank ASSOC RHS
ASSOCDFLT   = "*"               # Symbol for default association action
ASSOCEXCL   = "!"               # Symbol for association exclusion action
ASSOCIATE   = "ASSOC"           # Association keyword
ASSOCNOCASE = "/"               # Introducer used to indicate case-insensitive ASSOCiations
CONF        = ""                # Config file user selected with -c option
COMMENT     = r"#"              # Comment introducer string
ENVVBL      = r'$'              # Symbol denoting an environment variable
FAKEFIELD   = r'#FAKEFIELD'     # Unsplittable field used to preserve PROMPT/YESNO content
STARTUP     = r'Starting Up'    # Used when doing parse of first config file
VAREXECUTE  = r'`'              # Indicate we want content of variable name to be executed


# Names Of Conditionals, Directives, And Pre-Defined Symbols

CONDENDIF    = '.endif'
CONDEQUAL    = '=='
CONDIF       = '.if'
CONDNOTEQUAL = '!='
DIRECTINC    = '.include'
SYMOS        = '.OS'
SYMPLATFORM  = '.PLATFORM'

# Globals Supporting Configutration File Conditional Processing

ConditionalStack  = []         # Stack for tracking conditional state


# Variable Name Pattern Matching Stuff

DIRSC      = "DIRSC"                            # Directory Shortcut naming
reDIRSC    = r'^' + DIRSC + r'([1-9]|1[0-2])$'  # Regex describing Directory Shortcut names
rePROMPT   = r'\+{PROMPT:.*?\}'                 # Regex describing prompt builtin
reVAR      = r"\[.+?\]"                         # Regex describing variable notation
reYESNO    = r'\{YESNO:.*?\}'                   # Regex describing yes or no builtin
WILDFILTER = "WILDFILTER"                       # Configuration statement for pre-loading Filter list
WILDSELECT = "WILDSELECT"                       # Configuration statement for pre-loading Selection list


# Create actual regex matching engines

REDIRSC    = re.compile(reDIRSC)
REPROMPT   = re.compile(rePROMPT)
REVAR      = re.compile(reVAR)
REYESNO    = re.compile(reYESNO)
CONDVAR    = re.compile(r'^' + reVAR + r'$')

# Built-In Variables

DIR         = r'[DIR]'
DSELECTION  = r'[DSELECTION]'
DSELECTIONS = r'[DSELECTIONS]'
HASH        = r'[HASH]'
MEM1        = r'[MEM1]'
MEM2        = r'[MEM2]'
MEM3        = r'[MEM3]'
MEM4        = r'[MEM4]'
MEM5        = r'[MEM5]'
MEM6        = r'[MEM6]'
MEM7        = r'[MEM7]'
MEM8        = r'[MEM8]'
MEM9        = r'[MEM9]'
MEM10       = r'[MEM10]'
MEM11       = r'[MEM11]'
MEM12       = r'[MEM12]'
PROMPT      = r'{PROMPT:'
SELECTION   = r'[SELECTION]'
SELECTIONS  = r'[SELECTIONS]'
YESNO       = r'{YESNO:'

# Shortcuts to the builtins available in RUNCMD

RUNCMD_SC = {"[D]"  : DIR,
             "[DN]" : DSELECTION,
             "[DS]" : DSELECTIONS,
             "[SN]" : SELECTION,
             "[SS]" : SELECTIONS,
             "[1]"  : MEM1,
             "[2]"  : MEM2,
             "[3]"  : MEM3,
             "[4]"  : MEM4,
             "[5]"  : MEM5,
             "[6]"  : MEM6,
             "[7]"  : MEM7,
             "[8]"  : MEM8,
             "[9]"  : MEM9,
             "[10]" : MEM10,
             "[11]" : MEM11,
             "[12]" : MEM12
             }
              

#----------------------------------------------------------#
#            Prompts, & Application Strings                #
#----------------------------------------------------------#


#####
# Menu, Error, Information, & Warning  Messages
#####

# Title-Bar Strings

TTLAUTO       = "Auto:"
TTLHIDEDOT    = "HideDot:"
TTLFILES      = "Files:"
TTLFILTER     = "Filter:"
TTLSIZE       = "Size:"
TTLSORTFLD    = "Sort:"
TTLSORTREV    = "Rev:"
TTLSORTSEP    = "Sep:"
TTLSYMLINKS   = "Symlinks:"


# Convert Logical Values Into Yes/No String

YesOrNo       = {True:"Y", False:"N"}


# Menu Button Titles

COMMANDMENU   = 'Commands'        # Title for Command Menu button
DIRMENU       = 'Directories'     # Title for Directory Menu button
HISTMENU      = 'History'         # Title for History Menu button
SCMENU        = 'Shortcuts'       # Title for Shortcut Menu button
SORTMENU      = 'Sorting'         # Title for Sort Menu button
FILTERMENU    = 'Filter'          # Title for Wildcard Filter Menu button
SELECTMENU    = 'Select'          # Title for Wildcard Selection Menu button
HELPMENU      = 'Help'            # Title for Help Menu button

# Sort Menu-Related

# And their names - used in Sorting Menu

sSORTBY        = "Sort By"
sREVERSE       = "Reverse Sort"
sSEPARATE      = "Separate Dirs/Files"




# Help Menu-Related

WEBSITE       = "Homepage:\n\nhttp://www.tundraware.com/Software/twander"
ABOUT         = "%s %s\n\nCopyright %s %s\n%s\n\n%s\n\n%s"  % (PROGNAME, VERSION, CPRT, DATE, OWNER, RIGHTS, WEBSITE)
hABOUT        = 'About'
hASSOC        = 'Associations'
hCOMMANDS     = 'Command Definitions'
hINTVBLS      = 'Internal Program Variables'
hKEYS         = 'Keyboard Assignments'
hNONE         = 'No %s Found.'
hOPTVBLS      = 'User-Settable Options'
hUSERVBLS     = 'User-Defined Variables'


# Errors

eBADEXEC      = "Cannot Run %s.\n File Is Not Executable And Has No Application Association"
eBADROOT      = "%s Is Not A Directory"
eDIRRD        = "Cannot Open Directory : %s  ---  Check Permissions."
eERROR        = "ERROR"
eINITDIRBAD   = "Cannot Open Starting Directory : %s - Check Permissions - ABORTING!."
eOPEN         = "Cannot Open File: %s"
eTOOMANY      = "You Can Only Specify One Starting Directory."

# Information

iNOSTAT       = "Details Unavailable For This File:  "

# Prompts

pCHPATH       = "Change Path"
pSCCHANGE     = "Change Directory Shortcut"
pSCNUM        = "Assign Current Directory To Shortcut # (1-12):"
pENCMD        = "Enter Command To Run:"
pENPATH       = "Enter New Path Desired:"
pENWILD       = "Enter Wildcard - Use %s For Strict Matching:" % STRICTMATCH
pMANUALCMD    = "Manual Command Entry"
pRUNCMD       = "Run Command"
pWILDFILT     = "Filter Files By Wildcard"
pWILDSEL      = "Selection By Wildcard"

# Warnings

wBADCFGLINE   = "Ignoring Line %s.\nBogus Configuration Entry:\n\n%s"
wBADCMD       = "Incorrect Command Syntax At Line %s Of File %s"
wBADDEBUG     = "Ignoring Bogus Debug Level! - %s Is Not In Integer Or Hex Format."
wBADENDIF     = "Ignoring Line %s!\nBogus End-Of-Block Statement:\n\n%s"
wBADENVVBL    = "Ignoring Line %s.\nEnvironment Variable %s Not Set:\n\n%s"
wBADEXE       = "Could Not Execute Command:\n\n%s"
wBADIF        = "Ignoring Line %s.\nImproperly Formed Condition: \n\n%s"
wBADRHS       = "Ignoring Line %s.\nOption Assignment Has Bad Righthand Side:\n\n%s"
wBADSCNUM     = "Ignoring Line %s.\nShortcut Number Must Be From 1-12:\n\n%s"
wBADSORTFLD   = "Don't Know How To Sort By: %s\n\nWill Sort By %s Instead."
wBADVAREXEC   = "Ignoring Line %s.\nExecution Of Variable %s Failed:\n\n%s"
wBADYESNODFLT = "Bad Default Argument For Yes/No Prompt: '%s'\nCommand '%s' Aborted"
wCIRCULARREF  = "Circular .include Reference In '%s', Line '%s'!\n.include Not Processed!"
wCONFOPEN     = "Cannot Open Configuration File:\n%s"
wEXTRAENDIF   = "Ignoring Line %s!\nNo Conditional Block To End:\n\n%s"
wLINKBACK     = "%s Points Back To Own Directory"
wMISSENDIF    = "Configuration File Is Missing %s " + CONDENDIF +" Statement(s)"
wNOCMDS       = "Running With No Commands Defined!"
wNOREBIND     = "Ignoring Line %s.\nCannot Rebind This Keyboard Or Mouse Button Combination:\n\n%s"
wREDEFVAR     = "Ignoring Line %s.\nCannot Redefine Built-In Variable %s:\n\n%s"
wUNDEFVBL     = "Ignoring Line %s.\nUndefined Variable %s Referenced:\n\n%s"
wVBLTOODEEP   = "Ignoring Line %s.\nVariable Definition Nested Too Deeply:\n\n%s"
wWARN         = "WARNING"
wWILDCOMP     = "Cannot Compile Wildcard Expression: %s"


#####
# Debug-Related Stuff
#####

# Debug Levels

# Nibble #1

DEBUGVARS     = (1<<0)   # Dump internal variables
DEBUGSYMS     = (1<<1)   # Dump symbol table
DEBUGCTBL     = (1<<2)   # Dump command table
DEBUGKEYS     = (1<<3)   # Dump key bindings

# Nibble #2

DEBUGCMDS     = (1<<4)   # Dump command execution string
DEBUGDIRS     = (1<<5)   # Dump directory stack contents as it changes
DEBUGHIST     = (1<<6)   # Dump contents of command history stack after command execution
DEBUGMEM      = (1<<7)   # Dump contents of program memories as they change

# Nibble #3

DEBUGWILD     = (1<<8)   # Dump contents of wildcard stack as it changes
DEBUGASSOC    = (1<<9)   # Dump association table
DEBUGRSRV3    = (1<<10)  # Reserved for future use
DEBUGQUIT     = (1<<11)  # Dump debug info and quit program

# Debug Strings

dASSOC        = "ASSOCIATIONS"
dCMD          = "COMMAND"
dCMDTBL       = hCOMMANDS
dDIRSTK       = "DIRECTORY STACK"
dFALSE        = "False"
dFUNCKEYS     = 'Directory Shortcuts'
dHEADER       = "twander Debug Dump Run On: %s\n"
dHIST         = "COMMAND HISTORY STACK"
dINTVAR       = hINTVBLS
dKEYBINDS     = hKEYS
dMEM          = "CONTENTS OF MEMORY %s"
dMEMALL       = "CONTENTS OF ALL PROGRAM MEMORIES"
dNULL         = "None"
dOPTVAR       = hOPTVBLS
dSYMTBL       = hUSERVBLS
dTRUE         = "True"
dFILTER       = "FILTER"
dSELECT       = "SELECT"
dWILDLST      = "%s WILDCARDS"

# Debug Formatting

dASSOCWIDTH   = 10
dCMDWIDTH     = 20
dCOLNUM       = 3
dCOLWIDTH     = 50
dINTVARWIDTH  = 12
dKEYWIDTH     = 16
dOPTIONWIDTH  = 16
dSCWIDTH      = 6
dUSRVBLWIDTH  = 20

# List of internal program variables to dump during debug sessions

DebugVars = ["RCSID", "OSNAME", "HOSTNAME", "USERNAME", "OPTIONS", "CONF", "HOME", "PSEP", "POLLINT"]


#####
# Usage Information
#####

uTable = [PROGNAME + " " + VERSION + " - %s\n" % COPYRIGHT,
          "usage:  " + PROGNAME + " [-cdhqrstvwxy] [startdir] where,\n",
          "          startdir  name of directory in which to begin (default: current dir)",
          "          -c file   name of configuration file (default: $HOME/." + PROGNAME +
                     " or PROGDIR/." + PROGNAME + ")",
          "          -d level  set debugging level (default: 0, debugging off)",
          "                Bit Assignments:",
          "                         0 - Dump Internal Options & User-Settable Options (0x001)",
          "                         1 - Dump User-Defined Variables (0x002)",
          "                         2 - Dump Command Definitions (0x004)",
          "                         3 - Dump Key Bindings (0x008)",
          "                         4 - Display, Do Not Execute, Commands When Invoked (0x010)",
          "                         5 - Dump Directory Stack As It Changes (0x020)",
          "                         6 - Dump Command History Stack After Command Executes (0x040)",
          "                         7 - Dump Contents Of Program Memories As They Change (0x080)",
          "                         8 - Dump Contents Of Filter/Selection Wildcard Lists As They Change (0x100)",
          "                         9 - Dump Association Table (0x200)",
          "                        10 - Reserved (0x400)",
          "                        11 - Dump Requested Debug Information And Exit Immediately (0x800)",
          "          -h        print this help information",
          "          -q        quiet mode - no warnings (default: warnings on)",
          "          -r        turn off automatic content refreshing (default: refresh on)",
          "          -t        no quoting when substituting Built-In Variables (default: quoting on)",
          "          -v        print detailed version information",
          ]


#---------------------------Code Begins Here----------------------------------#


#----------------------------------------------------------#
#             General Support Functions                    #
#----------------------------------------------------------#


#####
# Print An Error Message
#####

def ErrMsg(emsg):
    showerror(PROGNAME + " " + VERSION + "    " + eERROR, emsg)

# End of 'ErrMsg()'


#####
# Convert A Dictionary In A Multicolumn List Of Strings
#####

def FormatMultiColumn(dict, numcols=dCOLNUM, lhswidth=dKEYWIDTH, colwidth=dCOLWIDTH):

    retval = []

    # Get and sort list of keys
    
    keys = dict.keys()
    keys.sort()

    # Make sure it is of proper length for multi-column output

    while len(keys) % numcols:
        keys.append("")

    # Produce output

    k=0
    columnlen = len(keys)/numcols
    while k != columnlen:

        # Produce output 'numcols' at a time
        
        entry = []
        for i in range(numcols):
            
            key = keys[k+(i*columnlen)]
            if key:
                val = dict[key]
            else:
                val = ""
            entry.append(PadString(key, lhswidth) + val)
            
        # Turn it into a single string

        s=""
        for x in entry:
            s += PadString(x, colwidth)

        # And stuff it into the return object

        retval.append(s)

        # Point to the next tuple of entries

        k += 1


    # Return the results

    return retval
    
# End of 'FormatMultiColumn()'


#####
# Run A Command, Returning Status And Output
# This Version Runs On Win32 Unlike commands.getstatusoutput()
#####

def GetStatusOutput(command):

    # Handle Windows variants

    if OSPLATFORM == 'win32':
        pipe = os.popen(command, 'r')

    # Handle Unix variants
    
    else: 
        pipe = os.popen('{ ' + command + '; } 2>&1', 'r')

    output = pipe.read()
    status = pipe.close()

    if status == None:
        status = 0
        
    if output[-1] == '\n':
        output = output[:-1]
        
    return status, output

# End of 'GetStatusOutput()'
 

#####
# Build List Of Win32 Drives
#####

def GetWin32Drives():

    # Get Win32 drive string, split on nulls, and get
    # rid of any resulting null entries.

    if WIN32ALL and USEWIN32ALL and WIN32ALLON:
        return filter(lambda x : x, GetDrives().split('\x00'))
    else:
        return ""

# End of 'GetWin32Drives()'


#####
# Convert A File Size Into Equivalent String With Scaling
# Files under 1 MB show actual length
# Files < 1 MB < 1 GB shown in KB
# Files 1 GB or greater, shown in MB
#####

def FileLength(flen):

    # Return actual length of file

    if ACTUALLENGTH:

        # Insert commas for readability

        length = str(flen)
        index  = len(length)-3
        flen   = ""

        while index > -3:
            if index <= 0:
                flen = length[:index+3] + flen
            else:
                flen = ',' + length[index:index+3] + flen
            index -= 3

    # Return normalized length of file

    else:

        # Set the scaling factor and indicator
        
        if flen >= GB:
            norms = (GB, "g")
        elif flen >= MB:
            norms = (MB, "m")
        elif flen >= KB:
            norms = (KB, "k")
        else:
            norms = (1, "")

        # Scale the results and convert into a string
        # displaying SCALEPRECISION worth of digits to
        # the right of the decimal point
        
        sep = ""
        if SCALEPRECISION:
            sep = "."

        factor = norms[0]
        if (factor > 1):
            l, r = str(float(flen)/factor).split(".")
            flen = l + sep + r[:SCALEPRECISION]
        else:
            flen = str(flen)

        flen += norms[1]

    return flen

# End of 'FileLength()'

#####
# Check to see if a passed string matches/does not match the currently
# active filtering wildcard.  If there is no active wildcard, everything
# passes.  This routine also filters any "dotfiles" if the HIDEDOTFILES
# option is enabled.
#####

def FilterMatching(matchthis):

    # Check to see if dotfiles should be hidden.

    if HIDEDOTFILES:

        # For symlinks we want the link name not the target name
        if matchthis.count(SYMPTR):
            fname = matchthis.split(SYMPTR)[-2].split()[-1]

        # Otherwise just use the filename
        else:
            fname = matchthis.split()[-1]

        if fname.startswith(DOTFILE):
            return False

    # Accomodate case-insensitive matching
    # But strict matching overrides this

    if WILDNOCASE and not UI.FilterWildcard[3]:
        wc = UI.FilterWildcard[2]
        matchthis = matchthis.lower()

    else:
        wc = UI.FilterWildcard[1]

    # If there's no active filter, everything matches

    if not wc:
        matched = True

    elif wc.match(matchthis):
        matched = True

    else:
        matched = False

    # Invert the sense of the logic if so dictated, but
    # only if there is actually a wildcard active.

    if wc and INVERTFILTER:
        matched = not matched

    return matched

# End of 'FilterMatching()'

#####
# Pad A String With Spaces To Specified Width.
# Return either that padded string or, if the passed
# string is too large, truncate it to specified length.
# Defaults to left-justification, but can be overriden.
# Optionally can rotate a specified number of leading
# spaces to become trailing spaces after justification
# is complete.
#####

def PadString(string, width, Rjust=False, Trailing=0):

    s = string[:(width-1)]
    if Rjust:
        s = s.rjust(width)
    else:
        s = s.ljust(width)

    # Rotate 'Trailing' number of spaces from left of string to right
    
    while (Trailing > 0) and (s[0] == ' ') :
        s = s[1:] + ' '
        Trailing -= 1

    return s

# End of 'PadString()'


#####
# Process The Configuraton File
# This is called once at program start time
# and again any time someone hits the READCONF key
# while the program is running.
#####

def ProcessConfiguration(event, DoOptionsProcessing=True):
    global CONF, UI, ConditionalStack

    # Cleanout any old configuration data

    UI.Associations  = {ASSOCEXCL:[]}
    UI.CmdTable      = {}
    UI.Commands      = []
    UI.ConfigVisited = []
    UI.DirSCKeys     = ["", "", "", "", "", "",
                        "", "", "", "", "", ""]
    UI.SymTable      = {}


    # Initialize internal parsing data structures

    ConditionalStack = [True,]      # This is a sentinel and guarantees there will
                                    # will always be something in this stack

    # Load Symbol Table with predefined symbols

    UI.SymTable[SYMOS] = os.name
    UI.SymTable[SYMPLATFORM] = OSPLATFORM


    # Unbind all existing key bindings
    for x in UI.KeyBindings.keys():
        UI.DirList.unbind(UI.KeyBindings[x])

    # Initialize keyboard binding variables to their defaults
    # These may be overriden in the configuration file
    # parsing process.

    UI.KeyBindings = {"CLRHIST":CLRHIST,
                      "FONTDECR":FONTDECR,
                      "FONTINCR":FONTINCR,
                      "MOUSECTX":MOUSECTX,
                      "MOUSEDIR":MOUSEDIR,
                      "MOUSEHIST":MOUSEHIST,
                      "MOUSESC":MOUSESC,
                      "MOUSESORT":MOUSESORT,
                      "KEYPRESS":KEYPRESS,
                      "QUITPROG":QUITPROG,
                      "READCONF":READCONF,
                      "REFRESH":REFRESH,
                      "TOGAUTO":TOGAUTO,
                      "TOGDETAIL":TOGDETAIL,
                      "TOGLENGTH":TOGLENGTH,
                      "TOGSYMDIR":TOGSYMDIR,
                      "TOGSYMEXPAND":TOGSYMEXPAND,
                      "TOGSYMRESOLV":TOGSYMRESOLV,
                      "TOGWIN32ALL":TOGWIN32ALL,
                      "CHANGEDIR":CHANGEDIR,
                      "DIRHOME":DIRHOME,
                      "DIRBACK":DIRBACK,
                      "DIRROOT":DIRROOT,
                      "DIRSTART":DIRSTART,
                      "DIRUP":DIRUP,
                      "DRIVELIST":DRIVELIST,
                      "MOUSEBACK":MOUSEBACK,
                      "MOUSEUP":MOUSEUP,
                      "SELALL":SELALL,
                      "SELINV":SELINV,
                      "SELNONE":SELNONE,
                      "SELNEXT":SELNEXT,
                      "SELPREV":SELPREV,
                      "SELEND":SELEND,
                      "SELTOP":SELTOP,
                      "PGDN":PGDN,
                      "PGUP":PGUP,
                      "PGRT":PGRT,
                      "PGLFT":PGLFT,
                      "RUNCMD":RUNCMD,
                      "SELKEY":SELKEY,
                      "MOUSESEL":MOUSESEL,
                      "KDIRSC1":KDIRSC1,
                      "KDIRSC2":KDIRSC2,
                      "KDIRSC3":KDIRSC3,
                      "KDIRSC4":KDIRSC4,
                      "KDIRSC5":KDIRSC5,
                      "KDIRSC6":KDIRSC6,
                      "KDIRSC7":KDIRSC7,
                      "KDIRSC8":KDIRSC8,
                      "KDIRSC9":KDIRSC9,
                      "KDIRSC10":KDIRSC10,
                      "KDIRSC11":KDIRSC11,
                      "KDIRSC12":KDIRSC12,
                      "KDIRSCSET":KDIRSCSET,
                      "MEMCLR1":MEMCLR1,
                      "MEMCLR2":MEMCLR2,
                      "MEMCLR3":MEMCLR3,
                      "MEMCLR4":MEMCLR4,
                      "MEMCLR5":MEMCLR5,
                      "MEMCLR6":MEMCLR6,
                      "MEMCLR7":MEMCLR7,
                      "MEMCLR8":MEMCLR8,
                      "MEMCLR9":MEMCLR9,
                      "MEMCLR10":MEMCLR10,
                      "MEMCLR11":MEMCLR11,
                      "MEMCLR12":MEMCLR12,
                      "MEMCLRALL":MEMCLRALL,
                      "MEMSET1":MEMSET1,
                      "MEMSET2":MEMSET2,
                      "MEMSET3":MEMSET3,
                      "MEMSET4":MEMSET4,
                      "MEMSET5":MEMSET5,
                      "MEMSET6":MEMSET6,
                      "MEMSET7":MEMSET7,
                      "MEMSET8":MEMSET8,
                      "MEMSET9":MEMSET9,
                      "MEMSET10":MEMSET10,
                      "MEMSET11":MEMSET11,
                      "MEMSET12":MEMSET12,
                      "SORTBYNONE":SORTBYNONE,
                      "SORTBYPERMS":SORTBYPERMS,
                      "SORTBYLINKS":SORTBYLINKS,
                      "SORTBYOWNER":SORTBYOWNER,
                      "SORTBYGROUP":SORTBYGROUP,
                      "SORTBYLENGTH":SORTBYLENGTH,
                      "SORTBYTIME":SORTBYTIME,
                      "SORTBYNAME":SORTBYNAME,
                      "SORTREV":SORTREV,
                      "SORTSEP":SORTSEP,
                      "MOUSEWILDFILTER":MOUSEWILDFILTER,
                      "MOUSEWILDSEL":MOUSEWILDSEL,
                      "FILTERWILD":FILTERWILD,
                      "SELWILD":SELWILD,
                      "TOGFILT":TOGFILT,
                      "TOGHIDEDOT":TOGHIDEDOT
                      }

    # Set all the program options to their default values
    # This means that a configuration file reload can
    # override the options set previously in the environment
    # variable or on the command line.

    for x in (UI.OptionsBoolean, UI.OptionsNumeric, UI.OptionsString):
        for o in x.keys():
            globals()[o] = x[o]

    # If user specified a config file, try that
    # Otherwise use HOME == either $HOME or ./

    if not CONF:
        CONF = os.path.join(HOME, "." + PROGNAME)

    # Actually read and parse the configuration file.
    ReadConfFile(CONF, STARTUP, 0)

    MissingEndIfs = len(ConditionalStack) - 1

    if MissingEndIfs:
        WrnMsg(wMISSENDIF % str(MissingEndIfs))

    # Make sure any options we've changed are implemented
    if DoOptionsProcessing:
        ProcessOptions()

    # Initialize the command menu
    UI.CmdBtn.menu.delete(0,END)

    # And disable it
    UI.CmdBtn.config(state=DISABLED)

    # Now load the menu with the final set of commands

    # First see if the user wanted the list sorted
    
    if CMDMENUSORT:
        UI.Commands.sort()

    for cmdkey in UI.Commands:
        cmdname = UI.CmdTable[cmdkey][0]
        UI.CmdBtn.menu.add_command(label=PadString(cmdname, CMDMENU_WIDTH) + "(" + cmdkey + ")",
                                   command=lambda cmd=cmdkey: CommandMenuSelection(cmd))
    # Enable the menu if it has entries.
    # If no commands are defined, warn the user.
    
    if UI.CmdBtn.menu.index(END):
        UI.CmdBtn['menu'] = UI.CmdBtn.menu
        UI.CmdBtn.configure(state=NORMAL)
    else:
        WrnMsg(wNOCMDS)

    

    return 'break'

# End of 'ProcessConfiguration()'


#####
# Read & Parse A Configuration File
# Called By ProcessConfiguration() And Each Time
# A '.include' Is Encountered Within A Configuration File
#####

def ReadConfFile(newfile, currentfile, linenum):

    # Keep track of every configuration file processed

    fqfilename = os.path.abspath(newfile)
    
    if fqfilename not in UI.ConfigVisited:
        UI.ConfigVisited.append(fqfilename)

    # And prevent circular references

    else:
        WrnMsg(wCIRCULARREF % (currentfile, linenum))
        return

    # Keep track of the line number on a per-file basis
    
    linenum = 0
    try:
        cf = open(newfile)
        # Successful open of config file - Begin processing it

        # Process and massage the configuration file
        for line in cf.read().splitlines():
            linenum += 1

            # Parse this line
            if line:
                ParseLine(line, newfile, linenum)

        # Close the config file
        cf.close()

    except:
        WrnMsg(wCONFOPEN % newfile)

# End of 'ReadConfFile()'


#####
# Parse A Line From A Configuration File
#####


def ParseLine(line, file, num):
    global UI, ConditionalStack

    ###
    # Cleanup the line
    ###
    
    # Get rid of trailing newline, if any

    if line[-1] == '\n':
        line = line[:-1]

    # Strip comments out
    
    idx = line.find(COMMENT)
    if idx > -1:
        line = line[:idx]

    # Strip off leading/trailing spaces
    cleanline = line.strip()

    # Preserve the contents of PROMPT or YESNO builtins.

    # If we didn't do this, the split() below would trash the
    # whitespace within prompts/defaults.  The user may
    # specifically *want* whitespace formatting in either the
    # prompt or the default, so we need to preserve their
    # entry exactly as-is.

    # Algorithm:
    #
    #   1) Find every instance of a PROMPT or YESNO builtin
    #   2) Save it in 'saveliteral'
    #   3) Replace it with a bogus,  *unsplittable* string ending with its 'saveliteral' index
    #   4) Split the line
    #   5) Replace original content in the appropriate spot(s)
    

    # Steps 1-3
    
    saveliteral = {}
    index = 0

    for matchtest in (REPROMPT, REYESNO):
        for match in matchtest.finditer(cleanline):
            fakefield = FAKEFIELD + str(index)
            found=match.group()
            saveliteral[fakefield] = found
            cleanline = cleanline.replace(found, fakefield)
            index += 1


    # Step 4: Split what's left into separate fields again

    fields = cleanline.split()

    # Step 5: Now restore the strings we want to preserve literally (if any)

    # Scan through each field, replacing fake entries with the original text.

    for fake in saveliteral.keys():
        index = 0
        while index < len(fields):
            if fields[index].count(fake):
                fields[index] = fields[index].replace(fake, saveliteral[fake])
            index += 1

    # Make a copy of the fields which is guaranteed to have at 
    # least two fields for use in the variable declaration tests.
    
    dummy = fields[:]
    dummy.append("")


    # Before going on, make sure we're even supposed to process the line.
    # If we are currently in the midst of a *false* conditional
    # block, we must throw this line away.  The only thing
    # we'll accept in that case is more conditional statements.

    if (not ConditionalStack[-1]) and (dummy[0] not in (CONDIF, CONDENDIF)):
        return
    
    ###
    # Blank Lines - Ignore
    ###

    if len(fields) == 0:
        pass

    ###
    # Conditionals
    ###

    # Legal conditional statements are in one of several forms:
    #
    # .if [SYMBOL]
    # .if [SYMBOL] == string OR .if [SYMBOL] != string
    # .if [SYMBOL]== string  OR .if [SYMBOL]!= string
    # .if [SYMBOL] ==string  OR .if [SYMBOL] !=string
    # .if [SYMBOL]==string   OR .if [SYMBOL]!=string
    # .endif

    # Additionally, [SYMBOL] can also be an environment
    # variable - [$SYMBOL]

    #####
    # Process Conditional Beginning-Of-Block Statement
    #####

    elif fields[0] == CONDIF:

        # Hack off the conditional statement so we can
        # process what's left

        condline = cleanline[len(CONDIF):].strip()
        
        # Iterate through all legitimate possible
        # beginning-of-block forms.  The iteration
        # tuple is in the form: (condition, # of required arguments)

        args = []
        condition, var, cmpstr = "", "", ""
        
        for condtype, numargs in [(CONDEQUAL, 2), (CONDNOTEQUAL, 2), (None, 1)]:

            # Process forms that have arguments following the variable reference
            if condtype:
                if condline.count(condtype):
                    args      = condline.split(condtype)
                    condition = condtype
                    break
                
            # Process the existential conditional form

            else:
                args      = condline.split()
                condition = condtype
                break

        # Check for correct syntax
        # We have to have the right number of arguments, AND
        # the condition variable has to be in proper variable reference form: [VAR] AND
        # the rightmost argument cannot be an empty string

        if (len(args) != numargs) or (not CONDVAR.match(args[0].strip())) or (not args[-1]):
            WrnMsg(wBADIF % (num, line), fn=file)
            return

        # Syntax OK, process the conditional test
        else:

            # Assume the conditional test fails
            conditional = False

            # Strip the reference syntax to get just the variable name
            var    = args[0].strip()[1:-1]

            # Handle the equality tests
            
            if condition:
                
                # De-reference the variable's contents, accomodating
                # both Environment and User-Defined variable types

                if var[0] == ENVVBL:
                    var = os.getenv(var[1:])

                else:
                    var = UI.SymTable.get(var)


                # Get the comparison string
                cmpstr = args[1].strip()

                # Now process each type of condition explicitly

                if condition == CONDEQUAL:
                    if var == cmpstr:
                        conditional = True

                elif condition == CONDNOTEQUAL:
                    if var != cmpstr:
                        conditional = True

            # Handle the existential conditional
            else:

                if var[0] == ENVVBL:
                    if os.environ.has_key(var[1:]):
                        conditional = True

                elif UI.SymTable.has_key(var):
                    conditional = True

        # Even if the current conditional is True, we do not
        # process its contents if the *containing* scope is False.
        # i.e., A given conditional's truth is determined by its
        # own state AND the state of the containing scope.

        ConditionalStack.append(ConditionalStack[-1] and conditional)

    #####
    # Process Conditional End-Of-Block Statement
    #####
    
    elif fields[0] ==  CONDENDIF:

        # The end-of-block statement must be on a line by itself
        
        if len(fields) != 1:
            WrnMsg(wBADENDIF % (num, line), fn=file)
            
        # The conditional stack must always have 1 value left in
        # it *after* all conditional processing.  If it does not,
        # it means there are more .endifs than .ifs.

        elif len(ConditionalStack) == 1:
            WrnMsg(wEXTRAENDIF % (num, line), fn=file)

        else:
            ConditionalStack.pop()

    #####
    # Process Include Directive
    #####

    elif fields[0] == DIRECTINC:
        ReadConfFile(cleanline.split(DIRECTINC)[1].strip(), file, num)
        

    ###
    # Variable Definitions And Special Assignments
    ###

    # A valid variable definition can
    # be 1, 2, or 3 fields:
    #
    #  x=y    - 1 field
    #  x= y   - 2 fields
    #  x =y
    #  x = y  - 3 fields
    #
    # But this is illegal
    #
    #  =.......
    #
    # However, the assignment character
    # must always been in the 1st or second
    # field.  If it is a 3rd field, it is not
    # a variable definition, but a command definition.
    #
    # If the LHS is one of the Program Function Names
    # used in key binding, the statement is understood
    # to be a key rebinding, not a user variable definition.
    #
    # If the LHS is one of the Directory Shortcut variables,
    # the RHS is added to the Directory Menu and assigned
    # to the associated Function Key (1-12).
    #
    # Finally, the LHS cannot be one of the program
    # Built-In Variables - it is an error, for example,
    # to have something like:
    #
    #        DIR = string
    #
    # because "DIR" is a Built-In Variable name.
    #

    elif ((dummy[0].count(ASSIGN) + dummy[1].count(ASSIGN)) > 0) and (fields[0][0] != ASSIGN):
        
        assign = cleanline.find(ASSIGN)
        name = cleanline[:assign].strip()
        val=cleanline[assign+1:].strip()

        # Error out on any attempt to "define" a Built-In Variable
        
        if UI.BuiltIns.has_key('[' + name + ']') or UI.BuiltIns.has_key('[' + name):
            WrnMsg(wREDEFVAR % (num, name, line), fn=file)
            return
            
        # Handle Directory Shortcut entries.
        
        if REDIRSC.match(name):

            # Get shortcut number
            sc = int(name.split(DIRSC)[1])

            # Process if in range
            if 0 < sc < NUMFUNCKEY + 1:

                # Associate the directory with the correct shortcut key
                UI.DirSCKeys[sc-1] = val

            # User specified an invalid shortcut number
            else:
                WrnMsg(wBADSCNUM % (num, line), fn=file)
                return

        # Process any wildcard definitions
        
        elif name == WILDFILTER:
            if val and (val not in UI.FilterHist):
                UpdateMenu(UI.FilterBtn, UI.FilterHist, MAXMENU, MAXMENUBUF, KeyFilterWild, newentry=val, fakeevent=True)
                
        elif name == WILDSELECT:
            if val and (val not in UI.SelectHist):
                UpdateMenu(UI.SelectBtn, UI.SelectHist, MAXMENU, MAXMENUBUF, KeySelWild, newentry=val, fakeevent=True)
                
        # Process any option variables - blank RHS is OK and means to leave
        # option set to its default value.

        elif name in UI.OptionsBoolean.keys():
            if val:
                val = val.capitalize()
                if val == 'True' or val == 'False':
                    globals()[name] = eval(val)               # !!! Cheater's way to get to global variables.
                else:
                    WrnMsg(wBADRHS % (num, line), fn=file)
                    return

        elif name in UI.OptionsNumeric.keys():
            if val:
                try:
                    val = StringToNum(val)
                    if val >= 0:
                        globals()[name] = val
                    else:
                        WrnMsg(wBADRHS % (num, line), fn=file)
                        return
                except:
                    WrnMsg(wBADRHS % (num, line), fn=file)
                    return

        elif name in UI.OptionsString.keys():
            if val:
                globals()[name] = val


        # Process other variable types.
        # Distinguish between internal program variables and
        # user-defined variables and act accordingly.  We inhibit
        # the rebinding of certain, special assignments, however.

        elif name in UI.KeyBindings.keys():
            if name in NOREBIND:
                WrnMsg(wNOREBIND % (num, line), fn=file)
                return
            else:
                UI.KeyBindings[name] = val
        else:
            UI.SymTable[name] = val

    ###
    # Command Definitions And Associations
    ###

    elif (len(fields[0]) == 1) or (fields[0] == ASSOCIATE):

        # Handle the case of association statements w/blank RHS

        if (len(fields) == 2) and (fields[0] == ASSOCIATE):
            fields.append(ASSOCBLANK)

        # Must have at least 3 fields for a valid command definition
        if len(fields) < 3:
            WrnMsg(wBADCFGLINE % (num, line), fn=file)
            return
        else:
            cmdkey = fields[0]
            cmdname = fields[1]
            cmd = " ".join(fields[2:])

            # A null return means there was a problem - abort
            if not cmd:
                return

            # Store associations for use at execution time

            if cmdkey == ASSOCIATE:

                # Blank RHS implies user wants association removed

                if cmd == ASSOCBLANK:
                    if cmdname == ASSOCEXCL:               # Null out the exclusion list
                        UI.Associations[cmdname] = []
                    else:
                        if cmdname in UI.Associations:  # Only blank out entries if they actually exist
                            del UI.Associations[cmdname]
                
                # Process association exclusions
                
                elif cmdname == ASSOCEXCL:
                    for exclude in cmd.split():
                        if exclude not in UI.Associations[cmdname]:  # Avoid duplicates
                            UI.Associations[cmdname].append(exclude)

                # Process normal association statements

                else:
                    UI.Associations[cmdname] = cmd
                return


            # Add the command entry to the command table.
            # If the key is a duplicate, the older definition is
            # overwritten.

            UI.CmdTable[cmdkey] = [cmdname, cmd]

            # Keep track of the order in which the commands
            # were defined - we want them to show up that
            # way in the Command Menu so user can put
            # most-used commands near the top.
            # Do this suppressing duplicates.

            if cmdkey in UI.Commands:
                UI.Commands.remove(cmdkey)

            UI.Commands.append(cmdkey)

    else:
        WrnMsg(wBADCFGLINE % (num, line), fn=file)

# End of 'ParseLine()'


#####
# Print Debug Information On stdout
#####

def PrintDebug(title, content):

    print '<%s>\n' % title.upper()
    if content:
        for i in content:
            print i
    else:
        print dNULL
    print

# End of 'PrintDebug()'


#####
# Setup The GUI Visual Parameters, Menus, & Help Information 
#####

def SetupGUI():

    # Start in detailed mode unless details are inhibited
    UI.SetDetailedView(not NODETAILS)

    # Rebind all the handlers
    UI.BindAllHandlers()

    # Any user-set options have now been read, set the GUI

    for i in (UI.CmdBtn, UI.DirBtn, UI.HistBtn, UI.ShortBtn, UI.SortBtn, UI.FilterBtn, UI.SelectBtn, UI.HelpBtn):
        i.config(foreground=MFCOLOR, background=MBCOLOR, font=(MFNAME, MFSZ, MFWT))
        i.menu.config(foreground=MFCOLOR, background=MBCOLOR, font=(MFNAME, MFSZ, MFWT))

    # Set Menu Bar background to match buttons
    UI.mBar.config(background=MBARCOL)

    UI.DirList.config(font=(FNAME, FSZ, FWT),
                      foreground=FCOLOR, background=BCOLOR)


    # Make sure menus conform to max lengths (which may have changed).

    UpdateMenu(UI.DirBtn, UI.AllDirs, MAXMENU, MAXMENUBUF, LoadDirList, sort=True)    
    UpdateMenu(UI.HistBtn, UI.CmdHist, MAXMENU, MAXMENUBUF, KeyRunCommand, fakeevent=True)
    UpdateMenu(UI.FilterBtn, UI.FilterHist, MAXMENU, MAXMENUBUF, KeyFilterWild, fakeevent=True)
    UpdateMenu(UI.SelectBtn, UI.SelectHist, MAXMENU, MAXMENUBUF, KeySelWild, fakeevent=True)

    # Initialize the Sorting Menu

    LoadSortMenu()

    # Initialize the Help Menu
    LoadHelpMenu()

    # Initialize the Shortcut Menu
    LoadShortcutMenu()

    # Size and position the display
    UIroot.geometry("%sx%s+%s+%s" % (WIDTH,  HEIGHT, STARTX, STARTY))

# End of 'SetupGUI()'


#####
# Load The Sorting Menu with the latest information
#####

def LoadSortMenu():

    # Sort Menu content is different if in Drive List View
    # Show options appropriate to the current view

    if UI.CurrentDir == SHOWDRIVES:
        idx = 2
    else:
        idx = 1

    # Clear out any old entries

    UI.SortBtn.config(state=DISABLED)
    UI.SortBtn.menu.delete(0,END)
    
    # Add the menu selections
    
    for entry in [fNONE, fPERMISSIONS, fLINKS, fOWNER, fGROUP, fLENGTH, fDATE, fNAME, fREVERSE, fSEPARATE]:

        t = Name2Key[entry.lower()]
        if t[idx]:
            UI.SortBtn.menu.add_command(label=t[idx], command=lambda parm=t[1] : KeySetSortParm(parm))

    # Store the current directory - used in subsequent calls to this function to
    # determine whether or not we're moving between Normal <--> Drive List Views

    UI.SortBtn.CurrentDir = UI.CurrentDir

    # Enable the menu selections
    
    UI.SortBtn['menu'] = UI.SortBtn.menu
    UI.SortBtn.config(state=NORMAL)

# End of 'LoadSortMenu()'


#####
# Load Help Menu with latest information
#####

def LoadHelpMenu():
    
    # Clear out existing content
    
    UI.HelpBtn.config(state=DISABLED)
    UI.HelpBtn.menu.delete(0,END)


    # Update the cascading submenus
    # We iterate across tuples of (Menu Name, Menu Variable, List Of Items)

    for mname, mvbl, mlist in ((hINTVBLS,  UI.IntVbls,  GetIntVars()),
                               (hOPTVBLS,  UI.OptVbls,  GetOptions()),
                               (hKEYS,     UI.Keys,     FormatMultiColumn(UI.KeyBindings)),
                               (hUSERVBLS, UI.UserVbls, GetUserVbls()),
                               (hCOMMANDS, UI.CmdDefs,  GetCommandTable()),
                               (hASSOC,    UI.Assocs,   GetAssocTable())
                              ):

        mvbl.delete(0,END)                       
        
        # Indicated if there is nothing to display for this class of help
        if not mlist:
            mvbl.add_command(label=hNONE % mname, command=None, foreground=HFCOLOR, background=HBCOLOR,
                             font=(HFNAME, HFSZ, HFWT))

        # Load the help class with relevant information
        else:
            for l in mlist:
                mvbl.add_command(label=l, command=None, foreground=HFCOLOR, background=HBCOLOR, font=(HFNAME, HFSZ, HFWT))

        UI.HelpBtn.menu.add_cascade(label=mname, menu=mvbl)

    # Setup the About item

    UI.HelpBtn.menu.add_command(label=hABOUT, command=lambda title=hABOUT, text=ABOUT : showinfo(title, text))

    # Enable the menu content
    
    UI.HelpBtn['menu'] = UI.HelpBtn.menu
    UI.HelpBtn.config(state=NORMAL)

# End of 'LoadHelpMenu()'



#####
# Load The Shortcut Menu with the latest information
#####

def LoadShortcutMenu():

    UI.ShortBtn.config(state=DISABLED)
    UI.ShortBtn.menu.delete(0,END)
    
    # Add Standard Navigation Shortcuts
    
    UI.ShortBtn.menu.add_command(label="Up", command=lambda: KeyUpDir(None))
    UI.ShortBtn.menu.add_command(label="Back", command=lambda: KeyBackDir(None))
    UI.ShortBtn.menu.add_command(label="Home", command=lambda: KeyHomeDir(None))
    UI.ShortBtn.menu.add_command(label="Startdir", command=lambda: KeyStartDir(None))
    UI.ShortBtn.menu.add_command(label="Root", command=lambda: KeyRootDir(None))

    # If were on Win32 and have the extensions loaded also offer the drive list
    
    if OSPLATFORM == 'win32' and GetWin32Drives():
        UI.ShortBtn.menu.add_command(label="DriveList", command=lambda: KeyDriveList(None))

    # Add Shortcut Key Definitions

    idx=1
    for entry in UI.DirSCKeys:
        if entry:
            pad=" "
            if idx < 10:
                pad += " "
            UI.ShortBtn.menu.add_command(label="SC%s:%s%s" % (idx, pad, entry),  command=lambda parm=idx: DirSCKeyPress(None, parm))
        idx += 1

    # Enable the menu selections
    
    UI.ShortBtn['menu'] = UI.ShortBtn.menu
    UI.ShortBtn.config(state=NORMAL)

# End of 'LoadShortcutMenu()'


#####
# Convert A String In Integer Or Hex Format To An Equivalent Numeric
# We assume that the string is either in correct format or that
# the calling routine will catch any error.
#####

def StringToNum(string):

    if string.lower().startswith('0x'):
        value = int(string, 16)
    else:
        value = int(string, 10)

    return value

# End of 'StringToNum()


#####
# Strip Trailing Path Separator
#####

def StripPSEP(s):

    if s and s[-1] == PSEP:
        return s[:-1]
    else:
        return s

# End of 'StripPSEP()'


#####
# Print Usage Information
#####

def Usage():

    for x in uTable:
        print x

# End of 'Usage()'


#####
# Check Debug Level To See If It Is A Properly Formed Integer Or Hex Value
# If So, Convert To Numeric, If Not, Warn User, And Set To 0
#####

def ValidateDebugLevel():
    global DEBUGLEVEL

    d = DEBUGLEVEL  # Save, in case of error
    try:
        DEBUGLEVEL = StringToNum(DEBUGLEVEL)
    except:
        DEBUGLEVEL = 0
        WrnMsg(wBADDEBUG % d)

# End of 'ValidateDebugLevel()'


#####
# Print A Warning Message
#####

def WrnMsg(wmsg, fn=""):
    if WARN:
        showwarning("%s %s    %s    %s" % (PROGNAME, VERSION, wWARN, fn), wmsg)

# End of 'WrnMsg()'


#----------------------------------------------------------#
#                    GUI Definition                        #
#----------------------------------------------------------#



#####
# Enacapsulate the UI in a class
#####


class twanderUI:

    def __init__(self, root):

        # Setup Menubar frame
        
        self.mBar = Frame(root, relief=RAISED, borderwidth=MENUBORDER)
        self.mBar.pack(fill=X)
        
        # Setup the Command Menu

        self.CmdBtn = Menubutton(self.mBar, text=COMMANDMENU, underline=0, state=DISABLED)
        self.CmdBtn.menu = Menu(self.CmdBtn)
        self.CmdBtn.pack(side=LEFT, padx=MENUPADX)

        # Setup the History Menu

        self.HistBtn = Menubutton(self.mBar, text=HISTMENU, underline=0, state=DISABLED)
        self.HistBtn.menu = Menu(self.HistBtn)
        self.HistBtn.pack(side=LEFT, padx=MENUPADX)

        # Setup the Directory Menu

        self.DirBtn = Menubutton(self.mBar, text=DIRMENU, underline=0, state=DISABLED)
        self.DirBtn.menu = Menu(self.DirBtn)
        self.DirBtn.pack(side=LEFT, padx=MENUPADX)

        # Setup the Shortcut Menu

        self.ShortBtn = Menubutton(self.mBar, text=SCMENU, underline=6, state=DISABLED)
        self.ShortBtn.menu = Menu(self.ShortBtn)
        self.ShortBtn.pack(side=LEFT, padx=MENUPADX)

        # Setup the Filter Wildcard Menu

        self.FilterBtn = Menubutton(self.mBar, text=FILTERMENU, underline=0, state=DISABLED)
        self.FilterBtn.menu = Menu(self.FilterBtn)
        self.FilterBtn.pack(side=LEFT, padx=MENUPADX)

        # Setup the Selection Wildcard Menu

        self.SelectBtn = Menubutton(self.mBar, text=SELECTMENU, underline=5, state=DISABLED)
        self.SelectBtn.menu = Menu(self.SelectBtn)
        self.SelectBtn.pack(side=LEFT, padx=MENUPADX)

        # Setup the Sort Menu

        self.SortBtn = Menubutton(self.mBar, text=SORTMENU, underline=0, state=DISABLED)
        self.SortBtn.menu = Menu(self.SortBtn)
        self.SortBtn.pack(side=LEFT, padx=MENUPADX)

        # Setup the Help Menu

        self.HelpBtn = Menubutton(self.mBar, text=HELPMENU, underline=2, state=DISABLED)
        self.HelpBtn.menu = Menu(self.HelpBtn)
        self.HelpBtn.pack(side=LEFT, padx=MENUPADX)
        
        # Setup the cascading submenus
        
        self.IntVbls  = Menu(self.HelpBtn.menu, foreground=MFCOLOR, background=MBCOLOR, font=(MFNAME, MFSZ, MFWT))
        self.OptVbls  = Menu(self.HelpBtn.menu, foreground=MFCOLOR, background=MBCOLOR, font=(MFNAME, MFSZ, MFWT))
        self.Keys     = Menu(self.HelpBtn.menu, foreground=MFCOLOR, background=MBCOLOR, font=(MFNAME, MFSZ, MFWT))
        self.UserVbls = Menu(self.HelpBtn.menu, foreground=MFCOLOR, background=MBCOLOR, font=(MFNAME, MFSZ, MFWT))
        self.CmdDefs  = Menu(self.HelpBtn.menu, foreground=MFCOLOR, background=MBCOLOR, font=(MFNAME, MFSZ, MFWT))
        self.Assocs   = Menu(self.HelpBtn.menu, foreground=MFCOLOR, background=MBCOLOR, font=(MFNAME, MFSZ, MFWT))

        # Setup the Directory Listing and Scrollbars

        self.hSB = Scrollbar(root, orient=HORIZONTAL)
        self.vSB = Scrollbar(root, orient=VERTICAL)
        self.DirList = Listbox(root, selectmode=EXTENDED, exportselection=0,
                               xscrollcommand=self.hSB.set, yscrollcommand=self.vSB.set)

        # Make them visible by packing
        
        self.hSB.config(command=self.DirList.xview)
        self.hSB.pack(side=BOTTOM, fill=X)
        self.vSB.config(command=self.DirList.yview)
        self.vSB.pack(side=RIGHT, fill=Y)
        self.DirList.pack(side=LEFT, fill=BOTH, expand=1)

        # End of method 'twanderUI.__init__()'


    ###
    # Bind the relevant event handlers
    ###
        
    def BindAllHandlers(self):

        ###
        # General Program Commands
        ###

        # Bind handler to invoke Clear Command History
        self.DirList.bind(self.KeyBindings["CLRHIST"], ClearHistory)

        # Bind handler to invoke Decrement Font Size
        self.DirList.bind(self.KeyBindings["FONTDECR"], FontDecr)

        # Bind handler to invoke Increment Font Size
        self.DirList.bind(self.KeyBindings["FONTINCR"], FontIncr)

        # Bind handler to invoke Command Menu
        self.DirList.bind(self.KeyBindings["MOUSECTX"], MouseClick)

        # Bind handler to invoke Directory Menu
        self.DirList.bind(self.KeyBindings["MOUSEDIR"], MouseClick)

        # Bind handler to invoke Directory Menu
        self.DirList.bind(self.KeyBindings["MOUSEHIST"], MouseClick)

        # Bind handler to invoke Directory Menu
        self.DirList.bind(self.KeyBindings["MOUSESC"], MouseClick)

        # Bind handler to invoke Directory Menu
        self.DirList.bind(self.KeyBindings["MOUSESORT"], MouseClick)

        # Bind handler for individual keystrokes
        self.DirList.bind(self.KeyBindings["KEYPRESS"], KeystrokeHandler)

        # Bind handler for "Quit Program"
        self.DirList.bind(self.KeyBindings["QUITPROG"], KeyQuitProg)

        # Bind handler for "Read Config File"
        self.DirList.bind(self.KeyBindings["READCONF"], ProcessConfiguration)

        # Bind handler for "Refresh Screen" 
        self.DirList.bind(self.KeyBindings["REFRESH"], lambda event : RefreshDirList(event, ClearFilterWildcard=True))

        # Bind handler for "Toggle Autorefresh" 
        self.DirList.bind(self.KeyBindings["TOGAUTO"], KeyToggleAuto)

        # Bind handler for "Toggle Detail" 
        self.DirList.bind(self.KeyBindings["TOGDETAIL"], KeyToggleDetail)

        # Bind handler for "Toggle Length Display" 
        self.DirList.bind(self.KeyBindings["TOGLENGTH"],lambda event :  KeyToggle(event, "ACTUALLENGTH"))

        # Bind handler for "Toggle Sorting Of Symlinks Pointing To Directories"
        self.DirList.bind(self.KeyBindings["TOGSYMDIR"],lambda event :  KeyToggle(event, "SYMDIR"))
        
        # Bind handler for "Toggle Expand Symlinks"
        self.DirList.bind(self.KeyBindings["TOGSYMEXPAND"],lambda event :  KeyToggle(event, "SYMEXPAND"))
        
        # Bind handler for "Toggle Resolve Symlinks"
        self.DirList.bind(self.KeyBindings["TOGSYMRESOLV"],lambda event :  KeyToggle(event, "SYMRESOLV"))
        

        # Bind handler for "Toggle win32all Features" 
        self.DirList.bind(self.KeyBindings["TOGWIN32ALL"], KeyToggleWin32All)

        ###
        # Directory Navigation
        ###

        # Bind handler for "Change Directory"
        self.DirList.bind(self.KeyBindings["CHANGEDIR"], KeyChangeDir)

        # Bind handler for "Home Dir"
        self.DirList.bind(self.KeyBindings["DIRHOME"], KeyHomeDir)

        # Bind handler for "Previous Dir"
        self.DirList.bind(self.KeyBindings["DIRBACK"], KeyBackDir)

        # Bind handler for "Root Dir"
        self.DirList.bind(self.KeyBindings["DIRROOT"], KeyRootDir)

        # Bind handler for "Starting Dir"
        self.DirList.bind(self.KeyBindings["DIRSTART"], KeyStartDir)

        # Bind handler for "Up Dir"
        self.DirList.bind(self.KeyBindings["DIRUP"], KeyUpDir)

        # Bind handler for "Display Drive View"
        self.DirList.bind(self.KeyBindings["DRIVELIST"], KeyDriveList)

        # Bind handler for "Mouse Back Dir"
        self.DirList.bind(self.KeyBindings["MOUSEBACK"], MouseDblClick)

        # Bind handler for "Mouse Up Dir"
        self.DirList.bind(self.KeyBindings["MOUSEUP"], MouseDblClick)

        ###
        # Selection Keys
        ###

        # Bind handler for "Select All"
        self.DirList.bind(self.KeyBindings["SELALL"], KeySelAll)

        # Bind handler for "Invert Current Selection"
        self.DirList.bind(self.KeyBindings["SELINV"], KeySelInv)

        # Bind handler for "Select No Items"
        self.DirList.bind(self.KeyBindings["SELNONE"], KeySelNone)

        # Bind handler for "Next Item"
        self.DirList.bind(self.KeyBindings["SELNEXT"], KeySelNext)

        # Bind handler for "Previous Item"
        self.DirList.bind(self.KeyBindings["SELPREV"], KeySelPrev)

        # Bind handler for "Last Item"
        self.DirList.bind(self.KeyBindings["SELEND"], KeySelEnd)

        # Bind handler for "First Item"
        self.DirList.bind(self.KeyBindings["SELTOP"], KeySelTop)


        ###
        # Scrolling Keys
        ###

        # Bind Handler for "Move Page Down
        self.DirList.bind(self.KeyBindings["PGDN"], KeyPageDown)

        # Bind Handler for "Move Page Up"
        self.DirList.bind(self.KeyBindings["PGUP"], KeyPageUp)

        # Bind Handler for "Move Page Right"
        self.DirList.bind(self.KeyBindings["PGRT"], KeyPageRight)

        # Bind Handler for "Move Page Up"
        self.DirList.bind(self.KeyBindings["PGLFT"], KeyPageLeft)

        ###
        # Execute Commands
        ###

        # Bind handler for "Run Command"
        self.DirList.bind(self.KeyBindings["RUNCMD"], lambda event : KeyRunCommand(event, DoCmdShell=True))

        # Bind handler for "Item Select"
        self.DirList.bind(self.KeyBindings["SELKEY"], DirListHandler)

        # Bind handler for "Mouse Select"
        self.DirList.bind(self.KeyBindings["MOUSESEL"], MouseDblClick)


        ###
        # Directory Shortcut Keys - All Bound To A Common Handler
        ###

        self.DirList.bind(self.KeyBindings["KDIRSC1"],  lambda event :DirSCKeyPress(event, 1))
        self.DirList.bind(self.KeyBindings["KDIRSC2"],  lambda event :DirSCKeyPress(event, 2))
        self.DirList.bind(self.KeyBindings["KDIRSC3"],  lambda event :DirSCKeyPress(event, 3))
        self.DirList.bind(self.KeyBindings["KDIRSC4"],  lambda event :DirSCKeyPress(event, 4))
        self.DirList.bind(self.KeyBindings["KDIRSC5"],  lambda event :DirSCKeyPress(event, 5))
        self.DirList.bind(self.KeyBindings["KDIRSC6"],  lambda event :DirSCKeyPress(event, 6))
        self.DirList.bind(self.KeyBindings["KDIRSC7"],  lambda event :DirSCKeyPress(event, 7))
        self.DirList.bind(self.KeyBindings["KDIRSC8"],  lambda event :DirSCKeyPress(event, 8))
        self.DirList.bind(self.KeyBindings["KDIRSC9"],  lambda event :DirSCKeyPress(event, 9))
        self.DirList.bind(self.KeyBindings["KDIRSC10"], lambda event :DirSCKeyPress(event, 10))
        self.DirList.bind(self.KeyBindings["KDIRSC11"], lambda event :DirSCKeyPress(event, 11))
        self.DirList.bind(self.KeyBindings["KDIRSC12"], lambda event :DirSCKeyPress(event, 12))

        # Open Dialog To Load Current Directory Into User-Selected Shortcut

        self.DirList.bind(self.KeyBindings["KDIRSCSET"], lambda event :DirSCSet(event))

        
        ###
        # Memory Keys - All Features Bound To A Common Handler
        ###

        self.DirList.bind(self.KeyBindings["MEMCLR1"],   lambda event : KeyMemHandler(mem=1,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR2"],   lambda event : KeyMemHandler(mem=2,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR3"],   lambda event : KeyMemHandler(mem=3,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR4"],   lambda event : KeyMemHandler(mem=4,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR5"],   lambda event : KeyMemHandler(mem=5,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR6"],   lambda event : KeyMemHandler(mem=6,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR7"],   lambda event : KeyMemHandler(mem=7,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR8"],   lambda event : KeyMemHandler(mem=8,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR9"],   lambda event : KeyMemHandler(mem=9,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR10"],  lambda event : KeyMemHandler(mem=10,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR11"],  lambda event : KeyMemHandler(mem=11,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLR12"],  lambda event : KeyMemHandler(mem=12,  clear=True))
        self.DirList.bind(self.KeyBindings["MEMCLRALL"], lambda event : KeyMemHandler(mem=13, clear=True))
        self.DirList.bind(self.KeyBindings["MEMSET1"],   lambda event : KeyMemHandler(mem=1))
        self.DirList.bind(self.KeyBindings["MEMSET2"],   lambda event : KeyMemHandler(mem=2))
        self.DirList.bind(self.KeyBindings["MEMSET3"],   lambda event : KeyMemHandler(mem=3))
        self.DirList.bind(self.KeyBindings["MEMSET4"],   lambda event : KeyMemHandler(mem=4))
        self.DirList.bind(self.KeyBindings["MEMSET5"],   lambda event : KeyMemHandler(mem=5))
        self.DirList.bind(self.KeyBindings["MEMSET6"],   lambda event : KeyMemHandler(mem=6))
        self.DirList.bind(self.KeyBindings["MEMSET7"],   lambda event : KeyMemHandler(mem=7))
        self.DirList.bind(self.KeyBindings["MEMSET8"],   lambda event : KeyMemHandler(mem=8))
        self.DirList.bind(self.KeyBindings["MEMSET9"],   lambda event : KeyMemHandler(mem=9))
        self.DirList.bind(self.KeyBindings["MEMSET10"],  lambda event : KeyMemHandler(mem=10))
        self.DirList.bind(self.KeyBindings["MEMSET11"],  lambda event : KeyMemHandler(mem=11))
        self.DirList.bind(self.KeyBindings["MEMSET12"],  lambda event : KeyMemHandler(mem=12))


        ###
        # Sort Selection Keys - All Bound To A Common Handler
        ###

        self.DirList.bind(self.KeyBindings["SORTBYNONE"], lambda event : KeySetSortParm(parm=fNONE))
        self.DirList.bind(self.KeyBindings["SORTBYPERMS"], lambda event : KeySetSortParm(parm=fPERMISSIONS))
        self.DirList.bind(self.KeyBindings["SORTBYLINKS"], lambda event : KeySetSortParm(parm=fLINKS))
        self.DirList.bind(self.KeyBindings["SORTBYOWNER"], lambda event : KeySetSortParm(parm=fOWNER))
        self.DirList.bind(self.KeyBindings["SORTBYGROUP"], lambda event : KeySetSortParm(parm=fGROUP))
        self.DirList.bind(self.KeyBindings["SORTBYLENGTH"], lambda event : KeySetSortParm(parm=fLENGTH))
        self.DirList.bind(self.KeyBindings["SORTBYTIME"], lambda event : KeySetSortParm(parm=fDATE))
        self.DirList.bind(self.KeyBindings["SORTBYNAME"], lambda event : KeySetSortParm(parm=fNAME))
        self.DirList.bind(self.KeyBindings["SORTREV"], lambda event : KeySetSortParm(parm=fREVERSE))
        self.DirList.bind(self.KeyBindings["SORTSEP"], lambda event : KeySetSortParm(parm=fSEPARATE))
        

        #####
        # Wildcard Related Keys
        #####

        # Bind handler to invoke Filter Wildcard Menu
        self.DirList.bind(self.KeyBindings["MOUSEWILDFILTER"], MouseClick)

        # Bind handler to invoke Selection Wildcard Menu
        self.DirList.bind(self.KeyBindings["MOUSEWILDSEL"], MouseClick)

        # Bind handler for "Filter With Wildcard"
        self.DirList.bind(self.KeyBindings["FILTERWILD"], KeyFilterWild)

        # Bind handler for "Select With Wildcard"
        self.DirList.bind(self.KeyBindings["SELWILD"], KeySelWild)

        # Bind handler for "Toggle Filter By Wildcard"
        self.DirList.bind(self.KeyBindings["TOGFILT"], KeyToggleFilter)

        # Bind handler for "Toggle Dotfile Hiding"
        self.DirList.bind(self.KeyBindings["TOGHIDEDOT"],lambda event :  KeyToggle(event, "HIDEDOTFILES"))


        # Give the listbox focus so it gets keystrokes
        self.DirList.focus()

    # End Of method 'twanderUI.BindAllHandlers()


    #####
    # Return tuple of all selected items
    #####

    def AllSelection(self):

        sellist = []
        nameindex = self.NameFirst

        for entry in self.DirList.curselection():
            sellist.append(self.DirList.get(entry)[nameindex:].split(SYMPTR)[0])

        return sellist

    # End of method 'twanderUI.AllSelection()'
        

    #####
    # Return name of currently selected item
    #####

    def LastInSelection(self):

        nameindex = self.NameFirst
        index = self.DirList.curselection()

        if index:
            return self.DirList.get(index[-1])[nameindex:].split(SYMPTR)[0]
        else:
            return ""

    # End of method 'twanderUI.LastInSelection()'


    #####
    # Support periodic polling to make sure widget stays
    # in sync with reality of current directory.
    #####

    def poll(self):

        # If new dir entered via mouse, force correct activation
        if self.MouseNewDir:
            self.DirList.activate(0)
            self.MouseNewDir = False

        # Do autorefreshing as required

        if AUTOREFRESH:

            # Is it time for a refresh?

            elapsed = int((time.time() - self.LastRefresh) * 1000)
            if elapsed >= REFRESHINT:

                # Don't autorefresh on drive list views
                if UI.CurrentDir != SHOWDRIVES:

                    # Don't autorefresh if there is a lock outstanding

                    if not UI.DirListMutex.test():
                        RefreshDirList(None)

        # Setup next polling event
        self.DirList.after(POLLINT, self.poll)

    # End of method 'twanderUI.poll()'


    #####
    # Set Detailed View -> False == No Details, True == Details
    #####

    def SetDetailedView(self, details):

        # See if we're forcing details to always be off
        if NODETAILS:
            self.DetailsOn = False
        else:
            self.DetailsOn = details
        
    # End of method 'twanderUI.SetDetailedView()'


    #####
    # Set a particular selection, w/bounds checking
    # Note that 'selection' is passed as a string
    # but 'active' is passed as a number.
    #####

    def SetSelection(self, selection, active):

        # Clear all current selection(s)
        self.DirList.selection_clear(0, END)

        # Get current maximum index
        maxindex =  self.DirList.size() - 1

        # And bounds check/adjust

        if active > maxindex:
            active = maxindex

        # Set desired selected items, if any

        if selection:
            for entry in selection:
                self.DirList.select_set(entry)
            self.DirList.see(selection[-1])

        # Now set the active entry
        self.DirList.activate(active)

    # End of method 'twanderUI.SetSelection()'


    #####
    # Update titlebar with most current information
    #####

    def UpdateTitle(self, mainwin, refreshing=""):

        if UI.CurrentDir == SHOWDRIVES:

            # SORTBYFIELD can have values not meaningful
            # in Drive List View - these are always mapped to fNAME
            
            if Name2Key[SORTBYFIELD.lower()][0] > MAXDLVKEY:
                srtfld = dlvLETTER.upper()
            else:
                srtfld = Name2Key[SORTBYFIELD.lower()][2].upper()

            sepsort = ""
            ttlfiles = str(self.DirList.size())
            
        else:
            srtfld = SORTBYFIELD.upper()
            srtsep = YesOrNo[SORTSEPARATE]
            sepsort = "%s %s" % (TTLSORTSEP, srtsep)
            ttlfiles = str(self.DirList.size()-1)     # We never count the ".." entry


        # Limit width of current directory name display in case
        # user get's *really* deeply nested in a file system.
        # This keeps the other stuff of interest visible on the titlebar

        # First, find out if current directory is descendant of this
        # user's home directory.  If so, substitute a shortcut to
        # save titlebar space.
        

        CurrentDir = UI.CurrentDir
        if ENVHOME:
            CurrentDir = os.path.realpath(UI.CurrentDir)
            envhome = os.path.realpath(ENVHOME)
            if CurrentDir.startswith(envhome):
                CurrentDir = CurrentDir.replace(envhome, HOMEDIRMARKER)
        
        # And make sure whatever we ended up with has an ending
        # separator character.

        if CurrentDir[-1] != PSEP:
            CurrentDir += PSEP
        
        pathlen = len(CurrentDir)
        if pathlen > TTLMAXDIR:
            CurrentDir = TTLDIR2LONG + CurrentDir[pathlen-TTLMAXDIR:]

        # Indicate Reverse sort by appending a '-' to the sort field name
        
        if SORTREVERSE:
            srtfld += "-"
            
        sortedby  = "%s %s    " % (TTLSORTFLD, srtfld)
        autostate = YesOrNo[AUTOREFRESH] + refreshing

        filterwc = UI.FilterWildcard[0]
        if WILDNOCASE and not UI.FilterWildcard[3]:
            filterwc = filterwc.lower()
        if INVERTFILTER:
            filterwc = "NOT " + filterwc
        filter    = "%s %s" % (TTLFILTER, filterwc)

        hidedotfile = "%s %s" % (TTLHIDEDOT, YesOrNo[HIDEDOTFILES])

        # Show state of symlink handling

        symlinks = "F"
        if SYMDIR:
            symlinks = "D"
        if SYMEXPAND:
            symlinks += "E"
            if SYMRESOLV:
                symlinks += "R"

        symlinks = "%s %s" % (TTLSYMLINKS, symlinks)
            
        mainwin.title("%s %s        %s:        %s        %s   %s     %s     %s  %s      %s  %s      %s%s  %s %s" % 
                      (PROGNAME, VERSION, FULLNAME, CurrentDir, symlinks, filter, hidedotfile,  TTLFILES, 
                       ttlfiles, TTLSIZE, FileLength(self.TotalSize), sortedby, sepsort, TTLAUTO, autostate))

        # Make sure the titlebar gets updated
        mainwin.update_idletasks()

    # End of method 'twanderUI.UpdateTitle()'

# End of class definition, 'twanderUI'


#----------------------------------------------------------#
#                   Handler Functions                      #
#----------------------------------------------------------#

#---------------- Mouse Click Dispatchers -----------------#

# We intercept all mouse clicks (of interest) here so it
# is easy to uniquely handle the Control, Shift, Alt,
# variations of button presses.  We use Tkinter itself
# keep track of single- vs. double-clicks and hand-off
# the event to the corresponding Mouse Click Dispatcher.

#####
# Event Handler: Single Mouse Clicks
#####

def MouseClick(event):

    event.state &= ~DontCareMask                     # Kill the bits we don't care about
    
    if event.state == Button3Mask:                   # Button-3 / No Modifier
        x, y = UI.DirList.winfo_pointerxy()          # Position near mouse
        PopupMenu(UI.CmdBtn.menu, x, y)              # Display Command Menu

    elif event.state == (Button3Mask | ShiftMask | ControlMask):     # Shift-Control-Button-3
        x, y = UI.DirList.winfo_pointerxy()          # Position near mouse
        PopupMenu(UI.HistBtn.menu, x, y)             # Display History Menu

    elif event.state == (Button3Mask | ShiftMask):   # Shift-Button-3
        x, y = UI.DirList.winfo_pointerxy()          # Position near mouse
        PopupMenu(UI.DirBtn.menu, x, y)              # Display Directory Menu

    elif event.state == (Button1Mask | AltMask | ControlMask):     # Control-Button-1
        x, y = UI.DirList.winfo_pointerxy()          # Position near mouse
        PopupMenu(UI.ShortBtn.menu, x, y)            # Display Shortcut Menu

    elif event.state == (Button3Mask | AltMask | ShiftMask):     # Alt-Shift-Button-3
        x, y = UI.DirList.winfo_pointerxy()          # Position near mouse
        PopupMenu(UI.SortBtn.menu, x, y)             # Display Sort Menu

    elif event.state == (Button2Mask | AltMask | ControlMask):     # Alt-Control-Button-2
        x, y = UI.DirList.winfo_pointerxy()          # Position near mouse
        PopupMenu(UI.FilterBtn.menu, x, y)           # Display Filter Wildcard Menu

    elif event.state == (Button3Mask | AltMask | ControlMask):     # Alt-Control-Button-3
        x, y = UI.DirList.winfo_pointerxy()          # Position near mouse
        PopupMenu(UI.SelectBtn.menu, x, y)           # Display Selection Wildcard Menu

# End Of 'MouseClick()'


#####
# Event Handler: Mouse Double-Clicks
#####

def MouseDblClick(event):

    event.state &= ~DontCareMask                      # Kill the bits we don't care about
    
    if event.state == Button1Mask:                    # Double-Button-1 / No Modifier
        DirListHandler(event)                         # Execute selected item

    elif event.state == (Button1Mask | ControlMask):  # Control-DblButton-1
        KeyBackDir(event)                             # Move back one directory

    elif event.state == (Button3Mask | ControlMask):  # Control-DblButton-3
        KeyUpDir(event)                               # Move up one directory

    return "break"

# End Of 'MouseDblClick()


#--------------- General Program Commands -----------------#

#####
# Event Handler: Clear Various Program Histories
#####

def ClearHistory(event):
    global UI
    
    UI.AllDirs          = []
    UI.CmdHist          = []
    UI.FilterHist       = []
    UI.SelectHist       = []
    UI.LastCmd          = ""
    UI.LastDir          = []
    UI.LastPathEntered  = ""
    UI.LastFiltWildcard = ""
    UI.LastSelWildcard  = ""

    for x in [UI.DirBtn, UI.HistBtn, UI.FilterBtn, UI.SelectBtn]:
        x.menu.delete(0,END)
        x['menu'] = x.menu
        x.config(state=DISABLED)

    return 'break'
    
# End of 'ClearHistory()'


#####
# Decrement Font Size
#####

def FontDecr(event):
    global FSZ, MFSZ, HFSZ
    
    if FSZ > 1:
        FSZ  -= 1
    if MFSZ > 1:
        MFSZ -= 1
    if HFSZ > 1:
        HFSZ -= 1

    SetupGUI()
    return 'break'

# End of 'FontDecr()'


#####
# Increment Font Size
#####

def FontIncr(event):
    global FSZ, MFSZ, HFSZ

    FSZ  += 1
    MFSZ += 1
    HFSZ += 1

    SetupGUI()
    return 'break'

# End of 'FontIncr()'


#####
# Event Handler: Individual Keystrokes
#####

def KeystrokeHandler(event):

    event.state &= ~DontCareMask                      # Kill the bits we don't care about

    # Check for, and handle accelerator keys

    if event.state == AltMask:
        
        # Set menu button associated with accelerator

        # Command Menu
        if event.char == 'c':
            button = UI.CmdBtn

        # Directory Menu
        elif event.char == 'd':
            button = UI.DirBtn

        # History Menu
        elif event.char == 'h':
            button = UI.HistBtn

        # Shortcut Menu
        elif event.char == 'u':
            button = UI.ShortBtn

        # Sort Menu
        elif event.char == 's':
            button = UI.SortBtn

        # Filter Menu
        elif event.char == 'f':
            button = UI.FilterBtn

        # Select Menu
        elif event.char == 't':
            button = UI.SelectBtn

        # Help Menu
        elif event.char == 'l':
            button = UI.HelpBtn

        # Unrecognized - Ignore
        else:
            return

        parts = button.winfo_geometry().split('+')     # Geometry returned as "WidthxHeight+X+Y"
        dims  = parts[0].split('x')

        x, y = int(parts[1]), int(parts[2])
        w, h = int(dims[0]), int(dims[1])

        x += UIroot.winfo_rootx()                      # This is relative to root window position
        y += UIroot.winfo_rooty()                      # So adjust accordingly

        # Display the requested menu
        PopupMenu(button.menu, x+MENUOFFSET, y+h)

        # Inhibit event from getting picked up by local accelerator key handlers
        return "break"

    #####
    # Otherwise, process single character command invocations.
    #####

    # We *only* want to handle simple single-character
    # keystrokes.  This means that there must be a character
    # present and that the only state modifier permitted
    # is the Shift key
    
    if not event.char or (event.state and event.state != 1):
        return 

    # If the key pressed is a command key (i.e., it is in the table of
    # defined commands), get its associated string and execute the command.

    cmd  = UI.CmdTable.get(event.char, ["", "", ""])[1]
    name = UI.CmdTable.get(event.char, ["", "", ""])[0]


    # cmd == null means no matching command key -  do nothing
    # Otherwise, replace config tokens with actual file/dir names

    if cmd:
        ExecuteCommand(cmd, name, ResolveVars=True)

   
# end of 'KeystrokeHandler()'
    

#####
# Event Handler: Program Quit
#####

def KeyQuitProg(event):
    sys.exit()

# End of 'KeyQuitProg()'


#####
# Event Handler: Generic Option Toggle
#####

def KeyToggle(event, option):
    global SYMEXPAND, SYMRESOLV
    
    exec("global %s; %s = not %s" % (option, option, option))

    # We may have just updated SYMRESOLV.  Changing its state implies
    # we want to see the link target (either expanded or resolved) so
    # force symlink targets to be displayed one way or the other.

    if option=="SYMRESOLV":
        SYMEXPAND = True
        
    RefreshDirList(event)

    # Update the help menu to reflect change
    LoadHelpMenu()
    
    return 'break'

# End of 'KeyToggle()'


#####
# Event Handler: Toggle Autorefresh
#####

def KeyToggleAuto(event):

    global AUTOREFRESH
    
    # Toggle the state
    AUTOREFRESH = not AUTOREFRESH

    # Update the titlebar to reflect this
    UI.UpdateTitle(UIroot)

    # Update the help menu to reflect change
    LoadHelpMenu()
    
    return 'break'

# End of 'KeyToggleAuto()'


#####
# Event Handler: Toggle Detail View
#####

def KeyToggleDetail(event):

    UI.SetDetailedView(not UI.DetailsOn)
    RefreshDirList(event)

    return 'break'

# End of 'KeyToggleDetail()'


#####
# Event Handler: Toggle Wildcard Filter Logic
#####

def KeyToggleFilter(event):
    global INVERTFILTER
    
    # Only toggle state if there is an active filtering wildcard
    # If we do, reset the cursor to the top, but select nothing
    
    if UI.FilterWildcard[1]:
        INVERTFILTER = not INVERTFILTER
        RefreshDirList(event)
        KeySelTop(event, clearsel=True)

    return 'break'

# End of 'KeyToggleFilter()'


#####
# Event Handler: Toggle win32all Features, If Available
#####

def KeyToggleWin32All(event):
    global WIN32ALLON
    
    if USEWIN32ALL and (UI.CurrentDir != SHOWDRIVES):
        WIN32ALLON = not WIN32ALLON
        RefreshDirList(event)
        LoadShortcutMenu()    # Decides whether or not to show drive list

    return 'break'
    
# End of 'KeyToggleWin32All()'


#------------------- Directory Navigation -----------------#


#####
# Event Handler: Change Directory/Path
####

def KeyChangeDir(event):

    newpath = askstring(pCHPATH, pENPATH, initialvalue=UI.LastPathEntered)

    if newpath:
        if MAXMENU > 0:
            UI.LastPathEntered = newpath
        LoadDirList(newpath)
        KeySelTop(event)
    UI.DirList.focus()

    return 'break'

# End of 'KeyChangeDir()'


#####
# Event Handler: Goto $HOME
#####

def KeyHomeDir(event):

    if HOME:
        LoadDirList(HOME)

    return 'break'

# End of 'KeyHomeDir()'


#####
# Event Handler: Move To Previous Directory
#####

def KeyBackDir(event):

    # Move to last directory visited, if any - inhibit this from
    # being placed on the directory traversal stack
    if UI.LastDir:
        LoadDirList(UI.LastDir.pop(), save=False)

    # No previous directory
    else:
        pass

    return 'break'

# End of 'KeyBackDir()'


#####
# Event Handler: Go To Root Directory
#####

def KeyRootDir(event):
    LoadDirList(PSEP)

    return 'break'

# End of 'KeyRootDir()'


#####
# Event Handler: Go Back To Initial Directory
#####

def KeyStartDir(event):
    LoadDirList(STARTDIR)

    return 'break'

# End of 'KeyStartDir()'


#####
# Event Handler: Move Up One Directory
#####

def KeyUpDir(event):

    # Move up one directory level unless we're already at the root
    if UI.CurrentDir != os.path.abspath(PSEP):
        LoadDirList(UI.CurrentDir + "..")

    # Unless we're running on Win32 and we are able to do
    # a Drive List View

    elif OSPLATFORM == 'win32' and GetWin32Drives():
        LoadDirList(SHOWDRIVES)

    return 'break'
    
# End of 'KeyUpDir()'

#####
# Event Handler: Display Drive List View On Win32, If Possible
#####

def KeyDriveList(event):

    # This is only possible on Win32 and if there is a list of
    # drives available - i.e, If Win32All is installed

    if OSPLATFORM == 'win32' and GetWin32Drives():
        LoadDirList(SHOWDRIVES)

    return 'break'

# End of 'KeyDriveList()


#---------------------- Selection Keys ---------------------#


#####
# Event Handler: Select All Items
#####

def KeySelAll(event):

    # In the case of a Drive List View, we want to literally
    # select everything.  In all other cases, we do not
    # want this feature to select the first item which is ".."

    if UI.CurrentDir == SHOWDRIVES:
        UI.DirList.selection_set(0, END)

    else:
        # Unselect first item in case it was
        UI.DirList.selection_clear(0)
    
        # We never want to select the first item which is ".."
        UI.DirList.selection_set(1, END)

    return 'break'

# End of 'KeySelAll()'


#####
# Event Handler: Invert Current Selection
#####

def KeySelInv(event):

    # List of current selections
    cs= UI.DirList.curselection()

    # Select everything
    UI.DirList.selection_set(0, END)

    # And unselect what was selected
    for v in cs:
        UI.DirList.selection_clear(v)

    # If we're not in a Drive List View, we never
    # select the first entry (".." this way)

    if UI.CurrentDir != SHOWDRIVES:
        UI.DirList.selection_clear(0)

    return 'break'

# End of 'KeySelInv()'


#####
# Event Handler: Select Next Item
#####

def KeySelNext(event):

    next = UI.DirList.index(ACTIVE)

    # Don't increment if at end of list
    if (next < UI.DirList.size() - 1):
        next += 1

    UI.SetSelection((str(next),), next)

    return 'break'

# End of 'KeySelNext()'


#####
# Event Handler: Select No Items
#####

def KeySelNone(event):
    UI.DirList.selection_clear(0, END)

    return 'break'

# End of 'KeySelNone()'


#####
# Event Handler: Select Previous Item
#####

def KeySelPrev(event):
    prev = UI.DirList.index(ACTIVE)

    # Only decrement if > 0
    if prev:
        prev -= 1

    UI.SetSelection((str(prev),), prev)

    return 'break'

# End of 'KeySelPrev()'


#####
# Event Handler: Select Last Item
#####

def KeySelEnd(event):

    # Get index of last item in listbox
    sz = UI.DirList.size() - 1

    # And setup to last item accordingly
    UI.SetSelection((str(sz),), sz)

    return 'break'

# End of 'KeySelEnd()'


#####
# Event Handler: Select First Item
#####

def KeySelTop(event, clearsel=False):

    UI.SetSelection(('0',),0)

    # In some cases, we call this routine just to position the cursor
    # at the top of the file list but we don't actually want anything
    # selected

    if clearsel:
        KeySelNone(event)

    return 'break'

# End of 'KeySelTop()'


#####
# Event Handler: Filter Using Wildcard
#####

def KeyFilterWild(event, initial=""):
    global UI

    prompt = pWILDFILT

    # Ask the user for the wildcard pattern, using initial string, if any
    if initial:
        uwc = askstring(prompt, pENWILD, initialvalue=initial)
    else:
        uwc = askstring(prompt, pENWILD, initialvalue=UI.LastFiltWildcard)        
    
    # Return focus to the main interface
    UI.DirList.focus()
    
    # Blank value means to abort
    if not uwc:
        return 'break'

    # Reposition cursor to top of display and deselect everything
    KeySelTop(event, clearsel=True)
    
    # Unless the user indicates otherwise, cook the regex so
    # a match can occur anywhere on the line.  If the user wants
    # strict matching, save this fact so it can escape WILDNOCASE.

    strict = False
    if uwc[0] == STRICTMATCH:
        wc = uwc[1:]
        strict = True
    else:
        wc = r".*" + uwc

    # Compile it - abort if compilation fails
    # Build both a normal and lower-case version
    # of the search engine so we can support case-insensitive
    # matching elswehere.
    
    try:
        wild = re.compile(wc)
        wildl = re.compile(wc.lower())
        
    except:
        WrnMsg(wWILDCOMP % wc)
        return 'break'

    # Refresh the display only showing entries that match
    
    UI.FilterWildcard = (wc, wild, wildl, strict)
    RefreshDirList(None)

    # Save the wildcard only if dynamic menus are enabled (MAXMENU > 0)
    # AND one of two conditions exist:
    #
    #    1) No initial string was provided (The user entered a command manually).
    #    2) An initial string was provided, but the user edited it.

    if (MAXMENU > 0) and ((not initial) or (uwc != initial)):
            UI.LastFiltWildcard = uwc

    # Add this wildcard to the menu if its not there already
    if uwc not in UI.FilterHist:
        UpdateMenu(UI.FilterBtn, UI.FilterHist, MAXMENU, MAXMENUBUF, KeyFilterWild, newentry=uwc, fakeevent=True)

    # Dump wildcard stack if debug requested it
    if DEBUGLEVEL & DEBUGWILD:
        PrintDebug(dWILDLST % dFILTER, UI.FilterHist)

    return 'break'

# End of 'KeyFilterWild()'


#####
# Event Handler: Filter Or Select Using Wildcard
#####

def KeySelWild(event, initial=""):
    global UI
    
    prompt = pWILDSEL

    # Ask the user for the wildcard pattern, using initial string, if any
    if initial:
        uwc = askstring(prompt, pENWILD, initialvalue=initial)
    else:
        uwc = askstring(prompt, pENWILD, initialvalue=UI.LastSelWildcard)        
    
    # Return focus to the main interface
    UI.DirList.focus()
    
    # Blank value means to abort
    if not uwc:
        return 'break'

    # Clear current selections
    KeySelNone(event)

    # Unless the user indicates otherwise, cook the regex so
    # a match can occur anywhere on the line.  If the user wants
    # strict matching, save this fact so it can escape WILDNOCASE.

    strict = False
    if uwc[0] == STRICTMATCH:
        wc = uwc[1:]
        strict = True
    else:
        wc = r".*" + uwc

    # Compile it - abort if compilation fails
    # Build both a normal and lower-case version
    # of the search engine so we can support case-insensitive
    # matching elswehere.
    
    try:
        wild = re.compile(wc)
        wildl = re.compile(wc.lower())
        
    except:
        WrnMsg(wWILDCOMP % wc)
        return 'break'

    # Iterate over the current directory listing saving the
    # indexes of items which match.  We start at 1 not 0 because
    # the first entry ("..") is never considered when doing
    # wildcard matching.  This routine also observes the
    # WILDNOCASE option - if set to True, case is collpased for
    # matching purposes.

    matches = []
    wc = wild
    if WILDNOCASE and not strict:
        wc = wildl

    for x in range(1,UI.DirList.size()):

        matchthis = UI.DirList.get(x)
        if WILDNOCASE and not strict:
            matchthis = matchthis.lower()

        if wc.match(matchthis):
            matches.append(x)

    # If anything matched, select it
    if matches:
        UI.SetSelection(matches, matches[0])

    # Save the wildcard only if dynamic menus are enabled (MAXMENU > 0)
    # AND one of two conditions exist:
    #
    #    1) No initial string was provided (The user entered a command manually).
    #    2) An initial string was provided, but the user edited it.

    if (MAXMENU > 0) and ((not initial) or (uwc != initial)):
            UI.LastSelWildcard = uwc

    # Add this wildcard to the menu if its not there already
    if uwc not in UI.SelectHist:
        UpdateMenu(UI.SelectBtn, UI.SelectHist, MAXMENU, MAXMENUBUF, KeySelWild, newentry=uwc, fakeevent=True)

    # Dump wildcard stack if debug requested it
    if DEBUGLEVEL & DEBUGWILD:
        PrintDebug(dWILDLST %dSELECT, UI.SelectHist)

    return 'break'

# End of 'KeySelWild()'


#---------------------- Scrolling Keys ---------------------#


#####
# Event Handler: Move Down A Page
#####

def KeyPageDown(event):
    UI.DirList.yview_scroll(1, "pages")
    UI.DirList.activate("@0,0")

    return 'break'

# End of 'KeyPageDown()'


#####
# Event Handler: Move Up A Page
#####

def KeyPageUp(event):
    UI.DirList.yview_scroll(-1, "pages")
    UI.DirList.activate("@0,0")

    return 'break'

# End of 'KeyPageUp()'


#####
# Event Handler: Move Page Right
#####

def KeyPageRight(event):
    UI.DirList.xview_scroll(1, "pages")

    return 'break'

# End of 'KeyPageRight()'


#####
# Event Handler: Move Page Left
#####

def KeyPageLeft(event):
    UI.DirList.xview_scroll(-1, "pages")

    return 'break'

# End of 'KeyPageLeft()'


#---------------------- Execute Commands -------------------#


#####
# Event Handler: Run Manually Entered Command
####

def KeyRunCommand(event, initial="", DoCmdShell=False):
    global UI

    # NOTE: DoCmdShell determines whether or not we do CMDSHELL
    # processing (if enabled).  It is *off* by default because
    # we do not want commands invoked via the command history
    # mechanism to use this feature - doing so would cause
    # cascading of the CMDSHELL string on each subsequent
    # invocation.  So, the only time we want to do CMDSHELL
    # processing is when the user presses the RUNCMD key.
    # The binding for this key thus sets DoCmdShell to True.

    # Prompt with passed initial edit string
    if initial:
        cmd = askstring(pRUNCMD, pENCMD, initialvalue=initial)

    # Prompt with last manually entered command - doesn't matter if it's null
    else:
        cmd = askstring(pRUNCMD, pENCMD, initialvalue=UI.LastCmd )

    # Execute command (if any) - Blank entry means do nothing/return
    if cmd:

        mycmd = cmd

        # Process any built-in shortcuts they may have used

        for sc in RUNCMD_SC.keys():
            mycmd = mycmd.replace(sc, RUNCMD_SC[sc])

        # Keep track of whether or not the user asked for a refresh after command completion
        # We have to strip it here of CMDSHELL processing will work.

        do_refresh_after = False
        if mycmd[0] == REFRESHAFTER:
            do_refresh_after = True
            mycmd = mycmd[1:]

        # Do CMDSHELL Processing if enabled and requested

        if CMDSHELL and DoCmdShell:                      # See if feature is enabled and requested
            if not mycmd.startswith(CMDSHELLESC):        # See if user is trying to escape the feature
                mycmd = "%s '%s'" % (CMDSHELL, mycmd)
            else:                                        # User is escaping the feature
                mycmd = mycmd[1:]

        # Request refreshing after command completion if it was desired

        if do_refresh_after:
            mycmd = REFRESHAFTER + mycmd
            
        ExecuteCommand(mycmd, pMANUALCMD, ResolveVars=True, SaveUnresolved=True)

        # Save the command only if Command History is enabled (MAXMENU > 0)
        # AND one of two conditions exist:
        #
        #    1) No initial string was provided (The user entered a command manually).
        #    2) An initial string was provided, but the user edited it.

        if (MAXMENU > 0) and ((not initial) or (cmd != initial)):
            UI.LastCmd = cmd

    UI.DirList.focus()

    return 'break'

# End of 'KeyRunCommand()'


#####
# Event Handler: Process Current Selection
#####

def DirListHandler(event):
    global UI
    
    # Get current selection.  If none, just return, otherwise process
    selected =  UI.LastInSelection()
    if not selected:
        return
    
    # If we're on Win32 and we just selected ".." from the root of
    # a drive, request a display of the Drive List.  LoadDirList()
    # will check to see if there is anything in the Drive List and
    # do nothing if it is empty (which happens if the user has not
    # installed the Win32All package).

    if OSNAME =='nt' and \
               os.path.abspath(UI.CurrentDir) == os.path.abspath(UI.CurrentDir + selected):

        LoadDirList(SHOWDRIVES, save=True)
        UI.MouseNewDir = True

    # If selection is a directory, move there and list contents.

    elif os.path.isdir(os.path.join(UI.CurrentDir, selected)):

        # On Unix, don't follow links pointing back to themselves

        if OSNAME == 'posix' and os.path.samefile(UI.CurrentDir, UI.CurrentDir + selected):

            # Protect with try/except because Tk loses track of things
            # if you keep hitting this selection very rapidly - i.e. Select
            # the entry and lean on the Enter key.  The try/except
            # prevents the error message (which is benign) from ever
            # appearing on stdout.
            
            try:
                WrnMsg(wLINKBACK % (UI.CurrentDir + selected[:-1]))
            except:
                pass
            return

        # Build full path name
        selected = os.path.join(os.path.abspath(UI.CurrentDir), selected)

        # Convert ending ".." into canonical path
        if selected.endswith(".."):
            selected = PSEP.join(selected.split(PSEP)[:-2])
        
        # Need to end the directory string with a path
        # separator character so that subsequent navigation
        # will work when we hit the root directory of the file
        # system.  In the case of Unix, this means that
        # if we ended up at the root directory, we'll just
        # get "/".  In the case of Win32, we will get
        # "DRIVE:/".

        if selected[-1] != PSEP:
            selected += PSEP

        # Load UI with new directory
        LoadDirList(selected, save=True)

        # Indicate that we entered a new directory this way.
        # This is a workaround for Tk madness.  When this
        # routine is invoked via the mouse, Tk sets the
        # activation *when this routine returns*.  That means
        # that the activation set at the end of LoadDirList
        # gets overidden.  We set this flag here so that
        # we can subsequently do the right thing in our
        # background polling loop.  Although this routine
        # can also be invoked via a keyboard selection,
        # we run things this way regardless since no harm
        # will be done in the latter case.

        UI.MouseNewDir = True


    # No, a *file* was selected with a double-click
    # We know what to do on Win32 and Unix.  We ignore
    # the selection elsewhere.

    elif (OSPLATFORM == 'win32') or (OSNAME == 'posix'):

        # Find out if the OS thinks this is an executable file

        executable = os.stat(selected)[ST_MODE] & (S_IXUSR|S_IXGRP|S_IXOTH)

        # Apply any relevant association information, skipping types
        # found in the exclusion list
        

        # Ignore things that are on the exclusion list
        
        excluded = False
        for exclude in UI.Associations[ASSOCEXCL]:

            # Handle case-insensitive exclusions

            if exclude[0] == ASSOCNOCASE:
                selected = selected.lower()
                exclude = exclude[1:].lower()

            # See if there is an exclusion

            if fnmatch(selected, exclude):
                excluded = True

        # Check the selection against every named association, but skip
        # the ASSOCDFLT and ASSOCEXCL associations because they are
        # special directives and not "real" associations.

        assocfound = False
        if not excluded:
            for assoc in UI.Associations:

                # Handle case-insensitive associations
                
                tstassoc = assoc
                if tstassoc[0] == ASSOCNOCASE:
                    selected = selected.lower()
                    tstassoc = tstassoc[1:].lower()

                # See if the selection matches the association

                if (assoc != ASSOCDFLT) and (assoc != ASSOCEXCL) and fnmatch(selected, tstassoc):
                    selected = UI.Associations[assoc]
                    assocfound = True

            # If we did not find a file association and a default
            # association is defined, apply it to everything
            # except executable files.

            if not assocfound and (ASSOCDFLT in UI.Associations) and not executable:
                selected = UI.Associations[ASSOCDFLT]
                assocfound = True

        
        # In the case of Unix-like OSs, if the file is non-executable
        # and has no association, this is an error and needs to
        # flagged as such.  In Windows, this may- or may-not be an
        # error because of Windows own association mechanism.  So, we
        # pass the request through on Windows and let it handle this
        # case.

        if not executable and not assocfound and OSNAME == 'posix':
            ErrMsg(eBADEXEC % selected)
            
        # Now execute the command

        else:

            usestartdir=False
            # If there is NOT an association, create absolute path to
            # selected command

            if not assocfound:
                selected = os.path.join(os.path.abspath(UI.CurrentDir), selected)

                # Win32 has a special command interface wherein its internal associations
                # are applied.  We only invoke command execution this way when twander
                # found no associations of its own.

                if OSPLATFORM == 'win32':
                    usestartdir=True

            ExecuteCommand(selected, '', ResolveVars=True, ResolveBuiltIns=True, UseStartDir=usestartdir)

    return 'break'

# End of 'DirListHandler()'


#####
# Event Handler: Process Directory Shortcut Request
#####

def DirSCKeyPress(event, index):

    # Process the keypress
    
    dir = UI.DirSCKeys[index-1]
    if dir:
        LoadDirList(ProcessVariables(dir, 0, dir))

    # Inhibit further processing of key - some Function Keys
    # have default behavior in Tk which we want to suppress.

    return "break"

# End of 'DirSCKeyPress()'


#####
# Event Handler: Set Desired Directory Shortcut Key To Current Directory
#####

def DirSCSet(event):

    index = askinteger(pSCCHANGE, pSCNUM, minvalue=1, maxvalue=12)
    UI.DirList.focus()

    # Set the indicated shortcut key to the current directory
    # And update the menus to reflect this fact

    if index:
        UI.DirSCKeys[index-1] = UI.CurrentDir
        LoadShortcutMenu()

    # Inhibit further processing of key - some Function Keys
    # have default behavior in Tk which we want to suppress.

    return "break"

# End of 'DirSCSet()'


#--------------------  Memory Features --------------------#

#####
# Event Handler: Menu-Related Features Handled By Single Handler
#####

def KeyMemHandler(mem, clear=False):
    global UI
    
    # Clearing Memory
    if clear:

        # Clear all
        if mem == NUMPROGMEM + 1:
            UI.ProgMem = [[], [], [], [], [], [], [], [], [], [], [], []]

        # Clear specific location
        if 0 < mem < NUMPROGMEM + 1:
            UI.ProgMem[mem-1] = []

    # Saving to memory
    else:
        for x in UI.AllSelection():
            UI.ProgMem[mem-1].append(StripPSEP(os.path.abspath(x)))

    if DEBUGLEVEL & DEBUGMEM:
        if 0 < mem < NUMPROGMEM + 1:
            PrintDebug(dMEM % mem, UI.ProgMem[mem-1])
        else:
            PrintDebug(dMEMALL, UI.ProgMem)


    # Inhibit further processing of keystroke so Tkinter
    # defaults like Alt-F10 don't take hold.
    
    return "break"

# End of 'KeyMemHandler()


#------------------  Sorting Features  --------------------#

#####
# Event Handler: Set Sort Parameters
#####

def KeySetSortParm(parm):
    global SORTBYFIELD, SORTREVERSE, SORTSEPARATE

    # Which entry in the Name2Key 

    refresh = False

    if parm == fREVERSE:
        SORTREVERSE = not SORTREVERSE
        refresh = True

    # Separate Dirs/Files Means Nothing In Drive List View - Suppress
    # this there to avoid an unnecessary refresh
    
    elif (parm == fSEPARATE):
        if  (UI.CurrentDir != SHOWDRIVES):
            SORTSEPARATE = not SORTSEPARATE
            refresh = True

    # Sort By Selected Parameter
    # In Drive List View only respond to those keys that have a
    # corresponding Sort Menu Entry
    
    else:

        
        # First determine whether we even want to act on this keystroke.
        # A given keystroke is ignored if the Name of the sort option associated
        # with the current view is None (the Python value None, not the string 'None').

        # Get index of desired entry in Name2Key tuple
        
        if UI.CurrentDir == SHOWDRIVES:
            idx = 2
        else:
            idx = 1

        # Get the tuple associated with new key
        n2k = Name2Key[parm.lower()]

        # Get the name associated with the new key appropriate for the current view
        sortname = n2k[idx]

        # If the new key is the same as the old key, ignore - ignore, we're already
        # sorted this way.  This avoids unnecessary refreshes.
        #
        # If the new key is (Python) None, it means we do not want to process this
        # keystoke, so ignore it.

        if (parm == SORTBYFIELD) or not sortname:
            return

        # Go ahead and do the new sort
        else:
            SORTBYFIELD = parm
            refresh = True

    if refresh:
        LoadHelpMenu()
        RefreshDirList(None)

    return 'break'

#End of 'KeySetSortParm()'


#-------------- Handler Utility Functions -----------------#

#####
# Event Handler: Popup Menus
#####

def PopupMenu(menu, x, y):

    # Popup requested menu at specified coordinates
    # but only if the menu has at least one entry.

    if menu.index(END):
        menu.tk_popup(x, y)

# End of 'PopupMenu()'


#####
# Execute A Command
#####

def ExecuteCommand(cmd, name, UseStartDir=False, ResolveVars=False, ResolveBuiltIns=True, SaveUnresolved=False):
    global UI

    # Do nothing on blank commands
    if not cmd.strip():
        return

    # Work with a copy of the passed command
    newcmd = cmd

    # Replace references to any Environment or User-Defined variables
    # but only when asked to.  This needs to be done *before*
    # we process the built-ins so that variable references within
    # a PROMPT or YESNO are resolved before we handle the prompting.
    
    if newcmd and ResolveVars:
        newcmd = ProcessVariables(newcmd, 0 , name)

    # Process references to any Built-In variables
    if ResolveBuiltIns:
        newcmd = ProcessBuiltIns(newcmd, name)

    # A leading REFRESHAFTER in the command string means the user wants
    # a display refresh after the command returns

    do_refresh_after = False
    if newcmd and newcmd[0] == REFRESHAFTER:
        newcmd = newcmd[len(REFRESHAFTER):]
        do_refresh_after = True

        
    # Just dump command if we're debugging

    if DEBUGLEVEL & DEBUGCMDS:
        PrintDebug(dCMD, [newcmd,])
    
    # A null return value means there was a problem - abort
    # Otherwise,actually execute the command.
    elif newcmd:
        
        # Run the command on Win32 using filename associations
        if UseStartDir:
            try:
                os.startfile(newcmd)
            except:
                WrnMsg(wBADEXE % newcmd)

        # Normal command execution for both Unix and Win32
        else:
            try:
                if (OSNAME == 'posix') and not USETHREADS:
                    os.system(newcmd + " &")
                else:
                    thread.start_new_thread(os.system, (newcmd,))
            except:
                WrnMsg(wBADEXE % newcmd)


    # Update the Command History observing MAXMENU
    # In most cases, we want to save the command with all the
    # variables (Built-In, Environment, User-Defined) resolved (dereferenced).
    # However, sometimes (e.g. manual command entry via KeyRunCommand()) we
    # want to save the *unresolved* version.  We also preserve the REFRESHAFTER
    # indicator for all commands - manual or from the config file.  This provides
    # consistency in the history regardless of the soure of the command.

    if SaveUnresolved:
        savecmd = cmd

    elif do_refresh_after:
        savecmd = REFRESHAFTER + newcmd

    else:
        savecmd = newcmd

    UpdateMenu(UI.HistBtn, UI.CmdHist, MAXMENU, MAXMENUBUF, KeyRunCommand, newentry=savecmd, fakeevent=True)
                
    # Dump Command History stack if requested
    
    if DEBUGLEVEL & DEBUGHIST:
        PrintDebug(dHIST, UI.CmdHist)

        
    # Do a display refresh if the user wanted it
    # Wait a while to give the command a chance to complete
    # Then clear any selections
    
    if do_refresh_after:
        time.sleep(AFTERWAIT)
        if AFTERCLEAR:
            KeySelNone(None)
        RefreshDirList(None)
        
# End of 'ExecuteCommand()


#####
# Load UI With Selected Directory
#####

def LoadDirList(newdir, save=True, updtitle=True):

    # Make sure we're permitted to navigate - we have to allow initial entry into STARTDIR
    if NONAVIGATE and (newdir != STARTDIR):
        return

    # Reset any active filtering
    UI.FilterWildcard = ("None", None, None, False)

    # Transform double forward-slashes into a single
    # forward-slash.  This keeps the Directory Stack
    # and Visited lists sane under Unix and prevents
    # Win32 from attempting to enter a Drive List View
    # when the user enters this string but Win32All has
    # not been loaded.

    if newdir == '//':
        newdir = '/'

    # Get path into canonical form unless we're trying
    # to display a Win32 Drive List
    
    if newdir != SHOWDRIVES:
        newdir = os.path.abspath(newdir)

        # Make sure newdir properly terminated
        if newdir[-1] != PSEP:
            newdir += PSEP

    # User has requested a Drive List View.  Make sure we're
    # running on Win32 and see the feature is available.  If
    # not available (which means Win32All is not installed),
    # just ignore and return, doing nothing.

    elif OSPLATFORM != 'win32' or  not GetWin32Drives():
        return

    # Indicate we are doing a refresh.
    # This defaults to always being done.
    # Exception is first call to this routine from setup logic.
    
    if updtitle:
        UI.UpdateTitle(UIroot, refreshing=REFRESHINDI)

    # Check right now to see if we can read
    # the directory.  If not, at least we
    # haven't screwed up the widget's current
    # contents or program state.

    try:
        contents = BuildDirList(newdir)
    except:
        # If CurrentDir set, we're still there: error w/ recovery
        if UI.CurrentDir:
            ErrMsg(eDIRRD % newdir)
            return

        # If not, we failed on the initial directory: error & abort
        else:
            ErrMsg(eINITDIRBAD % newdir)
            sys.exit(1)

    # Push last directory visited onto the visited stack

    # We do NOT save this to the stack if:
    #
    #    1) We've been told not to. - Passed when we're called (save=False).
    #    2) If we're trying to move into the current directory again.
    #       This can happen either when the user does a manual directory
    #       change or if they press ".." while in root.  We don't
    #       actually want to save the directory until we *leave* it,
    #       otherwise we'll end up with a stack top and current
    #       directory which are the same, and we'll have to go
    #       back *twice* to move to the previous directory.
    
    # Are we trying to move back into same directory?
    if os.path.abspath(UI.CurrentDir) == os.path.abspath(newdir):
        save = False

    # Now save if we're supposed to.
    if save and UI.CurrentDir:
        UI.LastDir.append(UI.CurrentDir)

    # Dump directory stack if debug requested it
    if DEBUGLEVEL & DEBUGDIRS:
        PrintDebug(dDIRSTK, UI.LastDir)

    # And select new directory to visit
    UI.CurrentDir = newdir

    # Wait until we have exclusive access to the widget

    while not UI.DirListMutex.testandset():
        pass

    # Clear out the old contents
    UI.DirList.delete(0,END)

    # Load new directory contents into UI
    for x in contents:
        UI.DirList.insert(END, x)

    # Also move the program context to the new directory
    # for everything except a Drive List View.  In that case
    # the program context remains in the directory from
    # which the Drive List View was selected

    if newdir != SHOWDRIVES:
        os.chdir(newdir)

    # Keep list of all unique directories visited in the Directory Menu
    UpdateDirMenu(newdir)

    # Nothing should be pre-selected in the new directory listing
    KeySelNone(None)

    # Update Sort Menu to reflect whether we're in Normal or Drive List View
    LoadSortMenu()

    # Update titlebar to reflect any changes
    UI.UpdateTitle(UIroot)

    #Release the lock
    UI.DirListMutex.unlock()

# End of 'LoadDirList():


#####
# Return Ordered List Of Directories & Files For Current Root
# Posts A Warning Message If SORTBYFIELD Is Out Of Range
#####

def BuildDirList(currentdir):
    global UI, SORTBYFIELD, REFRESHINT

    # Set time of the refresh
    begintime = time.time()

    # We'll need the nominal refresh interval later
    nominal = UI.OptionsNumeric["REFRESHINT"]

    # Check to see if SORTBYFIELD makes sense

    if SORTBYFIELD.lower() not in Name2Key.keys():
        default = UI.OptionsString["SORTBYFIELD"]
        WrnMsg(wBADSORTFLD % (SORTBYFIELD, default))
        SORTBYFIELD = default
        LoadHelpMenu()

    UI.TotalSize = 0

    fileinfo = []
    dKeys,  fKeys  = {}, {}
    
    # Indicate where in each display string the actual file name
    # can be found.  This is used both in the code in this routine
    # and other places in the program where just the file name is
    # needed - for example, when we want to execute it or replace it
    # in one of the built-ins.  This value depends on whether or
    # not we are viewing details or not.
    
    if UI.DetailsOn:
        if currentdir == SHOWDRIVES:
            UI.NameFirst = SZ_DRIVE_TOTAL
        else:
            UI.NameFirst = ST_SZTOTAL
    else:
        UI.NameFirst = 0

    # Two possible cases have to be handled:
    # A normal directory read and a Drive List View
    # under Win32.

    #####
    # Normal directory reads
    #####
    
    if currentdir != SHOWDRIVES:

        # Save the current OS directory context and temporarily set it
        # to the target directory

        cwd = os.path.abspath(os.path.curdir)
        os.chdir(currentdir)

        # Get and sort directory contents

        filelist = os.listdir(currentdir)
        keyindex = Name2Key[SORTBYFIELD.lower()][0]
        dList, fList = [], []

        
        for x in range(len(filelist)):

            # Get File/Dir name
            
            file = filelist[x]

            # Get detail display string as well as individual fields
            
            detail, fields = FileDetails(file, currentdir)

            # Add trailing path separator to directory entries
            # Pay attention to pickup symlinks pointing to directories
            
            if detail[0] == ST_SPECIALS["04"] or os.path.isdir(detail.split(SYMPTR)[-1].strip()):
                file   += PSEP
                detail += PSEP
                    
            # Check against any active filtering by wildcard.  Only allow files through that match.

            matchthis = file
            if UI.DetailsOn:
                matchthis = detail

            if not FilterMatching(matchthis):
                continue

            # Keep running tally of total files sizes

            UI.TotalSize += fields[Name2Key[fLENGTH.lower()][0]]

            # Decide whether we have to sort or not, act accordingly
            
            if SORTBYFIELD.lower() == fNONE.lower():

                # Nope, no sorting, just load-up the return data structures
                # with either the file name or the details string depending
                # on whether or not we're displaying details at the moment.

                if UI.DetailsOn:
                    dList.append(detail)
                else:
                    dList.append(file)

            # Yup, we're going to sort later - build index/return data structures
            else:

                # Get the keystring used for the actual sort
                # Collapse case on Win32 when sorting by name

                sortkey = fields[keyindex]
                if OSPLATFORM == 'win32' and (SORTBYFIELD.lower() == fNAME.lower()):
                    sortkey = sortkey.lower()

                # Keep track of the file name and its details,
                # separating directories from files Treat symlinks
                # pointing to directories as directories for this
                # purpose (if that's what the user wants).
                # Build corresponding key list for sorting.
                
                fileinfo.append((file, detail))
                currentpos = len(fileinfo)-1
                
                if detail[0] == ST_SPECIALS["04"] or (SYMDIR and os.path.isdir(detail.split(SYMPTR)[-1].strip())):
                    dKeys.setdefault(sortkey, []).append(currentpos)

                else:
                    fKeys.setdefault(sortkey, []).append(currentpos)
                    
        # If sorting has been requested, do so now
        
        if SORTBYFIELD.lower() != fNONE.lower():

            # Sort keys according to user's desire for Dir/File separation

            if SORTSEPARATE:
                dk = dKeys.keys()
                dk.sort()
                fk = fKeys.keys()
                fk.sort()

            else:
                # Combine the two key dicts into one composite
                # dictionary (dKeys)

                for key in fKeys.keys():
                    for val in fKeys[key]:
                        dKeys.setdefault(key, []).append(val)

                dk = dKeys.keys()
                dk.sort()
                fk = []

            # Reverse the sorts, if requested

            if SORTREVERSE:
                dk.reverse()
                fk.reverse()

            # Build corresponding dir/file lists, observing user's
            # request for detail information

            for x in dk:

                for index in dKeys[x]:

                    if UI.DetailsOn:
                        dList.append(fileinfo[index][1])
                    else:
                        dList.append(fileinfo[index][0])

            for x in fk:

                for index in fKeys[x]:

                    if UI.DetailsOn:
                        fList.append(fileinfo[index][1])
                    else:
                        fList.append(fileinfo[index][0])

            # Sorting logic ends here

        # Now return results in their final form

        if UI.DetailsOn:
            dotdot = [FileDetails(".." + PSEP, currentdir)[0],]
        else:
            dotdot = [".." + PSEP,]


        # If the user doesn't want symbolic link expansion, get rid of it.

        if not SYMEXPAND:
            for list in (fList, dList):

                for i in range(len(list)):

                    # Only necessary for symlinks
                    if list[i].count(SYMPTR):

                        # Preserve possible indication this is a directory
                        tail = list[i][-1]        

                        # Remove target portion of any symlinks
                        list[i] = list[i].split(SYMPTR)[0]

                        # If not already noted, indicate symlinks pointing to directories
                        if tail == PSEP and not list[i].endswith(PSEP):
                            list[i] += tail

        # Return the results
        # Entry to move up one directory is always first,
        # no matter what the sort.  This is necessary because
        # OSs like Win32 like to use '$' in file names  which
        # sorts before "."

        # Restore the original directory context

        os.chdir(cwd)

        # Dynamically adjust refresh interval if option enabled

        if ADAPTREFRESH:

            UI.LastRefresh    = time.time()
            length  = int((time.time() - begintime) * 1000)

            if length > nominal:
                REFRESHINT = int((length - nominal) * 1.5) + nominal
            else:
                REFRESHINT = nominal
            
        if SORTREVERSE:
            return dotdot + fList + dList
        else:
            return dotdot + dList + fList

    #####
    # The user requested Drive List View.
    #####
    
    else:


        dlv     = {}
        dList   = []

        # There are more keys in normal view than in Drive List View
        # If the user has selected one of these, map them to sort
        # by name in Drive List View.        

        dlvkey = Name2Key[SORTBYFIELD.lower()][0]
        if dlvkey > MAXDLVKEY:
            dlvkey = MAXDLVKEY

        drivelist = GetWin32Drives()

        # Create a detailed entry for each drive on the system
        # Store it as a string in the details list which will
        # then be returned to the caller

        for drive in drivelist:

            
            fields  = []      

            # Drive Label - Drive Might Not Be Available
            try:
                label = GetVolumeInformation(drive)[0]
            except:
                label = NODRIVE

            if not label:
                label = NOLABEL

            # Type Of Drive - We need this now to get hostname
            drivetype = GetDriveType(drive)
            typestring = ''

            for type, stype in win32all_type:
                if drivetype == type:
                    typestring = stype

            # Machine Hosting The Drive
            if drivetype == win32con.DRIVE_REMOTE:
                name = WNetGetUniversalName(drive, 1)
            else:
                name = label

            entry = PadString(name, SZ_DRIVE_SHARE)
            fields.append(name)

            # Add the drive type
            entry += PadString(typestring, SZ_DRIVE_TYPE)
            fields.append(typestring)

            # Get Drive Space Information - Drive Might Not Be Available
            try:
                clustersz, sectorsz, freeclusters, totalclusters = GetDiskFreeSpace(drive)

                # Free Space
                fspace = clustersz * sectorsz * freeclusters
                freespace = FileLength(fspace)

                # Total Space
                tspace = clustersz * sectorsz * totalclusters
                totalspace = FileLength(tspace)

            except:
                fspace, tspace = (0, 0)
                freespace, totalspace = ('0', '0')


            freespace  = PadString(freespace, SZ_DRIVE_FREE, Rjust=True, Trailing=SZ_TRAILING_SPACE)
            totalspace = PadString(totalspace, SZ_DRIVE_TTL, Rjust=True, Trailing=SZ_TRAILING_SPACE)
            entry += "%s%s%s%s" % (freespace, WIN32FREE, totalspace, WIN32TOTAL)

            fields.append(fspace)
            fields.append(tspace)


            # Finally, tack on the drive letter
            entry += drive
            fields.append(drive)

            # Filter through any active wildcard

            matchthis = drive
            if UI.DetailsOn:
                matchthis = entry

            if not FilterMatching(matchthis):
                continue

            # Keep running total of available space
            UI.TotalSize += tspace

            # If we're not going to sort later, just build the list
            # of drives now

            if SORTBYFIELD.lower() == fNONE.lower():
                if UI.DetailsOn:
                    dList.append(entry)
                else:
                    dList.append(drive)

            # Nope, prepare to sort later
            else:
                idx = fields[dlvkey]
                dlv.setdefault(idx,[]).append((drive, entry))


        # Now that we've built the list, sort by indicated parameter
        # if user has so indicated
        
        if SORTBYFIELD.lower() != fNONE.lower():

            
            indexes = dlv.keys()
            indexes.sort()

            if SORTREVERSE:
                indexes.reverse()

            # Now build output list in sorted order

            for x in indexes:

                for entry in dlv[x]:

                    if UI.DetailsOn:
                        dList.append(entry[1])
                    else:
                        dList.append(entry[0])

        # Dynamically adjust refresh interval if option enabled

        if ADAPTREFRESH:

            UI.LastRefresh    = time.time()
            length  = int((time.time() - begintime) * 1000)

            if length > nominal:
                REFRESHINT = int((length - nominal) * 1.5) + nominal
            else:
                REFRESHINT = nominal
            
        # Return the list

        return dList
                    

    
# End of  'BuildDirList()'


#####
# Get Details For A File Or Directory
# Returns Both A Formatted Display String With Detail Information,
# And A List Containing The Individual Detail Fields
#####

def FileDetails(name, currentdir):
    
    details = ""
    fields  = []
    
    # Condition the name

    fn = os.path.join(currentdir, name)
    if fn[-1] == PSEP:
        fn =fn[:-1]

    # Get file details from OS
    try:
        stinfo =  os.lstat(fn)

    # 'lstat' failed - provide entry with some indication of this

    except:
        pad  = (UI.NameFirst - len(iNOSTAT) - 1) * " "
        details = pad + iNOSTAT + " " + name
        fields  = ["-" * 10, 0, UNAVAILABLE, UNAVAILABLE, 0L, 0, name]

        # Done with this file
        return details, fields

    # Do Win32-specific mode if win32all is loaded
    if WIN32ALL and USEWIN32ALL and WIN32ALLON:
        modlen = len(win32all_mode)

        try:
            win32stat = GetFileAttributes(fn)
            mode = ""
        except:
            mode = UNAVAILABLE

        if not mode:

            # Test each attribute and set symbol in respective
            # position, if attribute is true.

            for i in range(modlen):
                mask, sym = win32all_mode[i]
                if win32stat & mask:
                    mode += sym
                else:
                    mode += '-'

    # We're either on Unix or Win32 w/o win32all available
    else:
        # Mode - 1st get into octal string

        mode = stinfo[ST_MODE]
        modestr =  str("%06o" % mode)

        # Set the permission bits

        mode = ""
        for x in [-3, -2, -1]:
            mode +=  ST_PERMIT[int(modestr[x])]

        # Deal with the special permissions

        sp = int(modestr[-4])

        # Sticky Bit

        if sp & STICKY_MASK:
            if mode[-1] == "x":
                mode = mode[:-1] + "t"
            else:
                mode = mode[:-1] + "T"

        # Setgid Bit

        if sp & SETGID_MASK:
            if mode[-4] == "x":
                mode = mode[:-4] + "s" + mode[-3:]
            else:
                mode = mode[:-4] + "S" + mode[-3:]

        # Setuid Bit

        if sp & SETUID_MASK:
            if mode[-7] == "x":
                mode = mode[:-7] + "s" + mode[-6:]
            else:
                mode = mode[:-7] + "S" + mode[-6:]

        # Pickup the special file types
        mode = ST_SPECIALS.get(modestr[0:2], "?") + mode


    # Pad the result for column alignment
    details += PadString(mode, ST_SZMODE)
    fields.append(mode)

    # Number of links to entry
    nlinks = stinfo[ST_NLINK]
    details += PadString(str(nlinks), ST_SZNLINK)
    fields.append(nlinks)

    # Get first ST_SZxNAME chars of owner and group names on unix

    if OSNAME == 'posix':

        # Convert UID to name, if possible
        try:
            owner = pwd.getpwuid(stinfo[ST_UID])[0][:ST_SZUNAME-1]

        # No valid name associated with UID, so use number instead
        except:
            owner = str(stinfo[ST_UID])

        # Convert GID to name, if possible
        try:
            group = grp.getgrgid(stinfo[ST_GID])[0][:ST_SZGNAME-1]

        # No valid name associated with GID, so use number instead
        except:
            group = str(stinfo[ST_GID])


    # Handle Win32 systems
    elif OSPLATFORM == 'win32':

        # Defaults
        owner = WIN32OWNER
        group = WIN32GROUP

        if WIN32ALL and USEWIN32ALL and WIN32ALLON:
            try:
                # Get the internal Win32 security information for this file.
                ho     = GetFileSecurity(fn, OWNER_SECURITY_INFORMATION)
                hg     = GetFileSecurity(fn, GROUP_SECURITY_INFORMATION)
                sido   = ho.GetSecurityDescriptorOwner()
                sidg   = hg.GetSecurityDescriptorGroup()

                # We have to know who is hosting the filesytem for this file

                drive = fn[0:3]
                if GetDriveType(drive) == win32con.DRIVE_REMOTE:
                    fnhost = WNetGetUniversalName(drive, 1).split('\\')[2]
                else:
                    fnhost = WIN32HOST

                # Now we can translate the sids into names

                owner  = LookupAccountSid(fnhost, sido)[0]
                group  = LookupAccountSid(fnhost, sidg)[0]

            # We assume the values are unavailable on any error
            except:
                owner = UNAVAILABLE
                group = UNAVAILABLE

     # Default names for all other OSs
    else:
        owner = OSNAME + FILEOWNER
        group = OSNAME + FILEGROUP

    # Add them to the detail

    details += PadString(owner, ST_SZUNAME)
    details += PadString(group, ST_SZGNAME)

    # Add them to the fields

    fields.append(owner)
    fields.append(group)

    # Length

    rlen = stinfo[ST_SIZE]
    flen = FileLength(rlen)
    details += PadString(flen, ST_SZLEN, Rjust=True, Trailing=SZ_TRAILING_SPACE)
    fields.append(rlen)

    # mtime

    rawtime = stinfo[ST_MTIME]
    
    # Get the whole time value
    ftime = time.ctime(rawtime).split()[1:]

    # Pad single-digit dates differently for US vs. ISO
    # date representation

    LEADFILL = " "
    if ISODATE:
        LEADFILL = "0"

    if len(ftime[1]) == 1:
        ftime[1] = LEADFILL + ftime[1]

    # Drop the seconds

    ftime[-2] = ":".join(ftime[-2].split(":")[:-1])

    # Turn into a single string in either ISO or US format

    if ISODATE:
        ftime = "-".join((ftime[3], ST_MONTHS[ftime[0]], ftime[1])) + \
                " " + ftime[2]

    # US Localized Format
    
    else:
        ftime = " ".join(ftime)

    details += PadString(ftime, ST_SZMTIME)
    fields.append(rawtime)

    # Add the File Name
    details += name
    fields.append(name)

    #  Include symlink details as necessary
    if details[0] == 'l':

        # Symlink targets can be displayed as defined (default)
        # or expanded to their absolute path string.
        
        if SYMRESOLV:
            f = os.path.realpath(currentdir + name)
        else:
            f = os.readlink(currentdir + name)

        # Strip trailing path separator
        # This will be handled by the caller

        if f[-1] == PSEP:
            f = f[:-1]

        details += SYMPTR + f

    return details, fields

# End of 'FileDetails()'


#####
# Process A Command Line Containing Built-In Variables
#####

def ProcessBuiltIns(cmd, name):

    # Do files & directories first.  That way they can be embedded in
    # prompting builtins.
    
    # Strip trailing path separators in each case to
    # give the command author the maximum flexibility possible

    # We have to treat built-ins specially if we're in a Drive List View
    # Most noteably, there is no meaning to [DIR] in this context

    if UI.CurrentDir == SHOWDRIVES:
        currentdir = ""
    else:
        currentdir = StripPSEP(UI.CurrentDir)


    selection = StripPSEP(UI.LastInSelection())
    dselection = ""

    if selection:
        dselection = QUOTECHAR + currentdir + PSEP + selection + QUOTECHAR
        selection  = QUOTECHAR + selection + QUOTECHAR
        
    selections = ""
    dselections = ""
    for selected in UI.AllSelection():

        # Fill the various built-ins
        selected = StripPSEP(selected)
        dselections += QUOTECHAR + currentdir + PSEP + selected + QUOTECHAR + " "
        selections  += QUOTECHAR + selected + QUOTECHAR + " "


    # Force Unix-style path separators if requested

    if FORCEUNIXPATH and OSPLATFORM == 'win32':
        currentdir   = currentdir.replace("\\", "/")
        dselection   = dselection.replace("\\", "/")
        dselections  = dselections.replace("\\", "/")
                

    # Now do the actual replacements

    cmd = cmd.replace(DIR, QUOTECHAR + currentdir + QUOTECHAR)
    cmd = cmd.replace(SELECTION, selection)
    cmd = cmd.replace(DSELECTION, dselection)
    cmd = cmd.replace(SELECTIONS, selections)
    cmd = cmd.replace(DSELECTIONS, dselections)
    cmd = cmd.replace(HASH, COMMENT)
    
    # Process references to program memories

    for x in range(NUMPROGMEM):

        # Only do this if there is a reference to the memory in
        # question.  This keeps the program from needlessly
        # churning on long lists of memory contents which are not needed.

        vblref = "[MEM%s]" % str(x+1)
        if cmd.count(vblref):
            s = ""
            for m in UI.ProgMem[x]:
                if FORCEUNIXPATH and OSPLATFORM == 'win32':
                    m = m.replace("\\", "/")
                s += QUOTECHAR + m + QUOTECHAR + " "
            cmd = cmd.replace(vblref, s)
                    
    # Now take care of the prompting

    for promptvar, handler, defaultarg, replace in ((YESNO, askyesno, "default", False),
                                                 (PROMPT, askstring, "initialvalue", True)):

        for x in range(cmd.count(promptvar)):
            b = cmd.find(promptvar)
            e = cmd.find("}", b)
            prompt = cmd[b + len(promptvar):e]

            # Pickup default value, if any

            default = {}
            prompt = prompt.split(DEFAULTSEP)
            prompt.append("")                                  # Guarantee a minimum of two entries
            prompt, default[defaultarg] = prompt[0], prompt[1]

            # Condition the default if its a YESNO builtin

            if promptvar == YESNO:
                default[defaultarg] = default[defaultarg].strip().lower()

                # YESNO dialogs can only accept two arguments (we just made them case-insensitive above)
            
                if (default[defaultarg] not in ("yes", "no", "")):

                    # Display an error
                    WrnMsg(wBADYESNODFLT % (default[defaultarg], name))

                    # We're done on an error
                    return

            # Everything OK - Run the dialog

            # If there is no default argument, then don't pass anything at all - Tk gets confused if we do

            if not default[defaultarg]:
                default = {}

            val = handler(name, prompt, **default)

            # Make sure our program gets focus back
            UI.DirList.focus()

            if val:
                if replace:
                    cmd = cmd.replace(cmd[b:e+1], QUOTECHAR + val + QUOTECHAR)
                else:
                    cmd = cmd.replace(cmd[b:e+1], '')

            # Null input means the command is being aborted
            else:
                return

    return cmd

# End of 'ProcessBuiltIns()'    


#####
# Process/Replace References To User-Defined & Environment Variables
#####

def ProcessVariables(cmd, num, line):

    doeval = True
    depth  = 0

    while doeval:

        # Bound the number of times we can nest a definition
        # to prevent self-references which give infinite nesting depth

        depth += 1
        if (depth > MAXNESTING):
            doeval = False

            # See if there are still unresolved variable references.
            # If so, let the user know

            if REVAR.findall(cmd):
                WrnMsg(wVBLTOODEEP % (num, cmd))
                return ""

        # Get a list of variable references
        vbls = REVAR.findall(cmd)

        # Throw away references to Built-In Variables - these are
        # processed at runtime and should be left alone here.

        # Note that we iterate over a *copy* of the variables
        # list, because we may be changing that list contents
        # as we go.  i.e., It is bogus to iterate over a list
        # which we are changing during the iteration.

        for x in vbls[:]:

            # Ignore references to Built-In Variables here - They are
            # processed at runtime.

            if UI.BuiltIns.has_key(x):
                vbls.remove(x)

            elif x.startswith(PROMPT):
                vbls.remove(x)

            elif x.startswith(YESNO):
                vbls.remove(x)

        if vbls:
            for x in vbls:
                vbl = x[1:-1]

                # Process ordinary variables
                if UI.SymTable.has_key(vbl):
                    cmd = cmd.replace(x, UI.SymTable[vbl])

                # Process environment variables.
                # If an environment variable is referenced,
                # but not defined, this is a fatal error

                elif vbl[0] == ENVVBL:
                    envvbl = os.getenv(vbl[1:])
                    if envvbl:
                        cmd = cmd.replace(x, envvbl)
                    else:
                        WrnMsg(wBADENVVBL % (num, x, line))
                        return ""

                # Process execution variables

                elif vbl[0] == vbl[-1] == VAREXECUTE:

                    # Strip indicators
                    
                    vbl = vbl[1:-1]

                    # Find out if user wants newlines stripped

                    stripnl = False
                    if vbl[0] == STRIPNL:
                        stripnl = True
                        vbl = vbl[1:]
                        
                    status, result = GetStatusOutput(vbl)

                    # Replace with results if there was no error
                    
                    if not status:

                        # Strip newlines if asked to
                        if stripnl:
                            result = result.replace('\n', ' ')
                            
                        # Place results into command string

                        cmd = cmd.replace(x, result)

                    # If there was an error, warn user, and terminate further processing
                    else:
                        WrnMsg(wBADVAREXEC % (num, x, line))
                        return ""

                # Process references to undefined variables
                else:
                    WrnMsg(wUNDEFVBL % (num, x, line))
                    return ""

        # No substitutions left to do
        else:
            doeval = False

    return cmd
                        
# End of 'ProcessVariables()'


#####
# Refresh Contents Of Directory Listing To Stay In Sync With Reality
#####

def RefreshDirList(event, ClearFilterWildcard=False):
    global UI, INVERTFILTER

    # Indicate that we are doing an refresh
    UI.UpdateTitle(UIroot, refreshing=REFRESHINDI)
    
    # Wait until we have exclusive access to the widget

    while not UI.DirListMutex.testandset():
        pass

    # Clearout any active wildcard filtering if asked to

    if ClearFilterWildcard:
        UI.FilterWildcard = ("None", None, None, False)
        INVERTFILTER = False
        
    # Keep track of current selection and active line *by name*.  This
    # will ensure correct reselection after a refresh where the
    # contents of the directory have changed.  Since this uses simple
    # string matching, the algorithm below has to be sensitive to
    # expanded symbolic links so that the match is made on the symlink
    # name, not it's expansion (which can change by toggling one of
    # the SYM* options).

    selections = []
    for sel in list(UI.DirList.curselection()) + [str(UI.DirList.index(ACTIVE))]:
        selections.append(StripPSEP(UI.DirList.get(sel).split(SYMPTR)[0].split()[-1]))

    # Save current scroll positions

    xs = UI.hSB.get()
    ys = UI.vSB.get()

    # Clean out old listbox contents

    UI.DirList.delete(0,END)

    # Get and load the new directory information, restoring selections
    # and active marker

    try:
        dirlist = BuildDirList(UI.CurrentDir)
        UI.DirList.insert(0, *dirlist)

        # Build list of all file and directory names

        names = []
        for entry in dirlist:
            names.append(StripPSEP(entry.split(SYMPTR)[0].split()[-1]))

        # Get the active entry off the list and convert to an integer index
        
        active = selections.pop()
        try:
            active = names.index(active)
        except:
            active = 0

        # Build a list of strings describing selections, discarding
        # references to files/directories that no longer exist
        
        sellist = []
        for name in selections:
            try:
                sellist.append(str(names.index(name)))
            except:
                pass

        # Restore selection(s)

        UI.SetSelection(sellist, active)

        # Restore scroll positions

        UI.DirList.xview(MOVETO, xs[0])
        UI.DirList.yview(MOVETO, ys[0])


    # Cannot read current directory - probably media removed.
    # Just revert back to the original starting directory
    # This won't work if the original starting directory is
    # no longer readable - i.e. *It* was removed.
    
    except:
        UI.CurrentDir=STARTDIR
        os.chdir(STARTDIR)
        UI.DirList.insert(0, *BuildDirList(UI.CurrentDir))
        KeySelTop(None, clearsel=True)

    # Update titlebar to reflect any changes
    UI.UpdateTitle(UIroot)

    # Release the mutex
    UI.DirListMutex.unlock()

    return 'break'

# End of 'RefreshDirList()


#---------------- Menu Support Functions ------------------#

#####
# Handle Command Menu Selections
#####

def CommandMenuSelection(cmdkey):

    class event:
        pass

    event.state = 0
    event.char  = cmdkey
    KeystrokeHandler(event)    

# End Of 'CommandMenuSelection()'


#####
# Process Options
#####

def ProcessOptions():

    #####
    # Setup The GUI Visual Parameters, Menus, & Help Information
    #####

    SetupGUI()

    #####
    # Reflect Our Changes In The Interface
    #####

    RefreshDirList(None)

    #####
    # Dump requested debug information
    #####
    
    # Keyboard Assignments
    if DEBUGLEVEL & DEBUGKEYS:

        # Keyboard Bindings
        PrintDebug(dKEYBINDS, FormatMultiColumn(UI.KeyBindings, numcols=1))
        
        # Function Keys (Directory Shortcuts)
        PrintDebug(dFUNCKEYS, GetDirShortcuts())

    # User-Defined Variables
    if DEBUGLEVEL & DEBUGSYMS:
        PrintDebug(dSYMTBL, GetUserVbls())

    # Command Definitions
    if DEBUGLEVEL & DEBUGCTBL:
        PrintDebug(dCMDTBL, GetCommandTable())        

    # Internal Program Variables AndOptions
    if DEBUGLEVEL & DEBUGVARS:

        # Internal variabled
        PrintDebug(dINTVAR, GetIntVars())

        # User-Settable options
        PrintDebug(dOPTVAR, GetOptions())

    # Associations Table

    if DEBUGLEVEL & DEBUGASSOC:
        PrintDebug(dASSOC, GetAssocTable())

    # If we just wanted debug output, quit now
    if DEBUGLEVEL & DEBUGQUIT:
        sys.exit()

# End of 'ProcessOptions()'


#####
# Add An Entry To The List Of All Directories Visited
# Do this only if it is not already on the list and
# observe the MAXMENU variable to keep list length bounded.
#####

def UpdateDirMenu(newdir):
    global UI
    
    # Win32 collapses case so that 'x' and 'X' refer to the same
    # directory.  We want to preserve this in the user's display
    # but we have to collapse case for the purposes of doing our
    # checks below otherwise the same directory with different
    # capitalization (if the user manually enteres it that way)
    # can appear twice in the Directory Menu

    addentry = False
    
    
    if OSPLATFORM == 'win32':

        # First make a case-collapsed copy of the existing list

        dlc = []
        [dlc.append(d.lower()) for d in UI.AllDirs]

        # Now see if our new entry is already there

        if newdir.lower() not in dlc:
            addentry = True

    elif newdir not in UI.AllDirs:
        addentry = True

    # Now add the entry if we decided it was necessary. observing MAXMENU value.

    if addentry:
        UpdateMenu(UI.DirBtn, UI.AllDirs, MAXMENU, MAXMENUBUF, LoadDirList, sort=True, newentry=newdir)

# End of 'UpdateDirMenu()'


#####
# Generic Menu Update Routine
#####

def UpdateMenu(menubtn, datastore, max, maxbuf, func, sort=False, newentry="", fakeevent=False):

    # First add the new data, if any, to the specified data storage stucture.

    if newentry:
        datastore.append(newentry)
    
    # Now trim it to requested maximum length. 'max' sets how
    # many entries we see in the menu, and 'maxbuf' sets how large
    # the actual storage buffer is allowed to get.

    datastore[:] = datastore[-maxbuf:]

    # We do not sort the data storage itself if sorting has been requested.
    # We sort the *copy*.  That way we get the 'last _max_ items in
    # sorted order.' (If we sorted the master copy, we would lose
    # track of the order in which things were placed there.)

    data = datastore[:]
    if not max:
        data = []
    elif len(data) > max:
        data = datastore[-max:]

    # Initialize the menu to empty

    menubtn.menu.delete(0,END)
    menubtn.config(state=DISABLED)
    
    if len(data):
        if sort:
            data.sort()
        for entry in data:
            if fakeevent:
                menubtn.menu.add_command(label=entry, command=lambda item=entry: func(None, item))
            else:
                menubtn.menu.add_command(label=entry, command=lambda item=entry: func(item))
        menubtn['menu'] = menubtn.menu

        # Menu now has content, enable it
        menubtn.config(state=NORMAL)

# End of 'UpdateMenu()'


#---------------- Debug Support Functions -----------------#


#####
# Return List Of Association Table Entries
#####

def GetAssocTable():

    debuginfo = []
    for assocname in UI.Associations:
        debuginfo.append(PadString(assocname, dASSOCWIDTH) + str(UI.Associations[assocname]))

        debuginfo.sort()
    return debuginfo

# End of 'GetAssocTable()'


#####
# Return List Of Command Table Entries
#####

def GetCommandTable():

    debuginfo = []
    for key in UI.CmdTable.keys():
        name = UI.CmdTable[key][0]
        cmd  = UI.CmdTable[key][1]
        debuginfo.append(PadString(key + "   " + name, dCMDWIDTH) + cmd)

        debuginfo.sort()
    return debuginfo

# End of 'GetCommandTable()'


#####
# Return List Of Current Directory Shortcuts
#####

def GetDirShortcuts():

    debuginfo = []
    for x in range(len(UI.DirSCKeys)):
        key = "F" + str(x+1)
        path = UI.DirSCKeys[x]
        if path:
            debuginfo.append(PadString(key, dSCWIDTH) + path)

    return debuginfo

# End of 'GetDirShortcuts()'


#####
# Return List Of Internal Variables
#####

def GetIntVars():

    debuginfo = []
    for v in DebugVars:
            debuginfo.append(PadString(v, dINTVARWIDTH) + (str(eval(v)) or dNULL))

    debuginfo.sort()
    return debuginfo

# End of 'GetIntVars()'


#####
# Return List Of User-Settable Options
#####

def GetOptions():

    options = {}
    for l,f in ((UI.OptionsBoolean, True), (UI.OptionsNumeric, False), (UI.OptionsString, False)):
        for v in l:
            
            value = eval(v)
            # Translate Booleans into True/False strings
            if f:
                if value:
                    s = dTRUE
                else:
                    s = dFALSE

            # Translate all others into string representations
            else:
                s = str(value)

            options[v] = s
 
    return FormatMultiColumn(options, numcols=2)

# End of 'GetOptions()'


#####
# Return List Of User-Defined Variables
#####

def GetUserVbls():

    debuginfo = []
    for sym in UI.SymTable.keys():
        debuginfo.append(PadString(sym, dUSRVBLWIDTH) + UI.SymTable[sym])

    debuginfo.sort()
    return debuginfo


# End of 'GetUserVbls()'


#----------------------------------------------------------#
#                  Program Entry Point                     #
#----------------------------------------------------------#

#####
# Create an instance of the UI
#####

UIroot = Tk()
UI = twanderUI(UIroot)

# Make the Tk window the topmost in the Z stack.
# 'Gotta do this or Win32 will not return input
# focus to our program after a startup warning
# display.

UIroot.tkraise()

#####
# Setup global UI variables
#####

# Setup Built-In Variables
UI.BuiltIns = {DIR:"", DSELECTION:"", DSELECTIONS:"", HASH:"",
               MEM1:"", MEM2:"", MEM3:"", MEM4:"", MEM5:"", MEM6:"",
               MEM7:"", MEM8:"", MEM9:"", MEM10:"", MEM11:"", MEM12:"", 
               PROMPT:"", SELECTION:"", SELECTIONS:"", YESNO:""}

# Options (and their default values) which can be set in the configuration file

UI.OptionsBoolean = {"ACTUALLENGTH":ACTUALLENGTH,
                     "ADAPTREFRESH":ADAPTREFRESH,
                     "AFTERCLEAR":AFTERCLEAR,
                     "AUTOREFRESH":AUTOREFRESH,
                     "CMDMENUSORT":CMDMENUSORT,
                     "FORCEUNIXPATH":FORCEUNIXPATH,
                     "HIDEDOTFILES":HIDEDOTFILES,
                     "INVERTFILTER":INVERTFILTER,
                     "ISODATE":ISODATE,
                     "NODETAILS":NODETAILS,
                     "NONAVIGATE":NONAVIGATE,
                     "SORTREVERSE":SORTREVERSE,
                     "SORTSEPARATE":SORTSEPARATE,
                     "SYMDIR":SYMDIR,
                     "SYMEXPAND":SYMEXPAND,
                     "SYMRESOLV":SYMRESOLV,
                     "USETHREADS":USETHREADS,
                     "USEWIN32ALL":USEWIN32ALL,
                     "WARN":WARN,
                     "WILDNOCASE":WILDNOCASE,
                     }

UI.OptionsNumeric = {"AFTERWAIT":AFTERWAIT,"DEBUGLEVEL":DEBUGLEVEL, "FSZ":FSZ, "MFSZ":MFSZ, "HFSZ":HFSZ,
                     "HEIGHT":HEIGHT, "MAXMENU":MAXMENU, "MAXMENUBUF":MAXMENUBUF, "MAXNESTING":MAXNESTING,
                     "REFRESHINT":REFRESHINT, "SCALEPRECISION":SCALEPRECISION, "STARTX":STARTX, "STARTY":STARTY, "WIDTH":WIDTH}

UI.OptionsString  = {"BCOLOR":BCOLOR,   "FCOLOR":FCOLOR,   "FNAME":FNAME,   "FWT":FWT,    # Main Font/Colors
                     "MBCOLOR":MBCOLOR, "MFCOLOR":MFCOLOR, "MFNAME":MFNAME, "MFWT":MFWT,  # Menu Font/Colors
                     "HBCOLOR":HBCOLOR, "HFCOLOR":HFCOLOR, "HFNAME":HFNAME, "HFWT":HFWT,  # Help Font/Colors
                     "MBARCOL":MBARCOL, "QUOTECHAR":QUOTECHAR, "SORTBYFIELD":SORTBYFIELD, # Other
                     "STARTDIR":STARTDIR, "CMDSHELL":CMDSHELL, "DEFAULTSEP":DEFAULTSEP, "DOTFILE":DOTFILE} 

# Prepare storage for key bindings
UI.KeyBindings = {}


# Storage For Associations

UI.Associations = {ASSOCEXCL:[]}

# Initialize list of all directories visited
UI.AllDirs    = []

# Initialize directory stack
UI.LastDir    = []

# Initialize storage for last manually entered directory path
UI.LastPathEntered = ""

# Initialize storage for last manually entered Filter and Selection wildcards
UI.LastFiltWildcard = ""
UI.LastSelWildcard = ""

# Initialize storage for current location
UI.CurrentDir = ""

# Initialize storage for filtering wildcard
UI.FilterWildcard = ("None", None, None, False)

# Initialize various menu data structures
ClearHistory(None)

# Initialize Storage For Program Memories

UI.ProgMem = [[], [], [], [], [], [], [], [], [], [], [], []]

# Need mutex to serialize on widget updates
UI.DirListMutex = mutex.mutex()

# Intialize the "new dir via mouse" flag
UI.MouseNewDir = False

# Initialize the refresh timers
UI.LastRefresh    = 0

# Initialize storage for list of configuration files processed
UI.ConfigVisited = []

# Start in detailed mode
UI.SetDetailedView(True)


#####
# Command line processing - Options are set with the
# following priority scheme (lowest to highest):
#
#    1) Defaults coded into the program
#    2) Options set in the configuration file
#    3) Options set in the environment variable
#    4) Options set on the command line
#
#####

# Concatenate any environment variable with the
# command line so the command line takes precedence.

OPTIONS = sys.argv[1:]
envopt = os.getenv(PROGNAME.upper())
if envopt:
    OPTIONS = envopt.split() + OPTIONS

try:
    opts, args = getopt.getopt(OPTIONS, '-c:d:hqrtv')
except getopt.GetoptError:
    Usage()
    sys.exit(1)

# If the user wants help or version information, do this first
# so we don't bother with other options processing

for opt, val in opts:
    if opt == "-h":
        Usage()
        sys.exit(0)
    if opt == "-v":
        print RCSID
        sys.exit(0)

# Read configuration file before any other arguments.  This allows the
# environment variable and then the command line to override any
# settings in the configuration file.

for opt, val in opts:
    if opt == "-c":
        CONF = os.path.abspath(val)

# Parse the configuration file, but suppress options
# processing - on startup this is done just before
# we enter the main message loop to make sure we
# pickup any options changes from the environment
# variable or command line.

ProcessConfiguration(None, DoOptionsProcessing=False)

# Process the rest of the options, if any

for opt, val in opts:
    if opt == "-d":
        DEBUGLEVEL = val
        ValidateDebugLevel()

        # If we're going to be dumping debug info, print header
        if DEBUGLEVEL:
            print dHEADER % time.asctime()

    if opt == "-q":
        WARN = False
    if opt == "-r":
        AUTOREFRESH = False
    if opt == "-t":
        UI.OptionsString["QUOTECHAR"] = QUOTECHAR = ""
    if opt == "-x":
        WIDTH = val
    if opt == "-y":
        HEIGHT = val

# Figure out where to start - Environment/Command Line overrides config
# file STARTDIR option.  Program can only have 0 or 1 arguments.  Make
# sure any startdir argument is legit

if len(args) > 1:
    ErrMsg(eTOOMANY)
    sys.exit(1)

if len(args) == 1:
    STARTDIR = args[0]

    # Windows is sloppy about accepting both '//' and '\\'
    # so we have to condition the command line input for consistency.

    if OSPLATFORM == 'win32' and STARTDIR == '//':
        STARTDIR = SHOWDRIVES

    # Make sure any user request to start in a Drive List View
    # is possible.  If not, just start in the root directory.
    
    if STARTDIR == SHOWDRIVES and (OSPLATFORM != 'win32' or not GetWin32Drives()):
        STARTDIR = PSEP
        
    if not os.path.isdir(STARTDIR):
        ErrMsg(eBADROOT % STARTDIR)
        sys.exit(1)

    # Save this value as the default for STARTDIR
    UI.OptionsString["STARTDIR"] = STARTDIR

# Get starting directory into canonical form
STARTDIR = os.path.abspath(STARTDIR)

# Initialize the UI directory listing
LoadDirList(STARTDIR, updtitle = False)

# Process options to catch any changes detected in
# environment variable or command line

ProcessOptions()

# And start the periodic polling of the widget
UI.poll()

# Run the program interface
UIroot.mainloop()

