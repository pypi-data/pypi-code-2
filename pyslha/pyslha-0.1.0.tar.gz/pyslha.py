#! /usr/bin/env python

"""\
A simple but flexible parser of SUSY Les Houches Accord (SLHA) model and decay files.

TODO: Write SLHA objects to string / file object.
"""

from __future__ import with_statement

__author__ = "Andy Buckley <andy.buckley@cern.ch"
__version__ = "0.1.0"

import re

def _autotype(var):
    if type(var) != str:
        return var
    if var.isdigit():
        return int(var)
    try:
        f = float(var)
        return f
    except ValueError:
        return var


class Block(object):
    """
    Object representation of any BLOCK elements read from the SLHA file.  Blocks
    have a name, may have an associated Q value, and then a collection of data
    entries, stored as a recursive dictionary. Types in the dictionary are
    numeric (int or float) when a cast from the string in the file has been
    possible.
    """
    def __init__(self, name, q=None):
        self.name = name
        self.entries = {}
        self.q = _autotype(q)

    def add_entry(self, entry):
        #print entry
        nextparent = self.entries
        if len(entry) < 2:
            raise Exception("Block entries must be at least a 2-tuple")
        #print "in", entry
        entry = map(_autotype, entry)
        #print "out", entry
        for e in entry[:-2]:
            if e is not entry[-1]:
                nextparent = nextparent.setdefault(e, {})
        nextparent[entry[-2]] = entry[-1]
        #print self.entries

    def __cmp__(self, other):
        return self.name < other.name

    def __str__(self):
        s = self.name
        if self.q is not None:
            s += " (Q=%s)" % self.q
        s += "\n"
        s += str(self.entries)
        return s


class Decay(object):
    """
    Object representing a decay entry on a particle decribed by the SLHA file.
    'Decay' objects are not a direct representation of a DECAY block in an SLHA
    file... that role, somewhat confusingly, is taken by the Particle class.

    Decay objects have three properties: a branching ratio, br, an nda number
    (number of daughters == len(ids)), and a tuple of PDG PIDs to which the
    decay occurs. The PDG ID of the particle whose decay this represents may
    also be stored, but this is normally known via the Particle in which the
    decay is stored.
    """
    def __init__(self, br, nda, ids, parentid=None):
        self.parentid = parentid
        self.br = br
        self.nda = nda
        self.ids = ids

    def __cmp__(self, other):
        return self.br < other.br

    def __str__(self):
        return "%e %s" % (self.br, self.ids)


class Particle(object):
    """
    Representation of a single, specific particle, decay block from an SLHA
    file.  These objects are not themselves called 'Decay', since that concept
    applies more naturally to the various decays found inside this
    object. Particle classes store the PDG ID (pid) of the particle being
    represented, and optionally the mass (mass) and total decay width
    (totalwidth) of that particle in the SLHA scenario. Masses may also be found
    via the MASS block, from which the Particle.mass property is filled, if at
    all. They also store a list of Decay objects (decays) which are probably the
    item of most interest.
    """
    def __init__(self, pid, totalwidth=None, mass=None):
        self.pid = pid
        self.totalwidth = totalwidth
        self.mass = mass
        self.decays = []

    def add_decay(self, br, nda, ids):
        self.decays.append(Decay(br, nda, ids))
        self.decays.sort()

    def __cmp__(self, other):
        if abs(self.pid) == abs(other.pid):
            return self.pid < other.pid
        return abs(self.pid) < abs(other.pid)

    def __str__(self):
        s = str(self.pid)
        if self.mass is not None:
            s += " : mass = %e GeV" % self.mass
        if self.totalwidth is not None:
            s += " : total width = %e GeV" % self.totalwidth
        for d in self.decays:
            if d.br > 0.0:
                s += "\n  %s" % d
        return s


def readSLHAFile(spcfilename):
    """
    Read an SLHA file, returning dictionaries of blocks and decays.
    """
    with open(spcfilename, "r") as f:
        return readSLHA(f.read())


def readSLHA(spcstr):
    """
    Read an SLHA definition from a string, returning dictionaries of blocks and decays.
    """
    blocks = {}
    decays = {}
    #
    currentblock = None
    currentdecay = None
    for line in spcstr.splitlines():
        ## Handle (ignore) comment lines
        if line.startswith("#"):
            continue
        if "#" in line:
            line = line[:line.index("#")]

        ## Handle BLOCK/DECAY start lines
        if line.upper().startswith("BLOCK"):
            match = re.match(r"BLOCK\s+(\w+)\s+(Q=\s*.+)?", line.upper())
            if not match:
                continue
            blockname = match.group(1)
            qstr = match.group(2)
            if qstr is not None:
                qstr = qstr[2:].strip()
            currentblock = blockname
            currentdecay = None
            blocks[blockname] = Block(blockname, q=qstr)
        elif line.upper().startswith("DECAY"):
            match = re.match(r"DECAY\s+(\d+)\s+([\d\.E+-]+).*", line.upper())
            if not match:
                continue
            pdgid = int(match.group(1))
            width = float(match.group(2))
            currentblock = "DECAY"
            currentdecay = pdgid
            decays[pdgid] = Particle(pdgid, width)
        else:
            ## In-block line
            if currentblock is not None:
                items = line.split()
                # TODO: Sort out tuple item types: autoconvert integers and floats
                if len(items) < 1:
                    continue
                if currentblock != "DECAY":
                    #print currentblock
                    if len(items) < 2:
                        ## Treat the ALPHA block differently
                        blocks[currentblock].value = _autotype(items[0])
                        blocks[currentblock].add_entry((0, items[0]))
                    else:
                        blocks[currentblock].add_entry(items)
                else:
                    br = float(items[0])
                    nda = int(items[1])
                    ids = map(int, items[2:])
                    decays[currentdecay].add_decay(br, nda, ids)

    ## Try to populate Particle masses from the MASS block
    for pid in blocks["MASS"].entries.keys():
        if decays.has_key(pid):
            decays[pid].mass = blocks["MASS"].entries[pid]

    return blocks, decays



if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        blocks, decays = readSpcFile(a)

        for bname, b in sorted(blocks.iteritems()):
            print b
            print

        print blocks["MASS"].entries[25]
        print

        for p in sorted(decays.values()):
            print p
            print
