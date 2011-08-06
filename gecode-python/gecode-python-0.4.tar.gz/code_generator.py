## -*- python -*-
##=============================================================================
## Copyright (C) 2011 by Denys Duchier
##
## This program is free software: you can redistribute it and/or modify it
## under the terms of the GNU Lesser General Public License as published by the
## Free Software Foundation, either version 3 of the License, or (at your
## option) any later version.
## 
## This program is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##=============================================================================

import re

class Type(object):

    DEFAULT   = re.compile("""^(.+)=(.+)$""")
    CONST     = re.compile("""^const\\b(.+)$""")
    UNSIGNED  = re.compile("""^unsigned\\b(.+)$""")
    REFERENCE = re.compile("""^(.+)&$""")

    def __init__(self, text):
        if isinstance(text, Type):
            self.clone_from(text)
            return
        text = text.strip()
        m = self.DEFAULT.match(text)
        if m:
            self.default = m.group(2).strip()
            text = m.group(1).strip()
        else:
            self.default = None
        m = self.CONST.match(text)
        if m:
            self.const = True
            text = m.group(1).strip()
        else:
            self.const = False
        m = self.UNSIGNED.match(text)
        if m:
            self.unsigned = True
            text = m.group(1).strip()
        else:
            self.unsigned = False
        m = self.REFERENCE.match(text)
        if m:
            self.reference = True
            text = m.group(1).strip()
        else:
            self.reference = False
        self.type = text

    def __str__(self):
        l = []
        if self.const: l.append("const ")
        if self.unsigned: l.append("unsigned ")
        l.append(self.type)
        if self.reference: l.append("&")
        if self.default is not None:
            l.append("=")
            l.append(self.default)
        return ''.join(l)

    def clone_from(self, other):
        self.const = other.const
        self.unsigned = other.unsigned
        self.type = other.type
        self.reference = other.reference
        self.default = other.default

    def clone(self):
        return type(self)(self)

class Constraint(object):

    DECL = re.compile("""^([^(]+)\\b(\w+)\((.*)\);$""")
    ARG  = re.compile("""((?:[^,<(]|<[^>]*>|\([^)]*\))+),?""")

    def __init__(self, line):
        if isinstance(line, Constraint):
            self.clone_from(line)
            return
        line = line.strip()
        m = self.DECL.match(line)
        self.rettype = Type(m.group(1).strip())
        self.name = m.group(2)
        argtypes = []
        for x in self.ARG.finditer(m.group(3).strip()):
            argtypes.append(Type(x.group(1)))
        self.argtypes = tuple(argtypes)
        self.api = None

    def __str__(self):
        l = []
        l.append(str(self.rettype))
        l.append(" ")
        l.append(self.name)
        sep = "("
        for x in self.argtypes:
            l.append(sep)
            sep = ", "
            l.append(str(x))
        l.append(")")
        if self.api is not None:
            l.append(" -> ")
            l.append(self.api)
        l.append(";")
        return ''.join(l)

    def clone_from(self, other):
        self.rettype = other.rettype.clone()
        self.name = other.name
        self.argtypes = tuple(t.clone() for t in other.argtypes)

    def clone(self):
        return type(self)(self)
    

COMMENT = re.compile("""^\\s*//.*$""")

def load_decls(filename):
    decls = []
    for line in open(filename):
        line = line.strip()
        if not line: continue
        m = COMMENT.match(line)
        if m: continue
        decls.append(Constraint(line))
    return decls

class DeclsLoader(object):

    def __init__(self, filename):
        self.decls = load_decls(filename)

    def print_decls(self):
        for con in self.decls:
            print str(con)

