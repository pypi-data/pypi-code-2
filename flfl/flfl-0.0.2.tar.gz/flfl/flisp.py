# encoding: utf-8

from flasmwrapper import *
from simplesexp import *

ctx_global=0
t_identifier = 0
t_list = 1
t_string = 2
t_int = 3
t_float = 4
t_nil = 5
t_symbol= 6

def getType(val):
    if isinstance(val, Ident):
        return t_identifier
    elif isinstance(val, Symbol):
        return t_symbol
    elif isinstance(val, list):
        return t_list
    elif isinstance(val, basestring):
        return t_string
    elif isinstance(val, float):
        return t_float
    elif isinstance(val, int):
        return t_int
    elif val is None:
        return t_nil
    else:
        raise Exception('unknown type')

class FlispCompiler:
    binding = {"#t":True, "true":True, "#f":False, "false":False, "nil":None}
    def __init__(self, swf=None, mid=None, indent=2):
        if swf:
            self.program = FlasmProgram(swf)
        else:
            self.program = FlasmMovieClip(mid, indent)
        self.env = FlispEnv()
        self.reader = Reader(FlispCompiler.binding)
        self.graph = FlispGraph()
        self.ctx_stack = []
        self.env.addSpecialForm('define', '+2:3', self.compileDefine, False)
        self.env.addSpecialForm('set!', '+2:3', self.compileSet, True)
        self.env.addSpecialForm('if', '+2:3', self.compileIf, True)
        self.env.addSpecialForm('while', '+1', self.compileWhile, True)
        self.env.addSpecialForm('begin', -1, self.compileBegin, True)
        self.env.addSpecialForm('with-mc', '+2', self.compileWithMc, False)
        self.env.addSpecialForm('cond', '+1', self.compileCond, True)
        self.env.addSpecialForm('define-mc', '+1', self.compileDefineMc, False)
        self.env.addSpecialForm('define-button', '+1', self.compileDefineButton, False)
        self.env.addSpecialForm('matrix', '+1', self.compileMatrix, True)
    def read(self, string):
        self.exprs = self.reader.read(string)
    def readFile(self, path):
        io = open(path)
        self.exprs = self.reader.read(io.read())
        io.close()
    def run(self, string=None):
        """コンパイル"""
        if not string and self.exprs:
            exprs = self.exprs
        elif string:
            exprs = self.reader.read(string)
        else:
            raise Exception('no source code')
        self.ctx_stack.append(ctx_global)
        for i in exprs:
            self.program.add(self.compileTop(i, None))
        self.program.end()
        if self.graph.check(): #循環参照のチェック
            return self.program.toString()
    def getStructure(self, exprs=None):
        if not exprs:
            if not self.exprs:
                raise Exception('no source code')
            exprs = self.exprs
        def isfunc(expr):
            return isinstance(expr, list) and len(expr) and str(expr[0])=='define' and isinstance(expr[1], list)
        def isbutton(expr):
            return isinstance(expr, list) and len(expr) and str(expr[0])=='define-button'
        def ismc(expr):
            return isinstance(expr, list) and len(expr) and str(expr[0])=='define-mc'
        def isexpr(expr):
            return not isfunc(expr) and not isbutton(expr) and not ismc(expr)
        r = {
            'frames': 0, 'objects': []
            }
        flen = len(filter(isfunc, exprs))
        r['frames'] = flen
        normal = len(filter(isexpr, exprs))
        r['hasmain'] = bool(normal)
        if normal:
            r['frames'] += 1
        for expr in exprs:
            if isbutton(expr):
                r['objects'].append(('button', expr[1]))
            elif ismc(expr):
                fr = len(filter(isfunc, expr[1:]))
                normal = len(filter(isexpr, expr[1:]))
                if normal:
                    fr += 1
                r['objects'].append(('mc', expr[1], fr, bool(normal)))
        return r
    def compileTop(self, expr, env):
        """一番左の式をコンパイル"""
        if len(expr)==0:
            return mkstmt('')
        f, r = self.compileExpr(expr, env)
        if not r:
            raise FlispSemanticException('invalid expression')
        if f.hasReturn:
            r.add(flPop()) #返り値を捨てる
        return r
    def compileExpr(self, expr, env):
        """式or文のコンパイル"""
        if not isinstance(expr, list):
            return toInstruction(expr)
        fname = str(expr[0])
        if self.env.isSpecialForm(fname):
            f = self.env.getSpecialForm(fname)
            r = f.doCompile(expr[1:], env)
            return (f, r)
        args = []
        for i in range(1, len(expr)):
            args.append(self.compileArg(expr[i], env))
        if not self.env.isFunction(fname):
            raise FlispSemanticException('undefined function: %s' % fname)
        func = self.env.getFunctionObject(fname)
        r = self.compileFunction(func, args, env)
        if not r:
            raise FlispSemanticException('invalid function: %s'% fname)
        return (func, r)
    def compileDefine(self, args, env):
        """define特殊式のコンパイル"""
        if len(args)==1:
            raise FlispSyntaxException('syntax-error: define')
        if len(args) != 2:
            raise FlispSyntaxException('syntax-error: define')
        if isinstance(args[0], list):
            #関数定義のコンパイル
            if len(args[0])<1:
                raise FlispSyntaxException('syntax-error: define')
            nameAndArgs = args[0]
            name = str(nameAndArgs[0])
            if not checkVarname(name):
                raise FlispSyntaxException('syntax-error: invalid variable name: %s') % name

            fargs = nameAndArgs[1:]
            s = mkstmt('')
            env = {}
            for idx, v in zip(range(len(fargs)), fargs):
                assertType(v, t_identifier)
                env[str(v)] = 'g_%s_args%d' % (name, idx)
            f = self.env.addFunction(name, len(fargs), True)
            hasR = False
            self.ctx_stack.append(f)
            for i in args[1:]:
                f2, r = self.compileExpr(i, env)
                hasR = f2.hasReturn
                s.add(r)
            f.hasReturn = hasR
            self.program.addFunction(name, s)
            self.ctx_stack.pop()
            return mkstmt('')
        else:
            #変数定義のコンパイル
            assertType(args[0], t_identifier)
            name = str(args[0])
            if not checkVarname(name):
                raise FlispSyntaxException('syntax-error: invalid variable name: %s' % name)
            compiledArg = self.compileArg(args[1], env)
            self.env.addVariable(name, compiledArg)
            return flSetVar(name, compiledArg)
    def compileSet(self, args, env):
        """set!のコンパイル"""
        name, val = args
        compiledVal = self.compileArg(val, env)
        if not self.env.isVariable(str(name)):
            raise FlispSemanticException('unknown variable: %s'%str(name))
        r = flSetVar(str(name), compiledVal).add(flGetVar(str(name)))
        return r
    def compileIf(self, args, env):
        """if特殊式のコンパイル"""
        pred, cnd = self.compileExpr(args[0], env)
        if not pred.hasReturn:
            cnd.add(flPushStr('undef'))
        f, thenstmt = self.compileExpr(args[1], env)
        if not f.hasReturn:
            thenstmt.add(flPushStr('undef'))
        elsestmt = None
        if len(args)==3:
            f2, elsestmt = self.compileExpr(args[2], env)
            if not f2.hasReturn:
                elsestmt.add(flPushStr('undef'))
        r = FlasmIf(cnd, thenstmt, elsestmt)
        return r
    def compileWhile(self, args, env):
        """while特殊式のコンパイル"""
        pred, cnd = self.compileExpr(args[0], env)
        if not pred.hasReturn:
            cnd.add(flPushStr('undef'))
        s = mkstmt('')
        hasRet = False
        for i in args[1:]:
            f2, code = self.compileExpr(i, env)
            hasRet = f2.hasReturn
            s.add(code)
        if not hasRet:
            s.add(flPushStr('undef'))
        r = FlasmWhile(cnd, s)
        return r
    def compileCond(self, args, env):
        """cond特殊式のコンパイル"""
        s = FlasmStmt()
        labels = []
        for expr in args[0:-1]:
            assertLen(expr, 2)
            f, cnd = self.compileExpr(expr[0], env)
            if not f.hasReturn:
                cnd.add(flPushStr('undef'))
            label = FlasmLabel()
            s.add(cnd)
            s.add(flBranchIfTrue(label))
            labels.append(label)
        last = args[-1]
        assertLen(last, 2)
        continuation = FlasmLabel()
        dostmts = map(lambda x:x[1], args)
        if getType(last[0])==t_identifier and str(last[0])=='else':
            #elseがある
            f, r = self.compileExpr(dostmts[-1], env)
            if not f.hasReturn:
                r.add(flPushStr('undef'))
            s.add(r)
            s.add(flBranch(continuation))
            dostmts.pop()
        else:
            #elseがない
            f, cnd = self.compileExpr(last[0], env)
            if not f.hasReturn:
                cnd.add(flPushStr('undef'))
            label = FlasmLabel()
            s.add(cnd)
            s.add(flBranchIfTrue(label))
            #すべての条件が偽
            s.add(flPushStr('undef'))
            s.add(flBranch(continuation))
            labels.append(label)
        for label, dostmt in zip(labels, dostmts):
            s.setLabel(label)
            f, compiledDo = self.compileExpr(dostmt, env)
            if not f.hasReturn:
                f.add(flPushStr('undef'))
            s.add(compiledDo)
            s.add(flBranch(continuation))
        s.setLabel(continuation)
        return s
    def compileBegin(self, args, env):
        """begin特殊式のコンパイル"""
        s = mkstmt()
        hasRet = False
        for i in args:
            #todo: 最後の式以外は返り値を捨てる
            f2, code = self.compileExpr(i, env)
            hasRet = f2.hasReturn
            s.add(code)
        if not hasRet:
            s.add(flPushStr('undef'))
        return s
    def compileWithMc(self, args, env):
        """with-mc特殊式のコンパイル"""
        s = self.compileBegin(args[1:], env)
        indent = self.getIndent()
        assertType(args[0], t_string)
        return FlasmSetTarget(str(args[0]), s, indent)
    def compileDefineMc(self, args, env):
        """define-mc特殊式のコンパイル"""
        defmc = self.env.getSpecialForm('define-mc')
        mid = str(args[0])
        indent = self.getIndent() + 2
        child = FlispCompiler(None, mid, indent)
        mc = child.program
        self.ctx_stack.append(mc)
        for expr in args[1:]:
            mc.add(child.compileTop(expr, None))
        self.ctx_stack.pop()
        self.program.addObject(mc)
        mc.adjustIndent()
        return mkstmt()
    def compileDefineButton(self, args, env):
        """define-button特殊式のコンパイル"""
        handlerMap = {
            'on-press': (0, flOnPress),
            'on-release': (0, flOnRelease),
            'on-rollout': (0, flOnRollout),
            'on-rollover': (0, flOnRollover),
            'on-keypress': (1, self.compileOnKeypress)
        }
        handlers = args[1:]
        defbutton = self.env.getSpecialForm('define-button')
        indent = self.getIndent()
        but = FlasmButton(str(args[0]), indent+2)
        for handler in handlers:
            evt = str(handler[0])
            handlerDef = handlerMap[evt]
            if not handlerDef:
                raise FlispSemanticException('undefine event :%s' % evt)
            arglen = handlerDef[0]
            func = handlerDef[1]
            forms = handler[(arglen+1):]
            codes = mkstmt()
            self.ctx_stack.append(but)
            for f in forms:
                cfunc, code = self.compileExpr(f, env)
                if cfunc.hasReturn:
                    code.add(flPop())
                code.setIndent(indent+4)
                codes.add(code)
            l = handler[1:arglen+1]
            l.append(codes)
            but.addHandler(func(*l))
            self.ctx_stack.pop()
        self.program.addObject(but)
        return mkstmt()
    def compileOnKeypress(self, key, codes):
        """on-keypress"""
        s = str(key)
        return flOnKeyPress(s, codes)
    def compileMatrix(self, val, env):
        """matrix"""
        compiledVals = map(lambda row: map(lambda x: self.compileArg(i, env), row), val)
        return flDefineMatrix(compiledVals)
    def compileArg(self, val, env):
        """引数のコンパイル"""
        t = getType(val)
        if t==t_list:
            f, r = self.compileExpr(val, env)
            if not f.hasReturn:
                return flPushStr('undef')
            else:
                return r
        elif t==t_identifier:
            return self.compileVar(val, env)
        elif t==t_string:
            return flPushStr(val)
        elif t==t_int or t==t_float:
            return flPushInt(val)
        elif t==t_nil:
            return flPushStr('nil')
    def compileFunction(self, func, args, env):
        """関数呼び出しのコンパイル"""
        if isinstance(func, FlispPrimitiveFunction):
            return func.doCompile(args)
        elif isinstance(func, FlispUserFunction):
            ctx = None
            for i in self.ctx_stack[::-1]:
                if isinstance(i, FlispUserFunction):
                    ctx = i
                    break
            if ctx and isinstance(ctx, FlispUserFunction):
                if ctx.name == func.name:
                    raise FlispSemanticException('recursive call: %s'%ctx.name)
                self.graph.path(ctx, func)
            checkArity(args, func.arity)
            s = mkstmt('')
            for idx, i in zip(range(len(args)), args):
                s.add(flSetVar('g_%s_args%d'%(func.name, idx), i))
            s.add(self.program.callFunction(func.name))
            return s
        else:
            raise FlispSemanticException('invalid type in FunctionTable')
    def compileVar(self, var, env):
        """変数のコンパイル"""
        if env and str(var) in env:
            return flGetVar(env[var])
        else:
            if not self.env.isVariable(str(var)):
                raise FlispSemanticException('unknown variable: %s'%str(var))
            return flGetVar(str(var))
    def getIndent(self):
        ctx = ctx_global
        for i in self.ctx_stack[::-1]:
            if isinstance(i, FlasmObject):
                ctx = i
                break
        if ctx == ctx_global:
            indent = 0
        else:
            indent = ctx.indent+2
        return indent

