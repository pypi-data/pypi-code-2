# encoding: utf-8

import re

class FlasmObject:
    def addIndent(self, line, indent=None):
        if not indent:
            indent = self.indent
        return (' '*indent) + line + "\n"
    def endTag(self):
        return self.addIndent("end")
    def toString(self):
        s = self.beginTag()
        for i in self.getList():
            s += i.toString()
        s += self.endTag()
        return s

class FlasmProgram(FlasmObject):
    def __init__(self, swf):
        self.swfname = swf
        self.frames = []
        self.indent = 0
        self.functionTable = {}
        self.current = self.createFrame()
        self.objects = []
        self.empty = True
    def add(self, p):
        if self.empty and p.size():
            self.empty = False
        self.current.add(p)
    def addObject(self, p):
        self.objects.append(p)
    def getList(self):
        if not self.empty:
            return self.objects + self.frames
        else:
            return self.objects
    def createFrame(self):
        f = FlasmFrame(len(self.frames), self.indent+2)
        self.frames.append(f)
        return f
    def adjustIndent(self):
        for f in self.frames:
            f.adjustIndent()
    def updateFunction(self, name, s):
        f = self.frames[self.functionTable[name]-1]
        if not f:
            raise Exception('update unknown function: ' + name)
        f.codes = s
    def addEmptyFunction(self,name):
        f = self.createFrame()
        self.functionTable[name] = len(self.frames)
    def addFunction(self, name, prg):
        f = self.createFrame()
        f.add(prg)
        self.functionTable[name] = len(self.frames)
    def callFunction(self, name):
        if not name in self.functionTable:
            raise Exception('unknown function: ' + name)
        s = flPushInt(self.functionTable[name])
        return s.add('callFrame')
    def end(self):
        self.current.end()
        map(lambda x: x.end(), self.frames[1:])
        self.current = None
    def beginTag(self):
        return self.addIndent("movie \'%s\'" % self.swfname)

class FlasmMovieClip(FlasmProgram):
    def __init__(self, mid, indent=2):
        self.frames = []
        self.indent = indent
        self.functionTable = {}
        self.current = self.createFrame()
        self.empty = False
        self.objects = []
        self.id = mid
    def beginTag(self):
        return self.addIndent("defineMovieClip %s"%self.id)

class FlasmButton(FlasmObject):
    def __init__(self, bid, indent=2):
        self.indent = indent
        self.list = []
        self.id = bid
    def beginTag(self):
        return self.addIndent("defineButton %s"%self.id)
    def addHandler(self, code):
        code.indent = self.indent+2
        self.list.append(code)
    def getList(self):
        return self.list
    def toString(self):
        return FlasmObject.toString(self)

class FlasmFrame(FlasmObject):
    def __init__(self, fid, indent=2):
        self.indent = indent
        self.codes = FlasmStmt(None, self.indent+2)
        self.id = fid
    def add(self,code):
        self.codes.add(code)
    def adjustIndent(self, indent=None):
        if not indent:
            indent = self.indent
        self.codes.setIndent(indent+2)
    def toString(self):
        s = self.beginTag()
        s += self.codes.toString()
        s += self.endTag()
        return s
    def beginTag(self):
        return self.addIndent("frame %d"%self.id)
    def endTag(self):
        return self.addIndent("end // of frame %d" % self.id)
    def end(self):
        self.codes.end()

class FlasmHandler(FlasmObject):
    def __init__(self, event, codes, indent=4):
        self.indent = indent
        if isinstance(event, list):
            self.event = ' '.join(event)
        else:
            self.event = event
        self.codes = FlasmStmt(codes)
        self.codes.indent = indent + 2
    def beginTag(self):
        return self.addIndent("on " + self.event)
    def add(self, codes):
        self.codes.add(codes)
    def toString(self):
        s = self.beginTag()
        s += self.codes.toString()
        s += self.endTag()
        return s

