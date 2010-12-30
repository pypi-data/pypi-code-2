#! /usr/bin/env python

# Public domain
# Idea from Georg Brandl. Foolishly implemented by Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk

import sys


def execute(arg):
    exec (compile(arg, '<cmdline>', 'single'))

def main(args):
    if not args:
        print ('Idea from Georg Brandl. Foolishly implemented by Michael Foord')
        sys.exit()

    first = args[0]
    try:
        execute(first)
    except NameError:
        try:
            __import__(first)
        except ImportError:
            # easy way to re-raise the original error
            execute(first)
        else:
            try:
                mod = sys.modules[first]
            except KeyError:
                print ('%s is not a valid module name' % first)
                sys.exit(1)
        
            location = getattr(mod, '__file__', 'None')
            if location.endswith('.pyc'):
                location = location[:-1]
            print (location)

    for x in args[1:]:
       execute(x)


if __name__ == '__main__':
    main(sys.argv[1:])
