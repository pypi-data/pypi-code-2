# Copyright 2011 Dustin C. Hatch
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''Stub controller classes

These classes can be used as base classes for controllers. While any
callable can technically be a controller, using a class that inherits
from one or more of these classes can make things significantly easier.

:Created: Mar 27, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''

import milla
import os

__all__ = ['Controller', 'FaviconController']

class Controller(object):
    '''The base controller class
    
    This class simply provides empty ``__before__`` and ``__after__``
    methods to facilitate cooperative multiple inheritance.
    '''

    def __before__(self, request):
        pass

    def __after__(self, request):
        pass

class FaviconController(Controller):
    '''A controller for the "favicon"
    
    This controller is specifically suited to serve a site "favicon" or
    bookmark icon. By default, it will serve the *Milla* icon, but you
    can pass an alternate file time to the constructor.
    
    :param icon: Path to an icon to serve    
    '''

    def __init__(self, icon=None):
        if not icon:
            icon = os.path.join(os.path.dirname(milla.__file__), 'milla.ico')
        try:
            self.icon = open(icon)
        except (IOError, OSError):
            self.icon = None

    def __call__(self, request):
        if not self.icon:
            raise milla.HTTPNotFound
        response = milla.Response()
        response.app_iter = self.icon
        response.headers['Content-Type'] = 'image/x-icon'
        return response
