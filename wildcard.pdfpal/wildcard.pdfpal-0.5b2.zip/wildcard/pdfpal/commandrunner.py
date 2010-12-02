import os
import subprocess

class command_subprocess(object):
    """
    idea of how to handle this shamelessly
    stolen from ploneformgen's gpg calls
    """
    paths = ['/bin', '/usr/bin', '/usr/local/bin']
    bin_name = None # implement this
        
    options = [
    ]
        
    def __init__(self):
        if os.name == 'nt':
            self.bin_name += '.exe'
        binary = self._findbinary()
        self.binary = binary
        if binary is None:
            raise IOError, "Unable to find gs binary"

    def _findbinary(self):
        if os.environ.has_key('PATH'):
            path = os.environ['PATH']
            path = path.split(os.pathsep)
        else:
            path = self.paths
        for dir in path:
            fullname = os.path.join(dir, self.bin_name)
            if os.path.exists( fullname ):
                return fullname
        return None
        
    def get_command(self, opt_values={}):
        command = [self.binary]
        for option in self.options:
            if '%s' not in option:
                option = option % opt_values
            
            command.append(option)
        return command
        
    def get_process(self, stdin=None, opt_values={}):
        command = self.get_command(opt_values)
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        
    def run_command(self, opt_values={}, stdin=None):
        process = self.get_process(stdin=stdin, opt_values=opt_values)
        
        if stdin:
            process.stdin.write(stdin)
            
        output = process.communicate()[0]
        
        if stdin:
            process.stdin.close()
            
        return process, output