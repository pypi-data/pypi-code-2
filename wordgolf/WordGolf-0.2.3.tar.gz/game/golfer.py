"""Prototype for the game of word golf"""

import random
import sys

# From http://en.wikipedia.org/wiki/Letter_frequency
raw_frequencies = '''a	8.167
b	1.492
c	2.782
d	4.253
e	12.702
f	2.228
g	2.015
h	6.094
i	6.966
j	0.153
k	0.772
l	4.025
m	2.406
n	6.749
o	7.507
p	1.929
q	0.095
r	5.987
s	6.327
t	9.056
u	2.758
v	0.978
w	2.360
x	0.150
y	1.974
z	0.074'''


class WordChecker(object):
    """Checks the spelling of words"""
    
    def __init__(self, filename):
        """Initialise the checker from a file"""
        self.loadFile(filename)
        
    def loadFile(self, filename):
        """Load the words from a file"""
        self.words = words = set()
        with file(filename, 'r') as f:
            for line in f.readlines():
                words.add(self._processLine(line))
    
    def _processLine(self, line):
        """Process a line from the file and return word"""
        return line.strip().replace("'", '')
    
    def isWord(self, word):
        """Return True if the word is a word"""
        return word in self.words
    
    
class BoardGenerator(object):
    """Generates a board of letters"""
    
    def __init__(self, size):
        """Initialise the board"""
        self.generateLetterFrequencies(raw_frequencies)
        self.generateBoard(size)
        
    def generateLetterFrequencies(self, text):
        """Generate the letter frequencies"""
        letters = []
        for line in text.splitlines():
            letter, pc = line.split()
            letters.append((float(pc), letter))
        letters.sort()
        tot = 0.0
        self.freq = []
        for pc, letter in letters:
            tot += pc
            self.freq.append((tot, letter))
        self.freq[-1] = (100.0, self.freq[-1][1])
        
    def generateBoard(self, size):
        """Create a board of the given size"""
        self.size = size
        self.board = []
        for row in range(size):
            self.board.append([])
            for col in range(size):
                self.board[-1].append(self.getLetter())
                
    def getLetter(self):
        """Return a letter"""
        position = 100.0*random.random()
        for pc, letter in self.freq:
            if position <= pc:
                return letter
        else:
            raise ValueError('Logic failed for position %s, %s' % (position, pc))
    
    def asText(self):
        """Return the board as some text"""
        return '\n'.join([''.join(row) for row in self.board])
    
    def asRawText(self):
        """Return the board as raw text"""
        return ''.join([''.join(row) for row in self.board])

# The following from http://everydayscripting.blogspot.com/2009/08/python-boggle-solver.html

class BoggleSolver:
    def __init__(self, letter_list, min_length):
        self.dictionary = Dictionary(['words/corncob_lowercase.txt', 'words/en_US.dic'])
        self.board = Board(letter_list)
        self.min_length = min_length
        self.found_words = set()

        # Find all words starting from each coordinate position
        for row in xrange(self.board.side_length):
            for column in xrange(self.board.side_length):
                self._find_words(Word.new(row, column), row, column)

    def _find_words(self, word, row, column):
        word.add_letter(self.board[row][column], row, column)

        if (self._can_add_word(word)):
            self.found_words.add(word.letter_sequence)

        for row, column in self._get_valid_coodinates_for_word(word, row, column):
            if(self.dictionary.contains_prefix(word.letter_sequence + self.board[row][column])):
                self._find_words(Word.new_from_word(word), row, column)

    def _can_add_word(self, word):
        return len(word) >= self.min_length and self.dictionary.contains_word(word.letter_sequence)

    def _get_valid_coodinates_for_word(self, word, row, column):
        for r in range(row - 1, row + 2):
            for c in range(column - 1, column + 2):
                if r >= 0 and r < self.board.side_length and c >= 0 and c < self.board.side_length:
                    if ((r, c) not in word.used_board_coordinates):
                        yield r, c

class Board:
    def __init__(self, letter_list):
        self.side_length = len(letter_list) ** .5
        if (self.side_length != int(self.side_length)):
            raise Exception("Board must have equal sides! (4x4, 5x5...)")
        else:
            self.side_length = int(self.side_length)

        self.board = []

        index = 0
        for row in xrange(self.side_length):
            self.board.append([])
            for column in xrange(self.side_length):
                self.board[row].append(letter_list[index])
                index += 1

    def __getitem__(self, row):
        return self.board[row]

class Word:
    def __init__(self):
        self.letter_sequence = ""
        self.used_board_coordinates = set()

    @classmethod
    def new(cls, row, column):
        word = cls()
        word.used_board_coordinates.add((row, column))
        return word

    @classmethod
    def new_from_word(cls, word):
        new_word = cls()
        new_word.letter_sequence += word.letter_sequence
        new_word.used_board_coordinates.update(word.used_board_coordinates)
        return new_word

    def add_letter(self, letter, row, column):
        self.letter_sequence += letter
        self.used_board_coordinates.add((row, column))

    def __str__(self):
        return self.letter_sequence

    def __len__(self):
        return len(self.letter_sequence)

class Dictionary:
    def __init__(self, dictionary_files):
        self.words = set()
        self.prefixes = set()
        for dictionary_file in dictionary_files:
            word_file = open(dictionary_file, "r")

            for word in word_file.readlines():
                self.words.add(word.strip().split('/')[0])
                for index in xrange(len(word.strip()) + 1):
                    self.prefixes.add(word[:index])

    def contains_word(self, word):
        return word in self.words

    def contains_prefix(self, prefix):
        return prefix in self.prefixes

if __name__ == "__main__":
    board = BoardGenerator(5)
    boggleSolver = BoggleSolver(board.asRawText())
    words = boggleSolver.found_words 
    print board.asText()
    print
    print '\n'.join(words)   