class PredGenerator(DeclsLoader):

    OMIT = ("DFA",              # NOT YET SUPPORTED!!!
            "TupleSet",         # NOT YET SUPPORTED!!!
            "VarBranchOptions",
            "ValBranchOptions",
            "TieBreakVarBranch<IntVarBranch>",
            "TieBreakVarBranchOptions",
            "TieBreakVarBranch<SetVarBranch>")

    def __init__(self, filename):
        super(PredGenerator, self).__init__(filename)
        self._change_home_to_space()
        self._change_intsharedarray_to_intargs()
        self._generate()
        self._number()

    def _change_home_to_space(self):
        for p in self.decls:
            for t in p.argtypes:
                if t.type=="Home":
                    t.type="Space"

    def _change_intsharedarray_to_intargs(self):
        for p in self.decls:
            for t in p.argtypes:
                if t.type=="IntSharedArray":
                    t.type="IntArgs"

    def _change_types_from_to(self,f,t):
        for p in self.decls:
            for t in p.argtypes:
                if t.type==f:
                    t.type=t

    def _generate(self):
        # drop the constraints and optional arguments we can't handle
        preds = []
        for con in self.decls:
            if self._con_ok(con):
                con = con.clone()
                con.argtypes = tuple(self._drop_deco(t) for t in con.argtypes
                                     if t.type not in self.OMIT)
                preds.append(con)
        # for each pred that has an argument with a default produce
        # 2 preds (1 without, 1 with).  repeat until all defaults have
        # been removed.
        again = True
        while again:
            preds_ = []
            again = False
            for con in preds:
                i = self._defaulted(con.argtypes)
                if i is None:
                    preds_.append(con)
                else:
                    again = True
                    before = con.argtypes[:i]
                    # without the default argument
                    # and therefore without the args that follow
                    con1 = con.clone()
                    con1.argtypes = before
                    preds_.append(con1)
                    # with the default argument (not default anymore)
                    con2 = con.clone()
                    arg = con.argtypes[i].clone()
                    arg.default=None
                    after = con.argtypes[i+1:]
                    con2.argtypes = before + (arg,) + after
                    preds_.append(con2)
            preds = preds_
        self.preds = preds

    def _con_ok(self, con):
        for t in con.argtypes:
            if (t.type in self.OMIT) and (t.default is None):
                return False
        return True

    def _drop_deco(self, t):
        # drop const, ref, and unsigned indications
        t.const = False
        t.reference = False
        t.unsigned = False
        return t

    def _defaulted(self, argtypes):
        i = 0
        for x in argtypes:
            if x.default is not None:
                return i
            i += 1
        return None

    def _number(self):
        i = 1
        for x in self.preds:
            x.api = "%s_%d" % (x.name,i)
            i += 1

    def print_preds(self):
        for p in self.preds:
            print str(p)

class CythonPredImplGenerator(PredGenerator):

    def __init__(self, filename):
        super(CythonPredImplGenerator, self).__init__(filename)
        self._change_types_()

    def _change_types_(self):
        for p in self.preds:
            for t in p.argtypes:
                if t.type=="bool":
                    t.type="bint"
                elif t.type not in ("int","bint") and t.type[-1]!="_":
                    t.type += "_"

    def generate(self):
        print 'cdef extern from "gecode-common.icc" namespace "Gecode":'
        for p in self.preds:
            args = ",".join(map(str,p.argtypes))
            print '    cdef void %s_ "::Gecode::%s"(%s)' % (p.name,p.name,args)

VARHANDLERS = {}

class CythonVar(object):
    def __init__(self, i):
        super(CythonVar, self).__init__()
        self.index = i
    def var(self):
        return "x%d" % self.index
    def nextvar(self):
        return "x%d" % (self.index+1)
    def lvar(self):
        return "y%d_%s" % (self.index,self.TYPE)
    def lvar_(self):
        return "y%d_%s_" % (self.index,self.TYPE)
    def ltype(self):
        return self.TYPE
    def ltype_(self):
        return "%s_" % self.TYPE
    def _test(self,x):
        return "isinstance(%s,%s)" % (x,self.ltype())
    def test(self, out):
        out.write(self._test(self.var()))
    def load(self, out, indent):
        self.load_lvar(out, indent)
        self.load_lvar_(out, indent)
    def load_lvar(self, out, indent):
        out.indent_to(indent)
        out.writeln("%s = %s" % (self.lvar(), self.var()))
    def load_lvar_(self, out, indent):
        out.indent_to(indent)
        out.writeln("%s = %s" % (self.lvar_(), self.lvar()))
    def lref(self):
        return self.lvar_()
    def create_local_vars(self, vars):
        vars[self.lvar()] = self.ltype()
        vars[self.lvar_()] = self.ltype_()

