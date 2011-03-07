# -*- coding: utf-8 -*-

"""
This transliterator handles conversion from the basic Coptic script to Roman script, but does not currently address some variants like Old Coptic
Copyright 2001, New York University
By Tom Elliott and Roger Bagnall
"""

copt_capital = {
    u"\u03E2" : "SH",    # Coptic capital letter shei
    u"\u03E3" : "sh",    # Coptic small letter shei
    u"\u03E4" : "F",    # Coptic capital letter fei
    u"\u03E5" : "f",    # coptic small letter fei
    u"\u03E6" : "KH",    # Coptic capital letter khei
    u"\u03E7" : "kh",    # Coptic small letter khei
    u"\u03E8" : "H",    # Coptic capital letter hori
    u"\u03E9" : "h",    # Coptic small letter hori
    u"\u03EA" : "J",    # Coptic capital letter gangia
    u"\u03EB" : "j",     # Coptic small letter gangia
    u"\u03EC" : "Q",     # Coptic captial letter shima
    u"\u03ED" : "q",     # Coptic small letter shima
    u"\u03EE" : "TI",     # Coptic captial letter dei
    u"\u03EF" : "ti",      # Coptic small letter dei    
        u"\u2C80" : "A",     # Coptic capital letter alfa
    u"\u2C82" : "B",     # Coptic capital letter vida
    u"\u2C84" : "G",     # Coptic capital letter gamma
    u"\u2C86" : "D",     # Coptic capital letter dalda
    u"\u2C88" : "E",     # Coptic capital letter eie
    # u"\u2C8A" : "",     Coptic capital letter sou  -- omitted per RSB
    u"\u2C8C" : "Z",     # Coptic capital letter zata
    u"\u2C8E" : "E",     # Coptic capital letter hate
    u"\u2C90" : "TH",     # Coptic capital letter thethe
    u"\u2C92" : "I",     # Coptic capital letter iauda
    u"\u2C94" : "K",     # Coptic capital letter kapa
    u"\u2C96" : "L",     # Coptic capital letter laula
    u"\u2C98" : "M",     # Coptic capital letter mi
    u"\u2C9A" : "N",     # Coptic capital letter ni
    u"\u2C9C" : "X",     # Coptic capital letter ksi
    u"\u2C9E" : "O",     # Coptic capital letter o
    u"\u2CA0" : "P",     # Coptic capital letter pi
    u"\u2CA2" : "R",     # Coptic capital letter ro
    u"\u2CA4" : "S",     # Coptic capital letter sima
    u"\u2CA6" : "T",     # Coptic capital letter tau
    u"\u2CA8" : "U",     # Coptic capital letter ua
    u"\u2CAA" : "PH",     # Coptic capital letter fi
    u"\u2CAC" : "CH",     # Coptic capital letter khi
    u"\u2CAE" : "PS",     # Coptic capital letter psi
    u"\u2CB0" : "O",     # Coptic capital letter oou
}

copt_small = {
    u"\u03E2" : "SH",    # Coptic capital letter shei
    u"\u03E3" : "sh",    # Coptic small letter shei
    u"\u03E4" : "F",    # Coptic capital letter fei
    u"\u03E5" : "f",    # coptic small letter fei
    u"\u03E6" : "KH",    # Coptic capital letter khei
    u"\u03E7" : "kh",    # Coptic small letter khei
    u"\u03E8" : "H",    # Coptic capital letter hori
    u"\u03E9" : "h",    # Coptic small letter hori
    u"\u03EA" : "J",    # Coptic capital letter gangia
    u"\u03EB" : "j",     # Coptic small letter gangia
    u"\u03EC" : "Q",     # Coptic captial letter shima
    u"\u03ED" : "q",     # Coptic small letter shima
    u"\u03EE" : "TI",     # Coptic captial letter dei
    u"\u03EF" : "ti",      # Coptic small letter dei    
        u"\u2C81" : "a",     # Coptic small letter alfa
    u"\u2C83" : "b",     # Coptic small letter vida
    u"\u2C85" : "g",     # Coptic small letter gamma
    u"\u2C87" : "d",     # Coptic small letter dalda
    u"\u2C89" : "e",     # Coptic small letter eie
    # u"\u2C8B" : "",     # Coptic small letter sou -- omitted per RSB
    u"\u2C8D" : "z",     # Coptic small letter zata
    u"\u2C8F" : "e",     # Coptic small letter hate
    u"\u2C91" : "th",     # Coptic small letter thethe
    u"\u2C93" : "i",     # Coptic small letter iauda
    u"\u2C95" : "k",     # Coptic small letter kapa
    u"\u2C97" : "l",     # Coptic small letter laula
    u"\u2C99" : "m",     # Coptic small letter mi
    u"\u2C9B" : "n",     # Coptic small letter ni
    u"\u2C9D" : "x",     # Coptic small letter ksi
    u"\u2C9F" : "o",     # Coptic small letter o
    u"\u2CA1" : "p",     # Coptic small letter pi
    u"\u2CA3" : "r",     # Coptic small letter ro
    u"\u2CA5" : "s",     # Coptic small letter sima
    u"\u2CA7" : "t",     # Coptic small letter tau
    u"\u2CA9" : "u",     # Coptic small letter ua
    u"\u2CAB" : "ph",     # Coptic small letter fi
    u"\u2CAD" : "ch",     # Coptic small letter khi
    u"\u2CAF" : "ps",     # Coptic small letter psi
    u"\u2CB1" : "o",     # Coptic small letter oou
}

# do these occur in names?
copt_combining = {
    u"\u2CEF" : "",    # Coptic combining ni above
    u"\u2CF0" : "",     # Coptic combining spiritus asper
    u"\u2CF1" : "",    # Coptic combining spiritus lenis
}

# legal punctuation (for lacunae)
legal_punctuation = {
    u"(" : "(",
    u")" : ")", 
    u"." : "."
}

# omitted ranges:
# Coptic Other Capitals
# Coptic Other Small
# Old Coptic
# Dialect P
# akhmimic
# Nubian
# cryptogrammic
# Coptic Symbols
# Coptic Punctuation

        
def validate(value, allow):
    invalids = []
    
    for i, c in enumerate(value):
        # verify character is within the possible general ranges, if not, mark it as invalid and move on
        # otherwise, check to make sure the character is truly valid (ranges are sparsely populated)
        cval = ord(c)
        if cval in range(0x2c80, 0x2d00) or cval in range(0x0370,0x0400) or c == u' ':
            b = None
            if c == u' ':
                b = c
            if not(b) and ('small' in allow or 'mixed' in allow or 'all' in allow):
                try:
                    b = copt_small[c]
                except:
                    pass
            if not(b) and ('capital' in allow or 'mixed' in allow or 'all' in allow):
                try:
                    b = copt_capital[c]
                except:
                    pass
            if not(b):
                try:
                    b = copt_combining[c]
                except:
                    pass
            if not(b):
                invalids.append({'position':i, 'character':c, 'reason':'illegal character in appropriate Unicode range'})
        else:
            invalids.append({'position':i, 'character':c, 'reason':'illegal character from outside appropriate Unicode range'})
    return invalids


def transliterate(value):
    transliteration = ''
    for c in value:
        if c == ' ':
            transliteration += c
            continue        
        b = '?'
        try:
            b = copt_small[c]
        except:
            try:
                b = copt_capital[c]
            except:
                try:
                    b = copt_combining[c]
                except:
                    try:
                        b = legal_punctuation[c]
                    except:
                        pass
        transliteration += b
    return transliteration.encode('utf-8')
    
    
        