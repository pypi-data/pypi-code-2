#!/usr/bin/env python
# encoding: utf-8
"""
auth.py

Created by Keith Fahlgren on 
Mon Jan 19 20:38:04 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

import base64

class BasicAuth:
    """A class for adding BasicAuth headers."""
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def headers(self):
        """A header for the authentication."""
        raw = "%s:%s" % (self.username, self.password)
        auth = 'Basic %s' % base64.encodestring(raw).strip()
        return {'Authorization': auth}

