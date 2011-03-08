"""Atom object.

An atom object holds information in a _properties dictionary:
chemical symbol, atomic number, position, mass, momentum, velocity,
magnetic moment (along arbitrary axis).
The chemical symbol and the atomic number are kept syncronized
- the same goes for the momentum and the velocity."""

import numpy as np

from crystal.ChemicalElements.symbol import symbols
from crystal.ChemicalElements.mass import masses
from crystal.ChemicalElements.ChemicalElements import numbers


class Atom:
    """Atom object. It holds a dictionary of properties (_properties[]).
    The chemical symbol and the atomic number are kept syncronized,
    and so are the momentum and the velocity."""

    def __init__(self, symbol=None, Z=None,
                 mass=None,
                 displacement=None,
                 force=None, momentum=None, velocity=None,
                 magmom=0.0):
        
        """Atom(symbol, displacement, ...) -> atom object.

        The chemical symbol or the atomic number must be given
        (``symbol`` or ``Z``).  The rest of the arguments (``mass``,
        ``displacement``, ``force``, ``momentum``, ``velocity`` and ``magmom``) have
        default values."""

        
        self._properties={}
        
        if symbol is None:
            if Z is None:
                raise ValueError, 'Missing symbol or atomic number!'
            symbol = symbols[Z]
        else:
            if Z is None:
                Z = numbers[symbol]
            else:
                if symbols[Z] != symbol:
                    raise ValueError, 'Incompatible atomic number and symbol'
        self._properties["Z"] = Z
        self._properties["symbol"] = symbol

        if mass is None:
            mass = masses[Z]
        self._properties["mass"] = mass

        # below we need to check that we pass valid arg to numpy array ctor. do later.
        if displacement is None:
            self._properties["displacement"] = np.array( (0.0, 0.0, 0.0) )
        else:
            self._properties["displacement"] = np.array(displacement)

        if force is None:
            self._properties["force"] = np.array( (0.0, 0.0, 0.0) )
        else:
            self._properties["force"] = np.array(force)

        if momentum is None:
            if velocity is None:
                self._properties["momentum"] = np.array((0.0, 0.0, 0.0))
            else:
                self._properties["velocity"] = np.array(velocity)
        else:
            if velocity is not None:
                raise ValueError, "You can't set both momentum and velocity!"
            self._properties["momentum"] = np.array(momentum)

        self._properties["magmom"] = float(magmom)

    def __repr__(self):
        rt = ""
        for item in self._properties.items():
            rt += " %s : %s \n" % (item[0], item[1])
        return rt

    def __cmp__(self, other):
        return cmp(self._properties["Z"], other._properties["Z"])

    def setProperty(self, type, value):
        self._properties[type] = value

    def getProperty(self, type):
        return self._properties[type]

    def getSymbol(self):
        return self._properties["symbol"]

    def getZ(self):
        return self._properties["Z"]

    def getMass(self):
        return self._properties["mass"]

    def setMass(self, mass):
        try:
            self._properties["mass"] = float(mass)
        except ValueError:
            raise ValueError, "The mass must be a number!"

    def getMagMom(self):
        return self._properties["magmom"]

    def setMagMom(self, magmom):
        try:
            self._properties["magmom"] = float(magmom)
        except ValueError:
            raise ValueError, "The magnetic moment must be a number!"
          
    def getDisplacement(self):
        return self._properties["displacement"]

    def setDisplacement(self, disp):
        # we should probably do some type checking on this, but do later
        self._properties["displacement"] = np.array(disp)       

    def getForce(self):
        return self._properties["force"]

    def setForce(self, force):
        # we should probably do some type checking on this, but do later
        self._properties["force"] = np.array(force)       

    def getMomentum(self):
        return self._properties["momentum"]
    
    def setMomentum(self, momentum):
        # we should probably do some type checking on this, but do later
        self._properties["momentum"] = np.array(momentum)       
        self._properties["velocity"] = self.getMomentum() / self.getMass()
        
    def getVelocity(self):
        return self._properties["velocity"]

    def setVelocity(self, velocity):
        # we should probably do some type checking on this, but do later
        self._properties["velocity"] = np.array(velocity)       
        self._properties["momentum"] = self.getVelocity() * self.getMass()

