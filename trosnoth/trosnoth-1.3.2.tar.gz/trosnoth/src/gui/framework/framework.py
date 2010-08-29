# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
from trosnoth.src.utils.utils import timeNow, RunningAverage

class Element(object):
    active = True
    hasFocus = False

    def __init__(self, app):
        self.app = app
        self.drawTime = RunningAverage(500)
    
    def processEvent(self, event):
        '''Processes the specified event and returns the event if it should
        be passed on, or None if it has been caught.'''
        return event

    def tick(self, deltaT):
        '''Gives the element a chance to update itself. deltaT is the time
        in seconds since the last tick cycle.'''

    def draw(self, screen):
        '''Gives the element a chance to draw itself onto the screen.'''

    def gotFocus(self):
        pass
    def lostFocus(self):
        pass
    
class CompoundElement(Element):
    # List of elements in order that they are drawn on screen. That is,
    # the first element in the list is drawn at the bottom.

    def __init__(self, app):
        super(CompoundElement, self).__init__(app)
        self.elements = []
    
    def processEvent(self, event):
        elements = list(self.elements)
        elements.reverse()
        for element in elements:
            event = element.processEvent(event)

            if event is None or not self.app._running:
                return None
        return event

    def tick(self, deltaT):
        try:
            for element in self.elements:
                if not element:
                    print self, self.elements
                element.tick(deltaT)
        except RuntimeError, e:
            if e.__str__() == 'maximum recursion depth exceeded':
                print 'ERROR: Infinite loop of elements:'
                if hasattr(element, 'elements'):
                    print element, 'contains', element.elements
            raise

    def draw(self, screen):
        for element in self.elements:
            t = timeNow()
            element.draw(screen)
            element.drawTime.noteValue(timeNow() - t)

    def getSlowestChild(self):
        result = None
        t = 0
        for element in self.elements:
            if element.drawTime.mean >= t:
                result = element
                t = element.drawTime.mean
        return result

    def clearFocus(self):
        self.setFocus(None)
        
    def setFocus(self, element):
        if element and element not in self.elements:
            return

        if element and element.hasFocus:
            return
            
        for el in self.elements:
            if el.hasFocus:
                el.hasFocus = False
                el.lostFocus()
        if element:
            element.hasFocus = True
            element.gotFocus()

class TabFriendlyCompoundElement(CompoundElement):
    def __init__(self, app):
        super(TabFriendlyCompoundElement, self).__init__(app)
        self.tabOrder = []

    def tabNext(self, sender):
        assert sender in self.tabOrder
        i = self.tabOrder.index(sender)
        i += 1
        i %= len(self.tabOrder)
        self.setFocus(self.tabOrder[i])
        
            
class SwitchingElement(Element):
    def __init__(self, app, elements=None, choice=None):
        super(SwitchingElement, self).__init__(app)
        if elements == None:
            self.elements = {}
        else:
            self.elements = elements

        self.setChoice(choice)

    def setChoice(self, choice):
        if isinstance(choice, Element):
            self.element = choice
        else:
            self.element = self.elements.get(choice, None)

    def processEvent(self, event):
        if not self.element:
            return event
        return self.element.processEvent(event)

    def tick(self, deltaT):
        if self.element:
            self.element.tick(deltaT)

    def draw(self, screen):
        if self.element:
            self.element.draw(screen)
