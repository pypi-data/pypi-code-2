#! /usr/bin/env python

"""\
A simple but flexible parser of SUSY Les Houches Accord (SLHA) model and decay files.

TODO: What to do about unlisted PIDs?
TODO: Split writeSLHA into writeSLHA{Blocks,Decays}
"""

from __future__ import with_statement

__author__ = "Andy Buckley <andy.buckley@cern.ch"
__version__ = "0.2.2"


def _autotype(var):
    """Automatically convert strings to numerical types if possible."""
    if type(var) is not str:
        return var
    if var.isdigit() or (var.startswith("-") and var[1:].isdigit()):
        return int(var)
    try:
        f = float(var)
        return f
    except ValueError:
        return var

def _autostr(var):
    """Automatically numerical types to the right sort of string."""
    if type(var) is float:
        return "%e" % var
    return str(var)



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
        return cmp(self.name, other.name)

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
        assert(self.nda == len(self.ids))

    def __cmp__(self, other):
        return cmp(other.br, self.br)

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
            return cmp(self.pid, other.pid)
        return cmp(abs(self.pid), abs(other.pid))

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


def readSLHAFile(spcfilename, **kwargs):
    """
    Read an SLHA file, returning dictionaries of blocks and decays.

    Other keyword parameters are passed to readSLHA.
    """
    with open(spcfilename, "r") as f:
        return readSLHA(f.read(), kwargs)


def readSLHA(spcstr, ignorenobr=False):
    """
    Read an SLHA definition from a string, returning dictionaries of blocks and
    decays.

    If the ignorenobr parameter is True, do not store decay entries with a
    branching ratio of zero.
    """
    blocks = {}
    decays = {}
    #
    import re
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
            #print line
            match = re.match(r"BLOCK\s+(\w+)(\s+Q=\s*.+)?", line.upper())
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
                if len(items) < 1:
                    continue
                if currentblock != "DECAY":
                    if len(items) < 2:
                        ## Treat the ALPHA block differently
                        blocks[currentblock].value = _autotype(items[0])
                        blocks[currentblock].entries = _autotype(items[0])
                    else:
                        blocks[currentblock].add_entry(items)
                else:
                    br = float(items[0])
                    nda = int(items[1])
                    ids = map(int, items[2:])
                    if br > 0.0 or not ignorenobr:
                        decays[currentdecay].add_decay(br, nda, ids)

    ## Try to populate Particle masses from the MASS block
    # print blocks.keys()
    try:
        for pid in blocks["MASS"].entries.keys():
            if decays.has_key(pid):
                decays[pid].mass = blocks["MASS"].entries[pid]
    except:
        raise Exception("No MASS block found, from which to populate particle masses")

    return blocks, decays


def readISAWIGFile(isafilename, **kwargs):
    """
    Read a spectrum definition from a file in the ISAWIG format, returning
    dictionaries of blocks and decays. While this is not an SLHA format, it is
    informally supported as a useful mechanism for converting ISAWIG spectra to
    SLHA.

    Other keyword parameters are passed to readSLHA.
    """
    with open(isafilename, "r") as f:
        return readISAWIG(f.read(), kwargs)


