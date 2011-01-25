# ntsRC.py
import sys, os, os.path, codecs
has_ntsrc = False

rc = []
added = []
msg = []
error = []
warn = []
fatal = False
warning = False
set_ed = False
tracing_level = 0

d_encoding = sys.stdout.encoding

search_path = os.getenv('PATH').split(os.pathsep)
cwd = os.getcwd()
homedir = os.path.expanduser("~")
ntsrc_maybe = os.path.join(cwd, 'rc')
if os.path.isfile(ntsrc_maybe):
    ntsrc = ntsrc_maybe
    ntsdir = cwd
    ntsdata = cwd
    ntsexport = os.path.join(ntsdir, 'export')
else:
    ntsdir = os.path.join(homedir, ".nts")
    ntsrc = os.path.join(homedir, ".nts", "rc")


if sys.platform == 'darwin':
    mac = True
    font_size = 12
    d_htmlfont = 8
    d_htmlprintfont = 5
else:
    mac = False
    font_size = 9
    d_htmlfont = 4
    d_htmlprintfont = 5

def PathSearch(filename, path=search_path):
    for pth in path:
        candidate = os.path.join(pth,filename)
        if os.path.os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return ''

d_pandoc = PathSearch('pandoc')
if d_pandoc:
    d_markup = 'pd'
else:
    d_markup = 'md'

def check(var):
    global rc, added
    name = var[0]
    defining_code = var[1]
    description = "\n### ".join(var[2:])
    if description:
        rc.append("\n### %s" % description)
    if name in globals():
        if type(globals()[name]) == str:
            if globals()[name] != "":
                s = "%s = '''%s'''" % (name, globals()[name])
                # print "not empty: %s = %s" % (name, globals()[name])
            else:
                s = "%s = ''" % (name)
        else:
            s = "%s = %s" % (name, globals()[name])
        rc.append(s)
    else:
        res = ''
        if type(defining_code) == str:
            try:
                exec "res = %s" % defining_code
            except:
                exec "res = '%s'" % defining_code
        elif type(defining_code) in [tuple, list]:
            exec "res = (%s)" % repr(defining_code)
        else:
            exec "res = %s" % defining_code
        globals()[name] = res
        if globals()[name] != "not set":
            # print "Adding: %s" % name
            if type(res) == str:
                if res != "":
                    s = "%s = '''%s'''" % (name, res)
                else:
                    s = "%s = ''" % (name)
            elif type(res) in [tuple, list]:
                s = "%s = %s" % (name, repr(res))
            else:
                s = "%s = %s" % (name, res)
            added.append(s)
            rc.append(s)


def set_ntsrc():
    global has_ntsrc
    if os.path.isfile(ntsrc):
        has_ntsrc = True
    return ntsrc

def check_ntsdir():
    if not os.path.isdir(ntsdir):
        os.mkdir(ntsdir)
        print("""
Created '%s' to hold nts system files.
\n""" % (ntsdir))
    return os.path.isdir(ntsdir)

def check_ntsdata():
    if not os.path.isdir(ntsdata):
        os.mkdir(ntsdata)
        print("""
Created '%s' to hold project files.
Users of earlier versions of nts will need either to move their
project files to this subdirectory or to correct the entry for
ntsdata in '%s'.\n""" % (ntsdata, ntsrc))
    return os.path.isdir(ntsdata)

def check_ntsexport():
    if not os.path.isdir(ntsexport):
        os.mkdir(ntsexport)
        print("""
Created '%s' to hold exported files.
This location is specified by the entry for ntsexport in '%s'.\n""" % (ntsexport, ntsrc))
    return os.path.isdir(ntsexport)

