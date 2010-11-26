"""
Playing with ncurses in Python to scroll up and down, left and right, through a list of data that is periodically refreshed. 
"""

import curses, sys

class Scroll:

    # what should be printed at the bottom of the screen?
    instructionString = "Scroll with arrow keys. U page up, D page down, H home, Q quit."

    # at which row and col must we draw the screen output?
    offsetV = 0
    offsetH = 0
    
    # the main screen object
    screen = None

    # the line position at which we're currently drawing
    currentLinePosition = 0
    currentXPosition = 0

    # set up the screen
    def screenSetup(self):
        self.screen = curses.initscr()
        self.screen.nodelay(1)
        curses.noecho()
        curses.cbreak()

    # restore sensible options to the terminal 
    def screenTeardown(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # act on certain keys
    def processKeyPress(self):
        key = self.screen.getch()
        if key == 113: raise KeyboardInterrupt		# q for quit
        elif key == 117: self.offsetV -= curses.LINES   # u - pg up
        elif key == 100: self.offsetV += curses.LINES   # d - pg down
        elif key == 104: self.offsetH = 0               # h - home
        elif key == 65: self.offsetV -= 1               # up
        elif key == 66: self.offsetV += 1               # down
        elif key == 67: self.offsetH += 1               # right
        elif key == 68: self.offsetH -= 1               # left
        if key < 0: key = 0
        return [key, chr(key)]

    # clear the screen
    def clearScreen(self):
        self.screen.clear()

    # draw a new line to the screen, takes an argument as to whether the screen should be immediately refreshed or not
    def drawString(self, newLine, refresh = True):
        self.screen.addstr(self.currentLinePosition, self.currentXPosition, newLine)
        if newLine.endswith('\n'):
            self.currentLinePosition += 1
            self.currentXPosition = 0
        else:
            self.currentXPosition += len(newLine)
        if refresh: self.screen.refresh()

    # draw the screen
    def drawScreen(self, data):
        # clear the screen
        self.screen.clear()
        numLinesTotal = len(data)
        # reserve the bottom line for instructions
        numLinesAvailable = curses.LINES - 1
        # can we fit everything on the screen?
        topLine = 0
        if numLinesTotal > numLinesAvailable:
            topLine = numLinesTotal - numLinesAvailable
        # check the offsets, vertical and horizontal
        self.offsetV = min(0, self.offsetV)
        self.offsetV = max(-1 * topLine, self.offsetV)
        self.offsetH = min(0, self.offsetH)
        # which line are we showing at the top?
        topLine += self.offsetV
        topLine = max(topLine, 0)
        bottomLine = min(numLinesTotal, topLine + numLinesAvailable)
        # add the lines to the curses screen one by one
        self.currentLinePosition = 0
        for lineNum in range(topLine, bottomLine):
            #data[lineNum] = "%03i-%03i-%03i-%03i-" % (topLine, lineNum, self.offsetV, self.offsetH) + data[lineNum]
            # truncate long lines...
            data[lineNum] = data[lineNum][-1 * self.offsetH:(-1 * self.offsetH) + curses.COLS]
            # and add the data to the screen
            self.screen.addstr(self.currentLinePosition, 0, data[lineNum] + '\n')
            self.currentLinePosition += 1
        self.screen.addstr(numLinesAvailable, 0, "Showing line %i to %i of %i. Column offset %i. %s" % (topLine, bottomLine, numLinesTotal, self.offsetH, self.instructionString))
        self.screen.refresh()

    # set and get the instruction string at the bottom
    def getInstructionString(self):
        return self.instructionString
    def setInstructionString(self, newString):
        self.instructionString = newString

# end of file

