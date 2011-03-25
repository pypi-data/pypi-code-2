#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Set', '_BaseSet', '_SetContainer', '_SetArray', '_ProductSet',
           'set_options']
import logging
import sys
import types
import copy
import pyutilib.misc
from pyutilib.component.core import alias
from component import *
import itertools

try:
    import bidict
    using_bidict=True
except:
    using_bidict=False

logger = logging.getLogger('coopr.pyomo')

#
# Decorator for set initializer functions
#
def set_options(**kwds):
    def decorator(func):
        func.set_options = kwds
        return func
    return decorator


##------------------------------------------------------------------------
##
## An abstract Set class
##
##------------------------------------------------------------------------

class _BaseSet(Component):
    """The base class for set objects that are used to index other Pyomo objects

       This class has a similar look-and-feel as a built-in set class.  However,
       the set operations defined in this class return another abstract
       Set object.  This class contains a concrete set, which can be 
       initialized by the load() method.
    """

    """ Constructor
        Arguments:
           name          The name of the set
           within        A set that defines the type of values that can
                          be contained in this set
           rule
           initialize    Default set members, which may be overriden
                          when setting up this set
           validate      Define a function for validating membership in a
                          set.  This has the functional form:
                          f: data -> bool
                          and returns true if the data belongs in the set
           dimen         Specify the set's arity.
           doc           Documentation for this object
           virtual       Indicate that this is a virtual set that does not
                            have concrete members.
    """
    def __init__(self, **kwds):
        Component.__init__(self, ctype=Set)

        self.order=[]
        # IMPT: order_dict keys are 1-based.
        if using_bidict:
            self.order_dict = bidict.bidict()
        else:
            self.order_dict = {}
            self.order_dict_inv = {}

        # 'rule' and 'initialize' are mutually exclusive options
        if "rule" in kwds and "initialize" in kwds:
            raise TypeError, "Cannot specify both 'rule' and 'initialize' " + \
                  "keywords in '%s'" % str(self)

        # Get keyword arguments
        self.initialize = kwds.pop("rule", None)
        self.initialize = kwds.pop("initialize", self.initialize)
        self.name       = kwds.pop("name", "_unknown_")
        self.validate   = kwds.pop("validate", None)
        self.ordered    = kwds.pop("ordered", False)
        self.virtual    = kwds.pop("virtual", False)
        self.doc        = kwds.pop("doc", "")
        self._bounds    = kwds.pop("bounds", None)
        self.filter     = kwds.pop("filter", None)

        # We can't access self.dimen after its been written, so we use
        # tmp_dimen until the end of __init__
        tmp_dimen = None

        # Get dimen from within, if possible
        self.domain = kwds.pop("within", None)
        if self.domain is not None:
            tmp_dimen = self.domain.dimen

        # Make sure dimen and implied dimensions don't conflict
        kwd_dimen = kwds.pop("dimen", None)
        if kwd_dimen is not None:
            if self.within is not None and tmp_dimen != kwd_dimen:
                raise ValueError, \
                      ("Value of keyword 'dimen', %s, differs from the " + \
                       "dimension of the superset '%s', %s") % \
                       (str(kwd_dimen), str(self.within.name), str(tmp_dimen))
            else:
                tmp_dimen = kwd_dimen

        # See there were any erroneous keyword arguments
        if len(kwds) != 0:
            msg = "Unknown keyword arguments in constructor of '%s': " % \
                  str(self)

            # Add unknown keyword arguments
            for (k, v) in kwds.items():
                msg += "%s=%s, " % (k, v)

            # Clip trailing ', '
            msg = msg[:-2]

            raise ValueError, msg
            
        if tmp_dimen is None:
            # We set the default to 1
            tmp_dimen = 1
        if self.initialize is not None:
            #
            # Convert generators to lists, since a generator is not copyable
            #
            if type(self.initialize) is types.GeneratorType:
                self.initialize = list(self.initialize)
            #
            # Try to guess dimen from the initialize list
            #
            tmp=None
            if type(self.initialize) is tuple:
                tmp = len(self.initialize)
            elif type(self.initialize) is list and len(self.initialize) > 0 \
                     and type(self.initialize[0]) is tuple:
                tmp = len(self.initialize[0])
            else:
                tmp = getattr(self.initialize, 'dimen', tmp)
            if tmp is not None:
                if kwd_dimen is not None and tmp != kwd_dimen:
                    raise ValueError, "Dimension argument differs from the data in the initialize list"
                else:
                    tmp_dimen = tmp

        self.dimen = tmp_dimen

    def reset(self):
        pass

    def dim(self):
        return self._ndim

    def display(self, ostream=None):
        self.pprint(ostream=ostream)

    def __getattr__(self,name):
        if name is "within":
           return self.domain
        raise AttributeError, "Unknown attribute "+name

    def __setattr__(self,name,val):
        if name is "within":
           self.domain = val
        return object.__setattr__(self,name,val)

    def _verify(self,element,use_exception=True):
        # A utility routine that is used to verify if the element
        # is valid for this set.
        if self.domain is not None and element not in self.domain:
           if use_exception:
              raise ValueError, "The value="+str(element)+" is not valid for set="+self.name+", because it is not within the domain="+self.domain.name
           return False
        if self.validate is not None and not self.validate(element,self.model):
           if use_exception:
              raise ValueError, "The value="+str(element)+" violates the validation rule of set="+self.name
           return False
        if self.dimen > 1 and type(element) is not tuple:
           if use_exception:
              raise ValueError, "The value="+str(element)+" is not a tuple for set="+self.name+", which has dimen="+str(self.dimen)
           return False
        elif self.dimen == 1 and type(element) is tuple:
           if use_exception:
              raise ValueError, "The value="+str(element)+" is a tuple for set="+self.name+", which has dimen="+str(self.dimen)
           return False
        elif type(element) is tuple and len(element) != self.dimen:
           if use_exception:
              raise ValueError, "The value="+str(element)+" does not have dimension="+str(self.dimen)+", which is needed for set="+self.name
           return False
        return True

    def bounds(self):
        """Return bounds information.  The default value is 'None', which
        indicates that this set does not contain bounds."""
        return self._bounds


