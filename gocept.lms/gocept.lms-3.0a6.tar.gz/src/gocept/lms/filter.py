# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import urlparse
import zope.component
import gocept.lms.interfaces


HOST_BLACKLIST = set(['localhost'])


def allow_host(host):
    return host not in HOST_BLACKLIST
