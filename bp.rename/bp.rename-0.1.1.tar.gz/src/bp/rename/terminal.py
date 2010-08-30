#!/usr/bin/env python2.6
# encoding: utf-8
"""
terminal.py

Created by disko on 2010-08-28.
Copyright (c) 2010 binary punks. All rights reserved.
"""

# IMPORTS

import fcntl
import os
import sys
import termios


# CONFIGURATION

# IMPLEMENTATION

class Terminal(object):
    """Helper class for command line sessions"""
    
    def __init__(self):
        
        super(Terminal, self).__init__()
    
    
    def requestSingleCharAnswerFromUser(self, question="Are you sure (y/n)?", allowed_answers=["y", "n", ]):
        """Ask the user a question and wait for a valid (single char) answer"""
        
        fd = sys.stdin.fileno()
        
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
        
        sys.stdout.write("%s (%s) " % (question, "/".join(allowed_answers), ))
        while True:
            try:
                answer = sys.stdin.read(1)
            except IOError:
                continue
            
            if answer in allowed_answers:
                break
        
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        
        print
        
        return answer
    
    

