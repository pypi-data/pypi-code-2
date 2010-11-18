import pynotify
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print 'Usage: naf <command_to_run>'
        sys.exit(1)
    command_string = u' '.join(sys.argv[1:])
    return_code = subprocess.call(command_string, shell=True)

    notification = pynotify.Notification(u'%s' % command_string, u'finished with return code %s' % return_code)
    notification.show()

    sys.exit(return_code)
