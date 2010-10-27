"""
Playing with ncurses in Python to scroll up and down, left and right, through a list of data that is periodically refreshed. 
"""

import curses, sys

class Scroll:

    # at which row and col must we draw the screen output?
    offsetV = 0
    offsetH = 0
    
    # the main screen object
    screen = None

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
        if key == 113: sys.exit(1)                      # q for quit
        elif key == 117: self.offsetV -= curses.LINES   # u - pg up
        elif key == 100: self.offsetV += curses.LINES   # d - pg down
        elif key == 104: self.offsetH = 0               # h - home
        elif key == 65: self.offsetV -= 1               # up
        elif key == 66: self.offsetV += 1               # down
        elif key == 67: self.offsetH += 1               # right
        elif key == 68: self.offsetH -= 1               # left
        return key

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
        lineCounter = 0
        for lineNum in range(topLine, bottomLine):
            #data[lineNum] = "%03i-%03i-%03i-%03i-" % (topLine, lineNum, self.offsetV, self.offsetH) + data[lineNum]
            # truncate long lines...
            data[lineNum] = data[lineNum][-1 * self.offsetH:(-1 * self.offsetH) + curses.COLS]
            # and add the data to the screen
            self.screen.addstr(lineCounter, 0, data[lineNum] + '\n')
            lineCounter += 1
        self.screen.addstr(numLinesAvailable, 0, "Showing line %i to %i of %i. Column offset %i. Scroll with arrow keys. U page up, D page down, H home." % (topLine, bottomLine, numLinesTotal, self.offsetH))
        self.screen.refresh()

# end of file

