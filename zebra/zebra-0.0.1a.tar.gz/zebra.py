#!/usr/bin/env python
# NOTE: this package is Linux specific at the moment

import subprocess
import os.path
import sys
if sys.platform.lower().startswith('win'):
    import win32print

class zebra(object):
    def __init__(self, queue=None):
        """queue - name of the printer queue"""
        self.queue = queue

    def _output_unix(self, commands):
        if self.queue == 'zebra_python_unittest':
            p = subprocess.Popen(['cat','-'], stdin=subprocess.PIPE)
        else:
            p = subprocess.Popen(['lpr','-P%s'%self.queue], stdin=subprocess.PIPE)
        if type(commands) == bytes:
            p.communicate(commands)
        else:
            p.communicate(str(commands).encode())
        p.stdin.close()

    def _output_win(self, commands):
        raise Exception('Not yet implemented')
    
    def output(self, commands):
        assert self.queue is not None
        if sys.platform.startswith('win'):
            self._output_win(commands)
        else:
            self._output_unix(commmands)

    def _getqueues_unix(self):
        queues = []
        output = subprocess.check_output(['lpstat','-p'], universal_newlines=True)
        for line in output.split('\n'):
            if line.startswith('printer'):
                queues.append(line.split(' ')[1])
        return queues

    def _getqueues_win(self):
        raise Exception('Not yet implemented')

    def getqueues(self):
        if sys.platform.startswith('win'):
            return self._getqueues_win()
        else:
            return self._getqueues_unix()

    def setqueue(self, queue):
        self.queue = queue

    def setup(self, direct_thermal=None, label_height=None, label_width=None):
        commands = '\n'
        if direct_thermal:
            commands += ('OD\n')
        if label_height:
           commands += ('Q%s,%s\n'%(label_height[0],label_height[1]))
        if label_width:
            commands += ('q%s\n'%label_width)
        self.output(commands)

    def store_graphic(self, name, filename):
        assert filename.endswith('.pcx')
        commands = '\nGK"%s"\n'%name
        commands += 'GK"%s"\n'%name
        size = os.path.getsize(filename)
        commands += 'GM"%s"%s\n'%(name,size)
        self.output(commands)
        self.output(open(filename,'rb').read())

if __name__ == '__main__':
    z = zebra()
    print 'Printer queues found:',z.getqueues()
    z.setqueue('zebra_python_unittest')
    z.setup(direct_thermal=True, label_height=(406,32), label_width=609)    # 3" x 2" direct thermal label
    z.store_graphic('logo','logo.pcx')
    label = """
N
GG419,40,"logo"
A40,80,0,4,1,1,N,"Tangerine Duck 4.4%"
A40,198,0,3,1,1,N,"Duty paid on 39.9l"
A40,240,0,3,1,1,N,"Gyle: 127     Best Before: 16/09/2011"
A40,320,0,4,1,1,N,"Pump & Truncheon"
P1
"""
    z.output(label)