class FlasmStmt:
    indentpat = re.compile("^\s*", re.M)
    emptypat = re.compile("^\s*$", re.M)
    def __init__(self, codes=None, indent=4):
        self.indent = indent
        self.codes = []
        self.fin = False
        self.labelCnt = 0
        if codes:
            self.add(codes)
    def size(self):
        return len(self.codes)
    def __repr__(self):
        return "FlastStmt(%s)"% self.codes
    def addIndent(self, line):
        if line.find(':') > 0:
            return (' ' * (self.indent-1)) + line
        else:
            return (' ' * self.indent) + line
    def lines2str(self, lines):
        if not lines:
            return ''
        return "\n".join([self.addIndent(i) for i in lines]) + "\n"
    def end(self):
        if self.labelCnt:
            self.add('branch finlabel')
            self.fin = True
    def toString(self):
        s = self.lines2str(self.codes)
        if self.fin:
            s += self.addIndent('finlabel:') + "\n"
        return s
    def setIndent(self, indent):
        self.indent = indent
    def setLabel(self, label):
        self.labelCnt += 1
        self.add(label.name+":")
        if label.codes:
            self.add(label)
    def addContext(self, stmt):
        self.codes += stmt.toString()
    def add(self, stmt):
        if not stmt:
            return
        if isinstance(stmt, FlasmObject):
            self.addContext(stmt)
            return self
        if isinstance(stmt, str):
            self.codes.append(stmt)
            return self
        elif isinstance(stmt, list):
            self.codes.extend(stmt)
            return self

        if stmt.codes:
            self.codes.extend(stmt.codes)
        if stmt.labelCnt:
            self.labelCnt += stmt.labelCnt
        return self

class FlasmSetTarget(FlasmObject):
    def __init__(self, target, codes, indent=4):
        self.indent = indent
        self.target = target
        codes.setIndent(self.indent + 2)
        self.codes = FlasmStmt(codes)
    def beginTag(self):
        return self.addIndent("setTarget \'%s\'"%self.target)
    def add(self, codes):
        self.codes.add(codes)
    def toString(self):
        s = self.beginTag()
        s += self.codes.toString()
        s += self.endTag()
        return s

class FlasmLabel(FlasmStmt):
    i = 0
    def __init__(self, codes=None, fid=None):
        FlasmStmt.__init__(self, codes)
        FlasmLabel.i += 1
        if not fid:
            self.id = FlasmLabel.i
        else:
            self.id = fid
        self.name = "label"+str(self.id)
    def __repr__(self):
        return "FlasmLabel(%s)"%self.name

class FlasmIf(FlasmStmt):
    def __repr__(self):
        return "FlastIf(%s)"%self.codes.split("\n")
    def __init__(self, condstmt, thenstmt, elsestmt=None, cont=None):
        self.condstmt = condstmt
        self.thenstmt = thenstmt
        self.elsestmt = elsestmt

        FlasmStmt.__init__(self)

        #まず条件分岐
        self.add(condstmt)

        #もどる場所
        if not cont:
            cont = FlasmLabel([])
        thenlabel = FlasmLabel(thenstmt)

        #trueならthenlabelへ
        if thenstmt.codes:
            self.add(flBranchIfTrue(thenlabel))
        else: #thenがない場合はすぐcontへ
            thenlabel = None
            self.add(flBranchIfTrue(cont))

        if(elsestmt): #elseがある場合は実行
            elsestmt.add(flBranch(cont))
            self.add(elsestmt)

        if thenlabel:
            self.setLabel(thenlabel)
        self.setLabel(cont)

class FlasmBegin(FlasmStmt):
    def __init__(self, *stmts):
        FlasmStmt.__init__(self)
        for i in stmts:
            self.add(i)

class FlasmWhile(FlasmStmt):
    def addDo(self, stmt):
        self.ifstmt.thenstmt.add(stmt)
    def __init__(self, condstmt, dostmt, cnt=None):
        FlasmStmt.__init__(self)

        loopstmt = FlasmLabel([])
        self.setLabel(loopstmt)
        dostmt.add(flBranch(loopstmt))
        self.ifstmt = FlasmIf(flNot(condstmt), FlasmStmt([]), dostmt, cnt)
        self.add(self.ifstmt)

reservedLabel = []
def flReserveLabel():
    l = FlasmLabel([])
    reservedLabel.append(l)
    return l

#命令:
#branch, branchIfTrue, push, pop,
#add, subtract, multiply, divide,
#oldEquals, oldLessThan,
#and, or, not
#stringEq, stringLength, substring, concat, stringLessThan
#mbSubtring, mbLength
#int, ord, chr, mbOrd, mbChr
#callFrame
#getVariable, setVariable
#getURL2, goto, setTargetExpr
#getProperty, setProperty
#duplicateClip, removeClip, startDrag, stopDrag
#ifFrameLoadedExpr, trace, getTimer, random
#increment, decrement, dup, swap

#flIntrunctions1 = "not,stringLength,mbLength,int,ord,chr,mbOrd,mbChr,callFrame,getVariable"
#flIntrunctions2 = "and,or,oldEquals,oldLessThan,stringEq,concat,setVariable".split(',')

