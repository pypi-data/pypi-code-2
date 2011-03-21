import functools

def a_log(glog,logsearch,logname,open_func,close_func=None,except_func=None):
    log_func, a_log_func, c_log_func = glog.get_trio_log(logname) 
    if close_func is None:
        close_func = []
    def render(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            if callable(open_func):
                a_log_func(logsearch,open_func(log_func,func,*args,**kwargs))
            else:
                a_log_func(logsearch,open_func)
            try:
                ret = func(*args,**kwargs)
            except Exception,e:
                if except_func:
                    if callable(except_func):
                        logparams = except_func(e,log_func,func,*args,**kwargs)
                    else:
                        logparams = except_func
                else:
                    if not callable(close_func):
                        logparams = close_func
                    else:
                        logparams = []
                c_log_func(logsearch,logparams)
                raise
            else:
                if callable(close_func):
                    logparams = close_func(ret,log_func,func,*args,**kwargs)
                else:
                    logparams = close_func
                c_log_func(logsearch,logparams)
                return ret
        return wrapper
    return render



