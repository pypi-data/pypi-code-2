from sys import argv, exit
from os import getenv, listdir, mkdir
from os import path
from shutil import copytree, copy2, rmtree

INFO = True 
def info(msg):
    if INFO:
        print msg

HOME = getenv('HOME',None)
QUICK_HOME = getenv('QUICK_HOME',path.join(HOME,'.quick'))
QUICK_PROJECTS = getenv('QUICK_PROJECTS',path.join(HOME,'quick'))

HERE = path.realpath(path.dirname(__file__))
INSTALLATION_FILES_DIR = path.join(HERE,'quick_files')

bashrc_template = u"""
#### QUICK INSTALLED OPTIONS #####
## DONT REMOVE OR EDIT THESE COMMENTED LINES
## OR YOU WILL NEED TO UNINSTALL QUICK BY HAND
export QUICK_HOME=$HOME/.quick
export QUICK_PROJECTS=$HOME/quick
source $QUICK_HOME/quick_bashrc
quick
#### END OF QUICK INSTALLED OPTIONS #####
"""

def install(upgrading=False):
    """installs quick in users home"""
    if path.exists(QUICK_HOME):
        if not path.isdir(QUICK_HOME):
            info('%s should not exist, or be a directory' % QUICK_HOME)
            exit(1)
        elif upgrading:
            for fname in listdir(INSTALLATION_FILES_DIR):
                fpath = path.join(INSTALLATION_FILES_DIR, fname)
                copy2(fpath, QUICK_HOME)
                info('Copied %s to %s' % (fpath, QUICK_HOME))
    else:
        copytree(INSTALLATION_FILES_DIR, QUICK_HOME)
        info('Copied folder %s to %s' % (INSTALLATION_FILES_DIR, QUICK_HOME))
    if not path.exists(QUICK_PROJECTS):
        mkdir(QUICK_PROJECTS)
        info('Created folder %s for quick projects' % QUICK_PROJECTS)
    if not already_in_bashrc():
        add_to_bashrc()
        info('You should run "source $HOME/.bashrc" in order to finish installation')

def upgrade():
    """overwrites quick installation files"""
    return install(upgrading=True)

def remove():
    """removes quick installation and files form users home"""
    if already_in_bashrc():
        remove_from_bashrc()
    if path.exists(QUICK_HOME):
        rmtree(QUICK_HOME)
        info('Removed %s and all items inside it' % QUICK_HOME)
    if path.exists(QUICK_PROJECTS):
        info('NOT REMOVED folder %s. Remove it by hand if desired' % QUICK_PROJECTS)

def show_help():
    """displays help and exit"""
    print 'Available commands:'
    sorted_commands = sorted(COMMANDS.items())
    print '\n'.join(['%s: %s'%(k,v.__doc__ or '') for k,v in sorted_commands])


def remove_from_bashrc():
    already_in_bashrc(remove_if_there=True)

def already_in_bashrc(remove_if_there=False):
    begin_marker = bashrc_template.splitlines()[1].strip()
    end_marker = bashrc_template.splitlines()[-1].strip()
    bashrc_path = path.join(HOME,'.bashrc')
    bashrc_file = file(bashrc_path,'r')
    bashrc_lines = [line.strip() for line in bashrc_file.readlines()]
    try:
        begin_index = bashrc_lines.index(begin_marker)
        end_index = bashrc_lines.index(end_marker)
    except ValueError:
        in_there = False
    else:
        in_there = begin_index < end_index
    bashrc_file.close()
    if in_there and remove_if_there:
        stripped_lines = bashrc_lines[:begin_index] + bashrc_lines[1+end_index:]
        bashrc_file = file(bashrc_path,'w')
        bashrc_file.write('\n'.join(stripped_lines))
        bashrc_file.close()
        info('Configurations from .bashrc removed ')
    return in_there

def add_to_bashrc():
    bashrc_path = path.join(HOME,'.bashrc')
    bashrc_file = file(bashrc_path,'r')
    base_content = bashrc_file.read()
    bashrc_file.close()
    bashrc_file = file(bashrc_path,'w')
    bashrc_file.write(base_content+bashrc_template)
    bashrc_file.close()
    info('Configurations added to .bashrc')    

COMMANDS = {'install': install,
            'upgrade': upgrade,
            'remove': remove,
            'help': show_help}

if __name__ == '__main__':
    if len(argv) < 2:
        print 'missing command argument'
        exit(1)
    if HOME is None:
        print 'missing user home env variable'
        exit(1)
    command = argv[1]
    if command in COMMANDS:
        COMMANDS[command]()
    else:
        print "command '%s' not valid" % command
        show_help()