class CythonInt(CythonVar):
    TYPE = "int"
    def create_local_vars(self, vars):
        vars[self.lvar()] = self.ltype()
    def load(self, out, indent):
        self.load_lvar(out, indent)
    def lref(self):
        return self.lvar()

VARHANDLERS["int"] = CythonInt

class CythonBint(CythonInt):
    TYPE = "bint"
    def _test(self,x):
        return "isinstance(%s,bool)" % x

VARHANDLERS["bint"] = CythonBint

class CythonGecodeVar(CythonVar):
    def load_lvar_(self, out, indent):
        out.indent_to(indent)
        out.writeln("%s = self._get_%svar(%s)" % (self.lvar_(),self.TYPE[0].lower(),self.lvar()))

class CythonIntVar(CythonGecodeVar):
    TYPE = "IntVar"
class CythonBoolVar(CythonGecodeVar):
    TYPE = "BoolVar"
class CythonSetVar(CythonGecodeVar):
    TYPE = "SetVar"

VARHANDLERS["IntVar"] = CythonIntVar
VARHANDLERS["BoolVar"] = CythonBoolVar
VARHANDLERS["SetVar"] = CythonSetVar

class CythonIntSet(CythonVar):
    TYPE = "IntSet"
    def ltype(self):
        return "IntSet"
    def ltype_(self):
        return "IntSet_*"
    def load_lvar_(self, out, indent):
        out.indent_to(indent)
        out.writeln("%s = %s._intset" % (self.lvar_(),self.lvar()))
    def lref(self):
        return "dereference(%s)" % self.lvar_()

VARHANDLERS["IntSet"] = CythonIntSet

class CythonEnum(CythonVar):
    def load(self, out, indent):
        out.indent_to(indent)
        out.writeln("%s = %s" % (self.lvar_(), self.var()))
    def create_local_vars(self, vars):
        vars[self.lvar_()] = self.ltype_()

class CythonArgs(CythonVar):
    def test(self, out):
        out.write("is_%s(%s)" % (self.TYPE,self.var()))
    def create_local_vars(self, vars):
        vars[self.lvar_()] = self.ltype_()
    def load(self, out, indent):
        out.indent_to(indent)
        out.writeln("%s = %s_from_list(%s)" % (self.lvar_(),self.TYPE.lower(),self.var()))

class CythonArgsWithSpace(CythonArgs):
    def load(self, out, indent):
        out.indent_to(indent)
        out.writeln("%s = %s_from_list(self,%s)" % (self.lvar_(),self.TYPE.lower(),self.var()))

class CythonIntArgs(CythonArgs):
    TYPE = "IntArgs"
class CythonIntSetArgs(CythonArgs):
    TYPE = "IntSetArgs"
class CythonTaskTypeArgs(CythonArgs):
    TYPE = "TaskTypeArgs"
class CythonIntVarArgs(CythonArgsWithSpace):
    TYPE = "IntVarArgs"
class CythonBoolVarArgs(CythonArgsWithSpace):
    TYPE = "BoolVarArgs"
class CythonSetVarArgs(CythonArgsWithSpace):
    TYPE = "SetVarArgs"

VARHANDLERS["IntArgs"] = CythonIntArgs
VARHANDLERS["IntSetArgs"] = CythonIntSetArgs
VARHANDLERS["TaskTypeArgs"] = CythonTaskTypeArgs
VARHANDLERS["IntVarArgs"] = CythonIntVarArgs
VARHANDLERS["BoolVarArgs"] = CythonBoolVarArgs
VARHANDLERS["SetVarArgs"] = CythonSetVarArgs

