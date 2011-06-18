#! /usr/bin/python
#
#     anagram.py
# 
#     Copyright (c) 2009, 2010, 2011 Umang Varma <umang.me@gmail.com>.
# 
#     This file is part of Pynagram
# 
#     Pynagram is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     Pynagram is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with Pynagram. If not, see <http://www.gnu.org/licenses/>.
# 

import random

class AnagramException(Exception): pass
class LengthException(AnagramException): pass
class WordException(AnagramException): pass


class Anagram:
    """The backend of pynagram that manages the current game.

    This class performs all the back-end tasks such as generating anagrams,
    checking if the input word exists, etc."""

    def __init__(self):
        """Initializes the class."""
        self.letters = []
        self.score = 0
        self.words = {}
        self.wordlist = []
        self.scoring = {3:3, 4:5, 5:8, 6:14, 7:20}
        self.solved_all = False
        self.qualified = False
        
    def read_from_file(self, wordlist):
        """Reads the wordlist from a file and stores it appropriately."""
        fsock = file(wordlist)
        lines = fsock.readlines()
        fsock.close()
        self.wordlist = self.filter_wordlist(lines)

    def filter_wordlist(self, lines):
        """Filters lines from a wordlist into a list."""
        return([x.strip() for x in lines if len(x) > 3])

    def find_letters(self, length=7):
        """Finds possible letters to make anagrams with from the wordlist"""
        # adapted from ActiveState Recipe #52560
        # ("Remove duplicates from a sequence")
        possible_words = [[word[x] for x in xrange(length)] \
            for word in self.wordlist if len(word) == length]
        #
        # Commented out the next few lines because the wordlist is not supposed
        # to have duplicates. It is none of our business to weed them out. If
        # any problems occur in the future, we'll uncomment these lines out.
        # These lines were initially supposed to remove duplicates in words.
        #
        # n = len(possible_words)
        # for x in xrange(n):
            # possible_words[x].sort()
        # possible_words.sort()
        # prev = possible_words[0]
        # next_free = 1
        # for x in xrange(1, n):
            # if possible_words[x] != prev:
                # possible_words[next_free] = prev = possible_words[x]
                # next_free += 1
        # possible_words = possible_words[:next_free]
        return random.choice(possible_words)

    def start_new(self, letters=None, length=7, no_word_error=False):
        """Starts a new game of Pynagram!"""
        self.qualified = False
        self.solved_all = False
        if (letters is not None) and len(letters) == 7:
            self.letters = letters
        elif (letters is not None) and len(letters) >= 3:
            raise LengthException("Bad number of letters given.")
        else:
            self.letters = self.find_letters(length)
        words = []
        for word in self.wordlist:
            is_anagram = True
            a_letters = self.letters[:]
            for x in word:
                if x in a_letters:
                    a_letters.remove(x)
                else:
                    is_anagram = False
                    break
            if is_anagram:
                words.append(word)
        words.sort(lambda x, y: len(y) - len(x))
        if len(words[0]) < length:
            raise WordException("There are no %d letter words that match \
this anagram" % length)
        self.words = dict([(word.lower(), False) for word in words])
        self.letters = [x.lower() for x in self.letters]

    def guess(self, word):
        """Attempts to solve (guess) an anagram"""
        if word in self.words:
            typed = self.words[word]
            self.words[word] = True
            if not typed:
                self.score += self.scoring[len(word)]
                if not self.qualified and len(word) is 7:
                    self.score += 30
                    self.qualified = True
                if not False in self.words.values() and not self.solved_all:
                    self.solved_all = True
                    self.score += 30
            return (True, typed)
        else:
            return (False, False)

    def clear_all(self):
        """Clears all data being used for a new game."""
        self.score = 0
        self.letters = []
        self.words = {}
        self.qualified = False
