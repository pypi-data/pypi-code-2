#!/usr/bin/python
# -*- coding: utf8 -*-
"""
Helper to repair encodings (especially umlauts)

It is alarming, that very often, special characters like umlauts break when
converting through different encodings. (You might want to take a look at the
German Amazon Marketplace.)
A broken umlaut is still valid in the target encoding and therefore can only be
detect through heuristics (magic).

Version 0.6: supporting utf-8 and latin1
For a full changeset, take a look at bitbucket.org/niels_mfo/encoding_repair
(bug reports will also be accepted there)

A common case that breaks a special character is the following:
    - An input string is coded in utf-8 (which uses multibyte chars)
    - It is interpreted as being a valid latin1 string
    - Latin1 has a valid representation for nearly all bytes
    - Latin1 uses single-byte chars
    - Now both bytes of the multi-byte char are interpreted as chars
    - The special char broke off into two different (valid!) characters

This scenario has many pitfalls:
    - The characters are irreversebly broken.
    - ... regardless of what you do with the string.
    - You can convert it through all encodings and the umlauts won't come back.
    - Only through a few heuristical replaces, this module is able to help you.

This module assumes, that a few special characters are always correct. They are
stored in the list 'umlauts'. Furthermore, the module assumes, that their
representation, that would be correct in the other encoding, is always broken in
the target-encoding.

NOTE:
This only happens, because people don't use unicode. If everybody would
consequently use unicode strings, I would not have to write this module.
The best and actually only way to handle encodings correctly is the following:
    - An input string comes into your programm.
    - If it is unicode, jump to point 6.
    - If it isn't, you might already need to repair umlauts.
    - You need to make sure, that you know the right encoding of the input
        string, because it is hardly possible to guess.
    - Convert it to unicode.
    - Use the unicode string throuout your whole programm.
    - If you can return unicode, return unicode.
    - If you are in doubt, return unicode.
    - If you really need to return anything else, return utf-8.
    - If you are certain, that the programm, which will take your output is not
        able to handle neither unicode nor utf-8, you better write a bug report.
"""


umlauts = list(u'ßäöüáàéèíìóòúùýçÄÖÜÁÀÉÈÍÌÓÒÚÙÝÇ')

utf8_to_latin1_umlauts = dict()
latin1_to_utf8_umlauts = dict()

for c in umlauts:
    utf8_to_latin1_umlauts[c.encode('utf8')] = c.encode('latin1')
    latin1_to_utf8_umlauts[c.encode('latin1')] = c.encode('utf8')


def replace_all(text, dict):
    """
    replace_all(text, dict) -> string

    Search for all occurances of dict's keys in text and replace them with their
    specific values.

    >>> s = u'one@two.com; two@three.com; 405@eleven.com'
    >>> replace = {
    ...     '@': '<at>',
    ...     '; ': ' and '
    ... }
    >>> replace_all(s, replace)
    u'one<at>two.com and two<at>three.com and 405<at>eleven.com'
    """
    # This function is actually pretty bad.
    # Please help me improving it.
    for search in dict:
        text = text.replace(search, dict[search])
    return text

def repair_umlauts_latin1(s):
    """
    repair_umlauts_latin1(s) -> str

    Return a copy of the string, with all umlauts replaced, that have accidently
    been encoded to utf8. Only looks for the umlauts from the list 'umlauts'.
    
    >>> ue_latin1 = '\xfc'
    >>> ue_utf8 = '\xc3\xbc'
    >>> repair_umlauts_latin1(ue_utf8) == ue_latin1
    True
    >>> repair_umlauts_latin1(ue_latin1) == ue_latin1
    True
    >>> oe_latin1 = '\xf6'
    >>> oe_utf8 = '\xc3\xb6'
    >>> repair_umlauts_latin1(oe_utf8) == oe_latin1
    True
    >>> repair_umlauts_latin1(oe_latin1) == oe_latin1
    True
    """
    return replace_all(s, utf8_to_latin1_umlauts)

def repair_umlauts_utf8(s):
    """
    repair_umlauts_utf8(s) -> str

    Return a copy of the string, with all umlauts replaced, that have accidently
    been encoded to latin1. Only looks for the umlauts from the list 'umlauts'.

    >>> ue_latin1 = '\xfc'
    >>> ue_utf8 = '\xc3\xbc'
    >>> repair_umlauts_utf8(ue_latin1) == ue_utf8
    True
    >>> repair_umlauts_utf8(ue_utf8) == ue_utf8
    True
    >>> oe_latin1 = '\xf6'
    >>> oe_utf8 = '\xc3\xb6'
    >>> repair_umlauts_utf8(oe_latin1) == oe_utf8
    True
    >>> repair_umlauts_utf8(oe_utf8) == oe_utf8
    True
    """
    return replace_all(s, latin1_to_utf8_umlauts)

def file_repair_umlauts_utf8(input_filename, output_filename=None):
    """
    file_repair_umlauts_utf8(input_filename[, output_filename]) -> None

    Reads the file's contents and replaces umlauts, that have accidently been
    encoded to latin1. Only looks for the umlauts from the list 'umlauts'.
    
    If no output-file is specified, the input file will be overwritten.
    """
    if output_filename is None: output_filename = input_filename
    s = file(input_filename).read()
    s = repair_umlauts_utf8(s)
    file(output_filename, 'w').write(s)

def file_repair_umlauts_latin1(input_filename, output_filename=None):
    """
    file_repair_umlauts_utf8(input_filename[, output_filename]) -> None

    Reads the file's contents and replaces umlauts, that have accidently been
    encoded to utf8. Only looks for the umlauts from the list 'umlauts'.
    
    If no output-file is specified, the input file will be overwritten.
    """
    if output_filename is None: output_filename = input_filename
    s = file(input_filename).read()
    s = repair_umlauts_latin1(s)
    file(output_filename, 'w').write(s)


def magic_to_utf8(s):
    """
    magic_to_utf8(s) -> string

    Guesses the input's encoding by assuming it is utf8. If there is no valid
    representation in utf8, it assumes, the input is latin1 (nearly every string
    is valid as a latin1 string) and converts it to utf8.
    Afterwards, it calls repair_umlauts_utf8 on the string which tries to
    replace broken special characters.
    
    Main author: Michael Brickenstein
    
    >>> ue_latin1 = '\xfc'
    >>> ue_utf8 = '\xc3\xbc'
    >>> ue_utf8 == magic_to_utf8(ue_latin1)
    True
    >>> magic_to_utf8(ue_utf8) == ue_utf8
    True
    >>> oe_latin1 = '\xf6'
    >>> oe_utf8 = '\xc3\xb6'
    >>> magic_to_utf8(oe_latin1) == oe_utf8
    True
    >>> magic_to_utf8(oe_utf8) == oe_utf8
    True
    >>> oe_utf8.decode('latin1') == oe_latin1.decode('latin1')
    False
    """
    if s is None:
        return None

    if isinstance(s, unicode):
        u = s.encode('utf8')
    else:
        try:
            u = s.decode('utf8')
            #seems valid utf8, although no garuantee
            u = s
        except:
            u = s.decode('latin1')
            u = u.encode('utf8')
    
    return repair_umlauts_utf8(u)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
