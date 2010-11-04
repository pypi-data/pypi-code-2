# * encoding: utf-8

__all__ = ['FljsCompiler']

from flfl.flasmwrapper import *
from flfl.fljsparser import *
import flfl.fljsparser

class CompilerStack():
    def __init__(self):
        self.stack = []
    def push(self, v):
        self.stack.append(v)
    def pop(self):
        return self.stack.pop()
    def top(self):
        return self.stack[-1]
    def search(self, type):
        r = None
        for i in self.stack[::-1]:
            if i.type == type:
                r = i
                break
        return r
    def searchFunc(self, f):
        r = None
        for i in self.stack[::-1]:
            if f(i.type):
                r = i
                break
        return r
    def searchAll(self, type):
        r = []
        for i in self.stack[::-1]:
            if i.type == type:
                r.append(i)
        return r

class CompilerCtx():
    def __init__(self, t):
        self.type = t
        self.dic = {}
    def __setitem__(self, key, v):
        self.dic[key] = v
    def __getitem__(self, key):
        return self.dic[key]
    def __len__(self):
        return len(self.dic)
    def __iter__(self):
        return self.dic.__iter__()
    def __repr__(self):
        return 'Ctx(%s)' % self.type

class FljsCompilerError(Exception):
    def __init__(self, msg, line=None):
        self.message = msg
        self.lineno = line

def assertType(t, expected):
    if t.type!=expected:
        raise FljsCompilerError('invalid type: '.t.type, t.lineno)
def assertCtx(t, msg='invalid context', lineno=None):
    if stack.top().type!=t:
        raise FljsCompilerError(msg, lineno)

stack = CompilerStack()

# stackにプッシュするもの
# PROGRAM
# MC
# ENV
# FUNC_ENV
# SWITCH
# LOOP

def program(t, swf):
    ctx = CompilerCtx('PROGRAM')
    prg = FlasmProgram(swf)
    ctx['PROGRAM'] = prg
    stack.push(ctx)
    stack.push(CompilerCtx('ENV'))
    for i in t['DEFINE_FUNCTION']:
        registFunc(i)
    for i in t['DEFINE_MC']:
        defMc(i)
    for i in t['DEFINE_BUTTON']:
        defButton(i)
    for i in t:
        s = statement(i)
        prg.add(s)
    for i in t['DEFINE_FUNCTION']:
        defFunc(i)
    stack.pop()
    return prg

def registFunc(t):
    checkLen(t, 3)
    assertCtx('ENV', 'define function invalid context, line %d' % t.lineno)
    assertType(t[0], 'IDENTIFIER')
    fname, args, body = t
    fname = fname.value
    prg = stack.searchFunc(lambda x: x=='PROGRAM' or x=='MC')
    prg['PROGRAM'].addEmptyFunction(fname)
    hasRet = hasReturn(body)
    user_functions[fname] = FljsUserFunction(len(args), fname, hasRet)

def defFunc(t):
    fname, args, body = t
    fname = fname.value
    env = CompilerCtx('FUNC_ENV')
    env['FUNC_NAME'] = fname
    for idx, i in enumerate(args):
        env[i.value] = 'g-%s-args%s' % (fname, idx)

    stack.push(env)

    s = block(body)

    stack.pop()

    prg = stack.searchFunc(lambda x: x=='PROGRAM' or x=='MC')
    prg['PROGRAM'].updateFunction(fname, s)

    return s

def handler(t):
    handlerMap = {
        'onPress': (0, flOnPress),
        'onRelease': (0, flOnRelease),
        'onRollout': (0, flOnRollout),
        'onRollover': (0, flOnRollover),
        'onKeypress': (1, flOnKeyPress)
        }
    if t[0].type=='IDENTIFIER':
        evt = t[0].value
    elif t[0].type=='CALL':
        evt = t[0][0].value
    else:
        raise FljsCompilerError('invalid handler: ' + t.value)

    df = handlerMap[evt]
    if not df:
        raise FljsCompilerError('unknown event: %s' % evt)
    if df[0]:
        l = map(lambda x: x.value, t[0][1])
    else:
        l = []
    codes = mkstmt()
    for i in t[1]:
        codes.add(statement(i))
    l.append(codes)
    return df[1](*l)

