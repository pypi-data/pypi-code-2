#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['_ParamBase', 'Param', '_SharedParamBase', 'SharedParam' ]

import sys
import types

from component import *
from coopr.pyomo.base.numvalue import *
from indexed_component import IndexedComponent
from numvalue import create_name
from plugin import IModelComponent
from pyutilib.component.core import alias
from set_types import *
from sets import _BaseSet
import pyomo


class _ParamValue(NumericConstant):
    """Holds the numeric value of a parameter"""

    """Constructor"""
    def __init__(self, name=None, domain=None, value=None):
        try:
            NumericConstant.__init__(self, name=name, domain=domain, value=value)
        except ValueError, e:
            msg = "Problem constructing parameter %s : %s"
            raise ValueError, msg % (name, str(e))

    def fixed_value(self):
        return True

    def __str__(self):
        return self.name



class _ParamBase(IndexedComponent):
    """A parameter value, which may be defined over a index"""

    """ Constructor
        Arguments:
           name       The name of this parameter
           index      The index set that defines the distinct parameters.
                         By default, this is None, indicating that there
                         is a single parameter.
           within     A set that defines the type of values that
                         each parameter must be.
           validate   A rule for validating this parameter w.r.t. data
                         that exists in the model
           default    A set that defines default values for this parameter
           rule       A rule for setting up this parameter with existing model
                         data
           nochecking If true, various checks regarding valid domain and index
                      values are skipped. Only intended for use by algorithm
                      developers - not modelers!
    """
    def __init__(self, *args, **kwd):
        if kwd.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

        tkwd = {'ctype': kwd.pop("ctype", Param)}
        IndexedComponent.__init__(self, *args, **tkwd)

        self._initialize = kwd.pop('initialize', None )
        self._initialize = kwd.pop('rule', self._initialize )
        self._validate   = kwd.pop('validate', None )
        self.doc         = kwd.pop('doc', None )
        self.domain      = kwd.pop('within', Any )
        self.mutable     = kwd.pop('mutable', False )
        self.name        = kwd.pop('name', 'unknown')
        self.nochecking  = kwd.pop('nochecking',False)
        defaultval       = kwd.pop('default', None )

        self._paramval   = {}
        self._default = _ParamValue(
          name   = self.name,
          domain = self.domain,
          value  = value(defaultval)
        )

        if ( kwd ):
            msg = "Unknown keyword to Param constructor: '%s'"
            raise ValueError, msg % kwd.values()[0]


    def initialize(self, data):
        self._initialize = data


    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self)),
        print >>ostream, "\tDomain="+self.domain.name
        if None in self._paramval:
           print >>ostream, "\t", self._paramval[None].value
        else:
           tmp=self._paramval.keys()
           tmp.sort()
           for key in tmp:
             if self.mutable:
                val = self._paramval[key].value
             else:
                val = self._paramval[key]
             print >>ostream, "\t"+str(key)+" : "+str(val)
        if self._default.value is not None and not self._default.value is None:
           print >>ostream, "\tdefault: "+str(self._default.value)

    def keys(self):
        if self._default.value is None:
            return self._paramval.keys()
        else:
            if not isinstance(self._index,_BaseSet):
                raise ValueError, "Expected a set object for _index"
            return self._index

    def __contains__(self, element):
        if self._default.value is None:
            return element in self._paramval
        else:
            return element in self._index

    def __iter__(self):
        if self._default.value is None:
            return self._paramval.keys().__iter__()
        else:
            return self._index.__iter__()

    def dim(self):
        return self._ndim

    def __len__(self):
        if not self._default.value is None:
           return len(self._index)
        return len(self._paramval)

    def __getitem__(self,ndx):
        """This method returns a _ParamVal object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        if ndx in self._paramval:
            return self._paramval[ndx]
        if ndx in self._index and self._default.value is not None:
            return self._default.value

        msg = "Unknown index '%s' in parameter '%s: keys=%s"
        raise KeyError, msg % (str(ndx), self.name, str(self._index.data()) )

    def __setitem__(self,ndx,val):
        if self._index_set is not None:
            # this is a "hack", in that we still need to check for legal
            # sub-components in the input index.
            if self.mutable:
                if ndx in self._paramval:
                    self._paramval[ndx].value = val
                else:
                    self._paramval[ndx]= _ParamValue(
                        name   = create_name(self.name,ndx),
                        domain = self.domain,
                        value  = val
                        )
            else:
                self._paramval[ndx]= val
            return
        #
        if type(ndx) is tuple and len(ndx) == 1 and ndx[0] in self._index:
            ndx = ndx[0]
        if (None in self._index) and (ndx is not None):
            # allow for None indexing if this is truly a singleton
            msg = "Cannot set an array value in the simple parameter '%s'"
            raise KeyError, msg % self.name
        #
        if (self.nochecking is False) and (ndx not in self._index):
            msg = "Cannot set the value of array parameter '%s' with invalid " \
                  "index '%s'"
            raise KeyError, msg % ( self.name, str(ndx) )
        #
        if self.mutable:
            if ndx in self._paramval:
                self._paramval[ndx].value = val
            else:
                self._paramval[ndx]= _ParamValue(
                    name   = create_name(self.name,ndx),
                    domain = self.domain,
                    value  = val
                    )
        else:
            self._paramval[ndx] = val
        #
        # This is at the end, so the user can write their validation
        # tests as if the data was already added.
        #
        if (self.nochecking is False) and (not self._valid_indexed_value(val ,ndx, False)):
            msg = "Invalid parameter value: %s[%s] = '%s'"
            raise ValueError, msg % ( self.name, str(ndx), str(val) )

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """
        if pyomo.debug("verbose"):      #pragma:nocover
           print "Constructing Param, name="+self.name+", from data="+`data`
        if self._constructed:
            return
        self._constructed=True
        #
        # Code optimization with local variables
        #
        _name=self.name
        _domain=self.domain
        #
        # Update the default value, if it's available
        #
        try:
            self._default.value = self.default
        except:
            pass

        if self._initialize is None:
            self._initialize = getattr(self,'rule',{})
        #
        # Construct using the initial data or the data loaded from an
        # external source.  Note:  data values will be queried in to following
        # order:
        #   1) the 'data' dictionary
        #   2) the self._initialize dictionary
        #   3) the default value
        #
        if data is not None or type(self._initialize) is not types.FunctionType:
            #
            # Singleton parameter
            #
            if type(self._index) is dict:
                if data is not None and None in data.keys():
                    self.value=data[None]
                elif type(self._initialize) is not dict:
                    self.value=self._initialize
                elif None in self._initialize:
                    self.value=self._initialize[None]
                elif self._default.value is not None:
                    self.value=self._default.value
                    #self._paramval[None] = self._default
                else:
                    msg = "Attempting to construct parameter '%s' without "   \
                          'parameter data'
                    raise ValueError, msg % _name

                # print "Z",type(self._paramval[None].value), \
                # self._paramval[None].value
                # print "Z",type(self.__call__())
                self._valid_indexed_value(self.value,(),True)
            else:
                #
                # Set external data values (if provided)
                #
                if data is not None:
                    for key in data:
                        if type(key) is tuple and len(key)==1:
                            tmpkey=key[0]
                        else:
                            tmpkey=key
                        self.__setitem__(key, data[key])
                #
                # Initialize with initialization data.
                #
                elif self._initialize is not None:
                    if type(self._initialize) is dict:
                        for key in self._initialize:
                            self.__setitem__(key, self._initialize[key])
                    else:
                        for key in self._index:
                            self.__setitem__(key, self._initialize)
        #
        # Construct using the rule
        #
        elif type(self._initialize) is types.FunctionType:
            if (type(self._index) is dict) and (None in self._index):
                # singleton
                tmp = []
                tmp.append(self.model)
                tval = self._initialize(*tmp)
                self.value = tval
            else:
                # non-singleton
                for val in self._index:
                    if isinstance(val, tuple):
                        tmp = list(val)
                    elif val is None:
                        tmp = []
                    else:
                        tmp = [val]

                    if len(tmp) > 0:
                        tname = create_name(_name,val)
                    else:
                         tname = _name

                    tmp.append(self.model)
                    tmp = tuple(tmp)
                    tval = self._initialize(*tmp)
                    self.__setitem__(val, tval)

    def _valid_indexed_value(self,value,index, use_exception):
        if index is ():
            if None not in self._index:
                msg = "Invalid index '%s' for parameter '%s'"
                raise ValueError, msg % ( str(None), self.name )
        elif type(index) is tuple and len(index)==1:
            if index not in self._index and index[0] not in self._index:
                msg = "Invalid index '%s' for parameter '%s'"
                raise ValueError, msg % ( str(index[0]), self.name)
        elif index not in self._index:
            msg = "Invalid index '%s' for parameter '%s'"
            raise ValueError, msg % ( str(index), self.name)
        #
        if self._validate is not None:
           tmp = [value]
           if index == ():
              index = (None,)*self._ndim

           if index is not None:
              if type(index) is tuple:
                 tmp = tmp + list(index)
              else:
                 tmp = tmp + [ index ]

           tmp.append(self.model)
           tmp = tuple(tmp)
           if self._validate(*tmp):
              return True
        elif self.domain is None or value in self.domain:
           return True
        #
        if use_exception:           #pragma:nocover
            msg = "Invalid value '%s' for parameter '%s'"
            raise ValueError, msg % ( str(value), self.name )
        #
        return False

    def data(self):
        tmp = {}
        for key in self.keys():
            if self.mutable:
                tmp[key] = self._paramval[key].value
            else:
                tmp[key] = self._paramval[key]
        return tmp


