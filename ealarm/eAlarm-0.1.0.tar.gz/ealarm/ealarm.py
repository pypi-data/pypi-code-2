################################################################################
#  Program:  eAlarm
#  Version: 1.0
#  Description:  Simple alarm that's run from the command line (no GUI)
#  Author:  x.seeks (x dot seeks at gmail dot com)
#  Requires:  Pyglet module, as well as libavbin (comes with pyglet in most
#cases, but not always if you're using GNU/Linux)
#  License:  GPLv3.  See LICENSE.txt for more info.
################################################################################

import time, sys, os, pickle, re, platform, shutil

try:
    import pyglet
except ImportError:
    print ''
    print ''
    print "!!!!  ----  ERROR  ----  !!!!"
    print ''
    print ''
    print "Can't import module 'pyglet'.  Make sure you have it installed."
    print ''
    print "You can find it online at http://pyglet.org"
    print ''
    print "Or, if you're running GNU/Linux, you can usually find it in your"
    print "distro's repositories.  To install in Ubuntu, type:"
    print ''
    print "sudo apt-get install python-pyglet"
    print ''
    print "You'll also want to install AVbin.  If you're using Windows, it"
    print "comes with the Pyglet installer.  Otherwise, you can find it at:"
    print ''
    print "http://code.google.com/p/avbin"
    print ''
    print "If you're using GNU/Linux, you can get it from the above site, or"
    print "install it from your distro's repo.  In Ubuntu, you would type:"
    print ''
    print "'sudo apt-get install libavbin0'"
    print ''
    print '[PyAlarm will not function without Pyglet.  Aborting.]'
    sys.exit()
            


platformname = platform.system()
release = platform.release()


restart_list = []
restart_list.append('-1')
def restart():
    '''
    Function that restarts the main loop, in a somewhat convoluted way.
    '''
    sys.exit(main())
    x = restart_list.pop()
    x *= -1
    restart_list.append(x)

def error_restart():
    '''
    This restarts the program, while letting the user know that their input was incorrect by making them press a key to acknowledge the prompt.
    '''
    print '\n\n'
    try:
        ui = raw_input('ERROR:  Incorrect input.  Returning to main menu.')
        if ui == 'q' or ui == 'Q' or ui == 'QUIT' or ui == 'quit':
            bye()
        else:
            restart()
    except KeyboardInterrupt:
        bye()

def bye():
    '''
    A quit function, basically.  Slightly less rude formatting that just a bare-bones sys.exit().
    '''
    print ''
    print 'Quitting.'
    print ''
    sys.exit()


def reg_time(hour, minute, second):
    '''
    The purpose of this function is simply to create a string that displays the time in proper 24-hour format, down to the second (12:00:00).
    '''
    hour = str(hour)
    minute = str(minute)
    second = str(second)
    new_hour = '0'
    new_minute = '0'
    new_second = '0'

    if len(hour) < 2:
        new_hour += hour
    else:
        new_hour = hour
    if len(minute) < 2:
        new_minute += minute
    else:
        new_minute = minute
    if len(second) < 2:
        new_second += second
    else:
        new_second = second

    reg_time = '%s:%s:%s' % (new_hour, new_minute, new_second)

    return reg_time

def nice_time(hour, minute, second):
    '''
    This function creates a string that displays the time in a more conventionally-worded 12-hour format.
    '''
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    ampm = ''
    if hour > 24:
        hour = 24
    elif hour < 0:
       hour = 0
    if minute < 0:
        minute = 0
    elif minute > 60:
        minute = 60
    if second < 0:
        second = 0
    elif second > 60:
        second = 60
    if hour >= 13:
        hour -= 12
        ampm += 'PM'
    elif hour == 00:
        hour += 12
        ampm += 'Midnight'
    elif hour == 12:
        ampm += 'Noon'
    else:
        ampm += 'AM'
    if second == 0:
        if minute == 0:
            nice_time = '%d %s' % (hour, ampm)
        else:
            nice_time = '%d:%d %s' % (hour, minute, ampm)
    else:
        nice_time = '%d:%d %s, %d seconds.' % (hour, minute, ampm, second)
    return nice_time





def noon_midnight(ui):
    '''
    This function sets the time correctly if the user has decided to type 'noon' or 'midnight' into a time-setting promp, or at the command-line.
    '''
    if ui == 'noon':
        set_hour = 12
        set_minute = 00
        set_second = 00
    elif ui == 'midnight':
        set_hour = 00
        set_minute = 00
        set_second = 00
    return set_hour, set_minute, set_second


def am_or_pm(new_time_str):
    '''
    This checks to see if the user typed 'am' or 'pm' at the end of their input, and strips the characters if they did.  It then returns new_time_str to parse_time, as well as letting parse_time know which (if either) was included by returning the 'ampm' string.
    '''
    ampm = ''
    am = ('am', 'AM', 'a', 'A')
    pm = ('pm', 'PM', 'p', 'P')
    for i in am:
        if i in new_time_str:
            new_time_str = re.sub(i,'',new_time_str,0)
            ampm += 'am'
            return new_time_str, ampm
    for i in pm:
        if i in new_time_str:
            new_time_str = re.sub(i,'',new_time_str,0)
            ampm += 'pm'
            return new_time_str, ampm
    return new_time_str, ampm

def strip_whitespaces(new_time_str):
    '''
    This function simply removes all whitespace (empty spaces) from new_time_str, and returns it to parse_time.
    '''
    new_time_str2 = ''
    if ' ' in new_time_str:
        new_time_str = re.sub(' ','',new_time_str,0)
    for i in new_time_str:
        if i == ' ':
            pass
        if i == '':
            pass
        else:
            new_time_str2 += i
    return new_time_str2