class FlispSemanticException(Exception): pass

class FlispSyntaxException(Exception): pass

def assertType(val, t):
    rt = getType(val)
    if rt != t:
        raise FlispSemanticException('invalid type %s'%val.__class__)
def assertArgsType(args):
    if not isinstance(args, list):
        raise FlispSemanticException('invalid argument %s' % args)
def assertLen(args, expectedLen):
    assertArgsType(args)
    if len(args) != expectedLen:
        raise FlispSemanticException('invalid argument %d to %d' % (len(args), expectedLen))
def assertArgsMin(args, minLen):
    assertArgsType(args)
    if len(args) < minLen:
        raise FlispSemanticException('invalid argument %d to %d' % (len(args), minLen))
def assertArgsMax(args, maxLen):
    assertArgsType(args)
    if len(args) > maxLen:
        raise FlispSemanticException('invalid argument %d to %d' % (len(args), maxLen))
varreg = re.compile('^[a-zA-Z][a-zA-Z0-9\-]*$')
def checkVarname(name):
    return not not varreg.match(name)
def checkArity(args, arity):
    if isinstance(arity, int) and arity >= 0:
        assertLen(args, arity)
    elif isinstance(arity, str) and arity[0] == '+':
        i = arity.find(':')
        if i > 0:
            minimum = int(arity[1:i])
            maximum = int(arity[i+1:])
            assertArgsMax(args, maximum)
        else:
            minimum = int(arity[1:])
            assertArgsMin(args, int(minimum))
    else:
        assertArgsType(args)