class CythonDTree(object):

    def __init__(self, i):
        self.index = i
        self.has_leaf = False
        self.dispatch = {}

    def set_is_last(self, m):
        if self.index == m:
            self.is_last = True
        else:
            self.is_last = False
            for d in self.dispatch.values():
                d.set_is_last(m)

    def enter(self, i, pred):
        a = pred.argtypes
        if len(a) == i:
            self.has_leaf = True
            self.pred = pred
        else:
            t = a[i]
            d = self.dispatch.get(t.type, None)
            if d is None:
                d = CythonDTree(i+1)
                self.dispatch[t.type] = d
            if t.type != "Space":
                d.cyvar = VARHANDLERS[t.type](i)
            d.enter(i+1, pred)

    def create_local_vars(self, vars):
        for d in self.dispatch.values():
            d.cyvar.create_local_vars(vars)
            d.create_local_vars(vars)

    def generate_body(self, lrefs, out, indent):
        if not hasattr(self, 'cyvar'):
            assert self.index == 1
            for d in self.dispatch.values():
                d.generate_body(lrefs, out, indent)
            out.indent_to(indent)
            out.writeln("raise TypeError()")
            return
        out.indent_to(indent)
        out.write("if ")
        self.cyvar.test(out)
        out.writeln(":")
        self.cyvar.load(out,indent+4)
        lrefs_ = lrefs + (self.cyvar.lref(),)
        if self.is_last:
            out.indent_to(indent+4)
            out.writeln("%s_(%s)" % (self.pred.name, ",".join(lrefs_)))
            out.indent_to(indent+4)
            out.writeln("return")
        else:
            out.indent_to(indent+4)
            out.writeln("if %s is None:" % self.cyvar.nextvar())
            out.indent_to(indent+8)
            if self.has_leaf:
                out.writeln("%s_(%s)" % (self.pred.name, ",".join(lrefs_)))
                out.indent_to(indent+8)
                out.writeln("return")
            else:
                out.writeln("raise TypeError()")
            for d in self.dispatch.values():
                d.generate_body(lrefs_,out,indent+4)
            out.indent_to(indent+4)
            out.writeln("raise TypeError()")

    def generate(self, vars, out, indent):
        self.load_space(out, indent)
        lvars = {}
        first = self.dispatch["Space"]
        first.create_local_vars(lvars)
        lvars_ = lvars.items()
        lvars_.sort()
        for v,t in lvars_:
            out.indent_to(indent)
            out.writeln("cdef %s %s" % (t,v))
        first.generate_body(("dereference(space_)",), out, indent)

    def load_space(self, out, indent):
        out.indent_to(indent)
        out.writeln("cdef GenericSpace* space = self._to_space()")
        out.indent_to(indent)
        out.writeln("cdef Space_* space_ = self._to_space_()")

class CythonConstraintGenerator(PredGenerator):

    def __init__(self, filename):
        super(CythonConstraintGenerator, self).__init__(filename)
        self._change_bool()
        self._classify()
        self._dtreefy()

    def _change_bool(self):
        for p in self.preds:
            for t in p.argtypes:
                if t.type=="bool":
                    t.type="bint"

    def _classify(self):
        classes = {}
        self.classes = classes
        for p in self.preds:
            c = classes.get(p.name, None)
            if c is None:
                c = []
                classes[p.name] = c
            c.append(p)

    def _dtreefy(self):
        dtrees = {}
        self.dtrees = dtrees
        for name,preds in self.classes.items():
            dt = CythonDTree(0)
            dtrees[name] = dt
            m = 0
            for p in preds:
                n = len(p.argtypes)
                if n>m: m=n
                dt.enter(0,p)
            dt.numargs = m
            dt.set_is_last(m)

    def generate(self, indent=0):
        out = OStream(sys.stdout)
        out.writeln("cdef class ApiSpace(ProtoSpace):")
        out.newline()
        for name,dtree in self.dtrees.items():
            vars = ("x%d" % (i+1) for i in range(dtree.numargs-1))
            parms = ("%s=None" % v for v in vars)
            out.indent_to(indent+4)
            if name in ("min","max"):
                # conflict with methods for getting min/max of
                # an IntVar's domain; so rename
                name = "_%s" % name
            out.writeln("def %s(self,%s):" % (name,",".join(parms)))
            dtree.generate(vars, out, indent+8)
            out.newline()

