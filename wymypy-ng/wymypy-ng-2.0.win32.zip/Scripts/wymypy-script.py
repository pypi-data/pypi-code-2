#!C:\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'wymypy-ng==2.0','console_scripts','wymypy'
__requires__ = 'wymypy-ng==2.0'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('wymypy-ng==2.0', 'console_scripts', 'wymypy')()
    )