def strip_separators(new_time_str):
    '''
    This checks for the presence of separator characters in the user's time input, and removes them if they exist.  It then returns new_time_str to parse_time.
    '''
    separators = (':','-','/',';',)
    for i in separators:
        if i in new_time_str:
            new_time_str = re.sub(i,'',new_time_str,0)
    if r'.' in new_time_str:
        new_time_str = re.sub(r'\.','',new_time_str,0)
    if r',' in new_time_str:
        new_time_str = re.sub(r'\,','',new_time_str,0)
    return new_time_str


def calc_pm(new_time_hour):
    '''
    If the user included 'pm' at the end of their input, this converts their input to 24-hour format.
    '''
    if new_time_hour == '12':
        return new_time_hour
    new_time_hour_int = int(new_time_hour)
    new_time_hour_int += 12
    new_time_hour = str(new_time_hour_int)
    return new_time_hour

def calc_am(new_time_hour):
    '''
    If the user included 'am' at the end of their input, this function converts their input to the proper 24-hour formatting.
    '''
    if new_time_hour == '12':
        new_time_hour = '00'
        return new_time_hour
    return new_time_hour


def parse_time(new_time_str):
    '''
    This is the master time parsing function.  Not only does it call various other parsing functions, it also calculates which time to set based both on the actual input and the length of said input.  The calculations are just my own best guesses as to what a person means when they enter something.
    '''
    new_time_hour = ''
    new_time_minute = ''
    new_time_second = ''
    last_chance_midnight_list = ['midnight','MIDNIGHT','midnite','MIDNITE']
    last_chance_noon_list = ['noon', 'NOON']
    new_time_str = strip_whitespaces(new_time_str)
    new_time_str = strip_separators(new_time_str)
    new_time_str, ampm = am_or_pm(new_time_str)
    if new_time_str in last_chance_midnight_list:
        new_time_hour += '00'
        new_time_minute += '00'
        new_time_second += '00'
        return new_time_hour, new_time_minute, new_time_second
    if new_time_str in last_chance_noon_list:
        new_time_hour += '12'
        new_time_minute += '00'
        new_time_second += '00'
        return new_time_hour, new_time_minute, new_time_second
    if len(new_time_str) == 1:
        new_time_hour += new_time_str
        new_time_minute += '00'
        new_time_second += '00'
    elif len(new_time_str) == 2:
        new_time_hour += new_time_str
        if int(new_time_hour) > 24:
            new_time_hour2 = new_time_hour
            new_time_hour = ''
            new_time_hour += new_time_hour2[0]
            new_time_minute += new_time_hour2[1]
            new_time_second = '00'
        else:
            new_time_minute += '00'
            new_time_second += '00'
    elif len(new_time_str) == 3:
        new_time_hour += new_time_str[0]
        new_time_minute += new_time_str[1:]
        new_time_second += '00'
    elif len(new_time_str) == 4:
        new_time_hour += new_time_str[0:2]
        new_time_minute += new_time_str[2:]
        new_time_second += '00'
    elif len(new_time_str) == 5:
        new_time_hour += new_time_str[0]
        new_time_minute += new_time_str[1:3]
        new_time_second += new_time_str[3:]
    elif len(new_time_str) == 6:
        new_time_hour += new_time_str[0:2]
        new_time_minute += new_time_str[2:4]
        new_time_second += new_time_str[4:]
    elif len(new_time_str) == 7:
        new_time_hour += new_time_str[0:2]
        new_time_minute += new_time_str[2:4]
        new_time_second += new_time_str[4:6]
    else:
        print ''
        print 'Should not see this', new_time_str
        error_restart()
    if ampm == 'pm':
        new_time_hour = calc_pm(new_time_hour)
    elif ampm == 'am':
        new_time_hour = calc_am(new_time_hour)

    new_time_hour = int(new_time_hour)
    new_time_minute = int(new_time_minute)
    new_time_second = int(new_time_second)

    return new_time_hour, new_time_minute, new_time_second



def return_six_characters(cfg_time_str):
    '''
    This function exists only because the re module won't properly strip all whitespaces in all instances, evidentally.  I'm 'manually' creating a new string strictly from the first <= 6 characters of the input string, and then returning it.
    '''
    new_cfg_time_str = ''
    midnight_list = ['midnight', 'MIDNIGHT', 'midnite','MIDNITE']
    noon_list = ['noon', 'NOON']
    if cfg_time_str in midnight_list:
        new_cfg_time_str += '000000'
        return new_cfg_time_str
    elif cfg_time_str in noon_list:
        new_cfg_time_str += '120000'
        return new_cfg_time_str
    else:
        for i in cfg_time_str[:-1]:
            new_cfg_time_str += i
        return new_cfg_time_str
        

