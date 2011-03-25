#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

"""
Block Properties:

1. Blocks are indexed components that contain other components (including blocks)

2. Blocks have a global attribute that defines whether construction is deferred.  This 
applies to all components that they contain except blocks.  Blocks contained by other blocks
use their local attribute to determine whether construction is deferred.

NOTE: Blocks do not currently maintain statistics about the sets, parameters, constraints, etc that
they contain, including these components from subblocks.
"""

__all__ = ['Block']

import sys

from plugin import *

from pyutilib.component.core import alias, ExtensionPoint
from pyutilib.misc import Container

from component import Component
from sets import Set, _ProductSet, _SetContainer, _BaseSet
from rangeset import RangeSet
from var import Var
from constraint import Objective, Constraint
from param import Param

from indexed_component import IndexedComponent
try:
    from components import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class BlockComponents(object):

    def __init__(self):
        #
        # Define component dictionary: component type -> instance
        #
        self._component={}
        for item in ModelComponentFactory.services():
            self._component[  ModelComponentFactory.get_class(item) ] = {}
        #
        # A list of the declarations, in the order that they are
        # specified.
        #
        self._declarations=OrderedDict()

    def __iter__(self):
        return self._declarations.iterkeys()

    def __getitem__(self, name):
        if isinstance(name,basestring):
            return self._declarations.get(name, None)
        return self._component.get(name, None)

    def _clear_attribute(self, name):
        val = self[name]
        if val is None:
            return

        if isinstance(val, Block):
            val.__dict__['_parent_block'] = None
            val.model = val
        else:
            val.model = None
            
        del self._component[ val.type() ][name]
        del self._declarations[name]
        self.__dict__[name]=None

    def _add_component(self, name, val):
        self._component[val.type()][name]=val
        self._declarations[name] = val
        self.__dict__[name]=val

    def __setattr__(self,name,val):
            #
            # Try to set the value. This may fail if the attribute
            # does not already exist in this model, if the set_value
            # function is not defined, or if a bad value is
            # provided. In the latter case, a ValueError will be
            # thrown, which # we raise. Otherwise, this is an object
            # that we need to set directly.
            #
            try:
                self.__dict__[name].set_value(val)
            except ValueError, e:
                raise
            except Exception, e:
                self.__dict__[name]=val

    def iterkeys(self):
        return self._declarations.iterkeys()

    def itervalues(self):
        return self._declarations.itervalues()

    def iteritems(self):
        return self._declarations.iteritems()

    def components(self, ctype=None):
        """
        Return information about the block components.  If ctype is None, return the dictionary
        that maps {component type -> {name -> instance}}.  Otherwise, return the dictionary
        that maps {name -> instance} for the specified component type.
        """
        if ctype is None:
            return self._component
        if ctype in self._component:
             return self._component[ctype]
        raise KeyError, "Unknown component type: %s" % str(ctype)

    def active_components(self, _ctype=None):
        """
        Returns the active components in this block.  If _ctype is None, return the
        dictionary that maps {component type -> {name -> instance}}.  Otherwise, return
        the dictionary that maps {name -> instance} for the specified component type.
        """
        tmp = {}
        if _ctype is None:
            for ctype in self._component:
                tmp[ctype]={}
        elif _ctype in self._component:
            tmp[_ctype]={}
        else:
            raise KeyError, "Unknown component type: %s" % str(_ctype)
        for ctype in tmp:
            for name in self._component[ctype]:
                comp = self._component[ctype][name]
                if comp.active:
                    tmp[ctype][name] = comp
        if not _ctype is None:
            return tmp[_ctype]
        return tmp

    def is_constructed(self):
       """
       A boolean indicating whether or not all *active* components of the
       input model have been properly constructed.
       """
       component_map = arg.active_components()
       for type, entries in component_map.iteritems():
          for component_name, component in entries.iteritems():
             if component.is_constructed() is False:
                return False
       return True

    def pprint(self, filename=None, ostream=None):
        """
        Print a summary of the model info
        """
        if ostream is None:
           ostream = sys.stdout
        if filename is not None:
           OUTPUT=open(filename,"w")
           self.pprint(ostream=OUTPUT)
           OUTPUT.close()
           return
        if ostream is None:
           ostream = sys.stdout
        #
        # We hard-code the order of the core Pyomo modeling
        # components, to ensure that the output follows the logical order
        # that expected by a user.
        #
        items = [Set, RangeSet, Param, Var, Objective, Constraint, Block]
        for item in ExtensionPoint(IModelComponent):
            if not item in items:
                items.append(item)

        # Currently, model components are not actually being registered
        # with the IModelComponent extension point (1 Nov 2010), so as a
        # workaround, we will loop through the components and add any
        # new components that actually have defined members.
        extra_items = []
        for item, members in self._component.iteritems():
            if item not in items and len(members):
                extra_items.append(item)
        # extra items get added alphabetically (so output is consistent)
        items.extend(sorted(extra_items))

        for item in items:
            if not item in self._component:
                continue
            keys = self._component[item].keys()
            keys.sort()
            #
            # NOTE: these conditional checks should not be hard-coded.
            #
            print >>ostream, len(keys), item.__name__+" Declarations"
            for key in keys:
                self._component[item][key].pprint(ostream=ostream)
            print >>ostream, ""
        #
        # Model Order
        #
        print >>ostream, len(self._declarations),"Declarations:",
        for name in self._declarations:
          print >>ostream, name,
        print >>ostream, ""


