#!/usr/bin/env python
# encoding: utf-8
"""
util.py

Created by dan mackinlay on 2010-12-15.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""
import subprocess
import shlex

def run_process(plain_old_command_string):
    """run a command given in a string and return the output"""
    return subprocess.Popen(
      shlex.split(plain_old_command_string),
      stdout=subprocess.PIPE
    ).communicate()[0]

def get_code_revision():
    """return revision number of hg tip"""
    return run_process("hg tip --template {node}")