def txt_to_tup(read_cfg):
    '''
    This function, which has clearly gotten out of hand, creates a tuple of correct time values from certain strings in the cfg file (text file).  In essence, it makes the strings ripped from the text file usable.
    '''
    preset_list = []
    current_0 = ''
    sound_0 = ''
    skip_0 = ''
    for i in read_cfg:
        if 'CURRENT_TIME' in i:
            current_0 += i
        if 'SOUND_FILE' in i:
            sound_0 += i
        if 'SKIP_WARNINGS' in i:
            skip_0 += i
    for i in range(10):
        for x in read_cfg:
            if 'PRESET_%d' % i in x:
                preset_list.append(x)
    current_a = re.sub('CURRENT_TIME','',current_0,0)
    current_b = re.sub('=','',current_a,0)
    sound_a = re.sub('SOUND_FILE','',sound_0,0)
    sound_b = re.sub('=','',sound_a,0)
    sound_c = re.sub('\n','',sound_b,0)
    sound_d = re.sub(' ','',sound_c, 0)
    skip_a = re.sub('SKIP_WARNINGS','',skip_0,0)
    skip_b = re.sub('=','',skip_a,0)
    skip_c = re.sub('\n','',skip_b,0)
    skip_d = re.sub(' ','',skip_c,0)

    preset1_a = re.sub('PRESET_1','',preset_list[0],0)
    preset2_a = re.sub('PRESET_2','',preset_list[1],0)
    preset3_a = re.sub('PRESET_3','',preset_list[2],0)
    preset4_a = re.sub('PRESET_4','',preset_list[3],0)
    preset5_a = re.sub('PRESET_5','',preset_list[4],0)
    preset6_a = re.sub('PRESET_6','',preset_list[5],0)
    preset7_a = re.sub('PRESET_7','',preset_list[6],0)
    preset8_a = re.sub('PRESET_8','',preset_list[7],0)
    preset9_a = re.sub('PRESET_9','',preset_list[8],0)
    preset1_b = re.sub('=','',preset1_a,0)
    preset2_b = re.sub('=','',preset2_a,0)
    preset3_b = re.sub('=','',preset3_a,0)
    preset4_b = re.sub('=','',preset4_a,0)
    preset5_b = re.sub('=','',preset5_a,0)
    preset6_b = re.sub('=','',preset6_a,0)
    preset7_b = re.sub('=','',preset7_a,0)
    preset8_b = re.sub('=','',preset8_a,0)
    preset9_b = re.sub('=','',preset9_a,0)

    current_c = return_six_characters(current_b)
    preset1_c = return_six_characters(preset1_b)
    preset2_c = return_six_characters(preset2_b)
    preset3_c = return_six_characters(preset3_b)
    preset4_c = return_six_characters(preset4_b)
    preset5_c = return_six_characters(preset5_b)
    preset6_c = return_six_characters(preset6_b)
    preset7_c = return_six_characters(preset7_b)
    preset8_c = return_six_characters(preset8_b)
    preset9_c = return_six_characters(preset9_b)

    


    current = parse_time(current_c)
    preset1 = parse_time(preset1_c)
    preset2 = parse_time(preset2_c)
    preset3 = parse_time(preset3_c)
    preset4 = parse_time(preset4_c)
    preset5 = parse_time(preset5_c)
    preset6 = parse_time(preset6_c)
    preset7 = parse_time(preset7_c)
    preset8 = parse_time(preset8_c)
    preset9 = parse_time(preset9_c)
    sound = sound_d
    skip = skip_d

    return current, preset1, preset2, preset3, preset4, preset5, preset6, preset7, preset8, preset9, sound, skip


def create_cfg(ealarm_dir):
    '''
    This function creates a default configuration (cfg) file, which is plain text that is designed to be easily modified by the user.  This is only called if the cfg file doesn't yet exist.
    '''
    sound_file_path = ealarm_dir + 'ring.wav'
    cfg_default_txt = '''####### CONFIG FILE FOR PYALARM
####### If you alter this, change only the values.
####### Changing the variable names, etc. will screw things up.

## Skip the AVbin warning (if necessary).  Valid values are 'yes' or 'no'.
SKIP_WARNINGS = no

## The sound file.  This is an absolute path to the sound file.
SOUND_FILE = %s


##### TIMES
##### All of the following times can be entered in various ways, but the most
##### common ways (24-hour format or 'standard' format) are best.  For instance,
##### 1600, 16, 16:00, 16:00:00, 4:00pm and 4 PM are all valid examples.

## The time that the alarm is currently set to.
CURRENT_TIME = 12:00:00

## The preset times, 1-9
PRESET_1 = 12:00:00
PRESET_2 = 12:00:00
PRESET_3 = 12:00:00
PRESET_4 = 12:00:00
PRESET_5 = 12:00:00
PRESET_6 = 12:00:00
PRESET_7 = 12:00:00
PRESET_8 = 12:00:00
PRESET_9 = 12:00:00''' % sound_file_path
    cfg_file = open('ealarm.cfg', 'w')
    cfg_file.write(cfg_default_txt)
    cfg_file.close()