def defButton(t):
    checkLen(t, 2)
    button = FlasmButton(t[0].value, 2)
    for i in t[1]:
        button.addHandler(handler(i))
    program = stack.search('PROGRAM')
    program['PROGRAM'].addObject(button)
    return mkstmt()

def defMc(t):
    checkLen(t, 2)
    ctx = CompilerCtx('MC')
    mc = FlasmMovieClip(t[0].value, 2)
    ctx['PROGRAM'] = mc
    stack.push(ctx)
    stack.push(CompilerCtx('ENV'))
    for i in t[1]['DEFINE_FUNCTION']:
        registFunc(i)
    for i in t[1]:
        mc.add(statement(i))
    for i in t[1]['DEFINE_FUNCTION']:
        defFunc(i)
    stack.pop()
    program = stack.search('PROGRAM')
    program['PROGRAM'].addObject(mc)
    return mkstmt()

def statement(t):
    r = None
    if t.type == 'BLOCK':
        r = block(t)
    elif t.type == 'VAR':
        r = defVar(t)
    elif t.type == 'EMPTY':
        r = FlasmStmt()
    elif t.type == 'EXPRESSION_STATEMENT':
        r = expr(t[0], False)
    elif t.type == 'IF':
        r = if_stmt(t)
    elif t.type == 'SWITCH':
        r = switch_stmt(t)
    elif t.type == 'WHILE':
        r = while_stmt(t)
    elif t.type == 'FOR':
        r = for_stmt(t)
    elif t.type == 'RETURN':
        r = return_stmt(t)
    elif t.type == 'BREAK':
        r = break_stmt(t)
    elif t.type == 'CONTINUE':
        r = continue_stmt(t)
    else:
        raise FljsCompilerError('unknown type statement: '+t.type)
    return r

def block(t):
    s = mkstmt()
    for i in t:
        s.add(statement(i))
    return s

def defVar(t):
    assertType(t[0], 'IDENTIFIER')
    #assertCtx('ENV', 'variable declaration in invalid context', t.lineno)
    ctx = stack.search('ENV')
    if not checkVarname(t[0].value):
        raise FljsCompilerError('invalid variable: ' . t.value, t.lineno)
    if len(t)==2:
        compiledValue = expr(t[1])
        ctx[t[0].value] = compiledValue
        return flSetVar(t[0].value, compiledValue)
    elif len(t)==1:
        ctx[t[0].value] = None
        return mkstmt('')

def if_stmt(t):
    checkLen(t, (2, 3))
    cnd = expr(t[0], True)
    thenstmt = statement(t[1])
    if not thenstmt:
        print(t[1])
        raise Exception()
    elsestmt = None
    if len(t)==3:
        elsestmt = statement(t[2])
    s = FlasmIf(cnd, thenstmt, elsestmt)
    return s

def switch_stmt(t):
    l = len(stack.searchAll('SWITCH'))
    label = FlasmLabel([])
    ctx = CompilerCtx('SWITCH')
    ctx['BREAK'] = label
    stack.push(ctx)
    tmp = 'g-swtmp%s' % l #ネストレベルに応じて変数名を変える
    s = flSetVar(tmp, t[0])
    ptr = s
    compiledlist = []
    for i in t[1:]:
        assertType(i, 'CASE')
        checkLen(i, (1, 2))
        compiled = expr(i[0], True)
        compiledlist.append(flEquals(flGetVar(tmp), compiled))

    def f(x, y):
        return FlasmIf(x, y, None, label)
    s = flFoldl(f, compiled[::-1])
    stack.pop()
    return s

def while_stmt(t):
    checkLen(t, 2)
    label = FlasmLabel([])
    ctx = CompilerCtx('LOOP')
    ctx['BREAK'] = label

    stack.push(ctx)

    dos = mkstmt()
    nextlabel = FlasmLabel([])
    ctx['NEXT'] = nextlabel
    dos.setLabel(nextlabel)
    dos.add(statement(t[1]))
    s = FlasmWhile(expr(t[0]), dos, label)

    stack.pop()
    return s

def for_stmt(t):
    checkLen(t, 4)
    label = FlasmLabel([])
    ctx = CompilerCtx('LOOP')
    ctx['BREAK'] = label
    stack.push(ctx)

    s = statement(t[0])
    cnd = expr(t[1], True)
    dos = mkstmt()
    nextlabel = FlasmLabel([])
    ctx['NEXT'] = nextlabel
    dos.setLabel(nextlabel)
    dos.add(statement(t[3]))
    expr_stmt = SyntaxTree([t[2]], 'EXPRESSION_STATEMENT')
    dos.add(statement(expr_stmt))
    s.add(FlasmWhile(cnd, dos, label))

    stack.pop()
    return s

