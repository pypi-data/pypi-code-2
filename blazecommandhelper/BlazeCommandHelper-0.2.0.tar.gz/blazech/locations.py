import sys
import os
from os import path

user_dir = os.path.expanduser('~')
system_config_file = user_config_file = system_log_file = user_log_file = \
    system_commands_dir = user_commands_dir = None

def set_paths(testing_dir=None):
    global system_config_file, user_config_file, system_log_file, user_log_file, \
        user_dir, system_commands_dir, user_commands_dir
    if testing_dir:
        system_config_file = path.join(testing_dir, 'system', 'blazech.conf')
        system_log_file = path.join(testing_dir, 'system', 'blazech.log')
        system_commands_dir = path.join(testing_dir, 'system')
        user_config_file = path.join(testing_dir, 'user', 'blazech.conf')
        user_log_file = path.join(testing_dir, 'user', 'blazech.log')
        user_commands_dir = path.join(testing_dir, 'user')
    else:
        if sys.platform == 'win32':
            sroot = os.environ.get('SYSTEMROOT', None)
            if sroot is None:
                sroot = path.abspath('/')
            else:
                # SYSTEMROOT => c:\windows, so take the dirname of that to get
                # the drive
                sroot = path.dirname(sroot)
            system_log_file = path.join(sroot, 'logs', 'blazech.log')
            system_commands_dir = path.join(sroot, 'etc', 'blazech')
            user_dir = os.environ.get('APPDATA', user_dir)
        else:
            sroot = '/'
            system_log_file = path.join(sroot, 'var', 'log', 'blazech.log')
            system_commands_dir = path.join(sroot, 'usr', 'local', 'lib', 'blazech')
        system_config_file = path.join(sroot, 'etc', 'blazech/blazech.conf')
        user_log_file = path.join(user_dir, '.blazech', 'blazech.log')
        user_commands_dir = path.join(user_dir, '.blazech')
        user_config_file = path.join(user_dir, '.blazech', 'blazech.conf')
set_paths()
