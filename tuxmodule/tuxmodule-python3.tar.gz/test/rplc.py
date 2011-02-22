import sys
import os
import re

getenv=os.environ.get

appdir = getenv('APPDIR', '')
tuxdir = getenv('TUXDIR', '')
tuxconfig = getenv('TUXCONFIG', '')
qmconfig = getenv('QMCONFIG', '')
uname = os.uname()[1]
pwd = os.getcwd()
python_exe = sys.executable

for line in sys.stdin.readlines():
    line = re.sub('%%APPDIR%%', appdir, line)
    line = re.sub('%%TUXDIR%%', tuxdir, line)
    line = re.sub('%%TUXCONFIG%%', tuxconfig, line)
    line = re.sub('%%QMCONFIG%%', qmconfig, line)
    line = re.sub('%%UNAME%%', uname, line)
    line = re.sub('%%PWD%%', pwd, line)
    line = re.sub('%%PYTHON_EXECUTABLE%%', python_exe, line)
    print(str.rstrip(line))