def return_stmt(t):
    ctx = stack.search('FUNC_ENV')
    if not ctx:
        raise FljsCompilerError('return not in function', t.lineno)
    return mkstmt('branch finlabel')

def break_stmt(t):
    ctx = stack.searchFunc(lambda x: x=='LOOP' or x=='SWITCH')
    if not ctx:
        raise FljsCompilerError('break not in loop', t.lineno)
    return flBranch(ctx['BREAK'])

def continue_stmt(t):
    ctx = stack.search('LOOP')
    if not ctx:
        raise FljsCompilerError('continue not in loop')
    return flBranch(ctx['NEXT'])

def expr(t, needRet=False):
    op = t.type
    if op=='STRING' or op=='NUMERIC':
        return toInstruction(t.value)
    if op=='IDENTIFIER':
        fenv = stack.search('FUNC_ENV')
        if fenv and t.value in fenv:
            return flGetVar(fenv[t.value])
        env = stack.search('ENV')
        if not t.value in env:
            raise FljsCompilerError('unknown variable: '+t.value, t.lineno)
        return flGetVar(t.value)
    compiledArg = []
    if op=='CALL':
        for i in t[1]:
            compiledArg.append(expr(i, True))
        return callFunc(t[0], compiledArg, needRet)
    if op in ['=', '+=', '-=', '*=', '/=', '%=', '++$', '--$', '$++', '$--']:
        compiledArg = [t[0].value]
        for i in t[1:]:
            compiledArg.append(expr(i, True))
        f = functions.get(op, None)
        return f.doCompile(compiledArg, needRet)
    for arg in t:
        compiledArg.append(expr(arg, True))
    f = functions.get(op.lower(), None)
    if f:
        if op in ['COND']:
            s = f.doCompile(compiledArg, needRet)
        else:
            s = f.doCompile(compiledArg)
        if not needRet and f.hasReturn:
            s.add(flPop())
        return s
    else:
        raise FljsCompilerError('unknown function:'+op)

def callFunc(t, args, needRet=False):
    fname = t.value
    f = functions.get(fname, None)
    if f:
        s = f.doCompile(args)
        if not needRet and f.hasReturn:
            s.add(flPop())
        return s
    f = user_functions.get(fname, None)
    if not f:
        raise FljsCompilerError('unknown function: '+fname, t.lineno)
    checkLen(args, f.arity)
    funcctx = stack.search('FUNC_ENV')

    prg = stack.searchFunc(lambda x: x=='MC' or x=='PROGRAM')
    s = mkstmt()
    for idx, i in enumerate(args):
        s.add(flSetVar('g-%s-args%d'%(fname, idx), i))
    s.add(prg['PROGRAM'].callFunction(fname))
    return s

varreg = re.compile('^[a-zA-Z\$\_][a-zA-Z0-9\$\_]*$')
def checkVarname(name):
    return not not varreg.match(name)
def checkLen(l, expected, msg='invalid argument: '):
    if isinstance(expected, tuple):
        minv, maxv = expected
        if not minv <= len(l) <= max:
            raise FljsCompilerError(msg + str(l))
    elif isinstance(expected, int):
        if expected < 0:
            return True
        if len(l)!=expected:
            raise FljsCompilerError(msg + str(l))
def let(lv, rv, needRet=False):
    r = flSetVar(lv, rv)
    if needRet:
        r.add(lv)
    return r
def addLet(lv, rv, needRet=False):
    r = flSetVar(lv, flAdd(flGetVar(lv), rv))
    if needRet:
        r.add(lv)
    return r
def subLet(lv, rv, needRet=False):
    r = flSetVar(lv, flSub(lv, rv))
    if needRet:
        r.add(lv)
    return r
def divLet(lv, rv, needRet=False):
    r = flSetVar(lv, flDivide(lv, rv))
    if needRet:
        r.add(lv)
    return r
def multiLet(lv, rv, needRet=False):
    r = flSetVar(lv, flMultiple(lv, rv))
    if needRet:
        r.add(lv)
    return r