class _SetContainer(_BaseSet):
    """A derived _BaseSet object that contains a single set."""

    def __init__(self, *args, **kwds):
        """ Constructor """
        if args != ():
            raise TypeError, "A _SetContainer expects no arguments"
        self._index_set=None
        self._index=[None]
        self._ndim=0
        self.value=set()
        _BaseSet.__init__(self,**kwds)

    def construct(self, values=None):
        """ Apply the rule to construct values in this set """
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing _SetContainer, name="+self.name+", from data="+repr(values))
        if self._constructed:
            return
        self._constructed=True

        if self.initialize is None:
            self.initialize = getattr(self,'rule',None)
        #
        # Construct using the values list
        #
        if values is not None:
           if type(self._bounds) is tuple:
                first=self._bounds[0]
                last=self._bounds[1]
           else:
                first=None
                last=None
           all_numeric=True
           for val in values[None]:
                if type(val) in [int,float,long]:
                    if first is None or val<first:
                        first=val
                    if last is None or val>last:
                        last=val
                else:
                    all_numeric=False
                self.add(val)
           if all_numeric:
                self._bounds = (first,last)
        #
        # Construct using the rule
        #
        elif type(self.initialize) is types.FunctionType:
           if self.model is None:
              raise ValueError, "Must pass a model in to initialize with a function"
           if self.initialize.func_code.co_argcount == 1:
              #
              # Using a rule of the form f(model) -> iterator
              #
              tmp = self.initialize(self.model)
              for val in tmp:
                if self.dimen is None:
                   if type(val) in [tuple,list]:
                        self.dimen=len(val)
                   else:
                        self.dimen=1
                self.add(val)
           else:
              #
              # Using a rule of the form f(z,model) -> element
              #
              ctr=1
              val = self.initialize(ctr,self.model)
              if self.dimen is None:
                   if type(val) in [tuple,list]:
                        self.dimen=len(val)
                   else:
                        self.dimen=1
              while val is not None:
                self.add(val)
                ctr += 1
                val = self.initialize(ctr,self.model)
           #
           # We should be verifying as part of the add() method
           #
           #for val in self.value:
             #self._verify(val)
        #
        # Construct using the default values
        #
        elif self.initialize is not None:
              if type(self.initialize) is dict:
                 raise ValueError, "Cannot initialize set "+self.name+" with dictionary data"
              if type(self._bounds) is tuple:
                first=self._bounds[0]
                last=self._bounds[1]
              else:
                first=None
                last=None
              all_numeric=True
              for val in self.initialize:
                if type(val) in [int,float,long]:
                    if first is None or val<first:
                        first=val
                    if last is None or val>last:
                        last=val
                else:
                    all_numeric=False
                self.add(val)
              #print "HERE",self.name,first,last,all_numeric
              if all_numeric:
                self._bounds = (first,last)

        #
        # Apply filter, if defined
        #
        if self.filter is not None:
            self._apply_filter()

    def _apply_filter(self):
        """
        Applies self.filter to each element. If self.filter returns True,
        the element remain in the Set; otherwise, it is removed.
        """
        toRemove = []
        for el in self.value:
            if not self.filter(el, self.model):
                toRemove.append(el)

        for el in toRemove:
            self.remove(el)
            
    def data(self):
        """The underlying set data."""
        if self.virtual:
           raise TypeError, "Cannot access underlying set data for virtual set "+self.name
        return self.value

    def clear(self):
        """Remove all elements from the set."""
        if self.virtual:
           raise TypeError, "Cannot clear virtual Set object `"+self.name+"'"
        self.value.clear()
        if using_bidict:
            self.order_dict = bidict.bidict()
        else:
            self.order_dict = {}
            self.order_dict_inv = {}

    def check_values(self):
        """ Verify that the values in this set are valid.
        """
        if self.virtual:
           return
        for val in self.value:
          self._verify(val)

    def add(self, *args):
        """Add one or more elements to a set."""
        if self.virtual:
           raise TypeError, "Cannot add elements to virtual set `"+self.name+"'"
        for val in args:
          tmp = pyutilib.misc.flatten_tuple(val)
          self._verify(tmp)
          try:
            if tmp in self.value:
                continue
                #raise ValueError, "Element "+str(tmp)+" already exists in set "+self.name
            self.value.add(tmp)
            if self.ordered:
               if tmp in self.order_dict:
                    raise ValueError, "Element "+str(tmp)+" already exists in ordered set "+self.name
               self.order.append(tmp)
               if using_bidict:
                    self.order_dict[tmp:] = len(self.order)
               else:
                    self.order_dict[tmp] = len(self.order)
                    self.order_dict_inv[len(self.order)] = tmp
               

          except TypeError:
            raise TypeError, "Problem inserting "+str(tmp)+" into set "+self.name

    def remove(self, element):
        """Remove an element from the set.
           If the element is not a member, raise an error.
        """
        if self.virtual:
            raise KeyError, "Cannot remove element `"+str(element)+"' from virtual set "+str(self.name)
        if element not in self.value:
            raise KeyError, "Cannot remove element `"+str(element)+"' from set "+str(self.name)
        self.value.remove(element)
        if self.ordered:
            id = self.order_dict[element]-1
            for i in xrange(id+1,len(self.order)):
                if using_bidict:
                    self.order_dict[self.order[i]] = i
                else:
                    self.order_dict[self.order[i]] = i
                    self.order_dict_inv[i] = self.order[i]
            del self.order[id]

    def discard(self, element):
        """Remove an element from the set.
           If the element is not a member, do nothing.
        """
        if self.virtual:
           raise KeyError, "Cannot discard element `"+str(element)+"' from virtual set "+str(self.name)
        if self.ordered and element in self.value:
           self.order.remove(element)
        self.value.discard(element)

    def first(self):
        if self.virtual:
            raise TypeError, "Cannot access the first element of virtual set `"+self.name+"'"
        return self.member(1)

    def last(self):
        if self.virtual:
            raise TypeError, "Cannot access the last element of virtual set `"+self.name+"'"
        return self.member(len(self.value))

    def __getitem__(self, key):
        return self.member(key)

    def member(self, key):
        if self.ordered:
            if using_bidict:
                return self.order_dict.inv[key]
            else:
                return self.order_dict_inv[key]
        #
        # If the set is not ordered, then we use the intrinsic ordering imposed by the set.
        # We convert the set to a list and return the specified value.
        #
        if key >= 1:
            return list(self.value)[key-1]
        elif key < 0:
            return list(self.value)[key]
        else:
            raise IndexError, "Valid index values for sets are 1 ... len(set) or -1 ... -len(set)"

    def ord(self, match_element):
        """ For ordered sets, return the position index (1-based) 
            of the input element.
        """
        if self.ordered is False:
           raise AttributeError, "Cannot invoke ord() method for unordered set="+str(self.name)
        try:
            return self.order_dict[match_element]
        except IndexError:
            raise IndexError, "Unknown input element="+str(match_element)+" provided as input to ord() method for set="+str(self.name)

    def next(self, match_element, k=1):
        # NOTE: we currently aren't consist (and don't actually deal with) w.r.t. unordered sets - see the implementation of member() above.
        try:
           element_position = self.order_dict[match_element]
        except KeyError:
           raise KeyError, "Cannot obtain next() member of set="+self.name+"; input element="+str(match_element)+" is not a member of the set!"

        try:
           return self.order[element_position+k-1] # "order" is a list, accessed 0-based.
        except KeyError:
           raise KeyError, "Cannot obtain next() member of set="+self.name+"; failed to access item in position="+str(element_position+k-1)

    def nextw(self, match_element, k=1):
        ndx = self.order_dict[match_element]+k
        total = len(self.order)
        if ndx > total:
            ndx -= total
        if ndx <= 0:
            ndx += total
        return self.order.inv[ndx]

    def prev(self, match_element, k=1):
        return self.next(match_element, k=-k)

    def prevw(self, match_element, k=1):
        return self.nextw(match_element, k=-k)

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tDim="+str(self.dim()),
        print >>ostream, "\tDimen="+str(self.dimen),
        print >>ostream, "\tSize="+str(len(self)),
        if self.domain is not None:
           print >>ostream, "\tDomain="+str(self.domain.name),
        else:
           print >>ostream, "\tDomain="+str(None),
        print >>ostream, "\tOrdered="+str(self.ordered),
        print >>ostream, "\tBounds="+str(self._bounds)
        if self.model is None:
           print >>ostream, "\t Model=None"
        else:
           print >>ostream, "\t Model="+str(self.model.name)
        if self.virtual:
           print >>ostream, "\t  Virtual"
        else:
           if self.ordered:
              tmp = copy.copy(self.order)
           else:
              tmp = copy.copy(list(self.value))
              tmp.sort()
           print >>ostream, "\t  ",tmp

    def __len__(self):
        """ The number of items in the set.
            The set is empty until a concrete instance has been setup.
        """
        if self.virtual:
           raise ValueError, "The size of a virtual set is unknown"
        return len(self.value)

    #def __repr__(self):
        #"""Return string representation of the underlying set"""
        #return str(self)+" : "+str(self.value)

    def __iter__(self):
        """Return an iterator for the underlying set"""
        if self.virtual:
           raise TypeError, "Cannot iterate over Set object `"+self.name+"', which is a virtual set"
        if self.ordered:
           return self.order.__iter__()
        return self.value.__iter__()

    def __hash__(self):
        """Hash this object"""
        return _BaseSet.__hash__(self)

    def __eq__(self,other):
        """ Equality comparison """
        try:
            tmp = self._set_repn(other)
        except TypeError:
            # An exception is raised if a non-set object is passed to _set_repn
            return False
        if self.virtual:
            if other.virtual:
                return hash(self) == hash(tmp)
            return False
        if self.dimen != other.dimen:
           return False
        return self.value.__eq__( tmp )

    def __ne__(self,other):
        return not self.__eq__(other)

    def __contains__(self, element):
        """Report whether an element is a member of this set.
        (Called in response to the expression 'element in self'.)
        """
        #
        # If the element is a set, then see if this is a subset
        #
        if isinstance(element,_SetContainer):
           return element.issubset(self)
        #
        # If this is not a valid element, then return False
        #
        if not self._verify(element,False):
           return False
        #
        # If the restriction rule is used then we do not actually
        # check whether the data is in the set self.value.
        #
        if self.validate is not None and self.virtual:
           return True
        #
        # The final check: return true if self.virtual is True, since we should
        # have already validated this value
        #
        return self.virtual or element in self.value

    def issubset(self,other):
        """Report whether another set contains this set"""
        if self.virtual:
           raise TypeError, "ERROR: cannot perform \"issubset\" test because the current set is a virtual set."
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        for val in self.value:
          if val not in other:
             return False
        return True

    def issuperset(self,other):
        """Report this set contains another set"""
        if isinstance(other,_BaseSet):
           if other.virtual:
              raise TypeError, "ERROR: cannot perform \"issuperset\" test because the target set is a virtual set."
           return other.issubset(self) and (self.virtual or len(self) >= len(other))
        for val in other:
          if val not in self:
             return False
        return True

    __le__ = issubset
    __ge__ = issuperset

    def __lt__(self,other):
        if self.virtual or \
           (isinstance(other,_BaseSet) and other.virtual):
           raise TypeError, "ERROR: cannot test for __lt__ because either or both of the sets are virtual."
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        for val in self.value:
          if val not in other:
             return False
        return len(self) < len(other)

    def __gt__(self,other):
        if self.virtual or \
           (isinstance(other,_BaseSet) and other.virtual):
           raise TypeError, "ERROR: cannot test for __lt__ because either or both of the sets are virtual."
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        for val in other:
          if val not in self.value:
             return False
        return len(self) > len(other)

    def _set_repn(self,other):
        if isinstance(other,_SetContainer) and other.virtual:
            return other
        if isinstance(other,_SetContainer) and type(other.value) is not dict:
           return other.value
        raise TypeError, "Cannot apply Set operation with a "+str(type(other))+" object"
        
    def __or__(self,other):
        """ Return a _SetContainer object that is the union of this set
        with another set. """
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        def SetUnionRule(model):
            data = set()
            for val in getattr(model,SetUnionRule.Set1):
              data.add(val)
            for val in getattr(model,SetUnionRule.Set2):
              data.add(val)
            return data
        SetUnionRule.Set1 = self.name
        SetUnionRule.Set2 = other.name
        return _SetContainer(dimen=self.dimen, initialize=SetUnionRule)

    def __and__(self,other):
        """Return a _SetContainer object that is the intersection of this set
        with another set"""
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)

        if (self._constructed is True) and (other._constructed is True):
           data = []
           for val in self:
              if val in other:
                 data.append(val)
           result = _SetContainer(dimen=self.dimen, initialize=data)
           # IMPT: construct here, as the & operator is often used in-line, such that the component is not part of any model - and therefore won't be constructed when it is added to a model!
           result.construct()
           return result
        else:
           def SetIntersectionRule(model):
               data = set()
               for val in getattr(model,SetIntersectionRule.Set1):
                 if val in getattr(model,SetIntersectionRule.Set2):
                    data.add(val)
               return data
           SetIntersectionRule.Set1 = self.name
           SetIntersectionRule.Set2 = other.name
           return _SetContainer(dimen=self.dimen, initialize=SetIntersectionRule)

    def __xor__(self,other):
        """Return a _SetContainer object that is the symmetric difference of 
        this set with another set"""
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        def SetSymmetricDifferenceRule(M):
            Set1 = getattr(M,SetSymmetricDifferenceRule.Set1)
            Set2 = getattr(M,SetSymmetricDifferenceRule.Set2)
            data = set()
            for val in Set1:
              if val not in Set2:
                 data.add(val)
            for val in Set2:
              if val not in Set1:
                 data.add(val)
            return data
        SetSymmetricDifferenceRule.Set1 = self.name
        SetSymmetricDifferenceRule.Set2 = other.name
        return _SetContainer(dimen=self.dimen, initialize=SetSymmetricDifferenceRule)

    def __sub__(self,other):
        """Return a _SetContainer object that is the difference between this set
        and another set"""
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        def SetDifferenceRule(model):
            data = set()
            for val in getattr(model,SetDifferenceRule.Set1):
              if val not in getattr(model,SetDifferenceRule.Set2):
                 data.add(val)
            return data
        SetDifferenceRule.Set1 = self.name
        SetDifferenceRule.Set2 = other.name
        return _SetContainer(dimen=self.dimen, initialize=SetDifferenceRule)

    def __mul__(self,other):
        """Return a _ProductSet that is the cross-product between this set and
        and another set"""
        if not isinstance(other,_SetContainer):
           raise TypeError, "Set operator __mul__ cannot be applied with an object of type "+str(type(other))
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if isinstance(self,_ProductSet) and self.name=="_unknown_":
           self.set_tuple = tuple( list(self.set_tuple) + [other] )
           self._compute_dimen()
           return self
        return _ProductSet(self,other)


