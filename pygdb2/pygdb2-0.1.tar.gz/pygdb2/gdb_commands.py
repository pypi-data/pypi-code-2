import sys
import signal
import gdb

# when we receive this signal, we stop the execution, let PyContinue() to do
# its magic, and then we discard it
PYGDB_MAGIC_SIGNAL = signal.SIGUSR2
gdb.execute("handle SIGUSR2 stop nopass")


class PyRun (gdb.Command):
 
    def __init__(self):
        gdb.Command.__init__(self, "pyrun", gdb.COMMAND_RUNNING)
 
    def invoke(self, arg, from_tty):
        gdb.execute("run")
        gdb.execute("c")


class PyContinue (gdb.Command):
 
    def __init__(self):
        gdb.Command.__init__(self, "c", gdb.COMMAND_RUNNING)
        self.at_prompt = False

    def read_commands(self):
        """
        If we are in a __sigqueue and the signal is SIGUSR2, then we read the
        associated sigval as a string and splitlines() it. Else, return None
        """
        try:
            cframe = gdb.selected_frame()
        except RuntimeError, e:
            return None # cannot get the frame
        if cframe.name() != '__sigqueue':
            return None
        signo = gdb.parse_and_eval("sig")
        if signo != PYGDB_MAGIC_SIGNAL:
            return None
        # XXX: if the program receives a PYGDB_MAGIC_SIGNAL which does not
        # come from pygdb2.execute(), sival_ptr might contain garbage
        data = gdb.parse_and_eval("(char*)val->sival_ptr").string()
        return data.splitlines()

    def exec_commands_maybe(self):
        cmds = self.read_commands()
        if cmds:
            for cmd in cmds:
                print 'pygdb2:', cmd
                gdb.execute(cmd)
            return True
        return False

    def invoke(self, arg, from_tty):
        while True:
            executed = self.exec_commands_maybe()
            if executed or self.at_prompt:
                self.at_prompt = False
                gdb.execute("continue")
            else:
                self.at_prompt = True
                return

class EnterPdb(gdb.Command):

    def __init__(self):
        gdb.Command.__init__(self, "pdb", gdb.COMMAND_RUNNING)
 
    def invoke(self, arg, from_tty):
        gdb.execute("signal SIGUSR1")


EnterPdb()
PyRun()
PyContinue()

