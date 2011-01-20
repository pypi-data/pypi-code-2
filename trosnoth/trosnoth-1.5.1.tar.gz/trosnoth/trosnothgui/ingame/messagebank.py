# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
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

from trosnoth.gui.framework import framework, elements
from trosnoth.gui import colours as guiColours

from trosnoth.gui.common import RelativeLocation

class MessageBank(framework.CompoundElement):
    '''Defines the implementation for a queue of Messages to be displayed
    on screen'''


    def __init__(self, app, maxSize, maxLength, startPt, L_R, U_D, font,
            timeLimit = 10):
        '''Parameters:
        maxSize: the number of lines that can be displayed at any one time
        maxLength: the maximum length of a line

        startPt is the corner closest to the edge of the screen
        that a message will get. For example, if aligned top left, this point
        will specify the top left position of the most recent message

        L_R defines the alignment of the text that appears
        U_D defines whether the text will be coming from the top or the
        bottom'''
        super(MessageBank, self).__init__(app)
        self.timeLimit = timeLimit
        if maxSize <= 0:
            raise ValueError, 'Must be able to display at least one message'
        # Stores all messages again, so that we have an order
        self.elements = []
        self.font = font
        self.maxSize = maxSize
        self.maxLength = maxLength
        self.currentLength = 0
        # Left or right-aligned; at top or bottom of screen.
        self.L_R = L_R
        self.U_D = U_D
        self.startPt = startPt

    def newMessage(self, text, colour):
        text = self.breakUp(text)
        if not text.__contains__('\n'):
            self.newIndividual(Message(self.app, text, colour, self,
                    self.timeLimit))
            return
        tempMessages = []
        i = 0
        while 1:
            while i < len(text) and text[i] != '\n':
                i+= 1
            tempMessages.append(Message(self.app, text[:i], colour, self,
                    self.timeLimit))
            text = text[i+1:]
            if i == len(text):
                break
            i = 0

        if self.U_D == "bottom":
            inc = 1
            j = 0
        else:
            inc = -1
            j = len(tempMessages) - 1

        while j >= 0 and j < len(tempMessages):
            self.newIndividual(tempMessages[j])
            j += inc

    def newIndividual(self, newMessage):
        if self.currentLength >= self.maxSize:
            self.delMessage(True)
        for message in self.elements:
            message.downByOne()

        self.elements.append(newMessage)
        self.currentLength += 1

    def delMessage(self, popped = False):
        # We'll always be deleting the oldest message
        self.elements.pop(0)
        self.currentLength -= 1

    def breakUp(self, text):
        '''Breaks the text up into seperate lines of max 50 chars. If there's
        a space within 20 characters of the end, it will break there, otherwise
        it will simply cut the current word in half'''
        maxLength = 50
        minLength = 30
        lineDelimiters = (' ', '\t', '-')
        i = 0
        pos = 0
        modPos = 0
        while i < len(text):
            char = text[i]
            # Line Delimiter found; make a record of it
            if char in lineDelimiters:
                pos = i + 1
            modPos += 1
            # Gone too far; break the line
            if modPos >= maxLength:

                # No line delimiters close to the end of this line; break the
                # current word
                if pos < minLength:
                    text = text[:i] + '-\n' + text[i:]
                    i += 2
                # Break at the latest line delimiter
                else:
                    text = text[:pos - 1] + '\n' + text[pos:]
                    # Since a new line has begun back a bit, set it back
                    i = pos
                modPos = 0
                pos = 0
            i+= 1
        # Remove trailing whitespace
        while text.endswith('\n') or text.endswith(' '):
            text = text[:len(text) - 1]
        return text

    def deleteAll(self):
        while len(self.elements) > 0:
            self.delMessage(True)

class Message(elements.TextElement):
    '''Sprite object that every player has which indicates the player's nick.'''
    def __init__(self, app, text, colour, messageBank, timeLimit):
        self.messageBank = messageBank
        if not colour:
            colour = app.theme.colours.grey
        super(Message, self).__init__(app, text, self.messageBank.font,
                                      self.messageBank.startPt,
                                      colour, shadow = True)
        if colour == guiColours.shadowDefault:
            self.setShadowColour(guiColours.shadowAgainstGrey)

        self.timeLeft = timeLimit

    def __repr__(self):
        return 'Message object: "%s"' % self.getText()

    def downByOne(self):
        # Defines where on the screen it is displayed
        if self.messageBank.U_D == "top":
            pos = RelativeLocation(self.pos, (0,
                    self.image.font.getHeight(self.app)))
        else:
            pos = RelativeLocation(self.pos, (0,
                    -self.image.font.getHeight(self.app)))
        self.setPos(pos)

    def tick(self, deltaT):
        if self.timeLeft is not None:
            self.timeLeft -= deltaT
            if self.timeLeft <=0:
                self.messageBank.delMessage()
