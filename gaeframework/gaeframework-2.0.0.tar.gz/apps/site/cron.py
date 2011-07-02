'''
Automatically run cron jobs every minute.

TODO: run all cron.py handlers in the each application.
'''
import os
from datetime import datetime 

NOW = datetime.now()

# run cron jobs for all applications
apps = [dir_name for dir_name in os.listdir("..") if not dir_name.startswith("_")]
for app_name in apps:
    print __import__("..%s" %app_name)

## clear expired sessions (every hour)
#if NOW.minute == 0:
#    from gae.sessions import delete_expired_sessions
#    delete_expired_sessions()