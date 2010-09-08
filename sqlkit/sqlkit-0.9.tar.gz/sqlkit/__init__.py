import os
import sys
import gettext

from sqlkit.misc import utils

__version__ = '0.9'


cwd = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(cwd, 'locale')
if not os.path.exists(path):
    # this is tru when we are in the pyinstaller executable
    path = os.path.join(os.path.dirname(sys.executable), 'sqlkit', 'locale')

# t = gettext.translation('sqlkit', path)
# _ = t.lgettext

gettext.bindtextdomain('sqlkit', path)
gettext.textdomain('sqlkit')
_ = gettext.gettext
   
from db.proxy import DbProxy
import exc


utils.check_sqlalchemy_version('0.5.0')
