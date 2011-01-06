"""Word completion for GNU readline 2.0.

This requires the latest extension to the readline module. The completer
completes keywords, built-ins and globals in a selectable namespace (which
defaults to __main__); when completing NAME.NAME..., it evaluates (!) the
expression up to the last dot and completes its attributes.

It's very cool to do "import sys" type "sys.", hit the
completion key (twice), and see the list of names defined by the
sys module!

Tip: to use the tab key as the completion key, call

    readline.parse_and_bind("tab: complete")

Notes:

- Exceptions raised by the completer function are *ignored* (and
generally cause the completion to fail).  This is a feature -- since
readline sets the tty device in raw (or cbreak) mode, printing a
traceback wouldn't work well without some complicated hoopla to save,
reset and restore the tty state.

- The evaluation of the NAME.NAME... form may cause arbitrary
application defined code to be executed if an object with a
__getattr__ hook is found.  Since it is the responsibility of the
application (or the user) to enable this feature, I consider this an
acceptable risk.  More complicated expressions (e.g. function calls or
indexing operations) are *not* evaluated.

- GNU readline is also used by the built-in functions input() and
raw_input(), and thus these also benefit/suffer from the completer
features.  Clearly an interactive application can benefit by
specifying its own completer function and using raw_input() for all
its input.

- When the original stdin is not a tty device, GNU readline is never
used, and this module (and the readline module) are silently inactive.

"""

import __builtin__
import __main__
import inspect
import keyword
import readline
import re
import sys
import termios,fcntl,struct

if 1:
    debugfile = open('/tmp/rlcompleter.log','w')
    def debug(obj):
        debugfile.write(str(obj).strip()+'\n')
        debugfile.flush()
else:
    debug = lambda obj: None

def public_attr(attr):
    if attr.startswith('__') and attr.endswith('__'):
        return False
    else:
        return True

class Completer:
    def __init__(self, namespace = None):
        """Create a new completer for the command line.

        Completer([namespace]) -> completer instance.

        If unspecified, the default namespace where completions are performed
        is __main__ (technically, __main__.__dict__). Namespaces should be
        given as dictionaries.

        Completer instances should be used as the completion mechanism of
        readline via the set_completer() call:

        readline.set_completer(Completer(my_namespace).complete)
        """

        if namespace and not isinstance(namespace, dict):
            raise TypeError,'namespace must be a dictionary'

        # Don't bind to namespace quite yet, but flag whether the user wants a
        # specific namespace or to use __main__.__dict__. This will allow us
        # to bind to __main__.__dict__ at completion time, not now.
        if namespace is None:
            self.use_main_ns = 1
        else:
            self.use_main_ns = 0
            self.namespace = namespace

    def gettermsize(self):
        call = fcntl.ioctl(0,termios.TIOCGWINSZ,"\000"*8)
        height,width = struct.unpack( "hhhh", call ) [:2]
        self.width = width
        self.height = height

    def getdoc(self, o):
        if type(o) not in [str, int, bool, float]:
            if hasattr(o,'__doc__'):
                if o.__doc__:
                    return o.__doc__
        return '-'

    def display_matches(self, text, matches, maxlen):
        print '<tab-completion>'
        fmt='\t%-' + str(maxlen+1) + 's = %-14s %-14s %s'
        print fmt % ('[object]', '[value]', '[type]', '[documentation]')
        print
        i = 0
        self.gettermsize()
        for m in matches:
            v = '-'
            if keyword.iskeyword(m):
                t = 'keyword'
                d = '-'
            else:
                o = eval(m, self.namespace)
                t = (str(type(o))[7:-2])[0:14]
                d = self.getdoc(o).strip().splitlines()
                if type(o) in [int, bool, float, str]:
                    v = str(o)[0:14]
            print fmt % (m, v, t, d[0])
            i += 1
            if((i %  self.height) == self.height - 2):
                print "more...",
                c = sys.stdin.read(1)
                print
                if c == 'q':
                    break
                i += 1
        print sys.ps1 + readline.get_line_buffer(),

    def display_info(self, fn, fdecl):
        print '<tab-getinfo>'
        print
        print '[declaration]'
        print fdecl
        print
        print '[value]'
        print str(fn)
        if fn is int:
            print hex(fn)
        print
        print '[documentation]'
        print self.getdoc(fn)
        print sys.ps1 + readline.get_line_buffer(),

    def complete(self, text, state):
        """Return the next possible completion for 'text'.
        This is called successively with state == 0, 1, 2, ... until it
        returns None.  The completion should begin with 'text'.
        """
        if self.use_main_ns:
            self.namespace = __main__.__dict__
        if state == 0:
            if text == '':
            	return '\t'
            if "." in text:
                self.matches = self.attr_matches(text)
            else:
                self.matches = self.global_matches(text)
        try:
            return self.matches[state]
        except IndexError:
            return None

    def filter_words(self, words, text):
        if text in words:
            # information mode
            return self.getinfo(text)
        else:
            # completion mode
            matches = []
            n = len(text)
            for word in words:
                if word[:n] == text:
                    matches.append(word)
            return matches

    def getinfo(self, text):
        obj = eval(text, self.namespace)
        if(obj):
            isfunct = inspect.isfunction(obj)
            ismethod = inspect.ismethod(obj)
            # type: function
            if isfunct or ismethod:
                args, vargs, kwargs, defaults = inspect.getargspec(obj)
                if(not defaults):
                    defaults = []
                if ismethod:
                    args = args[1:]
                i = 0
                params = ''
                for p in args:
                    if params:
                        params += ', '
                    params += p
                    j = i - len(args) + len(defaults)
                    if(j >= 0):
                        params += '=' + str(defaults[j])
                    i += 1
                if vargs:
                    if params:
                        params += ', *'
                    params += vargs
                if kwargs:
                    if params:
                        params += ', **'
                    params += kwargs
                self.display_info(obj, text + '(' + params + ')')
                # completion: add a '('
                return [text + '(']
            else:
                # other types
                self.display_info(obj, text)
        # no completion
        return [text]

    def global_matches(self, text):
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in functions and names currently
        defined in self.namespace that match.

        """
        matches  = self.filter_words(filter(public_attr, self.namespace), text)
        matches += self.filter_words(filter(public_attr, __builtin__.__dict__), text)
        matches += self.filter_words(filter(public_attr, keyword.kwlist), text)
        return matches

    def attr_matches(self, text):
        """Compute matches when text contains a dot.

        Assuming the text is of the form [NAME.]*, and is
        evaluatable in self.namespace, it will be evaluated and its attributes
        (as revealed by dir()) are used as possible completions.

        """
        m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
        if not m:
            return
        expr = m.group(1)
        obj = eval(expr, self.namespace)
        words = [expr + '.' + attr for attr in filter(public_attr, dir(obj))]
        return self.filter_words(words, text)

__completer__ = Completer()
readline.set_completer(__completer__.complete)
readline.set_completion_display_matches_hook(__completer__.display_matches)
readline.parse_and_bind("tab: complete");
