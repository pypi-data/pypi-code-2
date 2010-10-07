# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py 42329 2010-05-25 08:28:32Z sylvain $

from zope.publisher.interfaces.http import IHTTPRequest


class IRESTLayer(IHTTPRequest):
    """To this layer are registered the REST components.
    """


class MethodNotAllowed(Exception):
    """This method is not allowed.
    """

