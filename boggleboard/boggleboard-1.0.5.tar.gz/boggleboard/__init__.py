#!/usr/bin/env python
#
# Copyright 2009 Sebastian Raaphorst.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""boggleboard.py

A package to generate and manipulate Boggle-style boards. Boards of different
sizes can be randomly generated, and given a list of acceptable words (in the
form of a Trie - see below), the package can find all words in a particular
Boggle board.

Note that this module contains the following structures:

* defaultOldDice16: a list of list of strings representing the 16 default
                    dice in the original 4x4 Boggle board.
* defaultDice16: a list of lists of strings representing the 16 default dice
                 in a standard 4x4 Boggle board.
* defaultDice25: a list of lists of strings representing the 25 default dice
                 in a standard 5x5 Big Boggle board.
* defaultChallengeDie: a list of strings representing the default special
                       challenge die in some versions of Boggle.
* Trie class: a class representing a trie, which the BoggleBoard findWords
              method uses in order to locate valid words in a Boggle board.
              Note that a word list based on YAWL:
                   http://www.gtoal.com/wordgames/yawl
              is included in the yawl submodule in variable wordList, and thus
              a trie representing YAWL can be created simply via:
                 import boggleboard
                 import boggleboard.yawl
                 t = boggleboard.Trie(boggleboard.yawl.wordList)
* createWordTrie: a convenience function to create a Trie from a file which
                  contains one word per line. Note that calling this with the
                  file yawl dramatically saves time over the above method, as
                  it skips the tediously long step of importing a huge module.
* AbstractBoggleBoard: abstract implementation of a Boggle board.
* RectangularBoggleBoard: a rectangular boggle board.
* BoggleBoard: standard square boggle board.
* RectangularToroidalBoggleBoard: a rectangular toroidal boggle board.
* ToroidalBoggleBoard: standard square toroidal boggle board.
* Anagram: an anagram word descrambler. (Note: only finds single words.)

By using a graph to represent the adjacency of positions in a board, subclasses
of AbstractBoggleBoard can be created to represent any geometric board.

To simply create a random Boggle board:
    import boggleboard
    b = boggleboard.BoggleBoard()
    b.generateBoard()

To create a specific board, say r1=SGTI r2=YAKH r3=ASRN r4=PTOD, and find all
words of length 4 or higher in YAWL:
    import boggleboard
    import boggleboard.yawl
    t = boggleboard.Trie(boggleboard.yawl.wordList)
    b = boggleboard.BoggleBoard('SGTIYAKHASRNPTOD')
    # Or alternatively b = boggleboard.BoggleBoard(['S', 'G', 'T', 'I', 'Y', ...])
    # Note we need to use a list if 'QU' is on the board.
    b.findWords(t, 4)

