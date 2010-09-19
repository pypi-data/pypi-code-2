from repoze.bfg.configuration import Configurator

def main(global_config, **kw):
    """ This function returns a repoze.bfg.router.Router object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""
    config = Configurator(settings=kw)
    config.begin()
    config.load_zcml()
    config.end()
    return config.make_wsgi_app()