def modLet(lv, rv, needRet=False):
    r = flSetVar(lv, flMod(lv, rv))
    if needRet:
        r.add(lv)
    return r
def substr(s, idx, cnt):
    return flSubstr(cnt, idx, s)
def postInc(s, needRet=False):
    r = flSetVar(s, flAdd(flGetVar(s), 1))
    if needRet:
        r.add(s)
    return r
def postDec(s, needRet=False):
    r = flSetVar(s, flSub(flGetVar(s), 1))
    if needRet:
        r.add(s)
    return r
def preInc(s, needRet=False):
    if needRet:
        r = flSetVar('g-tmp', s)
        r.add(flSetVar(s, flAdd(flGetVar(s), 1)))
        r.add(flGetVar('g-tmp'))
    else:
        r = flSetVar(s, flAdd(flGetVar(s), 1))
    return r
def preDec(s, needRet=False):
    if needRet:
        r = flSetVar('g-tmp', s)
        r.add(flSetVar(s, flSub(flGetVar(s), 1)))
        r.add(flGetVar('g-tmp'))
    else:
        r = flSetVar(s, flSub(flGetVar(s), 1))
    return r
def cond(cnd, thenexp, elseexp, needRet=False):
    cnd2 = expr(cnd, True)
    thenexp2 = expr(thenexp, needRet)
    elseexp2 = expr(expr, needRet)
    return FlasmIf(cnd2, thenexp2, elseexp2)
def compileArray(*values):
    return flDefineArray(values)

class FljsBaseFunction(object):
    pass

class FljsPrimitiveFunction(FljsBaseFunction):
    def __init__(self, arity, name, compileFunc, hasReturn=True):
        self.arity = arity
        self.name = name
        self.compileFunc = compileFunc
        self.hasReturn = hasReturn
    def __repr__(self):
        return "primitive function(%s)" % self.name
    def doCompile(self, args, needReturn=None):
        checkLen(args, self.arity)
        if not needReturn is None:
            args = args[0:]
            args.append(needReturn)
        r = self.compileFunc(*args)
        return r

class FljsUserFunction(FljsBaseFunction):
    def __init__(self, arity, name, hasReturn=True):
        self.arity = arity
        self.name = name
        self.hasReturn = hasReturn

class FljsGraph:
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
                    raise FljsSemanticException('recursive call: %s'%"->".join(r))
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

def hasReturn(t):
    def checkAll(t):
        return any(map(lambda x: hasReturn(x), t))

    for i in t[::-1]:
        if i.type=='RETURN':
            return True
        elif i.type=='IF':
            f1 = hasReturn(i[1])
            f2 = True
            if len(t)==3:
                f2 = hasReturn(i[2])
            if f1 and f2:
                return True
        elif i.type=='FOR':
            f = hasReturn(i[3])
            if f: return f
        elif i.type=='WHILE':
            f = hasReturn(i[1])
            if f: return f
        elif i.type=='SWITCH':
            f = hasReturn(i[1])
            if f: return f
        elif i.type=='LIST':
            f = checkAll(i)
            if f: return f
        elif i.type=='CASE':
            f = hasReturn(i[1])
            if f: return f
        elif i.type=='BLOCK':
            f = checkAll(i)
            if f: return f
    return False