def flBranch(label):
    return FlasmStmt(["branch "+label.name])
def flBranchIfTrue(label):
    return FlasmStmt(["branchIfTrue "+label.name])
def flPushInt(i):
    return FlasmStmt(["push "+str(i)])
def flPushStr(s):
    return FlasmStmt(["push '%s'" % s])
def flPop():
    return FlasmStmt(['pop'])
def flGetVar(name):
    return applyn('getVariable', toInstruction(name))
def flSetVar(name, value):
    r = applyn('setVariable', toInstruction(name), toInstruction(value))
    return r
def flLessThan(lval, rval):
    return applyn('oldLessThan', lval, rval)
def flEquals(lval, rval):
    return applyn('oldEquals', lval, rval)
def flNotEquals(lval, rval):
    return flNot(applyn('oldEquals', lval, rval))
def flStrEquals(lval, rval):
    return applyn('stringEq', lval, rval)
def flStrLessThan(lval, rval):
    return applyn('stringLessThan', lval, rval)
def flStrLen(val):
    return applyn('stringLength', val)
def flMbStrLen(val):
    return applyn('mbLength', val)
def flMbStrSub(count, index, string):
    return applyn('mbSubtring', count, index, string)
def flConcat(val1, val2):
    return applyn('concat', val1, val2)
def flSubstr(count, index, string):
    return applyn('substring', count, index, string)
def flInc(varname):
    return flSetVar(varname, applyn('increment', flGetVar(varname)))
def flDec(varname):
    return flSetVar(varname, applyn('decrement', flGetVar(varname)))
def flAdd(val1, val2):
    return applyn('oldadd', val1, val2)
def flSub(val1, val2):
    return applyn('subtract', val1, val2)
def flMultiply(val1, val2):
    return applyn('multiply', val1, val2)
def flDivide(val1, val2):
    return applyn('divide', val1, val2)
def flNot(expr):
    return applyn('not', expr)
def flAnd(expr1, expr2):
    return applyn('and', expr1, expr2)
def flOr(expr1, expr2):
    return applyn('or', expr1, expr2)
def flInt(val):
    return applyn('int', val)
def flOrd(val):
    return applyn('ord', val)
def flChar(val):
    return applyn('chr', val)
def flMbOrd(val):
    return applyn('mbOrd', val)
def flMbChar(val):
    return applyn('mbChr', val)
def flRandom(max):
    return applyn('random', max)
def flMod(x, y):
    # x % y == x - (floor(x/y)*y)
    return flSub(toInstruction(x),
                 flMultiply(flInt(flDivide(toInstruction(x), toInstruction(y))),
                            toInstruction(y)))

prop_X=0
prop_Y=1
prop_xscale=2
prop_yscale=3
prop_currentframe=4
prop_totalframes=5
prop_alpha=6
prop_visible=7
prop_width=8
prop_height=9
prop_rotatation=10
prop_target=11
prop_framesloaded=12
prop_name=13
prop_droptarget=14
prop_url=15
prop_highquality=16
prop_focusrect=17
prop_soundbuftime=18
properties = {
    "x": 0, "y":1, "xscale":2, "yscale":3,
    "currentframe":4, "totalframes":5, "alpha":6,
    "visible": 7, "width": 8, "height": 9, "rotation": 10,
    "target": 11, "framesloaded": 12, "name": 13,
    "droptarget":14, "url": 15, "highquality": 16,
    "focusrect": 17, "soundbuftime": 18
}
def flGetProperty(obj, prop):
    return applyn('getProperty', obj, prop)
def flSetProperty(obj, prop, value):
    return applyn('setProperty', obj, prop, value)
def flDuplicateMovieClip(target, newname, depth=100):
    return applyn('duplicateClip', target, newname, depth)
def flFoldl(func, start, args):
    """func(func(func(a, b), c)...)"""
    r = reduce(lambda x,y: func(x, y),
               args, start)
    return r
def flFoldr(func, start, args):
    """func(c, func(b, func(a, ...)))"""
    r = reduce(lambda x,y: func(y, x),
               args, start)
    return r
def flAnd2(*args):
    """
    以下のように変換する
    (and a b c ..) -> (if (not a) 0 (if (not b) 0 ... 1))

    """
    def f(x, y):
        r = flNot(x)
        r = FlasmIf(r,
                       flPushInt(0), y)
        return r
    r = flFoldr(f,
                flPushInt(1), args[::-1])
    return r
