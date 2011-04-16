#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2011 Doug Hellmann.  All rights reserved.
#
"""Manage temporary virtual environments.
"""

import logging
import pkg_resources

log = logging.getLogger(__name__)

from virtualenvwrapper.user_scripts import make_hook, run_global

def initialize_source(args):
    """Define mktmpenv.
    """
    return pkg_resources.resource_string(__name__, 'tmpenv.sh')

def get_env_details(args):
    return

