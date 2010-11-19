import datetime as dt
import sys
import subprocess

if sys.platform == 'linux2':
    import pynotify as notify
    import gtk
else:
    import Growl as notify

def main():
    if len(sys.argv) < 2:
        print 'Usage: naf <command_to_run>'
        sys.exit(1)

    cr = CommandRunner(u' '.join(sys.argv[1:]))
    try:
        cr.run_command()
    except KeyboardInterrupt:
        cr.handle_interrupt()
        sys.exit(1)

class CommandRunner(object):
    duration = None
    start = None
    command = None

    def __init__(self, command):
        self.command = command

    def run_command(self):

        self.start = dt.datetime.now()
        return_code = subprocess.call(self.command, shell=True)
        self.duration = dt.datetime.now() - self.start

        self.display_notification(return_code)

        sys.exit(return_code)

    def handle_interrupt(self):
        self.duration = dt.datetime.now() - self.start
        self.display_notification()

    def display_notification(self, return_code=None):
        if return_code is None:
            description = (u'was aborted after\n%s'
                % self.string_duration())
        elif return_code == 0:
            description = (u'finished successfully\nin %s'
                % self.string_duration())
        else:
            description = (u'finished with return code %s\nin %s'
                % (return_code, self.string_duration()))

        if hasattr(notify, 'GrowlNotifier'):
            g = notify.GrowlNotifier(u'naf', notifications=['command_finished',])
            g.register()
            g.notify('command_finished', self.command, description)
        elif hasattr(notify, 'Notification'):
            if return_code == 0:
                icon = gtk.STOCK_DIALOG_INFO
            else:
                icon = gtk.STOCK_DIALOG_ERROR
            notification = notify.Notification(self.command, description, icon)
            notification.show()

    def string_duration(self):
        if self.duration.days == 0 and self.duration.seconds == 0:
            return u'0.%s seconds'% self.duration.microseconds
        hours, remainder = divmod(self.duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        days = self.duration.days

        self.duration_string = ''
        if days > 0:
            duration_string += u'%s %s ' % (days, self.get_plural(days, u'day'))
        if hours > 0:
            self.duration_string += u'%s %s ' % (hours, self.get_plural(hours, u'hour'))
        if minutes > 0:
            self.duration_string += u'%s %s ' % (minutes, self.get_plural(minutes, u'minute'))
        if len(self.duration_string) > 0:
            self.duration_string += u'and '
        self.duration_string += u'%s %s' % (seconds, self.get_plural(seconds, u'second'))

        return self.duration_string

    def get_plural(self, value, text):
        if value == 1:
            return text
        else:
            return text + u's'

if __name__ == '__main__':
    main()