By Sebastian Raaphorst, 2009."""

import sys
import random


# The old dice used by original Boggle in a 4x4 grid.
defaultOldDice16 = [
    ['a', 'a', 'c', 'i', 'o', 't'],
    ['a', 'h', 'm', 'o', 'r', 's'],
    ['e', 'g', 'k', 'l', 'u', 'y'],
    ['a', 'b', 'i', 'l', 't', 'y'],
    ['a', 'c', 'd', 'e', 'm', 'p'],
    ['e', 'g', 'i', 'n', 't', 'v'],
    ['g', 'i', 'l', 'r', 'u', 'w'],
    ['e', 'l', 'p', 's', 't', 'u'],
    ['d', 'e', 'n', 'o', 's', 'w'],
    ['a', 'c', 'e', 'l', 'r', 's'],
    ['a', 'b', 'j', 'm', 'o', 'qu'],
    ['e', 'e,' 'f', 'h', 'i', 'y'],
    ['e', 'h', 'i', 'n', 'p', 's'],
    ['d', 'k', 'n', 'o', 't', 'u'],
    ['a', 'd', 'e', 'n', 'v', 'z'],
    ['b', 'i', 'f', 'o', 'r', 'x']
]

# The default dice used by Boggle in a 4x4 grid.
defaultDice16 = [
    ['e', 'l', 'r', 't', 't', 'y'],
    ['h', 'l', 'n', 'n', 'r', 'z'],
    ['d', 'e', 'l', 'r', 'v', 'y'],
    ['e', 'e', 'g', 'h', 'n', 'w'],
    ['d', 'i', 's', 't', 't', 'y'],
    ['e', 'i', 'o', 's', 's', 't'],
    ['h', 'i', 'm', 'n', 'qu', 'u'],
    ['a', 'f', 'f', 'k', 'p', 's'],
    ['a', 'c', 'h', 'p', 'o', 's'],
    ['c', 'i', 'm', 'o', 't', 'u'],
    ['a', 'a', 'e', 'e', 'n', 'g'],
    ['e', 'h', 'r', 't', 'v', 'w'],
    ['a', 'o', 'o', 't', 't', 'w'],
    ['e', 'e', 'i', 'n', 's', 'u'],
    ['a', 'b', 'b', 'j', 'o', 'o'],
    ['d', 'e', 'i', 'l', 'r', 'x']
]

# The default dice used by Big Boggle in a 5x5 grid, minus the challenge die:
defaultDice25 = [
    ['a', 'a', 'a', 'f', 'r', 's'],
    ['a', 'a', 'e', 'e', 'e', 'e'],
    ['a', 'a', 'f', 'i', 'r', 's'],
    ['a', 'd', 'e', 'n', 'n', 'n'],
    ['a', 'e', 'e', 'e', 'e', 'm'],
    ['a', 'e', 'e', 'g', 'm', 'u'],
    ['a', 'e', 'g', 'm', 'n', 'n'],
    ['a', 'f', 'i', 'r', 's', 'y'],
    ['b', 'j', 'k', 'qu', 'x', 'z'],
    ['c', 'c', 'e', 'n', 's', 't'],
    ['c', 'e', 'i', 'i', 'l', 't'],
    ['c', 'e', 'i', 'l', 'p', 't'],
    ['c', 'e', 'i', 'p', 's', 't'],
    ['d', 'd', 'h', 'n', 'o', 't'],
    ['d', 'h', 'h', 'l', 'o', 'r'],
    ['d', 'h', 'l', 'n', 'o', 'r'],
    ['d', 'h', 'l', 'n', 'o', 'r'], # duplicate
    ['e', 'i', 'i', 'i', 't', 't'],
    ['e', 'm', 'o', 't', 't', 't'],
    ['e', 'n', 's', 's', 's', 'u'],
    ['f', 'i', 'p', 'r', 's', 'y'],
    ['g', 'o', 'r', 'r', 'v', 'w'],
    ['i', 'p', 'r', 'r', 'r', 'y'],
    ['n', 'o', 'o', 't', 'u', 'w'],
    ['o', 'o', 'o', 't', 't', 'u']
]

# The additional challenge die in some versions. This can be substituted in for
# one of the above, or added to the above, in which case, one die will be omitted
# randomly.
defaultChallengeDie = ['i', 'k', 'l', 'm', 'qu', 'u']

# The default tiles used in a Scrabble game, minus the blanks.
defaultTiles = ['a']*9 + ['b']*2 + ['c']*2 + ['d']*4 + ['e']*11 + ['f']*2 + ['g']*3 + ['h']*2 + ['i']*8 + ['l']*4 + ['m']*2 + ['n']*6 + ['o']*8 + ['p']*2 + ['r']*6 + ['s']*4 + ['t']*6 + ['u']*4 + ['v']*2 + ['w']*2 + ['y']*2 + ['j','k','q','x','z']



def wordSorter(x,y):
    """wordSorter(x,y)

    Function to determine the relative order of two words, x and y.
    Words are first sorted by length in nonincreasing order, and then lexicographically."""
    if len(x) > len(y):
        return -1
    if len(y) > len(x):
        return 1
    if x < y:
        return -1
    if x > y:
        return 1
    return 0



class Trie:
    """An immutable trie constructed from a list of lists.

    To traverse the trie, one should call getRoot() to get a pointer to the root node,
    and then repeatedly call getChild() with the root node and the desired child to
    access the child node, checking to make sure the child exists. An example is found
    in the BoggleBoard class findWords method."""

    def __init__(self, listOfLists):
        """__init__(listOfLists, childrenByFixedArray=False)

        Create a trie representing the data in list.
        Note that if listOfLists represents a list of words from a file, each
        entry from the file will likely have to be stripped. This can be
        easily accomplished by one of two techniques:

        1. List comprehension:
           [word.strip() for word in file('wordfile')]

        2. Map function (uses deprecated string module):
           from string import strip
           map(strip, file('wordfile'))
         """

        # The trie is represented, for reasons of efficiency, as an array of nodes.
        # Each node contains the following data:
        # 1. the list of data represented by this node (for convenience)
        # 2. a flag indicating if this is a terminal node (i.e. something in the list)
        # 3. a link to the parent
        # 4. a list of the children for this node, indexed by list key, stored as an
        #    associative array.

        # We begin with a dummy node, representing the empty list.
        self.nodes = [[[], False, -1, {}]]

        # Now iterate over the lists in list and create nodes for them.
        for curList in listOfLists:
            # We iterate over curList and find our way through self.nodes, creating nodes
            # as necessary.
            curNodeIdx = 0
            for elem in curList:
                # Check to see if curNode has a child with value elem.
                if elem in self.nodes[curNodeIdx][3]:
                    # It does, so we merely traverse.
                    curNodeIdx = self.nodes[curNodeIdx][3][elem]
                    continue

                # It does not, so we create a new node.
                newNode = [self.nodes[curNodeIdx][0][:] + [elem], False, curNodeIdx, {}]
                self.nodes.append(newNode)
                newNodeIdx = len(self.nodes)-1
                self.nodes[curNodeIdx][3][elem] = newNodeIdx
                curNodeIdx = newNodeIdx

            # Now we have a complete chain representing curList, which terminates at curNodeIdx,
            # so mark the node curNodeIdx as being terminal.
            self.nodes[curNodeIdx][1] = True


    def getRoot(self):
        """getRoot

        Returns a pointer to the root node. This is used in trie traversal."""

        return 0


    def getChild(self, node, child):
        """getChild(node, child)

        Return a pointer to the specified child of the given node, if one exists. If it does
        not, return -1."""

        if node > -1 and child in self.nodes[node][3]:
            return self.nodes[node][3][child]
        return -1


    def isTerminal(self, node):
        """isTerminal(node)

        Return whether or not the specified node is a terminal node."""

        return self.nodes[node][1]


    def contains(self, theList):
        """contains(theList)

        Determine if the trie contains elem. Returns True if it does, and False otherwise."""

        curNodeIdx = 0
        for elem in theList:
            if elem not in self.nodes[curNodeIdx][3]:
                return False
            curNodeIdx = self.nodes[curNodeIdx][3][elem]

        # The node must be terminal.
        return self.nodes[curNodeIdx][1]




class AbstractBoggleBoard:
    """An abstract representation of a boggle board, which, in its most generic
    form, is simply a number of letters without a specific shape.

    Subclasses of this class should impose a shape (through an adjacency graph)
    on the board; for example, the typical square boggle board, or the looping
    toroidal boggle board. Another interesting example is a boggle board over
    n letters with the adjacency graph K_n, which is simply a problem of
    letter unscrambling (i.e. using n=7 would give a standard Scrabble hand)."""

    def __init__(self, numLetters, layout=None):
        """__init__(numLetters, layout=None)

        Create a new Boggle board with the specified number of letters. If
        layout is given, it should be a list of length numLetters indicating
        the contents of each of the letter positions. A layout of None
        indicates that the board has not yet been generated."""

        assert(not(layout) or numLetters == len(layout))
        self.numLetters = numLetters
        self.layout = layout
        self.adjacencies = self._determineAdjacencies()


    def _determineAdjacencies(self):
        """_determineAdjacencies

        Creates an adjacency list representation of the graph representing
        the adjacencies of the boggle board.

        Assuming that the board represented by this object has size n (i.e.
        contains n letters), this method should return an array of length n,
        with entry i consisting of a list of the positions adjacent to position
        i in the boggle board.

        Note: this should never be called directly by the user, but should be
        overridden in subclasses of BoggleBoard."""

        return NotImplemented


    def generateBoard(self, dice, seed=-1):
        """generateBoard(dice, seed=-1):

        Generate a random board. Note that dice should be an array of length at
        least numLetters, with each entry consisting of a list of the possible
        faces for that die. For an example, see the defaultDice16 variable,
        which defines 16 dice for a 4x4 Boggle game (or any other Boggle game
        with 16 letter positions).

        This method then populates the layout member, by taking a random order
        on the dice, picking one entry from each list (i.e. one face from each
        die), and then assigning these faces to the layout. If there are more
        dice than positions, some dice are randomly omitted.

        Seed can be used to reliably recreate specific boards. If seed is
        specified and is nonnegative, then it is used to seed the RNG before
        the dice are "rolled", and thus calls to generateBoard with the same
        seed will result in identical boards.

        Although it is unlikely to be absolutely necessary, it is possible to
        override this method; this would most likely be done to specify a
        default value for dice, e.g. for a square 4x4 boggle board using
        the defaultDice16 set, we might implement:

        def generateBoard(self, dice=defaultDice16, seed=-1):
            AbstractBoggleBoard.generateBoard(self, dice, seed)"""

        assert(len(dice) >= self.numLetters)

        if seed >= 0:
            random.seed(seed)

        # Roll the dice.
        self.layout = map(random.choice, dice)

        # Arrange them randomly.
        random.shuffle(self.layout)

        # Truncate dice that didn't fit.
        self.layout = self.layout[:self.numLetters]

    

    def findWords(self, wordTrie, minimumSize=3):
        """findWords(wordTrie, minimumSize=3)

        Given a Trie, as per the trie module, backtrack through the Boggle board
        to locate all possible words. A list of words, sorted by size and then
        alphabetical order, is returned."""

        # We must try beginning at each position in the boggle board and expanding until it
        # is no longer possible to do so. In order to do this, we will use the adjacency
        # list created in the _determineAdjacencies method and stored in self.adjacencies.
        # A list of the words visited.
        wordList = []

        # Try beginning in every position.
        for i in range(self.numLetters):
            # Move to the node in the trie, if it exists. We support multi-letter cells, such
            # as 'qu', by looping over the contents of the cell.
            trieNode = wordTrie.getRoot()
            for letter in self.layout[i].lower():
                if trieNode == -1:
                    break
                trieNode = wordTrie.getChild(trieNode, letter)

            # If any initial configurations are not feasible (i.e. no trie words start in the
            # specified square), skip starting with this square completely.
            if trieNode == -1:
                continue

            # Information needed for the backtrack.
            # visitedSquares will consist of indexes into the adjacencies.
            visitedSquaresIdx = [-1] * self.numLetters
            visitedSquares = [-1] * self.numLetters
            visitedSquares[0] = i
            visitedFlags = [i == j for j in range(self.numLetters)]
            visitedNodes = [-1] * self.numLetters
            visitedNodes[0] = trieNode
            
            # Now perform the backtrack. We try until we can extend no further.
            idx = 1
            while idx >= 1:
                # If we have a complete word, process it.
                if wordTrie.isTerminal(visitedNodes[idx-1]):
                    # Much easier to just gather the word here from the visited squares rather
                    # than try to keep track as we go, especially with the allowance of multi
                    # character cells.
                    visitedWord = ''
                    for i in range(idx):
                        visitedWord += self.layout[visitedSquares[i]]
                    if len(visitedWord) >= minimumSize:
                        wordList.append(visitedWord)

                # If we have used all the letters but are still not at a terminal word, we
                # must backtrack.
                if idx == self.numLetters:
                    idx -= 1
                    continue

                # Extend if possible. We try the next candidate in the extensionCandidates, which
                # must correspond to a trie node.
                # If we have already selected a square here, we return it to the pool prior to
                # trying to extend.
                if visitedSquares[idx] >= 0:
                    visitedFlags[visitedSquares[idx]] = False

                chosenFlag = False
                while not chosenFlag:
                    visitedSquaresIdx[idx] += 1

                    # Check to see if we ran out of candidates.
                    if visitedSquaresIdx[idx] >= len(self.adjacencies[visitedSquares[idx-1]]):
                        break

                    # Determine the number of this candidate as a square in the range 0...self.numLetters-1.
                    visitedSquares[idx] = self.adjacencies[visitedSquares[idx-1]][visitedSquaresIdx[idx]]

                    # Check to see if this square has already been visited. If so, skip it.
                    if visitedFlags[visitedSquares[idx]]:
                        continue

                    # Check to see if this is a valid candidate, i.e. does it correspond to a
                    # node in the trie? We support cells with multiple characters as above in
                    # the initialization.
                    trieNode = visitedNodes[idx-1]
                    for letter in self.layout[visitedSquares[idx]]:
                        if trieNode == -1:
                            break
                        trieNode = wordTrie.getChild(trieNode, letter)

                    if trieNode >= 0:
                        # We have a valid candidate.
                        chosenFlag = True
                        break

                # If the chosen flag is still false, we could not extend, so we must backtrack.
                if not chosenFlag:
                    # Reset all the variables here.
                    visitedSquaresIdx[idx] = -1
                    visitedSquares[idx] = -1
                    visitedNodes[idx] = -1
                    idx -= 1
                    continue

                # Otherwise, we extended, so record this and continue.
                visitedFlags[visitedSquares[idx]] = True
                visitedNodes[idx] = trieNode
                idx += 1

        # Make the list unique and sort it.
        # TODO: We don't necessarily want to sort here.
        wordList = [word for word in set(wordList)]
        wordList.sort(cmp=wordSorter)
        return wordList


    def __str__(self):
        """__str__

        Convert a Boggle board to a readable string.
        In the abstract case, this is just a list of the contents for each
        entry. Subclasses can override this in order to make for a more
        elegant, human-readable representation."""

        return (self.layout if self.layout else [None] * self.numLetters)



class RectangularBoggleBoard(AbstractBoggleBoard):
    """An abstract subclass of AbstractBoggleBoard representing a BoggleBoard
    that can be physically represented to the end-user as a rectangle. Examples
    of such boards are the standard square boggle board and the toroidal boggle
    board, which, while not technically a rectangle, for the purposes of
    visualization, may be displayed as such."""

    def __init__(self, length, width, layout=None):
        """__init__(length, width, layout=None)

        Create a new length X width Boggle board. If the layout is specified, it
        should be a linear array of size length X width indicating the contents
        of the board as a collection of concatenated rows. A layout set to None
        indicates that the board has not yet been generated."""

        self.length = length
        self.width = width
        AbstractBoggleBoard.__init__(self, length * width, layout)


    def _determineAdjacencies(self):
        """_determineAdjacencies

        Creates an adjacency list representation of the graph representing
        the adjacencies of a standard rectangular boggle board."""

        # Create the adjacency array of size self.length * self.width
        adjacencies = [[] for i in range(self.numLetters)]
        for i in range(self.numLetters):
            # Try moving left. This is not possible if we are divisible by the width.
            if i % self.width != 0:
                adjacencies[i].append(i-1)

            # Try moving up. This is not possible if we are in the first row.
            if i >= self.width:
                adjacencies[i].append(i-self.width)

            # Try moving right. This is not possible if we are in the last column, i.e.
            # the move to the right is divisible by the width.
            if (i+1) % self.width != 0:
                adjacencies[i].append(i+1)

            # Try moving down. This is not possible if we are in the last row.
            if (i+self.width) < self.numLetters:
                adjacencies[i].append(i+self.width)

            # Try moving up and to the left.
            if i % self.width != 0 and i >= self.width:
                adjacencies[i].append(i-self.width-1)

            # Try moving up and to the right.
            if (i+1) % self.width != 0 and i >= self.width:
                adjacencies[i].append(i-self.width+1)

            # Try moving down and to the left.
            if i % self.width != 0 and (i+self.width) < self.numLetters:
                adjacencies[i].append(i+self.width-1)

            # Try moving down and to the right.
            if (i+1) % self.width != 0 and (i+self.width) < self.numLetters:
                adjacencies[i].append(i+self.width+1)

        return adjacencies


    def __str__(self):
        """__str__

        Convert a Boggle board to a readable string."""

        if self.layout == None:
            return ''
            
        # Determine the length of the longest object's string representation.
        twidth = max([len(a.__str__()) for a in self.layout])+1
        formatstr = '%%%ds' % twidth

        strRep = ''
        for i in range(self.length):
            for j in range(self.width):
                strRep += formatstr % self.layout[i*self.width+j].upper()
            strRep += '\n'
        return strRep



class BoggleBoard(RectangularBoggleBoard):
    """A standard n x n square Boggle board. (Default size is 4.)"""

    def __init__(self, size=4, layout=None):
        """__init__(size=4, layout=None)

        Create a standard size x size Boggle board."""

        RectangularBoggleBoard.__init__(self, size, size, layout)


    def generateBoard(self, dice=defaultDice16, seed=-1):
        """generateBoard(dice=defaultDice16, seed=-1)

        Generate a boggle board as per the generateBoard method of
        AbstractBoggleBoard using the specified dice set."""

        RectangularBoggleBoard.generateBoard(self, dice, seed)



class RectangularToroidalBoggleBoard(RectangularBoggleBoard):
    """A boggle board on the surface of a torus, i.e. the letters on the left
    side of the board are adjacent to those on the right side and vice versa,
    and the letters on the top of the board are adjacent to those on the bottom
    and vice versa. For example, if we have the 4x4 boggle board with entries
    indicated by a positional marker:

    0 1 2 3
    4 5 6 7
    8 9 A B
    C D E F

    Then note that we have that 0 is adjacent, as usual, to 1, 4, and 5, but
    furthermore, since the left side is adjacent to the right side, also
    3 and 7, and since the top is adjacent to the bottom, also C and D.
    Additionally, note that 0 is adjacent to F as well, as it is adjacent
    to both the right side and the bottom side.

    This board is more equitable towards letters, as every letter in the board
    is adjacent to exactly eight neighbouring letters, unlike the standard
    boggle board where only the four middle letters are adjacent to eight
    neighbours, the edge letters are adjacent to five, and the corners three."""

    def _determineAdjacencies(self):
        """_determineAdjacencies

        Create the adjacency graph to account for the left-right and top-bottom
        looping."""

        # Create a length x width grid containing the cell appearing in each position.
        # Then this is easily accomplished with modular arithmetic.
        grid = [[i*self.width + j for j in range(self.width)] for i in range(self.length)]

        # Create the adjacency array of size self.length * self.width
        adjacencies = [[] for i in range(self.numLetters)]

        for (entry,(i,j)) in enumerate((i,j) for i in range(self.length) for j in range(self.width)):
            # Try all offsets of the form [-1,0,1] X [-1,0,1] \ (0,0).
            for x,y in ((a,b) for a in [-1,0,1] for b in [-1,0,1] if a != 0 or b != 0):
                adjacencies[entry].append(grid[(i+x)%self.length][(j+y)%self.width])

        return adjacencies



class ToroidalBoggleBoard(RectangularToroidalBoggleBoard):
    """A standard (square) toroidal boggle board."""

    def __init__(self, size=4, layout=None):
        """__init__(size=4, layout=None)

        Create a standard size x size toroidal boggle board."""

        self.size = size
        RectangularToroidalBoggleBoard.__init__(self, size, size, layout)


    def generateBoard(self, dice=defaultDice16, seed=-1):
        """generateBoard(dice=defaultDice16, seed=-1)

        Generate a boggle board as per the generateBoard method of
        AbstractBoggleBoard using the specified dice set."""

        RectangularToroidalBoggleBoard.generateBoard(self, dice, seed)



class RectangularHexagonalBoggleBoard(AbstractBoggleBoard):
    """A Boggle board where instead of square tiles, we have hexagonal shaped
    ones."""

    def __init__(self, length=4, width=4, layout=None):
        """__init__(length=4, width=4, layout=None)

        Create a length by width Boggle board consisting of hexagonal tiles."""

        self.width = width
        self.length = length
        AbstractBoggleBoard.__init__(self, length*width, layout)


    def _determineAdjacencies(self):
        """_determineAdjacencies()

        Should not be called by the end user.
        Create the adjacency graph for the board."""

        adjacencies = [[] for i in range(self.numLetters)]

        # Unlike the rectangular boggle board, which has layout:
        #  0   1   2 ...
        #  w   w+1 w+2 ...
        #  etc...
        #
        # we instead first descend down columns and then across by rows:
        # 0       2w
        #    w         ...
        # 1       2w+1
        #    w+1       ...
        # 2       2w+2
        # .  w+2   .   ...
        # .   .    .
        # .   .    .
        for i in range(self.numLetters):
            # Try moving up. This is not possible if we are divisible by the length.
            if i % self.length != 0:
                adjacencies[i].append(i-1)
 
            # Try moving down. This is not possible if we are 1 short of the length.
            if (i+1) % self.length != 0:
                adjacencies[i].append(i+1)

            # Try moving left and up, and right and up. To do so, we must not be
            # an even multiple of the length.
            if i % (2*self.length) != 0:
                # To move left and up, we cannot be in the first column.
                if i >= self.length:
                    # Even column: move -length-1 positions.
                    # Odd column:  move -length positions.
                    adjacencies[i].append(i - self.length - (1 if (int(i / self.length)) % 2 == 0 else 0))
                # To move right and up, we cannot be in the last column.
                    # Even column: move length-1 positions.
                    # Odd column:  move length positions.
                if i < self.numLetters - self.length:
                    adjacencies[i].append(i + self.length - (1 if (int(i / self.length)) % 2 == 0 else 0))

            # Try moving left and down, and right and down. To do so, we must
            # not be 1 short of an even multiple of the length.
            if (i+1) % (2*self.length) != 0:
                # To move left and down, we cannot be in the first column.
                if i >= self.length:
                    # Even column: move -length positions.
                    # Odd column:  move -length+1 positions.
                    adjacencies[i].append(i - self.length + (int(i / self.length)) % 2)
                # To move right and down, we cannot be in the last column.
                if i < self.numLetters - self.length:
                    # Even column: move length positions.
                    # Odd column:  move length+1 positions.
                    adjacencies[i].append(i + self.length + (int(i / self.length)) % 2)

        return adjacencies


    def __str__(self):
        """__str__

        Convert a hexagonal Boggle board to a readable string."""

        if self.layout == None:
            return ''
            
        # Determine the length of the longest object's string representation.
        twidth = max([len(a.__str__()) for a in self.layout])+1
        formatstr = '%%%ds' % twidth

        # As we are hexagonal, we must modify spacing. We print all the even
        # columns on one row, then all the odd columns on the following row,
        # etc, as above in the comments for _determineAdjacencies.

        strRep = ''
        for i in range(self.length):
            strRep += (formatstr * self.width + '\n') % tuple([self.layout[self.length*j+i].upper() if j%2 == 0 else '' for j in range(self.width)])
            strRep += (formatstr * self.width + '\n') % tuple([self.layout[self.length*j+i].upper() if j%2 == 1 else '' for j in range(self.width)])
        return strRep



class HexagonalBoggleBoard(RectangularHexagonalBoggleBoard):
    """A standard n x n Boggle board with hexagonal tiles. (Default size is 4.)"""

    def __init__(self, size=4, layout=None):
        """__init__(size=4, layout=None)

        Create a standard size x size Boggle board with hexagonal tiles."""

        RectangularBoggleBoard.__init__(self, size, size, layout)


    def generateBoard(self, dice=defaultDice16, seed=-1):
        """generateBoard(dice=defaultDice16, seed=-1)

        Generate a boggle board as per the generateBoard method of
        AbstractBoggleBoard using the specified dice set."""

        RectangularBoggleBoard.generateBoard(self, dice, seed)



class RectangularToroidalHexagonalBoggleBoard(RectangularHexagonalBoggleBoard):
    """A boggle board on the surface of a torus, i.e. the letters on the left
    side of the board are adjacent to those on the right side and vice versa,
    and the letters on the top of the board are adjacent to those on the bottom
    and vice versa. For example, if we have the 4x4 boggle board with entries
    indicated by a positional marker:

    0   8
      4   C
    1   9
      5   D
    2   A
      6   E
    3   B
      7   F

    Then note that we have that 0 is adjacent, as usual, to 1 and 4, but
    furthermore, since the left side is adjacent to the right side, also
    C, and since the top is adjacent to the bottom, also 3 and 7.
    Additionally, note that 0 is adjacent to F as well, as it is adjacent
    to both the right side and the bottom side.

    This board is more equitable towards letters, as every letter in the board
    is adjacent to exactly six neighbouring letters, unlike the standard
    hexagonal boggle board where letters may be adjacent to 2, 3, 4, 5, or 6
    letters.

    NOTE: For the torus shape to work properly in the hexagonal case, we must
    have an even number of columns."""

    def __init__(self, length, width, layout=None):
        """__init__(length, width, layout=None)

        Create a rectangular hexagonal Boggle board on the surface of a torus.
        Note that the width must be even for the connections to make sense."""

        if width % 2 != 0:
            raise ValueError("Width for toroidal hexagonal board must be even: %s" % width)
        RectangularHexagonalBoggleBoard.__init__(self, length, width, layout)


    def _determineAdjacencies(self):
        """_determineAdjacencies

        Create the adjacency graph to account for the left-right and top-bottom
        looping."""

        # Create a grid representing the board for modular arithmetic to
        # simplify calculations.
        grid = [[i * self.length + j for j in range(self.length)] for i in range(self.width)]

        # Create the adjacency array of size self.length * self.width
        adjacencies = [[] for i in range(self.numLetters)]

        for (entry,(i,j)) in enumerate((i,j) for i in range(self.width) for j in range(self.length)):
            # Move up and down.
            adjacencies[entry].append(grid[i][(j-1) % self.length])
            adjacencies[entry].append(grid[i][(j+1) % self.length])
 
            # Move in all other directions.
            # Even column: for col+1, col-1, we move row, row-1.
            # Odd column:  for col+1, col-1, we move row, row+1.
            for x in (-1,1):
                adjacencies[entry].append(grid[(i+x) % self.width][j])
                adjacencies[entry].append(grid[(i+x) % self.width][(j + (-1 if i % 2 == 0 else 1)) % self.length])

        return adjacencies



class ToroidalHexagonalBoggleBoard(RectangularToroidalHexagonalBoggleBoard):
    """A standard (square) toroidal boggle board with hexagon tiles."""

    def __init__(self, size=4, layout=None):
        """__init__(size=4, layout=None)

        Create a standard size x size toroidal hexagonal boggle board."""

        self.size = size
        RectangularToroidalHexagonalBoggleBoard.__init__(self, size, size, layout)


    def generateBoard(self, dice=defaultDice16, seed=-1):
        """generateBoard(dice=defaultDice16, seed=-1)

        Generate a boggle board as per the generateBoard method of
        AbstractBoggleBoard using the specified dice set."""

        RectangularToroidalHexagonalBoggleBoard.generateBoard(self, dice, seed)



class Anagram(AbstractBoggleBoard):
    """An anagram can be represented by a BoggleBoard where every letter is
    considered to be adjacent to every other letter."""

    def __init__(self, size=7, layout=None):
        """__init__(size=7, layout=None)

        Create a hand of size letters."""

        AbstractBoggleBoard.__init__(self, size, layout)


    def _determineAdjacencies(self):
        """_determineAdjacencies()

        Should not be called by the end user.
        Create an adjacency graph where everyone is adjacent to everyone else."""

        return [[x for x in range(self.numLetters) if x != y] for y in range(self.numLetters)]


    def generateBoard(self, tiles=defaultTiles, seed=-1):
        """generateBoard(tiles=defaultTiles, seed=-1)

        Generate a random hand of letters from the supplied tiles."""

        shuffledTiles = tiles
        random.shuffle(shuffledTiles)
        self.layout = shuffledTiles[:self.numLetters]



def createWordTrie(filename='words'):
    """createWordTrie:

    Create a trie from the specified file."""

    infile = open(filename, 'r')
    t = trie.Trie([a.strip() for a in infile.readlines()])
    return t



if __name__ == '__main__':
    if len(sys.argv) > 2:
        sys.stderr.write('Usage: %s [board-number]\n' % sys.argv[0])
        sys.exit(-1)

    seed = 0
    if len(sys.argv) == 2:
        try:
            seed = int(sys.argv[1])
        except ValueError:
            sys.stderr.write('Illegal board number: %s' % sys.argv[1])
            sys.exit(-2)

    boggleBoard = BoggleBoard()
    board = boggleBoard.generateBoard(seed=seed)
    print(boggleBoard)