def set_editor_settings():
    global rc, added, set_ed, editor
    chooselater = ['choose later', '', '', '']
    comment = ""
    selected = []
    unselected = []
    if set_ed:
        return None
    else:
        set_ed = True
    if mac:
        options = {
            'bbedit' : [
                "editcmd = '''%(e)s +%(n)s -w --new-window %(f)s'''",
            ],
            'edit' : [
                "editcmd = '''%(e)s +%(n)s -w --new-window %(f)s'''",
            ],
            'mate' : [
                "editcmd = '''%(e)s -l %(n)s -w %(f)s'''",
            ],
            'vim' : [
                "editcmd = '''%(e)s -g -p -f +%(n)s %(f)s'''",
            ],
        }
        for name in ['vim', 'bbedit','mate', 'edit']:
            editor = PathSearch(name)
            # select the first that works and comment out the others
            if editor:
                if comment != "# ":
                    selected = (editor,
                        options[name][0])
                else:
                    unselected.append(name)
                rc.append("%seditor = '''%s'''" % (comment, editor))
                added.append("%seditor = '''%s'''" % (comment, editor))
                rc.append("%s%s" % (comment, options[name][0]))
                added.append("%s%s" % (comment, options[name][0]))
                comment = "# "
    else: # not mac
        options = {
            'gvim' : [
                "editcmd = '''%(e)s -f +%(n)s %(f)s'''",
            ],
            'emacs' : [
                "editcmd = '''%(e)s +%(n)s %(f)s'''",
            ]
        }
        for name in ['gvim','emacs']:
            editor = PathSearch(name)
            # select the first that works and comment out the others
            if editor:
                if comment != "# ":
                    selected = (editor,
                        options[name][0])
                else:
                    unselected.append(name)
                rc.append("%seditor = '''%s'''" % (comment, editor))
                added.append("%seditor = '''%s'''" % (comment, editor))
                rc.append("%s%s" % (comment, options[name][0]))
                added.append("%s%s" % (comment, options[name][0]))
                comment = "# "
    if selected == []:
        rc.append("editor = ''")
        rc.append("editcmd = ''")
        print("""
        You will need to specify values for:

            editor
            editcmd

        in %s.\n""" % ntsrc)
    else:
        print("""
Project files will be located in the directory

    ntsdata = '%s'

The following settings were made for your external editor:

    editor = '%s'
    editcmd = '%s'

Edit %s if you wish to make changes.\n""" % (ntsdata,
        selected[0], selected[1], ntsrc))
        if len(unselected) > 0:
            print("""\
Comparable settings were also made for

    %s

but were commented out. \n""" % ", ".join(unselected))
    return None

def set_editor():
    if not set_ed:
        set_editor_settings()
    return "not set"

def set_editcmd():
    if not set_ed:
        set_editor_settings()
    return "not set"

def trace(func):
    global tracing_level
    if enable_tracing:
        def callf(*args, **kwargs):
            global tracing_level
            tracing_log.write("%sCalling %s: %s, %s\n" %
                ('    '*tracing_level, func.__name__, args, kwargs))
            tracing_level += 1
            r = func(*args, **kwargs)
            tracing_level -= 1
            tracing_log.write("%s%s returned %s\n" % ('    '*tracing_level, func.__name__, r))
            return(r)
        return(callf)
    else:
        return(func)

def make_ntsrc():
    fo = open("%s" % ntsrc,'w')
    fo.write("""\
###       Configuration settings for nts: note taking simplified
###
### nts's current settings are obtained from a file named 'rc' in the 
### current working directory when nts is started or from '~/.nts/rc' if
### no such file exists. Missing settings from whichever rc file is used
### will be filled with default values and these settings will be written
### to the file. This means you can always restore any default settings you
### wish by removing the relevant lines from the rc file and then running
### n.py again.
###\n""")
    for line in rc:
        fo.write("%s\n" % line)
    fo.close()

