# Olivier Delaire - June 2007

__doc__ = """Converters for UnitCell."""

from UnitCell import *
from Atom import *
import ASE.ListOfAtoms
import ASE.Atom

def listOfAtom2UnitCell(loa):
    """Utility to convert a ListOfAtom instance to a UnitCell instance."""

    symbols = [x.symbol for x in loa]
    cartpos = [x.position for x in loa]

    cellvectors = loa.cell
    uc = UnitCell(cellvectors)
    fracpos = [uc.cartesianToFractional(x) for x in cartpos]

    for n in range(symbols):
        atom = Atom(symbol=symbols[n])
        uc.addAtom(atom, fracpos[n], '')

    return uc


def unitCell2ListOfAtom(uc):
    """Utility to convert a UnitCell instance to a ASE ListOfAtom instance."""

    loa = ASE.ListOfAtoms([],periodic=True) 
    loa.SetUnitCell(uc._cellvectors, fix=True)
    for site in uc:
        aseatom = ASE.Atom(site.getAtom().symbol, site.getPosition().tolist())
        loa.append(aseatom)
        
    return loa

