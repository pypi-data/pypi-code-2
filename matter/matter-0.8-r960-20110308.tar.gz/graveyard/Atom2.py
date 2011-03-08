from properties import *


# atom property curator

#static part of docstring of Atom class
doc = """Atom class

An object of this Atom class represent an atom in a (crystal) structure.

An atom can be created by its atomic number and optionally its atomic
mass number:

>>> Fe57 = Atom( 26, 57 )
>>> Fe = Atom( 26 )

You can obtain its property (for example, scattering length) in a similar
way one accesses a property of a normal python object:

>>> print Fe.scattering_length
"""        

#meta class for Atom class to collect all properties and set up
#some class constants.
#It establishes:
#  - Atom class's docstring
#  - a list of names of properties
#  - the list of setable attributes, "_setable", (to be used in method __setattr__ of Atom class).
class AtomPropertyCurator(type):
    

    def __init__(AtomClass, name, bases, dict):
        type.__init__(name, bases, dict)

        isotopeNumberProperties, inferredProperties, states = collectProperties( AtomClass )
        properties = isotopeNumberProperties + inferredProperties + states
        AtomClass.propertyNames = [ p.name for p in properties ]
        
        propStr = '\n'.join(
            [ "  %s: %s" % (p.name, p.doc) for p in properties ] )

        global doc
        doc += """
Here is a list of possible properties:

%s

""" % propStr

        AtomClass.__doc__ = doc
        
        AtomClass._setable = [ state.name for state in states ]
        
        pass # end of Atom

    pass #end of AtomPropertyCurator


#helper for atom property curator
def collectProperties( klass ):
    ctorargs = []
    inferred = []
    states = []
    registry = {
        CtorArg: ctorargs,
        InferredProperty: inferred,
        State: states,
        }
    for item in klass.__dict__.values():
        if not isinstance( item, Property ):continue
        registry[ item.__class__ ].append( item )
        continue
    return ctorargs, inferred, states




# Atom class
class Atom(object):


    def __init__(self, Z, mass=None):
        
        self.__dict__['Z'] = Z

        if mass is None: mass = self.averaged_mass
        self.__dict__['mass'] = mass
        
        return


    def __setattr__(self, name, value):
        if name not in Atom._setable:
            raise AttributeError, "Unknown attribute %s" % name
        return object.__setattr__(self, name, value)
        

    def __str__(self):
        l = []
        for prop in \
            self.propertyNames:

            value = self.__dict__.get( prop )
            if value is None: continue

            l.append( ( prop, value ) )
            continue

        rt = ','.join( ['%s=%s' % (name, value) for name,value in l ] )
        return "Atom " + rt


    # properties 
    
    # Z and mass
    Z = CtorArg( 'Z', 'atomic number' )
    mass = CtorArg( 'mass', 'atomic mass number' )


    # read-only, inferred properties
    import atomic_properties
    from utils import getModules
    modules = getModules( atomic_properties )
    del getModules, atomic_properties

    for module in modules:
        name = module.__name__.split( '.' )[-1]
        doc = module.__doc__
        lookup = module.lookup
        cmd = "%s=InferredProperty( name, doc, lookup )" % name
        exec cmd
        del name, doc, lookup, module, cmd
        continue
    del modules


    # states
    velocity = State('velocity', 'velocity of the atom')
    ### should add all possible states here including but
    ### not limit to:
    ###   position( displacement ), pseudopotential, force


    __metaclass__ = AtomPropertyCurator
    
    pass




import unittest

class TestCase( unittest.TestCase ):

    def test(self):
        Fe57 = Atom( 26, 57 )
        print "- Z=%s" % Fe57.Z
        print "- mass=%s" % Fe57.mass
        self._assertRaises( AttributeError , "Fe57.velocity", locals() )

        v = (0,0,1)
        print '- Set velocity to %s ... ' % (v,), 
        Fe57.velocity = v
        print ' velocity = %s ' % (Fe57.velocity,)
        print "- velocity's documentation: %s " % Atom.velocity.doc

        try: Fe57.some_very_very_strange_property = 1
        except AttributeError :
            print "Good. should not be able to set arbitrary property"
            pass
        else:
            raise 

        del Fe57.velocity
        self._assertRaises( AttributeError, 'Fe57.velocity', locals())
        Fe57.velocity = v


        self._assertRaises( AttributeError, "del Fe57.Z" , locals())

        print
        print Fe57

        Fe = Atom( 26 )
        print Fe

        return


    def _assertRaises(self, exceptionType, expression, locals):
        try:
            exec expression in locals
        except exceptionType:
            return
        
        raise AssertionError , "%s does not raise exception %s" % (
            expression, exceptionType)

    pass # end of TestCase


def main():
    testsuite = unittest.makeSuite( TestCase )
    unittest.TextTestRunner(verbosity=2).run(testsuite)
    return 

if __name__ == "__main__": main()
