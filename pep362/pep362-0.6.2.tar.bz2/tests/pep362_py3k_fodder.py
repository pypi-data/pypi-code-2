def keyword_only(*, a):
    pass

def keyword_only_default(*, a=42):
    pass

def arg_annotation(a:int):
    pass

def arg_annotation_default(a:int=42):
    pass

def arg_annotation_var(*args:int, **kwargs:str):
    pass

def arg_annotation_keyword_only(*, a:int):
    pass

def return_annotation() -> int:
    pass

def all_args(a:int, d=0, *args:int,
                g:int, h:int=8, **kwargs:int) -> int:
    return a, d, g, h, args, kwargs