class _ParamElement(_ParamBase,_ParamValue):

    def __init__(self, *args, **kwd):

        if kwd.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

        _ParamValue.__init__(self, \
                             name=kwd.get('name', None), \
                             domain=kwd.get('within', None), \
                             value=kwd.get('default', None))
        _ParamBase.__init__(self, *args, **kwd)

        self._paramval[None] = self

    #def simplify(self, model):
        #return self
        #return NumericConstant(value=self.value)

    def check_values(self):         #pragma:nocover
        #
        # Validate the values
        #
        if None not in self._index:
            raise ValueError, "Undefined value for parameter "+self.name
        if not self._valid_indexed_value(self.value,None,False):
            print "BUG",self.value,self._index
            msg = "Parameter '%s' failed validation test.  Value: %s"
            raise ValueError, msg % ( self.name, str(self.value) )

    def __call__(self, exception=True):
        return self._paramval[None].value


class _ParamArray(_ParamBase):

    def __init__(self, *args, **kwd):
        _ParamBase.__init__(self, *args, **kwd)

    def simplify(self, model):
        raise ValueError, "Cannot simplify array parameter "+self.name

    def __float__(self):
        msg = "Cannot access the value of array parameter '%s'"
        raise ValueError, msg % self.name

    def __int__(self):
        msg = "Cannot access the value of array parameter '%s'"
        raise ValueError, msg % self.name

    def set_value(self, value):
        for key in self._paramval:
            self.__setitem__(key,value)

    def check_values(self):         #pragma:nocover
        #
        # Validate the values
        #
        for key in self._paramval:
            if key not in self._index:
                msg = "Undefined value for parameter %s[%s]"
                raise ValueError, msg % ( self.name, str(key) )

            if self.mutable:
                val = self._paramval[key].value
            else:
                val = self._paramval[key]
            if not self._valid_indexed_value( val, key, False ):
                msg = "Parameter %s[%s] failed validation test.  Value: %s"
                raise ValueError, msg % ( self.name, str(key), str(tval) )

    def reset(self):
        pass                        #pragma:nocover

    def display(self, ostream=None):
        self.pprint(ostream=ostream)

    def __str__(self):
        return str(self.name)


