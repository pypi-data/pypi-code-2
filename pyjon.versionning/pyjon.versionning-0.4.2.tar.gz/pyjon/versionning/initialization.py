import os

from mercurial import hg

import logging
logger = logging.getLogger('VERSIONNING')

def init_repository(repo_ui, repo_folder):
    if not os.path.exists(repo_folder):
        os.mkdir(repo_folder)
    if not os.path.isdir(repo_folder):
        raise ValueError('The file %s exists but is not a folder...' % repo_folder)
    
    repository = hg.repository(repo_ui, repo_folder, True)