# -*- coding: utf-8 -*-

# Copyright 2011 Institute for the Study of the Ancient World, New York
# University

tr_capital = {
    u"A" : "A",    # Turkish capital letter a
    u"B" : "B",    # Turkish capital letter b
    u"C" : "C",    # Turkish capital letter c
    u"Ç" : "C",    # Turkish capital letter c-cedilla
    u"D" : "D",    # Turkish capital letter d
    u"E" : "E",    # Turkish capital letter e
    u"F" : "F",    # Turkish capital letter f
    u"G" : "G",    # Turkish capital letter g
    u"Ğ" : "G",    # Turkish captial letter g-breve
    u"H" : "H",    # Turkish capital letter h
    u"I" : "I",    # Turkish capital letter dotless i'
    u"İ" : "I",    # Turkish capital letter i
    u"J" : "J",     # Turkish capital letter j
    u"K" : "K",    # Turkish capital letter k
    u"L" : "L",    # Turkish capital letter l
    u"M" : "M",    # Turkish capital letter m
    u"N" : "N",    # Turkish capital letter n
    u"O" : "O",    # Turkish capital letter o
    u"Ö" : "O",
    u"P" : "P",    # Turkish capital letter p
    
    u"R" : "R",    # Turkish capital letter r
    u"S" : "S",    # Turkish capital letter s
    u"Ş" : "S",
    u"T" : "T",    # Turkish capital letter t
    u"U" : "U",    # Turkish captial letter u
    u"Ü" : "U",
    u"V" : "V",    # Turkish capital letter v
    
    u"Y" : "Y",    # Turkish capital letter y
    u"Z" : "Z"     # Turkish capital letter z
}

tr_small = {
    u"a" : "a",    # Turkish small letter a
    u"b" : "b",    # Turkish small letter b
    u"c" : "c",    # Turkish small letter c
    u"ç" : "c",    # Turkish small letter c-cedilla
    u"d" : "d",    # Turkish small letter d
    u"e" : "e",    # Turkish small letter e
    u"f" : "f",    # Turkish small letter f
    u"g" : "g",    # Turkish small letter g
    u"ğ" : "g",    # Turkish small letter g-breve
    u"h" : "h",    # Turkish small letter h
    u"ı" : "i",    # Turkish small letter dotless i
    u"i" : "i",    # Turkish small letter i
    u"j" : "j",     # Turkish small letter j
    u"k" : "k",    # Turkish small letter k
    u"l" : "l",    # Turkish small letter l
    u"m" : "m",    # Turkish small letter m
    u"n" : "n",    # Turkish small letter n
    u"o" : "o",    # Turkish small letter o
    u"ö" : "o",
    u"p" : "p",    # Turkish small letter p
    u"r" : "r",    # Turkish small letter r
    u"s" : "s",    # Turkish small letter s
    u"ş" : "s",
    u"t" : "t",    # Turkish small letter t
    u"u" : "u",    # Turkish small letter u
    u"ü" : "u",
    u"v" : "v",     # Turkish small letter v
    u"y" : "y",    # Turkish capital letter y
    u"z" : "z"     # Turkish capital letter z
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
        if cval in range(0x0028, 0x007B) or cval in range(0x0088, 0x0180) or c == u' ':
            b = None
            if c == u' ':
                b = c
            if not(b) and ('small' in allow or 'mixed' in allow or 'all' in allow):
                try:
                    b = tr_small[c]
                except:
                    pass
            if not(b) and (
                'capital' in allow or 'mixed' in allow or 'all' in allow):
                try:
                    b = tr_capital[c]
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
            b = tr_small[c]
        except:
            try:
                b = tr_capital[c]
            except:
                try:
                    b = legal_punctuation[c]
                except:
                    pass
        transliteration += b
    return transliteration.encode('utf-8')
    