class Param(Component):
    """
    Data objects that are used to construct Pyomo models.
    """

    alias("Param", "Parameter data that is used to define a model instance.")

    def __new__(cls, *args, **kwds):
        if args == ():
            self = _ParamElement(*args, **kwds)
        else:
            self = _ParamArray(*args, **kwds)
        return self

class SharedParam(SharedComponent, Param):
    """ A Param object to be shared between models. """

    alias("SharedParam", "A Param shared between Model objects.")

    def __new__(cls, *args, **kwds):
        kwds["ctype"] = kwds.get("ctype", SharedParam)
        if len(args) == 0:
            self = _SharedParamElement(*args, **kwds)
        else:
            self = _SharedParamArray(*args, **kwds)
        return self


class _SharedParamBase(SharedComponent, _ParamBase):
    """ _ParamBase object designed to be shared between Model instances """

    def __init__(self, *args, **kwds):
        kwds["ctype"] = kwds.get("ctype", _SharedParamBase)
        _ParamBase.__init__(self, *args, **kwds)


class _SharedParamElement(SharedComponent, _ParamElement):
    """ _ParamElement object designed to be shared between Model instances """

    def __init__(self, *args, **kwds):
        kwds["ctype"] = kwds.get("ctype", _SharedParamElement)
        _ParamElement.__init__(self, *args, **kwds)


class _SharedParamArray(SharedComponent, _ParamArray):
    """ _ParamElement object designed to be shared between Model instances """

    def __init__(self, *args, **kwds):
        kwds["ctype"] = kwds.get("ctype", _SharedParamArray)
        _ParamArray.__init__(self, *args, **kwds)