def write_cfg(cfg):
    '''
    This function writes the cfg file to disk.  First it creates a cfg string, plugging in the correct values (taken from the cfg dictionary object) in their appropriate spots as it does so.  Then it opens the cfg file, writes to it, then closes it.
    '''
    skip_warnings = cfg.get('skip_warnings')
    sound_file = cfg.get('sound_file')
    current = cfg.get('current')
    current_r_time = reg_time(current[0],current[1],current[2])
    current = current_r_time
    preset1 = cfg.get('preset1')
    preset1_r_time = reg_time(preset1[0],preset1[1],preset1[2])
    preset1 = preset1_r_time
    preset2 = cfg.get('preset2')
    preset2_r_time = reg_time(preset2[0],preset2[1],preset2[2])
    preset2 = preset2_r_time
    preset3 = cfg.get('preset3')
    preset3_r_time = reg_time(preset3[0],preset3[1],preset3[2])
    preset3 = preset3_r_time
    preset4 = cfg.get('preset4')
    preset4_r_time = reg_time(preset4[0],preset4[1],preset4[2])
    preset4 = preset4_r_time
    preset5 = cfg.get('preset5')
    preset5_r_time = reg_time(preset5[0],preset5[1],preset5[2])
    preset5 = preset5_r_time
    preset6 = cfg.get('preset6')
    preset6_r_time = reg_time(preset6[0],preset6[1],preset6[2])
    preset6 = preset6_r_time
    preset7 = cfg.get('preset7')
    preset7_r_time = reg_time(preset7[0],preset7[1],preset7[2])
    preset7 = preset7_r_time
    preset8 = cfg.get('preset8')
    preset8_r_time = reg_time(preset8[0],preset8[1],preset8[2])
    preset8 = preset8_r_time
    preset9 = cfg.get('preset9')
    preset9_r_time = reg_time(preset9[0],preset9[1],preset9[2])
    preset9 = preset9_r_time

    cfg_txt = '''####### CONFIG FILE FOR PYALARM
####### If you alter this, change only the values.
####### Changing the variable names, etc. will screw things up.

## Skip the AVbin warning (if necessary).  Valid values are 'yes' or 'no'.
SKIP_WARNINGS = %s

## The sound file.  This is an absolute path to the sound file.
SOUND_FILE = %s


##### TIMES
##### All of the following times can be entered in various ways, but the most
##### common ways (24-hour format or 'standard' format) are best.  For instance,
##### 1600, 16, 16:00, 16:00:00, 4:00pm and 4 PM are all valid examples.

## The time that the alarm is currently set to.
CURRENT_TIME = %s

## The preset times, 1-9
PRESET_1 = %s
PRESET_2 = %s
PRESET_3 = %s
PRESET_4 = %s
PRESET_5 = %s
PRESET_6 = %s
PRESET_7 = %s
PRESET_8 = %s
PRESET_9 = %s''' % (skip_warnings, sound_file, current, preset1, preset2,
        preset3, preset4, preset5, preset6, preset7, preset8, preset9)

    cfg_file = open('ealarm.cfg', 'w')
    cfg_file.write(cfg_txt)
    cfg_file.close()

def read_cfg():
    '''
    This function opens the cfg file, reads the lines from it, and calls the txt_to_tup function to convert the information into a useable format.  It then plugs the returned values into the cfg dict object, which is used throughout the program.  After that, it returns it.
    '''
    cfg_file = open('ealarm.cfg', 'r')
    cfg_read = cfg_file.readlines()
    cfg_file.close()
    (current, preset1, preset2, preset3, preset4, preset5, preset6, preset7,
            preset8, preset9, sound_file, skip_warnings) = txt_to_tup(cfg_read)
    cfg = {'current':current,'preset1':preset1,'preset2':preset2,
            'preset3':preset3,'preset4':preset4,'preset5':preset5,
            'preset6':preset6,'preset7':preset7,'preset8':preset8,
            'preset9':preset9,'sound_file':sound_file,
            'skip_warnings':skip_warnings}
    return cfg


def avbin_warning(cfg):
    '''
    This function displays a warning that AVbin couldn't be found on the user's computer.  It also gives them the choice to skip this warning in the future if they so desire... for instance, if they're on a Windows machine on which the program might not correctly detect the file, even if it does exist and function properly.
    '''
    print ''
    print ' !!!! ------ Warning ------- !!!! '
    print ''
    print "It doesn't look like you've got AVbin installed.  While PyAlarm"
    print "might still function without it, it is highly recommended that you"
    print "install it as soon as possible.  It's basically a necessity."
    print ''
    print "To find avbin, head to the project's page at:"
    print ''
    print 'http://code.google.com/p/avbin'
    print ''
    print 'In Windows:'
    print '    Just follow the instructions.  What they boil down to'
    print "is 1) Open the downloaded .zip file, and 2) Drag avbin.dll to your"
    print "C:\\Windows\\System32 directory.  Also note that on some versions of Windows,"
    print "Python might have difficulty reporting avbin.dll even if it's"
    print "there.  If that's the case for you, just choose to skip this message henceforth."
    print ''
    print "In GNU/Linux:"
    print "    You should really use your distribution's package manager for"
    print "this.  In Ubuntu, type 'sudo apt-get install libavbin0'."
    print "Failing that, you can download the source code from the website."
    print ''
    print '------------------------------'
    ui = raw_input('ENTER to continue, Q to quit, or S to skip this warning in the future:  ')
    if ui == 'q' or ui == 'Q' or ui == 'quit' or ui == 'QUIT':
        bye()
    elif ui == 's' or ui == 'S' or ui == 'skip' or ui == 'SKIP':
        print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
        print "Okay, we'll skip this warning from now on."
        print '\n\n\n\n\n'
        print '----------------------------'
        ui2 = raw_input("Press ENTER to continue, or 'Q' to quit/abort.")
        if ui2 == 'q' or ui2 == 'Q' or ui2 == 'quit' or ui2 == 'QUIT':
            bye()
        else:
            print ''
            cfg['skip_warnings'] = 'yes'
            write_cfg(cfg)
            pass
    else:
        pass



def check_for_avbin(cfg):
    '''
    This function checks for the presence of AVbin on the user's computer.  If it doesn't find it, it calls the avbin_warning function.
    '''
    if cfg.get('skip_warnings') == 'yes':
        return 0
    elif cfg.get('skip_warnings') == 'no':
        if platformname == 'Windows':
            if 'avbin.dll' in os.listdir("C:\\Windows\\System32"):
                return 0
            else:
                avbin_warning(cfg)
                return 0
        else:
            if 'libavbin.so' in os.listdir('/usr/lib'):
                return 0
            else:
                avbin_warning(cfg)
                return 0