class FlispBaseFunction(object):
    pass

class FlispSpecialForm(FlispBaseFunction):
    def __init__(self, arity, name, method, hasReturn=True, indent=0):
        self.arity = arity
        self.method = method
        self.name = name
        self.hasReturn = hasReturn
        self.indent = indent
    def doCompile(self, args, env):
        checkArity(args, self.arity)
        return self.method(args, env)

class FlispPrimitiveFunction(FlispBaseFunction):
    def __init__(self, arity, name, compileFunc, hasReturn=True):
        self.arity = arity
        self.name = name
        self.compileFunc = compileFunc
        self.hasReturn = hasReturn
    def __repr__(self):
        return "primitive function(%s)" % self.name
    def doCompile(self, args):
        checkArity(args, self.arity)
        r = self.compileFunc(*args)
        return r

class FlispUserFunction(FlispBaseFunction):
    def __init__(self, arity, name, hasReturn=True):
        self.arity = arity
        self.name = name
        self.hasReturn = hasReturn

def compileSubstr(string, start, end):
    return flSubstr(flAdd(flSub(end, start), 1), start, string)
def compileMc(targetPath, varName):
    if isinstance(targetPath, str) and isinstance(varName, str):
        return flGetVar(targetPath+':'+varName)
    else:
        return flGetVar(flConcat(targetPath, varName))
