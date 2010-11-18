import sys
import subprocess

if sys.platform == 'linux2':
    import pynotify as notify
else:
    import Growl as notify

def display_notification(command, return_code):
    description = u'finished with return code %s' % return_code

    if hasattr(notify, 'GrowlNotifier'):
        g = notify.GrowlNotifier(u'naf', notifications=['command_finished',])
        g.register()
        g.notify('command_finished', command, description)
    elif hasattr(notify, 'Notification'):
        notification = notify.Notification(command, description)
        notification.show()

def main():
    if len(sys.argv) < 2:
        print 'Usage: naf <command_to_run>'
        sys.exit(1)
    command_string = u' '.join(sys.argv[1:])
    return_code = subprocess.call(command_string, shell=True)

    display_notification(command_string, return_code)

    sys.exit(return_code)

if __name__ == '__main__':
    main()