def print_help():
    '''
    This is called by either the help_screen function or directly from the command-line.  It just prints some help info.
    '''
    print ''
    print '==================================================================='
    print '                            HELP'
    print '==================================================================='
    print ''
    print 'There are three ways to set the the time:  The first is to use the'
    print 'previously used setting by simply pressing ENTER.  Secondly, you can'
    print "set custom times (current time or presets) by typing 'S' or 'SET'."
    print "You can also test ealarm's (pyglet's) ringer function by typing 'T'"
    print "Lastly, you can enter a number (1-9) to simply select a preset time."
    print ''
    print "You can also use this program straight from the command line with"
    print "arguments, rather than running it 'standalone'.  To do so, at the"
    print "command-line simply type 'python ealarm.py <arg>'.  <arg> can be"
    print "a time, as well as 'help', 'version', 'about', or 'test'."
    print ''
    print "Some example include 'python ealarm.py 1300', 'python ealarm.py -h',"
    print "'python ealarm.py V', 'python ealarm.py 10am', and 'python ealarm.py --test."
    print '\n'
    print '''NOTE:  Times are displayed in both 'standard' and 24-hour format.  For exmaple,'''
    print "06:00 is 6AM, while 13:00 is 1PM, 00:00 is midnight, etc."
    print ''

def help_screen():
    '''
    An interactive (meaning, there is a prompt) help screen.
    '''
    print_help()
    print '-----------------------------------'
    try:
        user_input = raw_input("Press ENTER to go back, or input 'Q' to quit:  ")
        if user_input == 'q' or user_input == 'Q' or user_input == 'quit' or user_input == 'QUIT':
            bye()
        elif user_input == '':
            restart()
        else:
            restart()
    except KeyboardInterrupt:
        bye()


def print_about():
    '''
    This function prints the 'about' text.
    '''
    print ''
    print '==================================================================='
    print '                          ABOUT'
    print '==================================================================='
    print ''
    print ''
    print '''PyAlarm is, as the name might well have led you to believe, a simple CLI-based \nalarm-clock.  I wrote it because the other, much more fully-featured alarm \napplication that I had used kept crashing on me, which is bad news bears for \npeople that need to be woken up reliably.  I also wanted something that's very \nquick to shut up, and CTRL-C is much simpler than navigating a GUI to find a \nbutton that stops the alarm.



AUTHOR:  x dot seeks at gmail dot com
VERSION:  0.9
LICENSE:  GPLv3.  See License.txt for more information.
REQUIREMENTS:  Python (2.6, 2.7), the Pyglet module, and AVbin.  You can find
these at python.org, pyglet.org and code.google.com/p/avbin, respectively.'''
    print ''
    print ''

def about_screen():
    '''
    Interactive 'about' screen that calls print_about.
    '''
    print_about()
    print '-----------------------------------'
    try:
        user_input = raw_input("Press ENTER to go back, or input 'Q' to quit:  ")
        if user_input == 'q' or user_input == 'Q' or user_input == 'quit' or user_input == 'QUIT':
            bye()
        elif user_input == '':
            restart()
        else:
            restart()
    except KeyboardInterrupt:
        bye()

def sound_file_test(ealarm_dir):
    '''
    This function tests for the existence of the sound file in two locations:  The proper ealarm directory, and whichever directory the ealarm.py file is being run from if the former fails.  If the former fails but the latter succeeds, this function attempts to copy the sound file to the ealarm directory.  If that  fails, so does the program.
    '''
    try:
        sound_file = open(ealarm_dir+'ring.wav', 'r')
        sound_file.close()
        return 0
    except IOError:
        try:
            sound_file = open('ring.wav', 'r')
            print os.getcwd()
            shutil.copy('ring.wav', ealarm_dir)
            return 0
        except IOError:
            try:
                shutil.copy('/usr/local/share/ealarm/ring.wav', ealarm_dir)
                return 0
            except IOError:
                print '\n\n'
                print 'ERROR:'
                print ''
                print ''' Please ensure that the sound file (ring.wav by default) is in the \n ealarm directory.'''
                print ''
                print "The ealarm directory is located at:"
                print "GNU/Linux:  ~/.pylarm"
                print "Windows:  Documents/ealarm or My Documents/ealarm"
                print ''
                print 'Exiting.'
                bye()





def create_ealarm_dir():
    '''
    This function tests for the existence of the ealarm directory, and if it does not exist, creates it.  The directory location differs slightly depending on OS.
    '''
    if platformname == 'Windows':
        if release == 'XP' or release == 'NT':
            ealarm_dir = os.path.expanduser('~\\My Documents\\ealarm\\')
        else:
            ealarm_dir = os.path.expanduser('~\\Documents\\ealarm\\')
    else:
        ealarm_dir = os.path.expanduser('~/.ealarm/')
    try:
        os.listdir(ealarm_dir)
    except OSError:
        try:
            os.mkdir(ealarm_dir)
        except OSError:
            print ''
            print "Program doesn't have the necessary permissions.  Aborting."
            print ''
            bye()
    return ealarm_dir


