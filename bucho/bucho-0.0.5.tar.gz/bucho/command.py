import os
import sys
import cmd
import optparse
import bucho

description = '''
Actions are commands like "show", "latest_status" and "all_status".
If -i is specified or no action is specified on the command line, a
"shell" interpreting actions typed interactively is started. Use the
action "help" to find out about available actions.
'''

class BuchoOptions(object):

    def __init__(self):
        programname = os.path.basename(sys.argv[0])
        base, ext = os.path.splitext(programname)
        if ext == ".py":
            if base.endswith('-script'):
                base = base[:-7]
            programname = base
        sys.argv[0] = programname

        usage = 'usage: %prog [options] command'
        parser = optparse.OptionParser(usage=usage, description=description)
        parser.add_option('-i', '--interactive',
                help='start an interactive shell after executing commands',
                dest='interactive',
                action='store_true', default=False)

        parser.add_option('-p', '--prompt',
                help='prompt string',
                dest='prompt',
                action='store', default=(programname+">"))

        self.options, self.args = parser.parse_args()


        if not self.args and not self.options.interactive:
            self.options.interactive = 1

    def __getattr__(self, name):
        if hasattr(self.options, name):
            return getattr(self.options, name)
        raise AttributeError(name)

    def __add__(self, obj):
        return obj


class BuchoCmd(cmd.Cmd):

    def __init__(self, options):
        self.options = options
        self.prompt = self.options.prompt + ' '
        cmd.Cmd.__init__(self)

    def do_quit(self, arg):
        return 1

for name in ['show', 'latest_status', 'all_status', 'torumemo']:
    def makecmd(n):
        def f(self, arg):
            print(getattr(bucho, n)())
            return 0
        return f
    setattr(BuchoCmd, "do_" + name, makecmd(name))


def main(options=None, cmdclass=BuchoCmd):
    try:
        if options is None:
            options = BuchoOptions()
        c = cmdclass(options)
    except Exception, e:
        print e
        return

    if options.args:
        c.onecmd(" ".join(options.args))

    if options.interactive:
        try:
            import readline
        except ImportError:
            pass
        c.cmdloop()

def console():
    main()

if __name__ == '__main__':
    main()