prfunc = FljsPrimitiveFunction
user_functions = {}
functions = {
    '+': prfunc(2, '+', flAdd),
    '-': prfunc(2, '-', flSub),
    '/': prfunc(2, '/', flDivide),
    '*': prfunc(2, '*', flMultiply),
    '%': prfunc(2, '%', flMod),
    '==': prfunc(2, '=', flEquals),
    '!=': prfunc(2, '!=', flNotEquals),
    '<': prfunc(2, '<', flLessThan),
    '>=': prfunc(2, '>=', flGreaterEquals),
    '>': prfunc(2, '>', flGreaterThan),
    '<=': prfunc(2, '<=', flLessEquals),
    '=': prfunc(2, '=', let, False),
    '+=': prfunc(2, '+=', addLet, False),
    '-=': prfunc(2, '-=', subLet, False),
    '*=': prfunc(2, '*=', multiLet, False),
    '/=': prfunc(2, '/=', divLet, False),
    '%=': prfunc(2, '%=', modLet, False),
    'COND': prfunc(3, 'COND', cond, False),
    '!': prfunc(1, 'not', flNot),
    '&&': prfunc(2, 'and', flAnd2),
    '||': prfunc(2, 'or', flOr2),
    '$++': prfunc(1, '$++', postInc),
    '$--': prfunc(1, '$--', postDec),
    '++$': prfunc(1, '++$', preInc),
    '--$': prfunc(1, '--$', preDec),

    'streq': prfunc(2, 'strEq', flStrEquals),
    'strlt': prfunc(2, 'strLt', flStrLessThan),
    'strgt': prfunc(2, 'strGt', flStrGreaterThan),
    'substr': prfunc(3, 'substring', substr),
    'concat': prfunc(-1, 'concat', flConcat2),
    'random': prfunc(1, 'random', flRandom),
    'duplicateMc': prfunc(3, 'duplicate-mc', flDuplicateMovieClip),
    'array': prfunc(-1, 'array', compileArray, False),
    'array_ref': prfunc(2, 'arrayref', flArrayRef),
    'array_set': prfunc(3, 'array-set!', flArraySet),
    'length': prfunc(1, 'array-length', flArrayLen),
    'append': prfunc(2, 'array-append!', flArrayAppend),
}
class FljsEnv(object):
    def __init__(self):
        self.functionTable = FljsEnv.functions
        self.varTable = {}
        self.specialFormTable = {}
    def addSpecialForm(self, name, arity, func, hasReturn, indent=0):
        self.specialFormTable[name] = FljsSpecialForm(arity, name, func, hasReturn, indent)
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
        f = FljsUserFunction(arity, name, hasReturn)
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
    name = prop.title()
    getter = 'get%s' % name
    setter = 'set%s'% name
    functions[getter] = prfunc(1, getter, mkgetter(pid))
    functions[setter] = prfunc(2, setter, mksetter(pid), False)

def getStructure(tree):
    r = {
        'frames': 0, 'objects': []
        }
    r['frames'] = len(tree['DEFINE_FUNCTION'])
    r['hasmain'] = len(tree) > 0
    if r['hasmain']:
        r['frames'] += 1
    for i in tree['DEFINE_MC']:
        hasmain = len(i)>0
        c = 1 if hasmain else 0
        c += len(i['DEFINE_FUNCTION'])
        r['objects'].append(('mc', i[0].value, c,
                             len(i)>0))
    for i in tree['DEFINE_BUTTON']:
        r['objects'].append(('button', i[0].value))
    return r

class FljsCompiler:
    def __init__(self, swf):
        self.parser = flfl.fljsparser
        self.swf= swf
    def read(self, str):
        try:
            self.tree= self.parser.parse(str)
        except FljsSyntaxError, e:
            msg = "\tfile '%s'" % self.path
            if er.lineno:
                msg += ", line %s" % er.lineno
                msg += "\n"
            msg += er.message
            print msg
    def readFile(self, path, confpath):
        try:
            self.path = path
            io = open(path)
            self.tree= self.parser.parse(io.read(), confpath)
        except FljsSyntaxError, er:
            msg = "file '%s'" % self.path
            if er.lineno:
                msg += ", line %s" % er.lineno
                msg += "\n"
            msg += er.message
            print msg
            if not io.closed: io.close()
            exit(1)
        finally:
            io.close()
    def getStructure(self):
        strc = getStructure(self.tree)
        return strc
    def run(self):
        try:
            c = fljsCompile(self.tree, self.swf)
            return c.toString()
        except FljsCompilerError, er:
            msg = "file '%s'" % self.path
            if er.lineno:
                msg += ", line %s" % er.lineno
                msg += "\n"
            msg += er.message
            print msg
            exit(1)

def fljsCompile(tree, swf=''):
    prg = program(tree, swf)
    prg.end()
    return prg

if __name__ == '__main__':
    import sys

    if len(sys.argv)<=1:
        print('Usage: %s FILE' % sys.argv[0])
        exit(0)

    try:
        f = file(sys.argv[1])
        st = fljsparser.parse(f)
        c = fljsCompile(st)
        print(c.toString())
    except FljsCompilerError, er:
        msg = "\tfile '%s'" % sys.argv[1]
        if er.lineno:
            msg += ", line %s" % er.lineno
        msg += "\n"
        msg += er.message
        print msg

