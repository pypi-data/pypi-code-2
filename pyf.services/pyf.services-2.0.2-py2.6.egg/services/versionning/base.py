from tg import config

from pyf.services.model import Tube, TubeLayer, Descriptor, DBSession

from pyjon.versionning import SARepository

def get_repo_folder():
    return config.get('versionning.repository', './repo')

def get_repository():
    return SARepository(get_repo_folder(), DBSession, [Tube,
                                                       TubeLayer,
                                                       Descriptor])