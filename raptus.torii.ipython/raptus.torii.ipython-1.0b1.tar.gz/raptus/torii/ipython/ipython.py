import sys
import string
import StringIO
import cPickle
from raptus.torii.interpreter import AbstractInterpreter
from raptus.torii import config
from raptus.torii import carrier
from IPython.ipmaker import make_IPython
from IPython.ultraTB import AutoFormattedTB as BaseAutoFormattedTB
from IPython.iplib import SyntaxTB as BaseSyntaxTB
from pprint import PrettyPrinter

def result_display(self, arg):
    self.outStringIO = StringIO.StringIO()
    if self.rc.pprint:
        out =  PrettyPrinter().pformat(arg)
        if '\n' in out:
            self.outStringIO.write('\n')
        print >> self.outStringIO, out
    else:
        print >> self.outStringIO, repr(arg)
    return None 

class AutoFormattedTB(BaseAutoFormattedTB):
    errStringIO = StringIO.StringIO()
    def __call__(self, *args, **kw):
        self.errStringIO = StringIO.StringIO()
        kw.update(dict(out=self.errStringIO))
        return BaseAutoFormattedTB.__call__(self, *args, **kw)

class SyntaxTB(BaseSyntaxTB):
    errStringIO = StringIO.StringIO()
    def __call__(self, etype, value, elist):
        self.errStringIO = StringIO.StringIO()
        self.last_syntax_error = value
        print >> self.errStringIO, self.text(etype,value,elist)

class Completer(object):
    
    def __init__(self, sock):
        self.sock = sock
        self.memo = {'':[config.tab_replacement]}
        
    def completer(self, text, state):
        if not self.memo.has_key(text):
            cPickle.dump(carrier.FetchCompleter(text,state), self.sock.makefile())
            result = cPickle.load(self.sock.makefile())
            self.memo.update({text:result.result})
        for cmd in self.memo[text]:
            if cmd.startswith(text):
                if not state:
                    return cmd
                else:
                    state -= 1

class InitReadline(object):
    
    def __init__(self, rc):
        self.rc = rc
    
    def __call__(self, client):
        import IPython.rlineimpl as readline
        readline.parse_and_bind('tab: complete')
        readline.set_completer(Completer(client.sock).completer)

        sys.modules['readline'] = readline
        
        # Remove some chars from the delimiters list.  If we encounter
        # unicode chars, discard them.
        delims = readline.get_completer_delims().encode("ascii", "ignore")
        delims = delims.translate(string._idmap,
                                  self.rc.readline_remove_delims)
        readline.set_completer_delims(delims)
        # otherwise we end up with a monster history after a while:
        readline.set_history_length(1000)

class IPython(AbstractInterpreter):
    
    def __init__(self, locals):
        self.locals = locals
        self.interpreter = make_IPython(argv=[],embedded=True,user_global_ns=self.locals)
        self.interpreter.set_hook('result_display',result_display)
        color = self.interpreter.rc.colors
        self.interpreter.InteractiveTB = AutoFormattedTB(mode = 'Plain',
                                                         color_scheme=color,
                                                         tb_offset = 1)
        self.interpreter.SyntaxTB = SyntaxTB(color_scheme=color)
        
    def getReadline(self):
        return InitReadline(self.interpreter.rc)
    
    def getPrompt1(self):
        return str(self.interpreter.outputcache.prompt1)
    
    def getPrompt2(self):
        return str(self.interpreter.outputcache.prompt2)

    def getPromptOut(self):
        return str(self.interpreter.outputcache.prompt_out)

    def resetStream(self):
        self.interpreter.outStringIO = StringIO.StringIO()
        self.interpreter.InteractiveTB.errStringIO = StringIO.StringIO()
        self.interpreter.SyntaxTB.errStringIO = StringIO.StringIO()

    def push(self, line):
        return self.interpreter.push(line)
    
    def runcode(self, code):
        self.interpreter.runcode(code)
        
    def complete(self, text):
        return self.interpreter.complete(text)
        
    def getStdout(self):
        return self.interpreter.outStringIO
    
    def getErrorStream(self):
        return self.interpreter.InteractiveTB.errStringIO
    
    def getSyntaxErrorStream(self):
        return self.interpreter.SyntaxTB.errStringIO


