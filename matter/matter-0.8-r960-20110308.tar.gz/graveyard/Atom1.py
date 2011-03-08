


class Atom(object):


    def __init__(self, Z, mass=None):
        self._properties = {}
        
        self._properties['Z'] = Z

        if mass is None: mass = self.averaged_mass
        self._properties['mass'] = mass
        
        return


    def __str__(self):
        l = []
        for prop in \
            self.isotopeNumberTable.keys() + \
            self.propertyTable.keys() + \
            self.readonlyPropertyTable.keys() :

            value = self._properties.get( prop )
            if value is None: continue

            l.append( ( prop, value ) )
            continue

        rt = ','.join( ['%s=%s' % (name, value) for name,value in l ] )
        return "Atom " + rt


    # set up Z and mass
    isotopeNumberTable = {
        'Z': 'atomic number',
        'mass': 'atomic mass number'
        }


# Hi Jiao, do you want self as the first parameter?
    def _isotope_number_functions( name ):
        
        def fget(self):
            return self._properties[ name ]
        
        def fset(self, v):
            raise AttributeError, "%s is not setable. Please create a new atom" % name
            
        def fdel(self):
            raise AttributeError, "%s is not deletable." % name
            
        return fget, fset, fdel
    
    for name, doc in isotopeNumberTable.iteritems():
        fget, fset, fdel = _isotope_number_functions( name )
        exec "%s = property(fget, fset, fdel, doc) " % name
        del name, doc, fget, fset, fdel
        continue

    del _isotope_number_functions
    


    # set up read-write properties
    propertyTable = {

        #'mass':  'mass of the atom',
        'velocity': 'velocity of the atom'
        ### should add all possible properties here including but
        ### not limit to:
        ###   position( displacement ), pseudopotential, force
        }


    def _property_functions( name ):
        
        def fget(self):
            return self._properties[ name ]
        
        def fset(self, v):
            self._properties[name] = v
            
        def fdel(self):
            del self._properties[name]
            
        return fget, fset, fdel

    for name, doc in propertyTable.iteritems():
        fget, fset, fdel = _property_functions( name )
        exec "%s = property(fget, fset, fdel, doc) " % name
        del name, doc, fget, fset, fdel
        continue

    del _property_functions



    # set up read-only properties
    readonlyPropertyTable = {}
    import atomic_properties
    from utils import getModules
    modules = getModules( atomic_properties )
    del getModules, atomic_properties
    for module in modules:
        name = module.__name__.split( '.' )[-1]
        doc = module.__doc__
        lookup = module.lookup
        readonlyPropertyTable[ name ] = (doc, lookup)
        del module
        continue
    del modules


    def _readonly_property_functions(name, lookup_function):

        def fget(self):
            rt = self._properties.get(name)
            if rt is None:
                rt = self._properties[name] = lookup_function( self )
                pass
            return rt

        def fset(self, v):
            raise AttributeError, "property %s is readonly" % name

        def fdel(self):
            del self._properties[name]

        return fget, fset, fdel
    
    for name, (doc, lookup) in readonlyPropertyTable.iteritems():
        fget, fset, fdel = _readonly_property_functions( name, lookup )
        exec "%s = property(fget, fset, fdel, doc) " % name
        del name, doc, fget, fset, fdel, lookup
        continue

    del _readonly_property_functions
        
    pass # end of Atom


def test():
    Fe57 = Atom( 26, 57 )
    print "- Z=%s" % Fe57.Z
    print "- mass=%s" % Fe57.mass
    try:
        print "- Try to get velocity ... ", 
        Fe57.velocity
    except KeyError:
        print "Good. should raise exception because velocity has not been set"
        pass
    v = (0,0,1)
    print '- Set velocity to %s ... ' % (v,), 
    Fe57.velocity = v
    print ' velocity = %s ' % (Fe57.velocity,)
    print "- velocity's documentation: %s " % Atom.velocity.__doc__
    print
    print Fe57

    Fe = Atom( 26 )
    print Fe
    return


def main():
    test()
    return 

if __name__ == "__main__": main()