class _SetArray(_BaseSet):
    """An array of sets, which are indexed by other sets"""

    def __init__(self, *args, **kwds):      #pragma:nocover
        """ Constructor """
        self._index_set=None
        self.value={}
        self._ndim=len(args)
        if len(args) == 1:
            if isinstance(args[0],_BaseSet):
                self._index=args[0]
            else:
                try:
                    options = getattr(args[0],'set_options')
                    options['initialize'] = args[0]
                    self._index=Set(**options)
                except:
                    self._index=Set(initialize=args[0])
        else:
            self._index=None
            tmp = []
            for arg in args:
                if isinstance(arg,_BaseSet):
                    tmp.append(arg)
                else:
                    try:
                        options = getattr(arg,'set_options')
                        options['initialize'] = arg
                        tmp.append( Set(**options) )
                    except:
                        tmp.append( Set(initialize=arg) )
            self._index_set=tuple(tmp)
        _BaseSet.__init__(self,**kwds)
        self.value={}

    def keys(self):
        return self.value.keys()

    def __contains__(self, element):
        return element in self.value.keys()

    def clear(self):
        """Remove all elements from the set."""
        for key in self.value:
          self.value[key].clear()

    def data(self):
        """The underlying set data."""
        raise TypeError, "Cannot access underlying set data for array set "+self.name

    def __getitem__(self, key):
        if key not in self.value:
           if (key in self._index) and (self.initialize is not None) and (type(self.initialize) in [tuple,list]):
              return self.initialize
           raise KeyError, "Cannot access index "+str(key)+" in array set "+self.name
        return self.value[key]

    def __setitem__(self, key, val):
        if key not in self._index:
           raise KeyError, "Cannot set index "+str(key)+" in array set "+self.name
        if key in self.value:
           self.value[key].clear()
           for elt in val:
             self.value[key].add(elt)
        else:
           self.value[key] = Set(initialize=val,within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
           self.value[key].construct()

    def __len__(self):
        result = 0
        for val in self.value.values():
            result += len(val)
        return result

    def __iter__(self):
        """Return an iterator for the set array"""
        return self.value.__iter__()

    def check_values(self):
        for key in self.value:
          for val in self.value[key]:
            self._verify(val,True)

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tDim="+str(self.dim()),
        print >>ostream, "\tDimen="+str(self.dimen),
        if self.domain is None:
           print >>ostream, "\tDomain="+str(self.domain),
        else:
           print >>ostream, "\tDomain="+str(self.domain.name),
        print >>ostream, "\tArraySize="+str(len(self.value.keys())),
        print >>ostream, "\tOrdered="+str(self.ordered)
        if self.model is None:
           print >>ostream, "\t Model=None"
        else:
           print >>ostream, "\t Model="+str(self.model.name)        
        tmp=self.value.keys()
        if tmp is not None:
            tmp.sort()
        else:
            tmp=[]
        for val in tmp:
          if self.ordered:
             ttmp = copy.copy(self.value[val].order)
          else:
             ttmp = copy.copy(list(self.value[val].value))
             ttmp.sort()
          print >>ostream, "\t",self.name+"["+str(val)+"]\t",ttmp

    def construct(self, values=None):
        """ Apply the rule to construct values in each set"""
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing _SetArray, name="+self.name+", from data="+repr(values))
        if self._constructed:
            return
        self._constructed=True
        if self.virtual:                                #pragma:nocover
           raise TypeError, "It doesn't make sense to create a virtual set array"

        if self.initialize is None:
            self.initialize = getattr(self,'rule',None)

        #
        # Construct using the values list
        #
        if values is not None:
           for key in values:
             if type(key) is tuple and len(key)==1:
                tmpkey=key[0]
             else:
                tmpkey=key
             if tmpkey not in self._index:
                raise KeyError, "Cannot set index "+str(tmpkey)+" in array set "+self.name
             self.value[tmpkey] = Set(initialize=values[key],within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(tmpkey)+"]",dimen=self.dimen)
             self.value[tmpkey].model = self.model
             self.value[tmpkey].construct()
        #
        # Construct using the rule
        #
        elif type(self.initialize) is types.FunctionType:
           if self.model is None:
              raise ValueError, "Need model to construct a set array with a function"
           if self._index is None:
              raise ValueError, "No index for set "+self.name
           for key in self._index:
             if isinstance(key,tuple):
                tmp = list(key)
             else:
                tmp = [key]
             if self.initialize.func_code.co_argcount == len(tmp)+1:
                tmp.append(self.model)
                tmp = tuple(tmp)
                rule_list = list(self.initialize(*tmp))
             else:
                rule_list=[]
                ctr=1
                args = tuple(tmp+[ctr,self.model])
                val = self.initialize(*args)
                while val is not None:
                  rule_list.append(val)
                  ctr += 1
                  args = tuple(tmp+[ctr,self.model])
                  val = self.initialize(*args)
             if self.dimen is None and len(rule_list) > 0:
                   if type(rule_list[0]) in [tuple,list]:
                        self.dimen=len(rule_list[0])
                   else:
                        self.dimen=1
             self.value[key] = Set(initialize=rule_list,within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
             self.value[key].model = self.model
             self.value[key].construct()
        #
        # Construct using the default values
        #
        else:
           if self.initialize is not None:
              if type(self.initialize) is not dict:
                 for key in self._index:
                   self.value[key] = Set(initialize=self.initialize,within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
                   self.value[key].model = self.model
                   self.value[key].construct()
              else:
                 for key in self.initialize:
                   self.value[key] = Set(initialize=self.initialize[key],within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
                   self.value[key].model = self.model
                   self.value[key].construct()


##------------------------------------------------------------------------
##
## A set that defines an abstract cross-product set.
##
##------------------------------------------------------------------------

class _ProductSet(_SetContainer):
    """Set that represents a cross-product of other sets"""

    """ Constructor
        Arguments:
           name         The name of this set
           initialize   Default set members, which may be overriden
                            when setting up this set
           rule         A rule for setting up this set with
                            existing model data.  This has the functional form:
                            f: pyomo.Model -> set
    """
    def __init__(self, *args, **kwd):
        self._class_override=False

        # a base set container doesn't allow arguments - 
        # avoiding weird (and possibly incorrect) *()
        # syntax below.
        tmp=()
        _SetContainer.__init__(self,*tmp,**kwd)

        # the individual index sets definining the product set. 
        self.set_tuple = args

        # sets the "dimen" instance attribute.
        self._compute_dimen()

        # _len is the number of elements in the product 
        # set, computed in the obvious way. 
        # NOTE: this is not dynamically updated, so if
        #       the composite set contents are updated,
        #       the change will not be reflected here.
        self._len=0

    def __iter__(self):
        """Returns an iterator/generator for the cross-product""" 
        if sys.version_info[:2] >= (2,6):
            return (pyutilib.misc.flatten_tuple(i) for i in itertools.product(*self.set_tuple))
        else:
            return pyutilib.misc.flattened_cross_iter(*self.set_tuple)

    def __len__(self):
        return self._len

    def _compute_dimen(self):
        ans=0
        for set in self.set_tuple:
            if set.dimen is None:
                self.dimen=None
                return
            else:
                ans += set.dimen
        self.dimen = ans

    def _verify(self,element,use_exception=True):
        """
        If this set is virtual, then an additional check is made
        to ensure that the element is in each of the underlying sets.
        """
        tmp = _SetContainer._verify(self,element,use_exception)
        if not tmp or not self.virtual:
            return tmp

        next_tuple_index = 0
        member_set_index = 0
        for member_set in self.set_tuple:
           tuple_slice = element[next_tuple_index:next_tuple_index + member_set.dimen]
           if member_set.dimen == 1:
              tuple_slice = tuple_slice[0]
           if tuple_slice not in member_set:
             return False
           member_set_index += 1
           next_tuple_index += member_set.dimen
        return True
        
    def construct(self, values=None):
        """ Apply the rule to construct values in this set """
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing _ProductSet, name="+self.name+", from data="+repr(values))
        if self._constructed:
            return
        self._constructed=True

        if self.initialize is None:
            self.initialize = getattr(self,'rule',None)

        if self.virtual:
           if len(self.set_tuple) == 0:
              self._len=0
           else:
              self._len=1
              for val in self.set_tuple:
                self._len *= len(val)
        #
        # Construct using the values list
        #
        elif values is not None:
           for val in values[None]:
             self.add(val)
        #
        # Construct using the rule
        #
        elif type(self.initialize) is types.FunctionType:
           for val in self.initialize(self.model):
             self.add(val)
        #
        # Construct using the default values
        #
        else:
           if self.initialize is not None:
              if type(self.initialize) is dict:
                 for val in self.initialize:
                   self.add(val)
              else:
                 self.add(self.initialize)
           else:
              for val in pyutilib.misc.cross(self.set_tuple):
                self.add(val)
        #
        if not self.virtual:
            self._len=len(self.value)
        self._compute_dimen()
        if self.dimen is None:
            raise ValueError, "The product set dimension must be computeable after constructing this set!"


class Set(Component):
    """Set objects that are used to index other Pyomo objects

       This class has a similar look-and-feel as a built-in set class.  However,
       the set operations defined in this class return another abstract
       Set object.  This class contains a concrete set, which can be 
       initialized by the load() method.
    """

    alias('Set', "Set data that is used to define a model instance.")

    def __new__(cls, *args, **kwds):
        if args == ():
            self = _SetContainer(*args, **kwds)
        else:
            self = _SetArray(*args, **kwds)
        return self