def compileSetMc(targetPath, varName, value):
    if isinstance(targetPath, str) and isinstance(varName, str):
        return flSetVar(targetPath+':'+varName, value)
    else:
        return flSetVar(flConcat(targetPath, varName), value)
def compileArray(*values):
    return flDefineArray(values)

class FlispGraph:
    def __init__(self):
        self.paths = {}
    def path(self, caller, callee):
        if not caller.name in self.paths:
            self.paths[caller.name] = []
        self.paths[caller.name].append(callee.name)
    def check(self):
        for key in  self.paths.keys():
            for s in self.paths[key]:
                r = self.search(s, key)
                if r:
                    raise FlispSemanticException('recursive call: %s'%"->".join(r))
        return True
    def search(self, start, goal):
        stack = [start]
        cache = {}
        while stack:
            node = stack[-1]
            if node==goal:
                return stack
            children = self.paths[node]
            child = None
            for c in children:
                if not c in cache:
                    child = c
                    break
            if child:
                cache[child] = True
                stack.append(child)
            else:
                stack.pop()
        return None

prfunc = FlispPrimitiveFunction
flDefine = FlispPrimitiveFunction('+2:3', 'define', None)
class FlispEnv(object):
    functions = {
        '+': prfunc(-1, '+', flAdd2),
        '-': prfunc(-1, '-', flSub2),
        '/': prfunc('+1', '/', flDivide2),
        '*': prfunc(-1, '*', flMultiply2),
        '=': prfunc('+2', '=', flEquals),
        '<': prfunc('+2', '<', flLessThan),
        '>=': prfunc('+2', '>=', flGreaterEquals),
        '>': prfunc('+2', '>', flGreaterThan),
        '<=': prfunc('+2', '<=', flLessEquals),
        'string=?': prfunc(2, 'string=?', flStrEquals),
        'string<?': prfunc(2, 'string<?', flStrLessThan),
        'string<=?': prfunc(2, 'string<=?', flStrLessEquals),
        'string>?': prfunc(2, 'string>?', flStrGreaterThan),
        'string>=?': prfunc(2, 'string>=?', flStrGreaterEquals),
        'substring': prfunc(3, 'substring', compileSubstr),
        'string-append': prfunc(-1, 'string-append', flConcat2),
        'not': prfunc(1, 'not', flNot),
        'and': prfunc(-1, 'and', flAnd2),
        'or': prfunc(-1, 'or', flOr2),
        'random': prfunc(1, 'random', flRandom),
        'duplicate-mc': prfunc(3, 'duplicate-mc', flDuplicateMovieClip),
        'mc': prfunc(2, 'mc', compileMc),
        'set-mc!': prfunc(3, 'set-mc!', compileSetMc),
        'array': prfunc(-1, 'array', compileArray),
        'array-ref': prfunc(2, 'array-ref', flArrayRef),
        'array-set!': prfunc(3, 'array-set!', flArraySet),
        'array-length': prfunc(1, 'array-length', flArrayLen),
        'array-append!': prfunc(2, 'array-append!', flArrayAppend),
        'remainder': prfunc(2, 'remainder', flMod)
    }
    def __init__(self):
        self.functionTable = FlispEnv.functions
        self.varTable = {}
        self.specialFormTable = {}
    def addSpecialForm(self, name, arity, func, hasReturn, indent=0):
        self.specialFormTable[name] = FlispSpecialForm(arity, name, func, hasReturn, indent)
        return self
    def isSpecialForm(self, name):
        return name in self.specialFormTable
    def getSpecialForm(self, name):
        return self.specialFormTable[name]
    def addPrimitiveFunction(self, name, func):
        self.functionTable[name] = func
        return self
    def isFunction(self, name):
        return name in self.functionTable
    def getFunctionObject(self, name):
        if name in self.functionTable:
            return self.functionTable[name]
        else:
            return None
    def addFunction(self, name, arity, hasReturn):
        f = FlispUserFunction(arity, name, hasReturn)
        self.functionTable[name] = f
        return f
    def pushStack(self, obj):
        self.stack.append(obj)
    def popStack(self):
        return self.stack.pop()
    def isVariable(self, name):
        return name in self.varTable
    def addVariable(self, name, value):
        self.varTable[name] = 1
        return 1
def mkgetter(pid):
    def f(obj):
        return flGetProperty(obj, pid)
    return f
def mksetter(pid):
    def f(obj, value):
        return flSetProperty(obj, pid, value)
    return f
for prop,pid in properties.iteritems():
    name = prop.lower()
    getter = 'get-%s' % name
    setter = 'set-%s!'% name
    FlispEnv.functions[getter] = prfunc(1, getter, mkgetter(pid))
    FlispEnv.functions[setter] = prfunc(2, setter, mksetter(pid), False)