def flOr2(*args):
    """
    変換
    (or a b c) -> (if a 1 (if b 1) ... 0)
    """
    r = flFoldr(lambda x,y: FlasmIf(x, flPushInt(1), y),
                flPushInt(0), args[::-1])
    return r
def flAdd2(*args):
    if len(args)==0:
        return pushInt(0)
    elif len(args)==1:
        return toInstruction(args[0])
    else:
        return flFoldl(flAdd, flAdd(args[0], args[1]), args[2:])
def flSub2(*args):
    if len(args)==0:
        return pushInt(0)
    elif len(args)==1:
        return toInstruction(args[0])
    else:
        return flFoldl(flSub, flSub(args[0], args[1]), args[2:])
def flMultiply2(*args):
    if len(args)==0:
        return pushInt(0)
    elif len(args)==1:
        return toInstruction(args[0])
    else:
        return flFoldl(flMultiply, flMultiply(args[0], args[1]), args[2:])
def flDivide2(*args):
    if len(args)==1:
        return flDivide(1, args[0])
    else:
        return flFoldl(flDivide, flDivide(args[0], args[1]), args[2:])
    return flFoldl(flDivide, flPushInt(1), args)
def flConcat2(*args):
    if len(args)==0:
        return pushStr('')
    elif len(args)==1:
        return toInstruction(args[0])
    else:
        return flFoldl(flConcat, flConcat(args[0], args[1]), args[2:])
def flGreaterEquals(val0, val1):
    """
    (>= A B) ->
      (not (< A B))
    """
    return flNot(flLessThan(val0, val1))
def flLessEquals(val0, val1):
    """
    (<= A B) ->
    (begin
    (set! tmp0 A) (set! tmp1 B)
    (or (< tmp0 tmp1) (= tmp0 tmp1)))
    """
    s = flSetVar('i_tmp_0', val0)
    s.add(flSetVar('i_tmp_1', val1))
    s.add(flOr2(flLessThan(flGetVar('i_tmp_0'), flGetVar('i_tmp_1')),
                flEquals(flGetVar('i_tmp_0'), flGetVar('i_tmp_1'))))
    return s
def flGreaterThan(val0, val1):
    """
    (> A B) ->
    (not (<= tmp0 tmp1))
    """
    s = flNot(flLessEquals(
        val0, val1))
    return s
def flEquals2(*args):
    states = []
    for i in range(len(args)-1):
        states.append(flEquals(args[i], args[i+1]))
    return flAnd2(*states)
def flLessThan2(*args):
    states = []
    for i in range(len(args)-1):
        states.append(flLessThan(args[i], args[i+1]))
    return flAnd2(*states)
def flLessEquals2(*args):
    states = []
    for i in range(len(args)-1):
        states.append(flLessEquals(args[i], args[i+1]))
    return flAnd2(*states)
def flGreaterThan2(*args):
    states = []
    for i in range(len(args)-1):
        states.append(flGreaterThan(args[i], args[i+1]))
    return flAnd2(*states)
def flGreaterEquals2(*args):
    states = []
    for i in range(len(args)-1):
        states.append(flGreaterEquals(args[i], args[i+1]))
    return flAnd2(*states)
def flStrGreaterEquals(val0, val1):
    return flNot(flStrLessThan(val0, val1))
def flStrLessEquals(val0, val1):
    s = flSetVar('i_tmp_0', val0)
    s.add(flSetVar('i_tmp_1', val1))
    s.add(flOr2(flStrLessThan(flGetVar('i_tmp_0'), flGetVar('i_tmp_1')),
                flStrEquals(flGetVar('i_tmp_0'), flGetVar('i_tmp_1'))))
    return s
def flStrGreaterThan(val0, val1):
    s = flNot(flStrLessEquals(
        val0, val1))
    return s
flArrayCnt = 0
def flDefineArray(vals):
    global flArrayCnt
    vname = "ar_"+str(flArrayCnt)
    s = flSetVar(vname+"_len", len(vals))
    for i in range(len(vals)):
        s.add(flSetVar(vname+str(i), vals[i]))
    s.add(flPushStr(vname))
    flArrayCnt += 1
    return s
def flArrayLen(ar):
    return flGetVar(flConcat(ar, '_len'))
def flArrayRef(ar, idx):
    return flGetVar(flConcat(ar, idx))
def flArraySet(ar, idx, val):
    return flSetVar(flConcat(ar, idx), val)
