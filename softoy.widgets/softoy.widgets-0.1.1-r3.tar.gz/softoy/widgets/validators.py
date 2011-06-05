# -*- coding: utf-8 -*-
from formencode.validators import FancyValidator

# currency converter - number to unicode string that has commas
def comma3(n):
    s = str(n)
    sl = list(s)
    L = []
    cnt = 0
    while sl:
        L.append(sl.pop())
        cnt += 1
        if cnt % 3 == 0:
            L.append(',')
    if L[-1] == ',':
        L.pop()
    L.reverse()
    return u''.join(L)


class Currency(FancyValidator):
    def empty_proc(self, s):
        if len(s) == 0:
            if hasattr(self, 'not_empty') and self.not_empty:
                raise Invalid('Pease input a value')
            else:
                return True
        return True
    def _to_python(self, value, state):
        vs = value.strip()
        self.empty_proc(vs)
        if match_u(currency_pattern, vs) is None:
            raise Invalid(u'Not currency format', vs, state)
        else:
            try:
                vsr = vs.replace(',', '')
                self.empty_proc(vsr)
                return int(vsr)
            except:
                raise Invalid('Not integer', vs, state)

    def _from_python(self, value, state):
        return comma3(value)

