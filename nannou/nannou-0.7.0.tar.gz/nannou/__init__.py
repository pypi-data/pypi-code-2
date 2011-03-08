# -*- coding: utf-8 -*-
#
# Nannou - pattern matching template engine
#
# Портированный с яваскирпта шаблонизатор. К сожалению питон не придал
# ему изящности
#

import re

runtime = """
import pprint

class TemplateMatchError(Exception):
    \"\"\" Ошибка, возникающая когда шаблонизатор не может найти
    подходящий паттерн для данных \"\"\"
    def __init__(self, value):
        self.value = value
    def __str__(self):
         return pprint.pformat(self.value)
    def __unicode__(self):
         return pprint.pformat(self.value)

def __me(data, sep='\\n', lvl=-1):

    lvl += 1

    def arr(val):
        if type(val) <> type([]):
            return [val]
        return val

    def out(*args): return ''.join(args).strip()

    def maybe(acondb, els=[]):
        if acondb[1]:
            return ''.join(acondb)
        else:
            return ''.join(els)

    def f(obj):
        if type(obj) <> type({}):
            return unicode(obj)
%s
        else:
            raise TemplateMatchError(obj)

    if data == None:
        return data

    return sep.join(map(f, arr(data))).\\
        replace('\\n', '\\n'+(' '*3*lvl))
"""

def compile(template, rtl={}, debug=False):
    """ Конструктор шаблонизатора """

    fun = '__me'

    def toIfClause(rawCond):
        """ Парсит строку паттерна в тупл вида

        ([ключ1, ключ2], гвард)"""
        try:
            keys, guard = rawCond.split('|', 1)
        except ValueError:
            keys, guard = rawCond, None
        keyList = map(lambda x: x.strip() or None, keys.split(' '))
        return keyList, guard

    def toStringPipe(rawString):
        """ Парсит значение """
        def clean(code):
            return code.replace("\n",'\\n')

        def processExpr(m):
            """ Обрабатывает выражения в процентных скобках

            (<%some|expr%>)

            TODO: Описать синтаксис этих выражений"""
            fieldsRaw, kind, etc, sep = m.group(1), m.group(3), \
                m.group(4), m.group(6) or ''
            if sep:
                sep = 'sep="%s", ' % sep
            else:
                sep = ''
            fields = ', '.join(map(lambda x:"arr(obj.get('%s',''))" % x.strip(),\
                             fieldsRaw.split(',')))
            templ = '", %s(%%s, %s lvl=lvl), "' % (fun, sep)
            if kind == '|':
                return templ % ('map(%s, %s)' % (etc, fields))
            elif kind == '!':
                return templ % ('%s(%s)' % (etc, fields))
            elif kind == '.':
                return templ % ('map(lambda x:x.%s, %s)' % (etc, fields))
            else:
                return templ % fields

        def unfold(code):
            """ Метапрограммирует

            TODO: Как?"""
            unfVals = re.sub(
                r'<%\s*([,\w]+)\s*((\S)\s*(\w+)\s*)?(::(.*?))?%>',
                processExpr,
                code)
            unfBlocks = unfVals.\
                replace('<?', '", maybe(["<').\
                replace('?>', '>"]), "').\
                replace('>||<', '>"], ["<').\
                replace('\\?', '?')
            return 'return out("' + unfBlocks + '")'

        return clean(unfold(rawString.replace('"', '\\"')))

    def assemble(pmlist):
        """ Собирает шаблон 

        TODO: Обрабатывать гварды нормально, сейчас они - глючное
        неработающее говно"""
        out = ''
        for pm in pmlist:
            conds = []
            try:
                (keys, guard), matchee = pm
            except TypeError:
                continue
            for k in keys:
                if k:
                    conds.append("'%s' in obj" % k)
            if guard:
                conds.append(guard)
            out += '\t\telif %s:\n\t\t\t%s\n' % (' and '.join(conds), matchee)
        return runtime % out.replace('\t', '    ')

    def split2(pm):
        """ Разрезает цепочки 'a b ccc --> data <%data%> ' и парсит
        получившееся в тупл (паттерн, значение). """
        try:
            pattern, matchee = pm.split('-->')
        except ValueError:
            return None
        return (
            toIfClause(pattern),
            toStringPipe(matchee))

    def patternCmp(x, y):
        """ Критерий сортировки паттернов. Так как паттерн
        представляет собой список ключей разделенных пробелами,
        очевидно, более частные паттерны (они должны следовать
        впереди) будут иметь большую длину.
        """
        def norm(p): 
            return len(', '.join(map(lambda x: x or '', p)))
        if x == None or y == None:
            return 0
        return norm(y[0][0]) - norm(x[0][0])

    # Парсим и сортируем. Сортируем, чтобы избавиться от коллизий
    userconds = sorted(map(split2, template.split('<!--/')), \
                           cmp = patternCmp)

    exec(assemble(userconds)) in rtl, rtl
    if debug:
         return rtl[fun], assemble(userconds)
    return rtl[fun]
    