variables = [
    ['encoding', '"%s"' % d_encoding, 
        'The default encoding for terminal output. Your terminal must',
        ' be able to support output using this encoding.'],
    ['ntsdata', "%s" % os.path.join(ntsdir,"data"),
        'The directory containing all note files.'],
    ['ntsexport', "%s" % os.path.join(ntsdir, "export"),
        'The directory to hold rst (restructured text) note exports.'],
    ['ntstxt', ".txt",
        'The extension for plain text note files. Must include the beginning "."'],
    ['ntsenc', ".text",
        'The extension for encrypted note files. Must include the beginning "."'],
    #  ['quick', "quick.txt",
    ['quick', "quick.txt",
        'The file to use for quick notes. This name must include either the', 
        'ntstxt or the ntsenc file extension.'],
    ['editor', '"%s" % set_editor()',
        'Edit settings',
        'editor:  the full path to the editor to use for editing with the',
        'graphic user interface. ',
        'E.g., editor = "/usr/local/bin/vim"',
        'editcmd: the command for editing with the graphic user interface',
        'using the following SUBSTITUTIONS:',
        '   %(e)s -> editor',
        '   %(n)s -> the starting line number',
        '   %(f)s -> the file name',
        'E.g., editcmd = "%(e)s -g -f +%(n)s %(f)s"'],
    ['editcmd', '"%s" % set_editcmd()', ''],
    ['EDITOR', '',
        'EDITOR:  the full path to the editor to use for editing with the',
        'command line interface.',
        'E.g., EDITOR = "/usr/local/bin/vim"',
        'If left blank, the setting for "editor" will be used.',
        'EDITCMD: the command for editing with the command line interface',
        'using the following SUBSTITUTIONS:',
        '   %(e)s -> EDITOR',
        '   %(n)s -> the starting line number',
        '   %(f)s -> the file name',
        'E.g., EDITCMD = "%(e)s +%(n)s %(f)s"',
        'If left blank, the setting for "editcmd" will be used.'],
    ['EDITCMD', ''],
    ['font_size', font_size, 
        'The base font size.'],
    ['htmlfont', d_htmlfont, 
        'The starting html font size'],
    ['htmlprintfont', d_htmlprintfont, 
        'The starting html printing font size'],
    ['mono_tree', False, 
        'Use a monospaced font in the outline panel.'],
    ['mono_display', False, 
        'Use a monospaced font in the display panel in view mode.'],
    ['mono_edit', False, 
        'Use a monospaced font in the display panel in edit mode.'],
    ['markup', "%s" % d_markup,
        'The type of markup to use for html display and export. Enter',
        '"pd" for pandoc, "md" for markdown or "rst" for restructured text.'],
    ['newer', True,
        'Check for newer releases of nts on startup.'],
    ['numbaks', 3,
        'The number of backups of data files to keep'],
    ['pandoc', '"%s" % d_pandoc',
        'The full path to pandoc.'],
    ['stylesheet', "", 
        'The path to a custom css stylesheet to be used instead of the',
        'default stylesheet when creating html output. This and the',
         ' following two html font settings are only relevant if docutils',
         '      http://docutils.sourceforge.net/ ',
         'is installed.'],
    ]


# main
# set enable_tracing = True in ~/.nts/rc to enable tracing
enable_tracing = False
ntsrc = set_ntsrc()
if has_ntsrc:
    ntsrc_fo = open(ntsrc, 'r')
    exec(ntsrc_fo)
    ntsrc_fo.close()

for variable in variables:
    check(variable)

try:
    if sys.stdout.encoding.lower() != encoding.lower():
        # try to reset stdout to the encoding specified in ntsrc
        try:
            old_stdout = sys.stdout
            old_encoding = sys.stdout.encoding
            codec = codecs.lookup(encoding)
            new_stdout = codec[-1](sys.stdout)
            new_encoding = new_stdout.encoding
            sys.stdout = new_stdout
        except:
            print("""\
    Error. Output using encoding '%s' is not supported by your terminal.
    Please correct the setting for 'encoding' in ~/.nts/ntsrc.
    Using encoding '%s' instead.
    """ % (encoding, sys.stdout.encoding))
            sys.stdout = old_stdout
except:
    pass

check_ntsdir()
check_ntsdata()
check_ntsexport()

if fatal:
    sys.exit()

# show_ptitle = True
show_ptitle = False

tracing_log = None
if enable_tracing:
    tracinglog = os.path.join(ntsdir, 'tracing.log')
    tracing_log = open(tracinglog, "w", True)
    print "Tracing enabled. Writing to '%s'." % tracinglog

if len(added) > 0:
    if has_ntsrc:
        import shutil
        shutil.copyfile(ntsrc, "%s.bak" % ntsrc)
        make_ntsrc()
        ntsrc_fo = open(ntsrc, 'r')
        exec(ntsrc_fo)
        ntsrc_fo.close()
        print """\
IMPORTANT: Your configuration file

    %s

has as been copied to

    %s.bak

and a new configuration file which incorporates your settings together
with

    %s

has been saved as

    %s \n""" % (ntsrc, ntsrc, "\n    ".join(added), ntsrc)

    else:
        make_ntsrc()
        print("""\
A new configuration file with default settings has been saved as

    %s \n""" % ntsrc)

    print """\
Please join the nts discussion group at

    http://groups.google.com/group/notetakingsimplified

Continuing improvement depends upon your feedback.
"""
    raw_input('Press enter to continue')
    if warning:
        sys.exit()