def readISAWIG(isastr, ignorenobr=False):
    """
    Read a spectrum definition from a string in the ISAWIG format, returning
    dictionaries of blocks and decays. While this is not an SLHA format, it is
    informally supported as a useful mechanism for converting ISAWIG spectra to
    SLHA.

    ISAWIG parsing based on the HERWIG SUSY specification format, from
    http://www.hep.phy.cam.ac.uk/~richardn/HERWIG/ISAWIG/file.html

    If the ignorenobr parameter is True, do not store decay entries with a
    branching ratio of zero.
    """

    ## PDG MC ID codes mapped to HERWIG SUSY ID codes, based on
    ## http://www.hep.phy.cam.ac.uk/~richardn/HERWIG/ISAWIG/susycodes.html
    HERWIGID2PDGID = {}
    HERWIGID2PDGID[203] =  25 ## HIGGSL0
    HERWIGID2PDGID[204] =  35 ## HIGGSH0
    HERWIGID2PDGID[205] =  36 ## HIGGSA0
    HERWIGID2PDGID[206] =  37 ## HIGGS+
    HERWIGID2PDGID[207] = -37 ## HIGGS-
    HERWIGID2PDGID[401] =  1000001 ## SSDLBR
    HERWIGID2PDGID[407] = -1000001 ## SSDLBR
    HERWIGID2PDGID[402] =  1000002 ## SSULBR
    HERWIGID2PDGID[408] = -1000002 ## SSUL
    HERWIGID2PDGID[403] =  1000003 ## SSSLBR
    HERWIGID2PDGID[409] = -1000003 ## SSSL
    HERWIGID2PDGID[404] =  1000004 ## SSCLBR
    HERWIGID2PDGID[410] = -1000004 ## SSCL
    HERWIGID2PDGID[405] =  1000005 ## SSB1BR
    HERWIGID2PDGID[411] = -1000005 ## SSB1
    HERWIGID2PDGID[406] =  1000006 ## SST1BR
    HERWIGID2PDGID[412] = -1000006 ## SST1
    HERWIGID2PDGID[413] =  2000001 ## SSDR
    HERWIGID2PDGID[419] = -2000001 ## SSDRBR
    HERWIGID2PDGID[414] =  2000002 ## SSUR
    HERWIGID2PDGID[420] = -2000002 ## SSURBR
    HERWIGID2PDGID[415] =  2000003 ## SSSR
    HERWIGID2PDGID[421] = -2000003 ## SSSRBR
    HERWIGID2PDGID[416] =  2000004 ## SSCR
    HERWIGID2PDGID[422] = -2000004 ## SSCRBR
    HERWIGID2PDGID[417] =  2000005 ## SSB2
    HERWIGID2PDGID[423] = -2000005 ## SSB2BR
    HERWIGID2PDGID[418] =  2000006 ## SST2
    HERWIGID2PDGID[424] = -2000006 ## SST2BR
    HERWIGID2PDGID[425] =  1000011 ## SSEL-
    HERWIGID2PDGID[431] = -1000011 ## SSEL+
    HERWIGID2PDGID[426] =  1000012 ## SSNUEL
    HERWIGID2PDGID[432] = -1000012 ## SSNUELBR
    HERWIGID2PDGID[427] =  1000013 ## SSMUL-
    HERWIGID2PDGID[433] = -1000013 ## SSMUL+
    HERWIGID2PDGID[428] =  1000014 ## SSNUMUL
    HERWIGID2PDGID[434] = -1000014 ## SSNUMLBR
    HERWIGID2PDGID[429] =  1000015 ## SSTAU1-
    HERWIGID2PDGID[435] = -1000015 ## SSTAU1+
    HERWIGID2PDGID[430] =  1000016 ## SSNUTL
    HERWIGID2PDGID[436] = -1000016 ## SSNUTLBR
    HERWIGID2PDGID[437] =  2000011 ## SSEL-
    HERWIGID2PDGID[443] = -2000011 ## SSEL+
    HERWIGID2PDGID[438] =  2000012 ## SSNUEL
    HERWIGID2PDGID[444] = -2000012 ## SSNUELBR
    HERWIGID2PDGID[439] =  2000013 ## SSMUL-
    HERWIGID2PDGID[445] = -2000013 ## SSMUL+
    HERWIGID2PDGID[440] =  2000014 ## SSNUMUL
    HERWIGID2PDGID[446] = -2000014 ## SSNUMLBR
    HERWIGID2PDGID[441] =  2000015 ## SSTAU1-
    HERWIGID2PDGID[447] = -2000015 ## SSTAU1+
    HERWIGID2PDGID[442] =  2000016 ## SSNUTL
    HERWIGID2PDGID[448] = -2000016 ## SSNUTLBR
    HERWIGID2PDGID[449] =  1000021 ## GLUINO
    HERWIGID2PDGID[450] =  1000022 ## NTLINO1
    HERWIGID2PDGID[451] =  1000023 ## NTLINO2
    HERWIGID2PDGID[452] =  1000025 ## NTLINO3
    HERWIGID2PDGID[453] =  1000035 ## NTLINO4
    HERWIGID2PDGID[454] =  1000024 ## CHGINO1+
    HERWIGID2PDGID[456] = -1000024 ## CHGINO1-
    HERWIGID2PDGID[455] =  1000037 ## CHGINO2+
    HERWIGID2PDGID[457] = -1000037 ## CHGINO2-
    HERWIGID2PDGID[458] =  1000039 ## GRAVTINO

    blocks = {}
    decays = {}
    LINES = isastr.splitlines()

    def getnextvalidline():
        while LINES:
            s = LINES.pop(0).strip()
            ## Return None if EOF reached
            if len(s) == 0:
                continue
            ## Strip comments
            if "#" in s:
                s = s[:s.index("#")].strip()
            ## Return if non-empty
            if len(s) > 0:
                return s

    def getnextvalidlineitems():
        return map(_autotype, getnextvalidline().split())

    ## Populate MASS block and create decaying particle objects
    masses = Block("MASS")
    numentries = int(getnextvalidline())
    for i in xrange(numentries):
        hwid, mass, lifetime = getnextvalidlineitems()
        width = 1.0/(lifetime * 1.51926778e24) ## width in GeV == hbar/lifetime in seconds
        pdgid = HERWIGID2PDGID.get(hwid, hwid)
        masses.add_entry((pdgid, mass))
        decays[pdgid] = Particle(pdgid, width, mass)
        #print pdgid, mass, width
    blocks["MASS"] = masses

    ## Populate decays
    for n in xrange(numentries):
        numdecays = int(getnextvalidline())
        for d in xrange(numdecays):
            #print n, numentries-1, d, numdecays-1
            decayitems = getnextvalidlineitems()
            hwid = decayitems[0]
            pdgid = HERWIGID2PDGID.get(hwid, hwid)
            br = decayitems[1]
            nme = decayitems[2]
            daughter_hwids = decayitems[3:]
            daughter_pdgids = []
            for hw in daughter_hwids:
                if hw != 0:
                    daughter_pdgids.append(HERWIGID2PDGID.get(hw, hw))
            if not decays.has_key(pdgid):
                #print "Decay for unlisted particle %d, %d" % (hwid, pdgid)
                decays[pdgid] = Particle(pdgid)
            decays[pdgid].add_decay(br, len(daughter_pdgids), daughter_pdgids)


    ## Now the SUSY parameters
    TANB, ALPHAH = getnextvalidlineitems()
    blocks["MINPAR"] = Block("MINPAR")
    blocks["MINPAR"].add_entry((3, TANB))
    blocks["ALPHA"] = Block("ALPHA")
    blocks["ALPHA"].entries = ALPHAH
    #
    ## Neutralino mixing matrix
    blocks["NMIX"] = Block("NMIX")
    for i in xrange(1, 5):
        nmix_i = getnextvalidlineitems()
        for j, v in enumerate(nmix_i):
            blocks["NMIX"].add_entry((i, j+1, v))
    #
    ## Chargino mixing matrices V and U
    blocks["VMIX"] = Block("VMIX")
    vmix = getnextvalidlineitems()
    blocks["VMIX"].add_entry((1, 1, vmix[0]))
    blocks["VMIX"].add_entry((1, 2, vmix[1]))
    blocks["VMIX"].add_entry((2, 1, vmix[2]))
    blocks["VMIX"].add_entry((2, 2, vmix[3]))
    blocks["UMIX"] = Block("UMIX")
    umix = getnextvalidlineitems()
    blocks["UMIX"].add_entry((1, 1, umix[0]))
    blocks["UMIX"].add_entry((1, 2, umix[1]))
    blocks["UMIX"].add_entry((2, 1, umix[2]))
    blocks["UMIX"].add_entry((2, 2, umix[3]))
    #
    THETAT, THETAB, THETAL = getnextvalidlineitems()
    import math
    blocks["STOPMIX"] = Block("STOPMIX")
    blocks["STOPMIX"].add_entry((1, 1,  math.cos(THETAT)))
    blocks["STOPMIX"].add_entry((1, 2, -math.sin(THETAT)))
    blocks["STOPMIX"].add_entry((2, 1,  math.sin(THETAT)))
    blocks["STOPMIX"].add_entry((2, 2,  math.cos(THETAT)))
    blocks["SBOTMIX"] = Block("SBOTMIX")
    blocks["SBOTMIX"].add_entry((1, 1,  math.cos(THETAB)))
    blocks["SBOTMIX"].add_entry((1, 2, -math.sin(THETAB)))
    blocks["SBOTMIX"].add_entry((2, 1,  math.sin(THETAB)))
    blocks["SBOTMIX"].add_entry((2, 2,  math.cos(THETAB)))
    blocks["STAUMIX"] = Block("STAUMIX")
    blocks["STAUMIX"].add_entry((1, 1,  math.cos(THETAL)))
    blocks["STAUMIX"].add_entry((1, 2, -math.sin(THETAL)))
    blocks["STAUMIX"].add_entry((2, 1,  math.sin(THETAL)))
    blocks["STAUMIX"].add_entry((2, 2,  math.cos(THETAL)))
    #
    ATSS, ABSS, ALSS = getnextvalidlineitems()
    blocks["AU"] = Block("AU")
    blocks["AU"].add_entry((3, 3, ATSS))
    blocks["AD"] = Block("AD")
    blocks["AD"].add_entry((3, 3, ABSS))
    blocks["AE"] = Block("AE")
    blocks["AE"].add_entry((3, 3, ALSS))
    #
    MUSS = getnextvalidlineitems()[0]
    blocks["MINPAR"].add_entry((4, MUSS))
    #
    return blocks, decays


