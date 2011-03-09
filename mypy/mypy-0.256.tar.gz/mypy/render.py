from mypyconfig import LOOKUP, FUNC_MODULE_PREFIX_LEN, LOCAL
from types import FunctionType
from byteplay import Code, opmap
import inspect

from decorator import decorator

from hmako.template import Template
import hmako.lookup


class Render(object):
    __lookup = hmako.lookup.TemplateLookup(**LOOKUP)

    def __init__(self, template=None):
        self.__template = template

    def __getattr__(self, name):
        return None

    def __call__(self, **kwds):
        return self.__lookup.get_template(self.__template).render(G=self, **kwds)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def __getitem__(self, name):
        return getattr(self, name)


def get_request():
    return LOCAL.request

def _transmute(opcode, arg):
    if (
        (opcode==opmap['LOAD_GLOBAL']) and
        (arg=='G' or arg=='request')
    ):
        return opmap['LOAD_FAST'], arg
    return opcode, arg

def render_para_func(func):
    code = Code.from_code(func.func_code)
    code.args = tuple(['request', 'G'] + list(code.args))
    code.code = [_transmute(op, arg) for op, arg in code.code]
    func.func_code = code.to_code()
    return func


def render_func(func):
    if type(func) is str:
        return lambda f:_render_func(f, func)
    else:
        template = "/%s/%s.htm"%(
            func.__module__[FUNC_MODULE_PREFIX_LEN:].replace(".", "/"),
            func.__name__
        )
        return _render_func(func, template)

def _render_func(func, template):
    if not template.startswith("/"):
        template = "%s/%s"%(
            func.__module__[FUNC_MODULE_PREFIX_LEN:].replace(".", "/"),
            template
        )
    def  _wrap_func(func, *args, **kwds):
        G = Render(template)
        request = get_request()
        r = func(request, G, *args, **kwds)

        if type(r) is str:
            return r
        elif r is False:
            return ''
        else:
            return G(request=request)

    f = decorator(_wrap_func, func)

    func = render_para_func(func)

    return f


def render_doc(func):
    template = Template(
        func.__doc__,
        input_encoding='utf-8',
        output_encoding='utf-8',
        disable_unicode=True,
        default_filters=['str', 'h']
    )

    arg_names, varargs, varkw, defaults = inspect.getargspec(func)

    if varargs or varkw:
        raise Exception("do not support varargs")

    defaults = defaults or {}
    if defaults:
        a = dict(zip(arg_names[-len(defaults):], defaults))
    else:
        a = {}

    def _func(func, *args, **kwds):
        aa = a.copy()
        aa.update(zip(arg_names, args))
        aa.update(kwds)

        request = get_request()
        G = Render()

        r = func(request, G, **aa)


        if type(r) is str:
            return r
        else:
            #print aa
            return template.render(G=G, request=request, **aa)

    f = decorator(_func, func)

    func = render_para_func(func)

    return f

if __name__ == "__main__":

    @render_doc
    def test():
        """
        my name is ${G.x}
        request is ${request}
        %if G.not_existxxxx:
        xxx
        %else:
            ${G.not_existxxxx}
        %endif
        """
        G.x = "zsp<"

    print test()