def setup():
    '''
    This is the 'master' setup function.  It calls all the other various setup functions that allow for proper functioning of the program, as well as gathering and creating various 'objects', which will be used frequently throughout the program.
    '''
    ealarm_dir = create_ealarm_dir()
    sound_file_test(ealarm_dir)
    try:
        os.chdir(ealarm_dir)
    except OSError:
        print ''
        print "Program doesn't have the necessary permissions.  Aborting."
        print ''
        bye()
    try:
        cfg = read_cfg()
    except IOError:
        create_cfg(ealarm_dir)
        cfg = read_cfg()
    check_for_avbin(cfg)
    sound_file = cfg.get('sound_file')
    set_hour = cfg.get('current')[0]
    set_minute = cfg.get('current')[1]
    set_second = cfg.get('current')[2]
    return set_hour, set_minute, set_second, sound_file, cfg

def ring(sound_file):
    '''
    This function lets pyglet do its magic, creating a 'sound player' that loops whenever the sound object that's loaded is finished playing.
    '''
    os.chdir(os.path.dirname(sound_file))
    sound = os.path.basename(sound_file)
    ringplayer = pyglet.media.Player()
    ring = pyglet.media.load(sound)
    ringplayer.queue(ring)
    ringplayer.eos_action = pyglet.media.Player.EOS_LOOP
    ringplayer.play()
    pyglet.app.run()



        

def set_time_func(cfg, p_choice):
    '''
    This function is a bit unwieldy, I'll admit.  It does a few things.  First, it displays the basic information needed by a person who wants to change a time... i.e., what format to use, etc.  Depending on whether or not they chose a preset in set_time (p_choice), it changes either the current time or whichever preset they chose.

    It does this by taking their input and converting it to a string, and sending that string (new_time_str) to parse_time.  Three values are returned from that function, namely new_time_hour, new_time_minute, and new_time_second.  These are then converted to integers (set_hour, set_minute, set_second) and those integers are put into a tuple (new_time).

    That tuple is then stored as the cfg object's new 'current' value, as well as its preset value for whichever preset the user chose, if indeed they chose one at all.  The cfg object is then saved to disk, and four values are retuned to set_time:  set_hour, set_minute, set_second, and cfg.
    '''
    print ''
    if p_choice == '':
        print ''
        print '==============================================================='
        print '               CHANGING CURRENT TIME'
        print '==============================================================='
        print ''
    else:
        print ''
        print '==============================================================='
        print '               CHANGING', p_choice.upper()[0:6],p_choice[6]
        print '==============================================================='
        print ''
    print ''
    print "To set a new time for you alarm, simply type it in using the 24-hour"
    print "('military') format.  Examples:"
    print ''
    print '13:00:00, 13:00, 13, 06.30.00, 06.30, 6, etc.'
    print ""
    print "You can also add 'AM' or 'PM' to the end of your string if you're"
    print "uncomfortable with time in 24-hour format.  Examples:"
    print ''
    print "12:30AM, 1pm, 4.45am, 550p, 6:30:25PM, etc."
    print ''
    print "Enter the time using as many as six digits, using numbers or"
    print "numbers separated by colons (:) or periods (.).  Examples:"
    print "14:30:00 (2:30 PM), 01:45:00 (1:45 AM), 00:00:00 (Midnight), etc."
    print "14:30 or 01:45 would also work, as would 1430, 0145, or 145."
    print ''
    if p_choice == '':
        current_time = cfg.get('current')
        ch = current_time[0]
        cm = current_time[1]
        cs = current_time[2]
        r_time = reg_time(ch, cm, cs)
        n_time = nice_time(ch, cm, cs)
        print 'The time is currently set to:  %s (%s)' % (r_time, n_time)
        print ''
    elif p_choice in range(9):
        preset_time = cfg.get(p_choice)
        ph = preset_time[0]
        pm = preset_time[1]
        ps = preset_time[2]
        r_time = reg_time(ph, pm, ps)
        n_time = nice_time(ph, pm, ps)
        print p_choice, ' is currently set to:  %s (%s)' % (r_time, n_time)
        print ''
    print '------------------------------------------'
    ui = raw_input("Enter the new time:  ")
    new_time_str = str(ui)
    if ui == 'noon' or ui == 'NOON' or ui == 'n' or ui == 'N':
        ui = 'noon'
        new_time_hour, new_time_minute, new_time_second = noon_midnight(ui)
    elif ui == 'midnight' or ui == 'MIDNIGHT' or ui == 'midnite' or ui == 'MIDNITE' or ui == 'm' or ui == 'm':
        ui = 'midnight'
        new_time_hour, new_time_minute, new_time_second = noon_midnight(ui)
    else:
        new_time_hour, new_time_minute, new_time_second = parse_time(new_time_str)
    try:
        set_hour = int(new_time_hour)
    except ValueError:
        print "ERROR:  Numbers only.  Exiting."
        bye()
    try:
        set_minute = int(new_time_minute)
    except ValueError:
        print "ERROR:  Numbers only.  Exiting."
        bye()
    try:
        set_second = int(new_time_second)
    except ValueError:
        print "ERROR:  Numbers only.  Exiting."
        bye()
    new_time = (set_hour, set_minute, set_second)
    cfg['current'] = new_time
    if p_choice != '':
        cfg[p_choice] = new_time

    write_cfg(cfg)

    return set_hour, set_minute, set_second, cfg