# output stream that keeps track of the current column
# to facilitate proper indentation

import sys

class OStream(object):

    def __init__(self, fd=sys.stdout):
        self.file = fd
        self.column = 0

    def write(self, s):
        reset = False
        for x in s.split('\n'):
            if reset:
                self.newline()
            else:
                reset = True
            self.file.write(x)
            self.column += len(x)

    def newline(self):
        self.file.write("\n")
        self.column = 0

    def writeln(self, s=None):
        if s is not None:
            self.write(s)
        self.newline()

    def indent_to(self, n):
        if n<self.column:
            self.newline()
        n = n - self.column
        while n>0:
            self.write(' ')
            n -= 1

class IntRelType(object):
    TYPE = 'IntRelType'
    ENUM = ('IRT_EQ','IRT_NQ','IRT_LQ','IRT_LE','IRT_GQ','IRT_GR')

class BoolOpType(object):
    TYPE = 'BoolOpType'
    ENUM = ('BOT_AND','BOT_OR','BOT_IMP','BOT_EQV','BOT_XOR')

class IntConLevel(object):
    TYPE = 'IntConLevel'
    ENUM = ('ICL_VAL','ICL_BND','ICL_DOM','ICL_DEF')

class SetRelType(object):
    TYPE = 'SetRelType'
    ENUM = ('SRT_EQ','SRT_NQ','SRT_SUB','SRT_SUP','SRT_DISJ','SRT_CMPL')

class SetOpType(object):
    TYPE = 'SetOpType'
    ENUM = ('SOT_UNION','SOT_DUNION','SOT_INTER','SOT_MINUS')

class IntVarBranch(object):
    TYPE = 'IntVarBranch'
    ENUM = ('INT_VAR_NONE','INT_VAR_RND','INT_VAR_DEGREE_MIN',
            'INT_VAR_DEGREE_MAX','INT_VAR_AFC_MIN','INT_VAR_AFC_MAX',
            'INT_VAR_MIN_MIN','INT_VAR_MIN_MAX','INT_VAR_MAX_MIN',
            'INT_VAR_MAX_MAX','INT_VAR_SIZE_MIN','INT_VAR_SIZE_MAX',
            'INT_VAR_SIZE_DEGREE_MIN','INT_VAR_SIZE_DEGREE_MAX',
            'INT_VAR_SIZE_AFC_MIN','INT_VAR_SIZE_AFC_MAX',
            'INT_VAR_REGRET_MIN_MIN','INT_VAR_REGRET_MIN_MAX',
            'INT_VAR_REGRET_MAX_MIN','INT_VAR_REGRET_MAX_MAX')

class IntValBranch(object):
    TYPE = 'IntValBranch'
    ENUM = ('INT_VAL_MIN','INT_VAL_MED','INT_VAL_MAX',
            'INT_VAL_RND','INT_VAL_SPLIT_MIN','INT_VAL_SPLIT_MAX',
            'INT_VAL_RANGE_MIN','INT_VAL_RANGE_MAX',
            'INT_VALUES_MIN','INT_VALUES_MAX')

class SetVarBranch(object):
    TYPE = 'SetVarBranch'
    ENUM = ('SET_VAR_NONE','SET_VAR_RND','SET_VAR_DEGREE_MIN',
            'SET_VAR_DEGREE_MAX','SET_VAR_AFC_MIN','SET_VAR_AFC_MAX',
            'SET_VAR_MIN_MIN','SET_VAR_MIN_MAX','SET_VAR_MAX_MIN',
            'SET_VAR_MAX_MAX','SET_VAR_SIZE_MIN','SET_VAR_SIZE_MAX',
            'SET_VAR_SIZE_DEGREE_MIN','SET_VAR_SIZE_DEGREE_MAX',
            'SET_VAR_SIZE_AFC_MIN','SET_VAR_SIZE_AFC_MAX')

