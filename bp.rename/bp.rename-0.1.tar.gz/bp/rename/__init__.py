#!/usr/bin/env python2.6
# encoding: utf-8
"""
__init__.py

Created by disko on 2010-08-28.
Copyright (c) 2010 binary punks. All rights reserved.
"""

# IMPORTS

import baker
import os
import os.path
import sys
import table
import terminal


# IMPLEMENTATION

@baker.command
def replace(pattern, replace, *files):
    """replace every occurance of <pattern> with <replace> in all filenames"""
    
    old_filenames = []
    new_filenames = []
    
    for f in files:
        oldname = f.split("/")[-1]
        old_filenames.append(oldname)
        
        newname  = oldname.replace(pattern, replace)
        new_filenames.append(newname)
    
    rename_tuples = [ t for t in zip(old_filenames, new_filenames) if t[0] != t[1] ]
    
    t = table.Table(rename_tuples)
    print "\n%s\n" % t.draw()
    
    yn = terminal.Terminal().requestSingleCharAnswerFromUser("Is this what you want?")
    
    if yn == "y":
        for names in zip(files, new_filenames):
            
            src = names[0]
            
            if not os.path.exists(src):
                print "No such file:", src
                continue
            
            directory_path = os.path.dirname(src)
            dst = os.path.join(directory_path, names[1])
            
            if dst == src:
                continue
            
            if os.path.exists(dst):
                print "Cannot rename '%s' to '%s': a file with the target name already exists." % (src, dst, )
                continue
            
            os.rename(src, dst)
        
        print "\ndone.\n"
    elif yn == "n":
        print "\naborted.\n"


@baker.command
def remove(pattern, *files):
    """removes every occurance of <pattern> from all filenames"""
    
    replace(pattern, "", *files)


def main():
    """main entry point"""
    
    try:
        baker.run()
    except baker.CommandError, e:
        print "\n%s\n" % e
        print "Run '%s -h' for help.\n" % os.path.split(sys.argv[0])[-1]


if __name__ == '__main__':
    main()
