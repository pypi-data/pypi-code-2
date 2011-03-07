# -*- coding: utf-8 -*-

# Copyright 2011 Institute for the Study of the Ancient World, New York
# University

en_capital = {
    u"A" : "A",    # English capital letter a
    u"B" : "B",    # English capital letter b
    u"C" : "C",    # English capital letter c
    u"D" : "D",    # English capital letter d
    u"E" : "E",    # English capital letter e
    u"F" : "F",    # English capital letter f
    u"G" : "G",    # English capital letter g
    u"H" : "H",    # English capital letter h
    u"I" : "I",    # English capital letter i
    u"J" : "J",     # English capital letter j
    u"K" : "K",    # English capital letter k
    u"L" : "L",    # English capital letter l
    u"M" : "M",    # English capital letter m
    u"N" : "N",    # English capital letter n
    u"O" : "O",    # English capital letter o
    u"P" : "P",    # English capital letter p
    u"Q" : "Q",    # English capital letter q
    u"R" : "R",    # English capital letter r
    u"S" : "S",    # English capital letter s
    u"T" : "T",    # English capital letter t
    u"U" : "U",    # English captial letter u
    u"V" : "V",    # English capital letter v
    u"W" : "W",   # English capital leter W
    u"X" : "X",    # English capital letter x
    u"Y" : "Y",    # English capital letter y
    u"Z" : "Z"     # English capital letter z
}

en_small = {
    u"a" : "a",    # English small letter a
    u"b" : "b",    # English small letter b
    u"c" : "c",    # English small letter c
    u"d" : "d",    # English small letter d
    u"e" : "e",    # English small letter e
    u"f" : "f",    # English small letter f
    u"g" : "g",    # English small letter g
    u"h" : "h",    # English small letter h
    u"i" : "i",    # English small letter i
    u"j" : "j",     # English small letter j
    u"k" : "k",    # English small letter k
    u"l" : "l",    # English small letter l
    u"m" : "m",    # English small letter m
    u"n" : "n",    # English small letter n
    u"o" : "o",    # English small letter o
    u"p" : "p",    # English small letter p
    u"q" : "q",    # English small letter q
    u"r" : "r",    # English small letter r
    u"s" : "s",    # English small letter s
    u"t" : "t",    # English small letter t
    u"u" : "u",    # English small letter u
    u"v" : "v",     # English small letter v
    u"w" : "w",    # English small letter w
    u"x" : "x",    # English capital letter x
    u"y" : "y",    # English capital letter y
    u"z" : "z"     # English capital letter z
}

# legal punctuation (for lacunae)
legal_punctuation = {
    u"(" : "(",
    u")" : ")", 
    u"." : "."
}


def validate(value, allow):
    invalids = []
    for i, c in enumerate(value):
        # verify character is within the possible general ranges, if not, mark
        # it as invalid and move on otherwise, check to make sure the character
        # is truly valid (ranges are sparsely populated)
        cval = ord(c)
        if cval in range(0x0028, 0x007B) or c == u' ':
            b = None
            if c == u' ':
                b = c
            if not(b) and ('small' in allow or 'mixed' in allow or 'all' in allow):
                try:
                    b = en_small[c]
                except:
                    pass
            if not(b) and ('capital' in allow or 'mixed' in allow or 'all' in allow):
                try:
                    b = en_capital[c]
                except:
                    pass
            if not(b):
                invalids.append({
                    'position': i, 
                    'character': c, 
                    'reason': 'illegal character in appropriate Unicode range'})
        else:
            invalids.append({
                'position': i, 
                'character': c, 
                'reason': 'illegal character outside appropriate Unicode range'})
    return invalids

def transliterate(value):
    transliteration = ''
    for c in value:
        if c == ' ':
            transliteration += c
            continue
        b = '?'
        try:
            b = en_small[c]
        except:
            try:
                b = en_capital[c]
            except:
                try:
                    b = legal_punctuation[c]
                except:
                    pass
        transliteration += b
    return transliteration
    
