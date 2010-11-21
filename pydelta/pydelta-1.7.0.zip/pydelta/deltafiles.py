"""This module contains routines for loading DELTA format text files.
The main function is:
deltafiles.load("chars", "items", "specs", "cnotes")
"""
from __future__ import absolute_import
from .pydelta import *
# For splitting strings while ignoring splitters within comments.
from . import structxt

#----- CONFOR directives (can be "*TEXT" or "* TEXT", so check for the
#         * separately
showDirective   = "SHOW"
itemDirective   = "ITEM DESCRIPTIONS"
charDirective   = "CHARACTER LIST"
typeDirective   = "CHARACTER TYPES"
depDirective    = "DEPENDENT CHARACTERS"
cnoteDirective  = "CHARACTER NOTES"
cimgDirective   = "CHARACTER IMAGES"
timgDirective   = "TAXON IMAGES"
impvalDirective = "IMPLICIT VALUES"

#----- PANKEY directives
headingDirective = "HEADING"
altCharDirective = "CHARACTER DESCRIPTIONS"

def load(chars_fname, items_fname, specs_fname=None, cnotes_fname=None):
    """Load a set of DELTA files. As a minimum, this needs a chars files
    and an items file. The specs and cnotes files can also be loaded."""
    chars = parse_characters(chars_fname)
    if cnotes_fname:
        parse_cnotes(cnotes_fname, chars)
    items = parse_items(items_fname)
    delta = Delta(chars, items)
    if specs_fname:
        parse_specs(specs_fname, delta)
    return delta
    
def extract_attributes(attrlst):
    """
    Processes a DELTA attribute list (for an item, or in the specs, e.g. for
    implicit values). Returns a dictionary of the attributes.
    """
    attribs = {}
    for attrchunk in structxt.splitwithout(attrlst, " ", [("<", ">")]):
        if not attrchunk.strip(): # ignore blank segments
            continue
        
        # Normal attribute format is: charnum,value (e.g. 5,1-2)
        bits = structxt.splitwithout(attrchunk, ",", [("<", ">")])
        if len(bits) == 2:
            charnums, value = bits
            charnums = remove_comments(charnums)
        else:   # Text character (text value stored like a comment: 6<text>)
            charnums = remove_comments(attrchunk)
            if charnums:
                value = extract_comment(attrchunk)
        
        #--- Store attribute
        charnums = expand_range(charnums)
        for charnum in charnums:
            attribs[charnum] = value
    
    return attribs

#----- Reads the feature of a character
def __read_character(cline): 
    char = CharDescr()
    cbits = structxt.splitwithout(cline, '/', containermarks = [("<",">")])
    char.feature = cbits[0][cbits[0].find('.')+1:].lstrip()
    if len(cbits) <= 3:
        char.char_type = CT['IN']
        if cbits[1]:
            char.unit = cbits[1].strip()
    else:
        for cstate in cbits[1:-1]:
            char.states.append(cstate[cstate.find('.')+1:].strip())
        char.char_type = CT['UM']
    # These character types may be overridden when a Specs file is read.
    
    return char
    
#----- Reads a character note, returns it with the relevant character number
def __read_cnote(cnotetxt):
    bits = cnotetxt.partition(". ")
    cnums = expand_range(bits[0].strip('# \t'))
    return (cnums, bits[2])
    
#----- Parses the character list file and extracts the character and character state names
def parse_characters(fname):
    """
    Parses the list of characters from the file.
    """
    fchars = open(fname, "r")
    
    charlist = DeltaCharList(fname)
            
    #--- Reading loop
    for cline in fchars:        
        if cline.startswith('*'):
            #--- Reading a directive
            if cline.find(showDirective) != -1:
                charlist.title = cline.partition(showDirective)[-1].strip()
            elif cline.find(charDirective) != -1:
                charbuffer = ""
                break
            else:
                charlist.directives.append(cline)
        elif cline.startswith("#"):
            # We're already on the character list
            charbuffer = cline
            break
                
    for cline in fchars:
        cline = cline.strip()
        if not cline:
            continue   # Blank line
            
        if cline.startswith("#"):   # Next item
            if charbuffer:
                charlist.append(__read_character(charbuffer))
            charbuffer = cline
        else:   # Add line to current item.
            charbuffer += " " +cline
    
    # Add last character from list:
    if charbuffer:
        charlist.append(__read_character(charbuffer))
        
    fchars.close()
    return charlist
    