def set_time(cfg):
    '''
    This function displays the initial 'set time' screen.  It prints out a list of preset times, as well as the current time.  It sends the user's input to set_time_func, be it one of the presets or nothing at all  - in which case, the user will only change the current time.
    '''
    print ''
    print '==================================================================='
    print '                   SET NEW TIME'
    print '==================================================================='
    print ''
    print "To change a preset time, enter 1-9 for whichever preset you'd like to change."
    print ''
    print "Otherwise, just press enter to change the current time."
    print ''
    print 'Current preset times are as follows:  '
    print ''
    for i in range(9):
        preset_num = i+1
        preset_num_str = str(preset_num)
        preset_str = 'preset'+preset_num_str
        preset_hour = cfg.get(preset_str)[0]
        preset_minute = cfg.get(preset_str)[1]
        preset_second = cfg.get(preset_str)[2]
        n_time = nice_time(preset_hour, preset_minute, preset_second)
        r_time = reg_time(preset_hour, preset_minute, preset_second)
        print 'PRESET %d  ----  %s (%s)' % (preset_num, r_time, n_time) 
    print ''
    ch = cfg.get('current')[0]
    cm = cfg.get('current')[1]
    cs = cfg.get('current')[2]
    cr_time = reg_time(ch, cm, cs)
    cn_time = nice_time(ch, cm, cs)
    print 'The CURRENT time is:  %s (%s)' % (cr_time, cn_time)
    print ''
    print '---------------------------'
    user_input = raw_input('Input command (1-9 or ENTER):  ')
    try:
        user_input = int(user_input)
        if int(user_input) > 0 and int(user_input) < 10:
            ui = str(user_input)
            p_choice = 'preset' + ui
            set_hour, set_minute, set_second, cfg = set_time_func(cfg, p_choice)
    except ValueError:
        if user_input == '' or user_input == 'c' or user_input == 'C' or user_input == 'current' or user_input == 'CURRENT':
            p_choice = ''
            set_hour, set_minute, set_second, cfg = set_time_func(cfg, p_choice)
        elif user_input == 'q' or user_input == 'Q' or user_input == 'quit' or user_input == 'QUIT' or user_input == 'exit' or user_input == 'EXIT':
            bye()
        else:
            print "Press ENTER, input 1-9, or enter 'q' to quit."
    try:
        return set_hour, set_minute, set_second, cfg
    except UnboundLocalError:
        error_restart()


def message(set_hour, set_minute, set_second):
    '''
    This prints a short message to the screen after the user's committed him-or-herself to starting the alarm.  It's a reminder of what time the alarm will ring.
    '''
    print '\n\n\n\n\n\n\n'
    print '               ==============================================='
    print '            --------------     ALARM IS ACTIVE    ---------------'
    print '               ==============================================='
    r_time = reg_time(set_hour, set_minute, set_second)
    n_time = nice_time(set_hour, set_minute, set_second)
    print '\n\n\n\n\n\n'
    print "                     Alarm is set to:  %s (%s)" % (r_time, n_time)
    print '\n\n'
    print "                            Use CTRL-C to exit."


def alarm_test(sound_file):
    '''
    This is a test alarm function, which allows the user to see whether or not the alarm (pyglet) will function properly on their system.
    '''
    print '\n\n\n\n\n\n\n'
    print '               ==============================================='
    print '            ------------    TEST ALARM IS ACTIVE    ------------'
    print '               ==============================================='
    print '\n\n\n\n\n\n'
    print "                 It should ring in approximately 5 seconds."
    print '\n\n'
    print "                            Use CTRL-C to exit."
    set_hour = time.localtime()[3]
    set_minute = time.localtime()[4]
    set_second = time.localtime()[5]
    set_second += 03
    while True:
        try:
            if set_hour == time.localtime()[3]:
                if set_minute == time.localtime()[4]:
                    if set_second <= time.localtime()[5]:
                        ring(sound_file)
            time.sleep(1)
        except KeyboardInterrupt:
            bye()


def alarm(set_hour, set_minute, set_second, sound_file, cfg):
    '''
    This is the actual alarm function.  Every second (roughly), it checks the set time against the computer's clock (time.localtime).  When they match, it starts ringing (the ring() function).

    Before that, it also stores all of the set_time objects into the cfg dict object, which is again written to disk.
    '''
    new_time = (set_hour, set_minute, set_second)
    cfg['current'] = new_time
    write_cfg(cfg)
    while True:
        try:
            if set_hour == time.localtime()[3]:
                if set_minute == time.localtime()[4]:
                    if set_second <= time.localtime()[5]:
                        ring(sound_file)
            time.sleep(1)
        except KeyboardInterrupt:
            bye()


