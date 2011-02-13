def tuple_args((a, (b,))):
    return a, b

def default_tuple_args((a, (b,))=(1, (2,))):
    pass

def all_args(a, (b, (c,)), d=0, (e, (f,))=(4, (5,)), *g, **h):
    return a, b, c, d, e, f, g, h