def parse_cnotes(fname, charlist):
    """
    Parses character notes from the specified file, adding
    them to the characters in the given list.
    """
    fcnotes = open(fname,"r")
    charlist.cnotedirectives = []
    charlist.cnotes_fname = fname
    
    cnotebuffer = ""
    #--- Reading loop
    for cline in fcnotes:
        cline = cline.strip()        
        if cline.startswith('*'):
            #--- Reading a directive
            if cline.find(cnoteDirective) != -1:
                break   # Move on to read the notes
            else:
                charlist.cnotedirectives.append(cline)
        elif cline.startswith("#"):  
            # We're already on the notes list.
            cnotebuffer = cline
            break
                
    for cline in fcnotes:
        cline = cline.strip()
        if not cline:
            continue   # Blank line
            
        if cline.startswith("#"):   # Next item
            if cnotebuffer:
                charnums, note = __read_cnote(cnotebuffer)
                for charnum in charnums:
                    charlist[charnum].notes = note
            cnotebuffer = cline
        else:   # Add line to current item.
            cnotebuffer += " " +cline
            
    # Add last cnote from list:
    if cnotebuffer:
        charnums, note = __read_cnote(cnotebuffer)
        for charnum in charnums:
            charlist[charnum].notes = note
                        
    fcnotes.close()
    return True
    
#----- Parses the items list file and extracts the item names and taxon attributes
def parse_items(fname):
    """
    Parse the list of items (typically taxa) from the file.
    """
    #--- Open the items file
    fitems = open(fname, "r")
    
    itemlist = DeltaItemList(fname)
     
    itembuffer = ""
    # Read directives:
    i = 0
    for cline in fitems:
        #--- Processing the line
        cline = cline.strip()
        if cline.startswith('*'):
            #--- Reading a directive
            if showDirective in cline:
                itemlist.title = cline.partition(showDirective)[-1].strip()
            elif itemDirective in cline:
                break   # Move on to read items
            else:
                itemlist.directives.append(cline)
        elif cline.startswith("#"):
            itembuffer = cline
            break    # We're already on the item list.
    
    # Read items:
    for cline in fitems:
        cline = cline.strip()
        if not cline:
            continue # Blank line
            
        if cline.startswith("#"): #Next item
            if itembuffer:
                itemlist.append(__read_item(itembuffer))
            itembuffer = cline
        else:   # Add line to current item.
            itembuffer += " " + cline
                
    # Add the last one in the list:
    if itembuffer:
        itemlist.append(__read_item(itembuffer))
    
    fitems.close()
    return itemlist
    
#----- Reads an item
def __read_item(cline):
    #-- Is given a line starting with #, and reads an item
    item = ItemDescr()
    cline = cline.strip('# \t')

    item = ItemDescr()
    item.name, dummy, attrlst = cline.partition('/')
    item.comment = extract_comment(item.name)
    item.attributes = extract_attributes(attrlst)
    return item
    
#----- Parse the specifications file
def parse_specs(fname, delta):
    """
    Parse the specifications from file.
    """
    #--- Open the items file
    fspecs = open(fname,"r")
    
    delta.specs_directives = []
    delta.specs_title = []
    
    specbuffer = []
    for cline in fspecs:
        cline = cline.strip()
        if not cline:             
            continue     # Blank line
        
        if cline.startswith('*'):
            #--- A new directive, I give unto you.
            if specbuffer:   # Process the previous directive
                __process_directive(" ".join(specbuffer), delta)
            specbuffer = [cline]
        else:    # Continuation of a directive.
            specbuffer.append(cline)
    
    # And take care of the last item:
    if specbuffer:
        __process_directive(" ".join(specbuffer), delta)
            
    fspecs.close()
    return True
    
def __process_directive(directive, delta):
    if showDirective in directive:
        delta.specs_title = directive.partition(showDirective)[-1].strip()
    elif typeDirective in directive:
        #--- Parse and read in the character types
        __parse_char_types(delta.chars, directive) 
    elif impvalDirective in directive:
        #-- Reading implicit values
        __parse_implicit_values(delta.chars, directive)
    ##elif depDirective in cline:
        #--- Reading dependent characters (not yet implemented)
        ##__parse_char_dependencies(delta.chars, cline)
    else:
        delta.specs_directives.append(directive)
    
#----- Parses "IMPLICIT VALUES" directive
def __parse_implicit_values(char_list, cline):
    cline = cline.partition("VALUES ")[2]
    impvals = extract_attributes(cline)
    for k, v in impvals.items():
        char_list[k].implicit = v
    return True
    
    
    #----- Retrieves the number of dependent characters
    #----- for a given control character and state
##    def get_depchar_nb(self, ccnum, ccstate): 
##        pass
    
    #----- Retrieves a dependent character (in 'rank' position)
    #----- for a given control character and state 
##    def get_depchar(self, ccnum, ccstate, rank): 
##        pass
    
    #----- Test if a character is dependent from
    #----- a given control character and state
##    def is_dependent(self, dcnum, ccnum, ccstate): 
##        pass
    
    # Protected member functions

#----- Parses "CHARACTER TYPES" directive
def __parse_char_types(char_list, cline):
    ctypes = cline.partition(typeDirective)[-1].split()
    for ctype in ctypes: 
        laux = ctype.split(',')
        
        #--- Store character type
        if laux[0].find('-') != -1: 
            chars = expand_range(laux[0])
            for charnum in chars:
                char_list[charnum].char_type = CT[laux[1]]
        else:
            char_list[int(laux[0])].char_type = CT[laux[1]]
    return
    
    #----- Parses "DEPENDENT CHARACTERS" directive
##    def __parse_char_dependencies(self, char_list, cline):
##        pass