def get_input(sound_file, cfg):
    '''
    This is the main interactive menu.  From here, the user can navigate to the 'help' menu, the 'about' menu and the 'set time' menu.  They can also quit the program, or simply hit the enter key to use the most recently used settings.

    Depending on the user's input, it may also spit up an error or two.
    '''
    print '==================================================================='
    print '                           PyAlarm'
    print '==================================================================='
    print ''
    print "[S] to SET the current time, or to set a preset time.  [T] to TEST the alarm."
    print "[H] for help, [A] for information about this program, [Q] to QUIT."
    print "[1-9] to choose a preset, or simply [ENTER] to use the current time."
    print ''
    print 'Current preset times are as follows (24-hour format):'
    print ''
    testing = False
    for i in range(9):
        preset_num = i+1
        preset_num_str = str(preset_num)
        preset_str = 'preset'+preset_num_str
        preset_hour = cfg.get(preset_str)[0]
        preset_minute = cfg.get(preset_str)[1]
        preset_second = cfg.get(preset_str)[2]
        n_time = nice_time(preset_hour, preset_minute, preset_second)
        r_time = reg_time(preset_hour, preset_minute, preset_second)
        print 'PRESET %d  ----  %s (%s)' % (preset_num, r_time, n_time)
    ctime_hour = cfg.get('current')[0]
    ctime_minute = cfg.get('current')[1]
    ctime_second = cfg.get('current')[2]
    r_time = reg_time(ctime_hour, ctime_minute, ctime_second)
    n_time = nice_time(ctime_hour, ctime_minute, ctime_second)
    print ''
    print 'The alarm is currently set to ring at: %s  (%s)' % (r_time, n_time)
    print ''
    print '-----------------------------------'
    try:
        user_input = raw_input("Input command or just press ENTER:  ")
        try:
            ui = int(user_input)
            if ui > 0 and ui < 10:
                p_choice = 'preset'+user_input
                alarm_time = cfg.get(p_choice)
                set_hour = int(alarm_time[0])
                set_minute = int(alarm_time[1])
                set_second = int(alarm_time[2])
                message(set_hour, set_minute, set_second)
                alarm(set_hour, set_minute, set_second, sound_file, cfg)
            else:
                error_restart()
        except ValueError:
            pass
        if user_input == '':
            pass
        elif user_input == 's':
            set_hour, set_minute, set_second, cfg = set_time(cfg)
            message(set_hour, set_minute, set_second)
            alarm(set_hour, set_minute, set_second, sound_file, cfg)
        elif user_input == 'q' or user_input == 'Q' or user_input == 'quit' or user_input == 'QUIT' or user_input == 'exit' or user_input == 'EXIT':
            bye()
        elif user_input == 'h' or user_input == 'H' or user_input == 'help' or user_input == 'HELP':
            help_screen()
        elif user_input == 'a' or user_input == 'A' or user_input == 'about' or user_input == 'ABOUT':
            about_screen()
        elif user_input == 't':
            alarm_test(sound_file)
        else:
            print ''
            user_input = raw_input("Input a valid command, please.")
            print ''
            if user_input == '':
                main()
            else:
                main()
    except KeyboardInterrupt:
        bye()


def main():
    '''
    This is the main function, which calls everything else.  The setup function sets things up, the get_input function leads to a myriad of menus and various other useful bits of interactivity, the message function displays the 'final' message on the screen while the alarm is active, and the alarm function does the actual alarm work.
    '''
    set_hour, set_minute, set_second, sound_file, cfg = setup()
    get_input(sound_file, cfg)
    message(set_hour, set_minute, set_second)
    alarm(set_hour, set_minute, set_second, sound_file, cfg)

def cli_main(cli_input):
    '''
    This is similar to the other main function, except it skips all the interactive bits and goes straight to the alarm with no additional input required.  It's meant to be used with input from the command-line, thus its name.
    '''
    if cli_input == 'testing':
        set_hour, set_minute, set_second, sound_file, cfg = setup()
        alarm_test(sound_file)
    elif cli_input == 'noon' or cli_input == 'midnight':
        ui = cli_input
        set_hour, set_minute, set_second, sound_file, cfg = setup()
        set_hour, set_minute, set_second = noon_midnight(ui)
    else:
        set_hour, set_minute, set_second, sound_file, cfg = setup()
        try:
            new_time_str = str(cli_input)
            new_new_time_str, ampm = am_or_pm(new_time_str)
            new_time_hour, new_time_minute, new_time_second = parse_time(new_new_time_str)
            set_hour = int(new_time_hour)
            set_minute = int(new_time_minute)
            set_second = int(new_time_second)
            if ampm == 'pm':
                if set_hour == 0:
                    pass
                elif set_hour > 12:
                    pass
                elif set_hour < 12:
                    set_hour += 12
            elif ampm == 'am':
                if set_hour == 12:
                    set_hour -= 12

        except:
            print 'Whoops!  Incorrect input!'
            bye()
    message(set_hour, set_minute, set_second)
    alarm(set_hour, set_minute, set_second, sound_file, cfg)







if __name__ == '__main__':
    try:
        if sys.argv[1] == 'help' or sys.argv[1] == 'h' or sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print_help()
            sys.exit()
        elif sys.argv[1] == 'about' or sys.argv[1] == 'a' or sys.argv[1] == '--about':
            print_about()
            sys.exit()
        elif sys.argv[1] == 'version' or sys.argv[1] == 'v' or sys.argv[1] == '--version' or sys.argv[1] == '-v':
            print ''
            print "PyAlarm version 0.9"
            print ''
        elif sys.argv[1] == 't' or sys.argv[1] == 'T' or sys.argv[1] == 'test' or sys.argv[1] == 'TEST' or sys.argv[1] == '-t' or sys.argv[1] == '--test':
            cli_input = 'testing'
            cli_main(cli_input)
        elif sys.argv[1] == 'noon' or sys.argv[1] == 'NOON' or sys.argv[1] == 'n' or sys.argv[1] == 'N':
            cli_input = 'noon'
            cli_main(cli_input)
        elif sys.argv[1] == 'midnight' or sys.argv[1] == 'MIDNIGHT' or sys.argv[1] == 'm' or sys.argv[1] == 'M':
            cli_input = 'midnight'
            cli_main(cli_input)
        else:
            if len(sys.argv) > 2:
                cli_input = sys.argv[1]+sys.argv[2]
                cli_main(cli_input)
            else:
                cli_input = sys.argv[1]
                cli_main(cli_input)
    except IndexError:
        if restart_list[0] == '-1':
            main()
        elif restart_list[0] == '1':
            main()
