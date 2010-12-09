import logging
import subprocess
import sys

class _AbortCommand(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

class BaseCommand(object):
    name = None
    help = None

    def __init__(self, subparsers):
        self.parser = subparsers.add_parser(self.name, help=self.help)
        self.parser.set_defaults(func=self.execute_wrapper)
        self.init_logging()
        self.create_arguments()

    def init_logging(self):
        mname = self.__class__.__module__
        self.log = logging.getLogger('%s:%s' % (mname, self.name))

    def create_arguments(self):
        pass

    def abort(self, msg=None, code=2):
        raise _AbortCommand(code, msg)

    def execute_wrapper(self, parser, args):
        try:
            retval = self.execute(args)
            if retval is None:
                retval = 0
            parser.exit(retval)
        except _AbortCommand, e:
            msg = e.msg
            if msg:
                msg = msg.rstrip() + '\n'
            parser.exit(e.code, msg)

    def execute(self, args):
        raise NotImplimentedError('The Command object "%s" did not have an "execute" method')

class SystemProcessMixin(object):

    def sysproc(self, *args, **kwargs):
        self.log.vdebug('cmd args: %s', args)
        for arg in args:
            if not isinstance(arg, basestring):
                raise TypeError('arg %s is %s, but needs to be a string' % (arg, type(arg)))
        proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                **kwargs
            )
        stdout, stderr = proc.communicate('123\n')
        self.log.debug('cmd return code: %s', proc.returncode)
        self.log.debug('cmd stdout: %s', stdout)
        self.log.debug('cmd stderr: %s', stderr)
        return proc.returncode, stdout, stderr

    def checkcall(self, *args, **kwargs):
        """
            Same as sysproc, but will check the returncode and if non-zero
            will print stdout, stderror, and raise an exception that
            will prevent any further commands from being run.
        """
        ok_codes = kwargs.pop('ok_codes', [0])
        rc, so, se = self.sysproc(*args, **kwargs)
        if rc not in ok_codes:
            if so:
                print so
            if se:
                print >> sys.stderr, se
            self.abort()
        return rc, so, se
