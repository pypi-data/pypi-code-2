########################################################################
#  Program:  pylinebreak
#  Author:  x.seeks (x.seeks@gmail.com)
#  Version:  0.10
#  Date:  2011-04-01
#  Description:  Formats text files without proper line breaks into
#  something a bit more pleasing to look at on a TTY / shell terminal.
########################################################################

import os
import sys
import textwrap
import re
import shutil
import platform



############ User-set variables ########################################

MARGIN = 80
BACKUPS = 1

########################################################################



platformname = platform.system()

########### COLORS


if platformname == "Windows":
    COLOR_BLACK = ''
    COLOR_RED =   ''
    COLOR_LG = ''
    COLOR_LC = ''
    COLOR_LB = ''
    COLOR_YELLOW = ''
    COLOR_DG = ''
    COLOR_PURPLE = ''
    COLOR_BROWN = ''
    COLOR_LP = ''
    
else:
    COLOR_BLACK = "\033[00m"
    COLOR_RED =   "\033[1;31m"
    COLOR_LG = "\033[1;32m"
    COLOR_LC = "\033[1;36m"
    COLOR_LB = "\033[1;34m"
    COLOR_BROWN="\033[0;33m"
    COLOR_YELLOW = "\033[1;33m"
    COLOR_DG = "\033[1;30m"
    COLOR_PURPLE = "\033[0;35m"
    COLOR_LP = "\033[1;35m"


def print_help():
    print "Usage:  pylinebreak [FILE1]... [FILE2]... [FILE3]..."
    print ''
    print COLOR_YELLOW+"Pylinebreak"+COLOR_BLACK+" is a simple, somewhat ugly program that will convert text that \nhasn't been formated for an 80-character margin to something that's a bit \neasier to read on a TTY / terminal shell / whatever."
    print ''
    print "If the program has been properly installed, type 'pylinebreak [FILE]'.\nIf it hasn't, it still works with 'python <path/to/pylinebreak.py> [FILE]'.\n"
    print "Files are saved to their current directory, and backups are automatically\ncreated with '.old' appended to their filenames.  You can also specify \nmultiple files on the command line, separated by spaces.  Example:\npylinebreak [FILE1] [FILE2] [FILE3]'.  Alternately, you can just wildcard (*)\nwhichever directory you'd like and every file in it will be converted.\n"
    print "Currently, command-line options aren't supported.  If you want to change the \nmargin or stop the program from creating backups ("+COLOR_RED+"not recommended"+COLOR_BLACK+"), \nyou can edit the source code - pylinebreak.py - easily enough."
    print ''
    print "Lastly, executing the program without any arguments will simply print this \nhelp text, as you have no doubt noticed.  Running the program with either the \n'--help' argument or the '-h' argument will do the same thing.\n\n"
    sys.exit()


def format_text(start_file):
    ###### Make a backup of the file
    if BACKUPS == 1:
        shutil.copy(start_file, start_file+'.old')
        print COLOR_YELLOW+"Creating a backup of '"+start_file+"'..."+COLOR_BLACK
    else:
        pass
    
    print ''
    print COLOR_YELLOW+"Linebreaking '"+start_file+"'..."+COLOR_BLACK
    ######## Open the file for reading
    text_file_read = open(start_file, 'r')


    ##### 'Convert' the file to a string
    text_string = text_file_read.read()
    
    ##### Close file, then open it for writing
    text_file_read.close()
    text_file = open(start_file, 'w')


    ###### Format the string properly with the textwrap module
    text_filled = textwrap.fill(text_string, replace_whitespace=False, width=MARGIN)

    ##### Replace three whitespaces with a double linebreak
    text_finished = re.sub('   ', '\n\n', text_filled)
    
    #### write to file
    text_file.write(text_finished)
    
    print ''
    print COLOR_LG+"All done with '"+start_file+"'!"+COLOR_BLACK
    print ''

    text_file.close()


#~ def main():
    #~ while running == 1:
        #~ print "Enter the path/name of the file you'd like to convert.  Absolute or \nrelative paths both work.\n\n"
        #~ print "You can also type 'h' for help or 'q' to quit."
        #~ user_input = raw_input("Select a file to convert:  ")
        #~ 
        #~ if user_input == 'q':
            #~ sys.exit()
        #~ elif user_input == 'h':
            #~ print_help()
        #~ else:
            #~ start_file = str(user_input)
            #~ 
            #~ try:
                #~ format_text(start_file)
            #~ except:
                #~ print "\nSorry, that didn't work.  Try again.\n"



if __name__ == '__main__':
    try:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print_help()
        else:
            for i in sys.argv[1:]:
                start_file_arg = i
                start_file = str(start_file_arg)
                format_text(start_file)
    except:
        if len(sys.argv[:]) == 1:
            print_help()
        else:
            pass
                