def flArrayAppend(ar, val):
    s = flSetVar('g_tmp', flLenArray(ar))
    s.add(flSetVar(flSetVar(ar,'_len'), flAdd(flGetVar('g_tmp'), 1)))
    s.add(flSetArray(ar, flGetVar('g_tmp'), val))
    return s
flMatrixCnt = 0
def flDefineMatrix(vals):
    global flMatrixCnt
    vname = "mtr_"+str(flMatrixCnt)
    w = max(map(len, vals))
    s = FlasmStmt()
    s.add(setVar(vname + '_h', len(vals)))
    s.add(setVar(vname + '_w', w))
    for y, row in range(len(vals)), vals:
        for x in range(w):
            if x in row:
                s.add(setVar('%s_%s_%s' % [vname, y, x], row[x]))
            else:
                s.add(setVar('%s_%s_%s' % [vname, y, x], 0))
    s.add(flPushStr(vname))
    flMatrixCnt += 1
    return s
def flMatrixHeight(ar):
    return flGetVar(flConcat(ar, '_h'))
def flMatrixWidth(ar):
    return flGetVar(flConcat(ar, '_w'))
def flMatrixRef(ar, x, y):
    name = flFoldl(flConcat, x, ['_', y, '_', ar])
    return flGetVar(name)
def flMatrixSet(ar, x, y, val):
    name = flFoldl(flConcat, x, ['_', y, '_', ar])
    return flSetVar(name, val)
flDictCnt = 0
def flDefineDict(dic):
    global flDictCnt
    vname = 'dic_'+str(flDictCnt)
    s = flSetVar(vname+'_keys', flDefineVector(dic.keys()))
    for k,v in dic:
        s.add(setVar(vname+'_'+str(k), v))
    return s
def flDictKeys(d):
    return flGetVar(flConcat(d, '_keys'))
def flDictRef(d, key):
    return flGetVar(flConcat(flConcat(d, '_'), key))
def flDictSet(d, key, val):
    return flSetVar(flConcat(flConcat(d, '_'), key), val)

ev_press = 0
ev_release = 1
ev_rollout = 2
ev_rollover = 3
ev_keypress = 4
def getStateTransision(ev):
    if ev == ev_press:
        return 'overUpToOverDown'
    elif ev == ev_release:
        return 'overDownToOverUp'
    elif ev == ev_rollout:
        return 'overUpToIdle'
    elif ev == ev_rollover:
        return 'idleToOverUp'
    elif ev == ev_keypress:
        return 'keyPress'
    else:
        raise FlasmException('unknown event')
def flOnPress(code):
    return FlasmHandler(getStateTransision(ev_press), code)
def flOnRelease(code):
    return FlasmHandler(getStateTransision(ev_release), code)
def flOnRollout(code):
    return FlasmHandler(getStateTransision(ev_rollout), code)
def flOnRollover(code):
    return FlasmHandler(getStateTransision(ev_rollover), code)
def flOnKeyPress(key, code):
    return FlasmHandler([getStateTransision(ev_keypress), getKeyName(key)], code)
key_left = 1
key_right = 2
key_enter = 13
key_up = 14
key_down = 15
key_pageup = 16
key_pagedown = 17
keymaps = {
    'left': key_left,
    'right': key_right, 'enter': key_enter,
    'up': key_up, 'down': key_down,
    'pageup': key_pageup, 'pagedown': key_pagedown
}
def getKeyName(key):
    if key in keymaps:
        key = keymaps[key]

    if key == key_left:
        return "_LEFT"
    elif key == key_right:
        return "_RIGHT"
    elif key == key_enter:
        return "_ENTER"
    elif key == key_up:
        return "_UP"
    elif key == key_down:
        return "_DOWN"
    elif key == key_pageup:
        return "_PAGEUP"
    elif key == key_pagedown:
        return "_PAGEDOWN"
    elif isinstance(key, str):
        return "\'%s\'" % key[0]
    else:
        raise FlasmException('unknown key')

#util
class FlasmException(Exception): pass
def toInstruction(name):
    if isinstance(name, FlasmStmt):
        return name
    elif isinstance(name, str):
        return flPushStr(name)
    elif isinstance(name, float):
        return flPushInt(name)
    elif isinstance(name, int):
        return flPushInt(name)
    else:
        raise FlasmException('unknown type:' + str(name.__class__))
def mkstmt(s=None):
    if not s:
        return FlasmStmt(None)
    else:
        return FlasmStmt([s])
def applyn(op, *args):
    s = FlasmStmt([])
    for i in args:
        s.add(toInstruction(i))
    s.add(op)
    return s
