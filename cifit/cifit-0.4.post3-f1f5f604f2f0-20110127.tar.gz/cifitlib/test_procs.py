#!/usr/bin/env python
# encoding: utf-8
"""
test_procs.py

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2009, 2010 Craig Sawyer (csawyer@yumaed.org). All rights reserved. see LICENSE.
"""

import nose
import procs

def test_isRunning():
    assert procs.isRunning('launchd')

def test_getByCommand():
	assert len(procs.getProcesses().getByCommand('login')) == 8

if __name__ == '__main__':
    nose.run()