def writeSLHAFile(spcfilename, blocks, decays, **kwargs):
    """
    Write an SLHA file from the supplied blocks and decays dicts.

    Other keyword parameters are passed to writeSLHA.
    """
    with open(spcfilename, "w") as f:
        f.write(writeSLHA(blocks, decays, kwargs))


## TODO: Split writeSLHA into writeSLHA{Blocks,Decays}

def writeSLHA(blocks, decays, ignorenobr=False):
    """
    Return an SLHA definition as a string, from the supplied blocks and decays dicts.
    """
    sep = "   "
    out = ""
    def dict_hier_strs(d, s=""):
        if type(d) is dict:
            for k, v in sorted(d.iteritems()):
                for s2 in dict_hier_strs(v, s + sep + _autostr(k)):
                    yield s2
        else:
            yield s + sep + _autostr(d)
    ## Blocks
    for bname, b in sorted(blocks.iteritems()):
        namestr = b.name
        if b.q is not None:
            namestr += " Q= %e" % b.q
        out += "BLOCK %s\n" % namestr
        for s in dict_hier_strs(b.entries):
            out += sep + s + "\n"
        out += "\n"
    ## Decays
    for pid, particle in sorted(decays.iteritems()):
        out += "DECAY %d %e\n" % (particle.pid, particle.totalwidth or -1)
        for d in sorted(particle.decays):
            if d.br > 0.0 or not ignorenobr:
                products_str = "   ".join(map(str, d.ids))
                out += sep + "%e" % d.br + sep + "%d" % len(d.ids) + sep + products_str + "\n"
        out += "\n"
    return out



if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        if a.endswith(".isa"):
            blocks, decays = readISAWIGFile(a)
        else:
            blocks, decays = readSLHAFile(a)

        for bname, b in sorted(blocks.iteritems()):
            print b
            print

        print blocks.keys()

        print blocks["MASS"].entries[25]
        print

        for p in sorted(decays.values()):
            print p
            print

        print writeSLHA(blocks, decays, ignorenobr=True)
