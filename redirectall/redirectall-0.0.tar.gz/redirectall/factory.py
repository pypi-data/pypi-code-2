from dispatcher import RedirectAll

def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""
    keystr = 'redirectall.'
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    return RedirectAll(**args)
    
