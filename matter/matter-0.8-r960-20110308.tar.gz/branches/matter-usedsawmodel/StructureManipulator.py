# StructureManipulator 

from pyre.components.Component import Component
from UnitCell import UnitCell

#try:
#    from crystal.AtomLoader import AtomLoader
#except:
#    from AtomLoader import AtomLoader
#from pyparsing import *


class AtomLoader(Component):
    def __init__(self, name='AtomLoader', facility='AtomLoader'):
        Component.__init__(self, name, facility)
        return
    def setAtoms(self, atoms):
        self.atoms = atoms
        return
    


class StructureManipulator(Component):  
    """UnitCell facility with convenience functions for IO."""
    
    class Inventory(Component.Inventory):
        import pyre.inventory as inv  
#        filename = inv.str('Atomic List', default='atoms.in')
#        filename.meta['tip'] = 'The file containing atoms, their type, and positions (i.e. C core/shell 0.0 1.0 2.1)'
        #atoms = inv.facility('Atomic/Species information',default=AtomLoader())
        atoms = inv.str('Atomic/Species information',default='')
        atoms.meta['tip'] = '''i.e. H core  0.0  0.0  0.0
O shell  1.0  0.0  0.0'''
#        unitCell = inv.facility('unitCell', default=UnitCell())
#        unitCell.meta['tip'] = 'Set the unit cell parameters.'
        a = inv.str('a', default='1.0 0.0 0.0')
        a.meta['tip'] = 'the a unit cell vector'
        a.meta['importance'] = 10
        b = inv.str('b', default='0.0 1.0 0.0')
        b.meta['tip'] = 'the b unit cell vector'
        b.meta['importance'] = 9
        c = inv.str('c', default='0.0 0.0 1.0')
        c.meta['tip'] = 'the c unit cell vector'  
        c.meta['importance'] = 8
        spaceGroup = inv.str('Space Group', default='1')
        spaceGroup.meta['tip'] = 'space group of the unit cell'
        #unitCell.validator=inv.choice(["UnitCell", None])
        #b = inv.str('b', default='0.0 1.0 0.0')
        #b.meta['tip'] = 'the b unit cell vector'
        #c = inv.str('c', default='0.0 0.0 1.0')
        #c.meta['tip'] = 'the c unit cell vector'  
        #atoms = multiLineStr('Atoms',default='''"H" 0.0 0.0 0.0\n"H" 1.0 0.0 0.0''')  
        #atomFile = inv.str('atom and position file',defa)
        #atomFile
    
    def __init__(self, name='StructureManipulator', unitcell=None, cellvectors=None, filename='atoms.xyz'):
        Component.__init__(self, name, facility='facility')
        self.i=self.inventory
#        if unitcell is None:
#            unitcell = self.i.unitCell#UnitCell()
#        else:
#	       cellvectors = unitcell.getCellVectors()

        self._uc = unitcell
        self._cellvec = cellvectors
        self._filename = filename
        return

    def buildFromXYZ(self):
    	"""Builds the unitcell atom coordinates from an XYZ format file."""
        self._uc = UnitCell(self._cellvec)
        try:
            f = open(self._filename, 'r')
    	except IOError, (errno, strerror):
            print "I/O error(%s): %s" % (errno, strerror)
 	
	
	#number = Combine( Optional('-') + ( '0' | Word('123456789',nums) ) + \
        #          Optional( '.' + Word(nums) ) + \
        #          Optional( Word('eE',exact=1) + Word(nums+'+-',nums) ) )

	#digits = "0123456789"
	#integer = Word(digits)

	#def convertNumbers(s,l,toks):
    	#    n = toks[0]
    	#    try: return int(n)
    	#    except ValueError, ve: return float(n)
        #    raise

        #number.setParseAction( convertNumbers )
        #integer.setParseAction( convertNumbers )
        #vector3 = Group(number + number + number)
	
    	for line in f:
                data = line.split()
                symbol = data[0]
                data = data[1:]
                pos = []
                pos.append([float(value) for value in data])
                self._uc.addAtom(Atom(symbol), pos)

        return  #end of buildFromXYZ()

    def getUnitCell(self):
        """Returns the unit cell from the builder."""
        return self._uc
    
    def gulpFormatUcNAtoms(self):
        uc=self._uc
        atoms=s
        
    def getAtomsAsString(self):
        """returns a string containing atoms in xyz format, one per line"""
        return self.i.atoms
        
    def getCellVectors(self):
        return self.i.unitCell.getCellVectors()


