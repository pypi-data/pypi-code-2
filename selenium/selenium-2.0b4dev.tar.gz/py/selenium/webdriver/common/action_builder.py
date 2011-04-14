# Copyright 2008-2011 WebDriver committers
# Copyright 2008-2011 Google Inc.
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

from mouse import Mouse
from keyboard import Keyboard
from selenium.common.exceptions import WebDriverException

class ActionBuilder(object):

    actions = []

    def __init__(self, mouse, keyboard):
        '''

        '''
        self.mouse = mouse
        self.keyboard = keyboard

    def key_down(self, key):
        pass


    def perform(self):
        for action in actions:
            if hasattr(Mouse, action):
                value = getattr(Mouse, action)
            elif hasattr(Keyboard, action):
                value = getattr(Keyboard, action)
            else:
                raise WebDriverException("Action can not be performed with mouse or keyboard")

