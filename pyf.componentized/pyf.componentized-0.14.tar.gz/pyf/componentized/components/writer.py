import datetime
import tempfile
import os
import logging
log = logging.getLogger(__name__)

from pyf.componentized.components.base import Component

class Writer(Component):
    pass

class BaseFileWriter(Writer):
    def __init__(self, config_node, name):
        self.name = name
        self.config_node = config_node

    def get_secure_filename(self):
        """OBSOLETE: creates a tempfile in the most secure manner possible,
        make sure is it closed and return the filename for
        easy usage.
        """
        log.warning("DeprecationWarning: this method is deprecated and "   + \
                "should not be used anymore as it will be removed in the " + \
                "future. Instead, use pyjon.utils.get_secure_filename")

        from pyjon.utils import get_secure_filename
        return get_secure_filename()
    
    def prepare_filename(self, base_filename, **kwargs):
        target_filename = datetime.datetime.strftime(datetime.datetime.now(),
                                                     base_filename)
        for key, value in kwargs.iteritems():
            if not isinstance(value, unicode) and not isinstance(value, str):
                value = repr(value)
                
            target_filename = target_filename.replace('##%s##' % key, value)
        
        return target_filename
    
class FileWriter(BaseFileWriter):
    gets_filename = True
    
    def __init__(self, config_node, name, target_filename):
        self.name = name
        self.config_node = config_node
        self.target_filename = target_filename
