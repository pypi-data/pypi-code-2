#!/usr/bin/env python3

"""simple control of ascii terminal output."""

from sys import stdout
CSI = '\x1b['
def write(str):
    home()
    stdout.write(str)
def control(str):
    stdout.write(CSI+str)
    stdout.flush()
def erase():
    control('2K')
def home():
    control('G')
def priorline():
    control('A')
def hide():
    control('?25l')
def show():
    control('?25h')

def blue(text):
    return CSI+"1;34m" + text + CSI+"0m"
def red(text):
    return CSI+"1;31m" + text + CSI+"0m"
def lightblue(text):
    return CSI+"0;34m" + text + CSI+"0m"
def lightred(text):
    return CSI+"0;31m" + text + CSI+"0m"
