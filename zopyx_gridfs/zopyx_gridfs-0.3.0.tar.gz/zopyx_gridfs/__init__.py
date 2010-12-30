from pyramid.config import Configurator
from zopyx_gridfs.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    zcml_file = settings.get('configure_zcml', 'configure.zcml')
    config = Configurator(root_factory=Root, settings=settings)
    config.add_route('gridfs_upload_form', '/{collection}/upload_form')
    config.add_route('gridfs_upload_action', '/{collection}/upload_action')
    config.add_route('gridfs', '/{collection}/{filename}')
    config.load_zcml(zcml_file)
    return config.make_wsgi_app()