class SetValBranch(object):
    TYPE = 'SetValBranch'
    ENUM = ('SET_VAL_MIN_INC','SET_VAL_MIN_EXC','SET_VAL_MED_INC',
            'SET_VAL_MED_EXC','SET_VAL_MAX_INC','SET_VAL_MAX_EXC',
            'SET_VAL_RND_INC','SET_VAL_RND_EXC')

class TaskType(object):
    TYPE = 'TaskType'
    ENUM = ('TT_FIXP','TT_FIXS','TT_FIXE')

class ExtensionalPropKind(object):
    TYPE = 'ExtensionalPropKind'
    ENUM = ('EPK_DEF','EPK_SPEED','EPK_MEMORY')

class IntAssign(object):
    TYPE = 'IntAssign'
    ENUM = ('INT_ASSIGN_MIN', 'INT_ASSIGN_MED', 'INT_ASSIGN_MAX', 'INT_ASSIGN_RND')

class SetAssign(object):
    TYPE = 'SetAssign'
    ENUM = ('SET_ASSIGN_MIN_INC', 'SET_ASSIGN_MIN_EXC', 'SET_ASSIGN_MED_INC',
            'SET_ASSIGN_MED_EXC', 'SET_ASSIGN_MAX_INC', 'SET_ASSIGN_MAX_EXC',
            'SET_ASSIGN_RND_INC', 'SET_ASSIGN_RND_EXC')

ENUM_CLASSES = (IntRelType, BoolOpType, IntConLevel,
                SetRelType, SetOpType, IntVarBranch,
                IntValBranch, SetVarBranch, SetValBranch,
                TaskType, ExtensionalPropKind, IntAssign, SetAssign)

for e in ENUM_CLASSES:
    class C(CythonEnum, e): pass
    VARHANDLERS[e.TYPE] = C

class CythonEnumImpl(object):

    def generate(self):
        print '    cdef enum %s_ "::Gecode::%s":' % (self.TYPE, self.TYPE)
        sep = ""
        for x in self.ENUM:
            print '%s        %s_ "::Gecode::%s"' % (sep,x,x) ,
            sep = ",\n"
        print
        print

class CythonEnumImplGenerator(object):

    def generate(self):
        print 'cdef extern from "gecode-common.icc" namespace "Gecode":'
        for c in ENUM_CLASSES:
            class C(c,CythonEnumImpl): pass
            o = C()
            o.generate()

class CythonEnumWrap(object):

    def generate(self):
        print "class %s(int): pass" % self.TYPE
        for x in self.ENUM:
            print '%s = %s(%s_)' % (x,self.TYPE,x)
        print

class CythonEnumWrapGenerator(object):

    def generate(self):
        for c in ENUM_CLASSES:
            class C(c,CythonEnumWrap): pass
            o = C()
            o.generate()

def gecode_version():
    from distutils.ccompiler import new_compiler, customize_compiler
    import os
    cxx = new_compiler()
    customize_compiler(cxx)
    file_hh = "_gecode_version.hh"
    file_txt = "_gecode_version.txt"
    f = file(file_hh,"w")
    f.write("""#include "gecode/support/config.hpp"
@@GECODE_VERSION""")
    f.close()
    cxx.preprocess(file_hh,output_file=file_txt)
    f = open(file_txt)
    version = ""
    for line in f:
        if line.startswith("@@"):
            version = line[3:-2]
            break
    f.close()
    os.remove(file_hh)
    os.remove(file_txt)
    return version

def generate_files():
    filename = "gecode-prototypes-%s.hh" % gecode_version()
    stdout = sys.stdout
    try:
        sys.stdout = file("gecode_python_enum.pxi","w")
        CythonEnumImplGenerator().generate()
        CythonEnumWrapGenerator().generate()
        sys.stdout.close()
        sys.stdout = file("gecode_python_pred.pxi","w")
        CythonPredImplGenerator(filename).generate()
        sys.stdout.close()
        sys.stdout = file("gecode_python_api.pxi","w")
        CythonConstraintGenerator(filename).generate()
        sys.stdout.close()
    finally:
        sys.stdout = stdout
