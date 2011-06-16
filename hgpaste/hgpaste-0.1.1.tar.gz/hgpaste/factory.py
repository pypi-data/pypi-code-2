__all__ = ['wsgi_app', 'make_app']

def wsgi_app(config_file):
    """wsgi application"""
    from mercurial import demandimport; demandimport.enable()
    from mercurial.hgweb.hgwebdir_mod import hgwebdir
    application = hgwebdir(config_file)
    return application    

def make_app(global_conf, config_file):
    """make an app for paster"""
    return wsgi_app(config_file)
