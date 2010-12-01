import logging

from spitter import models

import sqlalchemy as sqla
from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.configuration import Configurator
from pyramid_jinja2 import renderer_factory
from repoze import tm
from sqlalchemy import orm
from werkzeug import script
from werkzeug import serving


DEFAULT_CONNECT_STRING = 'sqlite:///spitter.db'

def init_settings(settings={}):
    settings = dict(settings)
    settings.setdefault('jinja2.directories', 'spitter:templates')
    settings.setdefault('reload_templates', True)
    settings.setdefault('spitter.db_connect_string', DEFAULT_CONNECT_STRING)

    settings['spitter.db_engine'] = sqla.create_engine(settings['spitter.db_connect_string'])
    settings['spitter.db_session_factory'] = orm.sessionmaker(bind=settings['spitter.db_engine'],
                                                              autocommit=False,
                                                              autoflush=False,
                                                              extension=ZopeTransactionExtension())
    return settings

def make_app(settings={}):
    """ This function returns a WSGI application.
    """

    settings = init_settings(settings)

    authentication_policy = AuthTktAuthenticationPolicy('oursecret',
                                                        callback=models.groupfinder)
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=models.get_root,
                          settings=settings,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy)
    config.add_renderer('.html', renderer_factory)
    config.add_static_view('static', 'spitter:static')
    config.scan('spitter')

    rootapp = config.make_wsgi_app()
    app = tm.TM(rootapp)

    return app

def init_logging(verbosity):
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    if verbosity >= 1:
        logging.getLogger('werkzeug').setLevel(logging.INFO)
    if verbosity >= 2:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    if verbosity >= 3:
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.INFO)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
        logging.getLogger('sqlalchemy.orm').setLevel(logging.INFO)
    if verbosity >= 4:
        logging.getLogger('werkzeug').setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy.orm').setLevel(logging.DEBUG)


def main():

    def action_runserver(hostname=('h', '0.0.0.0'), port=('p', 8080),
                         debug=('d', False), verbosity=('v', 0)):
        '''Run the development server.

        :param verbosity: increase level of logging for more verbose logging
        '''
 
        logging.basicConfig()
        init_logging(verbosity)

        serving.run_simple(hostname, port, make_app(),
                           use_reloader=debug,
                           use_debugger=debug,
                           use_evalex=debug)

    def action_syncdb():
        settings = init_settings()
        models.Base.metadata.create_all(settings['spitter.db_engine'])

    script.run()


if __name__ == '__main__':
    main()
