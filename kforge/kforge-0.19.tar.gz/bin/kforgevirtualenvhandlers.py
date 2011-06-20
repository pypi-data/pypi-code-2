# Code for virtualenv.
import os
activateThisPath = os.path.join(os.path.dirname(__file__), 'activate_this.py')
execfile(activateThisPath, dict(__file__=activateThisPath))

# KForge Apache 'access' handler.
try:
    from kforge.handlers.projecthost import accesshandler as accesshandler
except:
    pass

# KForge Apache 'authen' handler.
try:
    from kforge.handlers.projecthost import authenhandler as authenhandler
except:
    pass

# KForge Django handler
try:
    from kforge.handlers.kui.modpython import handler as djangohandler
except:
    pass

# KForge Trac handler
try:
    from trac.web.modpython_frontend import handler as trachandler
except:
    try:
       # For Trac version < v0.9.
       import trac.ModPythonHandler as trachandler
    except:
       pass

