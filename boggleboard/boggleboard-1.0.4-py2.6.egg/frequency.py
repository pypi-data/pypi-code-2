#!/usr/bin/env python
#
# Copyright 2010 Sebastian Raaphorst.
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

"""frequency.py

Functions to deal with frequency of symbols in lists of strings of said symbols.
In the context of the boggleboard library specifically, we use this to iterate
over a list of words and find letter frequency (treating 'qu' as its own letter
as is standard). Then this information can be used to construct random Boggle
boards or a set of dice for Boggle boards."""


import random


# The default symbols for Boggle are:
# a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, qu, r, s, t, u, v, w, x, y, z.
defaultSymbols = [_a if _a != 'q' else 'qu' for _a in map(chr, range(ord('a'), ord('z')+1))]



def estimateFrequencies(wordList, symbols=defaultSymbols):
    """estimateFrequencies(wordList, symbols=defaultSymbols)

    Given a list of words over the specified collection of symbols, calculate
    the frequency of each symbol in the word list. The results are returned
    as a dictionary with keys from symbols and values the relative frequency
    of the symbol (i.e. a value in the range [0,1]). Note that symbols must
    not contain duplicate entries.

    Note that this function does not take into account the fact that some
    symbols might be subsymbols of others and should thus be treated
    differently, e.g. in Boggle, the u in qu should not be taken to contribute
    to the overall frequency of u; this is why we call the function an
    estimation. In the case where no symbol is contained in any other, then it
    is a fully accurate calculation."""

    # Assure that there are no duplicates in symbols.
    assert(len(symbols) == len(set(symbols)))

    # First calculate a list with entries (symbol, count), i.e. the number of
    # times symbol appears in the wordList.
    f = [(symbol, sum([w.count(symbol) for w in wordList])) for symbol in symbols]

    # Find the total number of symbols (of interest, i.e. from symbols) in
    # wordList.
    numSymbols = sum([i[1] for i in f])

    # Create a dictionary with keys from symbols and values the relative
    # frequencies of each.
    return dict([(i[0],float(i[1])/float(numSymbols)) for i in f])



def calculateFrequencies(wordList, symbols=defaultSymbols, subsymbol=lambda x,y: True if y.find(x) >= 0 else False):
    """calculateFrequencies(wordList, symbols=defaultSymbols,
                            subsymbol=lambda x,y: True is y.find(x) >= 0 else False)

    Given a list of words over the specified collection of symbols, calculate
    the frequency of each symbol in the word list. The results are returned
    as a dictionary with keys from symbols and values the relative frequency
    of the symbol (i.e. a value in the range [0,1]). Note that symbols must
    not contain duplicate entries.

    subsymbol is a function taking two arguments, x and y, which returns True if
    x is a subsymbol of y and False otherwise. (Since symbols is not permitted
    to contain duplicate entries, proper vs. nonproper subsymbols need not be a
    consideration.) The default implementation works for strings in the standard
    subsymbol as subset interpretation; other representations of symbols will
    require their own subsymbol implementation.

    If no symbol is contained in any other, then estimateFrequencies returns the
    same result as calculateFrequenices and is significantly more efficient."""

    # Make sure there are no duplicate symbols.
    assert(len(symbols) == len(set(symbols)))

    # First we determine an order in which to count symbols.
    processingOrder = []

    # If s, t are symbols such that s is a subsymbol of t, i.e. s is contained
    # in t, then t must be counted before s: we will count all occurences of
    # symbol t in a word and then remove them from the word so that we do not
    # count each t as contributing to s as well. Store this information in
    # a dependency forest.
    deps = dict([(key, set([i for i in symbols if i != key and subsymbol(key,i)])) for key in symbols])

    # Continue while there are symbols remaining.
    while deps:
        processed = []
        for symbol, depset in deps.items():
            # If we have dependencies that have not yet been satisfied, wait
            # to process this symbol.
            if depset:
                continue

            # Otherwise, we can process this symbol now.
            processingOrder.append(symbol)
            processed.append(symbol)
            for psymbol, pdepset in deps.items():
                pdepset.discard(symbol)

        # Remove all processed symbols from deps.
        for symbol in processed:
            deps.pop(symbol)

    # We now have a valid order in which to process symbols as described above.
    # Create a dictionary to hold the count for each symbol.
    f = dict.fromkeys(symbols, 0)

    # Iterate over each word and count all the symbols.
    for word in wordList:
        for symbol in processingOrder:
            # If the word is empty, we have exhausted it, so stop immediately
            # instead of continuing to check it for more symbols.
            if not word:
                break

            # Count all instances of symbol in word and remove them.
            f[symbol] += word.count(symbol)
            word = word.replace(symbol, '')

    # Now we have a dictionary of symbols and their counts. Calculate the
    # total number of symbols found and use to return a dictionary of
    # relative frequencies.
    numSymbols = sum(f.values())
    return dict([(symbol, float(count)/float(numSymbols)) for symbol, count in f.items()])



def createDice(frequencies, diceSpecs=[6]*16):
    """createDice(frequencies, diceSpecs=[6]*16)

    Given a relative frequency table (i.e. a table mapping symbols to their
    relative frequency in the word list that will be used), create a set of
    Boggle-like "dice" to try to capture the frequencies.

    diceSpecs is a list of specifications of the dice: diceSpecs[i] should
    be the number of faces to appear on the ith die. By default, we specify
    16 standard 6-sided dice."""

    # Calculate the number of times each symbol should appear, by frequency.
    totalNumberOfFacesRemaining = sum(diceSpecs)
    numberOfFacesPerSymbol = {}

    # In order to handle floating point numbers and rounding, we process one
    # symbol at a time. Calculate the number of faces it should appear on
    # (minimum 1), and then recalculate the proportions.
    modifiedFrequencies = sorted(map(list, frequencies.items()), key=lambda x:x[1], reverse=True)
    while modifiedFrequencies:
        # Get the first symbol and its frequency and remove it. Do this from
        # smallest to largest frequency for rounding reasons: for smaller
        # frequencies, we require at least 1 face, so if we wait until the end
        # to process a small frequency that barely appears, we may have no faces
        # left to distribute. By dealing with the small frequencies first, this
        # problem is avoided.
        symbol, frequency = modifiedFrequencies.pop()

        # Calculate the number of faces. Every symbol must appear at least once.
        numberOfFaces = max(1, int(round(frequency * totalNumberOfFacesRemaining)))
        numberOfFacesPerSymbol[symbol] = numberOfFaces
        totalNumberOfFacesRemaining -= numberOfFaces

        # Now recalculate the proportions for the remaining symbols.
        totalProportion = sum(map(lambda x:x[1], modifiedFrequencies))
        for frequencyPair in modifiedFrequencies:
            frequencyPair[1] /= totalProportion

    # Now make sure that we have the right number of faces.
    assert(sum(numberOfFacesPerSymbol.values()) == sum(diceSpecs))

    # Distribute the faces randomly. Do this by creating a list of all faces and
    # then shuffling them and distributing them to each die.
    faces = [symbol
             for (symbol, numberOfFaces) in numberOfFacesPerSymbol.items()
             for i in range(numberOfFaces)]
    random.shuffle(faces)
    dice = []
    for spec in diceSpecs:
        dice.append(faces[:spec])
        faces[:spec] = []

    # Make sure there are no faces left.
    assert(not faces)

    return dice


if __name__ == '__main__':
    import boggleboard.yawl
    f = calculateFrequencies(boggleboard.yawl.wordList)
    print(createDice(f))
