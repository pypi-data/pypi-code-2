# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, os, sys

from benri.app import WSGIApp
from paste.fileapp import FileApp

class Static(WSGIApp):
    
    def __init__(self, static_path, prefix='/static/'):
        """
        Serve static files under the given prefix.
        
        ``static_path`` - directory where the static files are stored
        """
        join = os.path.join
        
        if not static_path.endswith('/'):
            static_path += '/'
        
        all_files = []
        for dirpath, dirnames, filenames in os.walk(static_path):
            for f in filenames:
                all_files.append(join(dirpath, f).replace(static_path, ''))
                
        self.routes = dict([(join(prefix, f), dict(GET=FileApp(join(static_path, f)))) for f in all_files])