class Block(IndexedComponent):
    """
    A block in an optimization model.  By default, this defers construction of 
    components until data is loaded.
    """

    alias("Block", "Blocks are indexed components that contain one or more " + \
          "other model components.")

    def __init__(self, *args, **kwargs):
        """Constructor"""
        if 'ctype' in kwargs:
            tkwargs = {'ctype':kwargs['ctype']}
        else:
            tkwargs = {'ctype':Block}
        IndexedComponent.__init__(self, *args, **tkwargs)
        #
        self.name=kwargs.get('name', 'unknown')
        self._defer_construction=True
        # By default, a Block is a top-level (i.e. Model) block
        self.model = self
        self._parent_block = None
        self.components =  BlockComponents()

    def concrete_mode(self):
        """Configure block to immediately construct components"""
        self._defer_construction=False

    def symbolic_mode(self):
        """Configure block to defer construction of components"""
        self._defer_construction=True

    def components(self, ctype=None):
        """
        Return information about the block components.  If ctype is None, return the dictionary
        that maps {component type -> {name -> instance}}.  Otherwise, return the dictionary
        that maps {name -> instance} for the specified component type.
        """
        return self.components.components(ctype)

    def active_components(self, _ctype=None):
        """
        Returns the active components in this block.  If _ctype is None, return the
        dictionary that maps {component type -> {name -> instance}}.  Otherwise, return
        the dictionary that maps {name -> instance} for the specified component type.
        """
        return self.components.active_components(_ctype)
        
    def _add_temporary_set(self,val):
        if val._index_set is not None:
            ctr=0
            for tset in val._index_set:
                if tset.name == "_unknown_":
                    self._construct_temporary_set(
                      tset,
                      val.name+"_index_"+str(ctr)
                    )
                ctr += 1
            val._index = self._construct_temporary_set(
              val._index_set,
              val.name+"_index"
            )
        if isinstance(val._index,_SetContainer) and \
            val._index.name == "_unknown_":
            self._construct_temporary_set(val._index,val.name+"_index")
        if getattr(val,'domain',None) is not None and val.domain.name == "_unknown_":
            self._construct_temporary_set(val.domain,val.name+"_domain")

    def _construct_temporary_set(self, obj, name):
        if type(obj) is tuple:
           if len(obj) == 1:                #pragma:nocover
                  raise Exception, "Unexpected temporary set construction"
           else:
                  tobj=_ProductSet(*obj)
                  setattr(self,name,tobj)
                  tobj.virtual=True
                  return tobj
        if isinstance(obj,_BaseSet):
           setattr(self,name,obj)
           return obj

    def _clear_attribute(self, name, only_block=False):
        """
        Cleanup the pre-existing model attribute
        """
        #
        # We don't delete here because that would destruct the component, which might
        # be shared with another block.
        #
        self.__dict__[name]=None
        if only_block:
            return

        self.components._clear_attribute(name)

    def _add_component(self, name, val):
        self._clear_attribute(name)

        # all Pyomo components have names. but not all have labels (e.g., sets, params).
        # if it does have a label, sync the default label with the new name.
        val.name=name
        if hasattr(val,'label') is True:
           val.sync_label()

        self._add_temporary_set(val)
        self.components._add_component(name,val)
        self.__dict__[name]=val

        # Presumably self.model refers to the 'root' Block that will
        # eventually be solved, whereas '_parent_block' refers to the
        # immediate parent.

        # Update the (new) child block's _parent_block.  
        if isinstance(val, Block):
            if val._parent_block is not None:
                # Nothing really wrong here, but until we are more
                # careful about checking that this actually works,
                # complain loudly.
                raise Exception, "Reassigning a block attached to a model"
            # NB: use __dict__ directly to prevent infinite recursion
            val.__dict__['_parent_block'] = self

        # Update the new component's model pointer
        val.model = self.model
        
        frame = sys._getframe(2)
        locals_ = frame.f_locals
        if getattr(val,'rule',None) is None and val.name+'_rule' in locals_:
            val.rule = locals_[val.name+'_rule']
        if not self._defer_construction:
            val.construct(None)

    def __setattr__(self,name,val):
        """Set attributes"""
        #
        # Set Model Declaration
        #
        if name == "model":
            if val is not None and not isinstance(val, Block):
                raise ValueError, "Cannot set Block.model to a non-Block " \
                      "object (%s)" % ( val )
            self.__dict__["model"] = val
            # Update all child components.  NB: use __dict__.get because
            # Component.__init__() assigns "self.model = None" before
            # Block.__init__ defines the _declarations map.
            components = self.__dict__.get('components', None)
            if not components is None:
                for subcomp in components.itervalues():
                    subcomp.model = val
        elif name != "components" and isinstance(val, Component):
            #
            # If this is a component type, then simply set it
            #
            self._add_component(name,val)
        else:
            #
            # Try to set the value. This may fail if the attribute
            # does not already exist in this model, if the set_value
            # function is not defined, or if a bad value is
            # provided. In the latter case, a ValueError will be
            # thrown, which # we raise. Otherwise, this is an object
            # that we need to set directly.
            #
            try:
                self.__dict__[name].set_value(val)
            except ValueError, e:
                raise
            except Exception, e:
                self.__dict__[name]=val

    def pprint(self, filename=None, ostream=None):
        """
        Print a summary of the model info
        """
        self.components.pprint(filename=filename, ostream=ostream)

    def display(self, filename=None, ostream=None):
        """
        Print the Pyomo model in a verbose format.
        """
        if filename is not None:
           OUTPUT=open(filename,"w")
           self.display(ostream=OUTPUT)
           OUTPUT.close()
           return
        if ostream is None:
           ostream = sys.stdout
        if self.type() is Block:
            print >>ostream, "Block "+self.name
        else:
            print >>ostream, "Model "+self.name
        #
        print >>ostream, ""
        print >>ostream, "  Variables:"
        VAR = self.active_components(Var)
        if len(VAR) == 0:
            print >>ostream, "    None"
        else:
            for ndx in VAR:
                VAR[ndx].display(prefix="    ",ostream=ostream)
        #
        print >>ostream, ""
        print >>ostream, "  Objectives:"
        OBJ = self.active_components(Objective)
        if len(OBJ) == 0:
            print >>ostream, "    None"
        else:
            for ndx in OBJ:
                OBJ[ndx].display(prefix="    ",ostream=ostream)
        print >>ostream, ""
        #
        CON = self.active_components(Constraint)
        print >>ostream, "  Constraints:"
        if len(CON) == 0:
            print >>ostream, "    None"
        else:
            for ndx in CON:
                CON[ndx].display(prefix="    ",ostream=ostream)

