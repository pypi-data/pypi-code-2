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


class Mouse(object):
 
    def click(self, element):
        ''' Clicks on the element 
            @args 
              element - Webelement that you would like to click on
        '''
        element.click()

    def double_click(self, element):
        ''' Double clicks on the element
            @args
                element - WebElement that you would like to double click on
        '''
        element.double_click()

    def context_click(self, element):
        ''' Executes a context click (right-click) on the element
            @args
                element - WebElement that you would like to context click on

        '''
        element.context_click()

    def down(self, element):
        ''' Does a mouse down on the element
            @args
                element - WebElement that you would like to mouse down on
        '''
        element.mouse_down()

    def up(self, element):
        ''' Does a mouse up on the element
            @args
                element - Webelement that you would like to mouse up on
        '''
        element.mouse_up()

    def move_to(self, element, down_by=None, right_by=None):
        ''' Does a mouse up on the element
            @args
                element - Webelement that you would to move to
                down_by - Offset from that location
                right_by - Offset from that location
        '''
        element.mouse_move_to(element.id, down_by, right_by):
