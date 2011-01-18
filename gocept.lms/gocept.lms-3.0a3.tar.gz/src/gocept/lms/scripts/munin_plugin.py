#!/usr/bin/env python
# vim:fileencoding=utf-8
# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""LMS graph definitions for munin.

Symlink this script to /etc/munin/plugins/ and name it appropriately.

"""

from gocept.munin.client import SimpleGraph, main


class queuesize(SimpleGraph):
    key = name = 'queue-size'
    title = 'Checking queue size'
    category = 'LMS'


class threadpool(SimpleGraph):
    key = name = 'thread-pool'
    title = 'Active checker threads'
    category = 'LMS'

main()
