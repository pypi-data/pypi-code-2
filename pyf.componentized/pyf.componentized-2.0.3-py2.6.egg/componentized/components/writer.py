import datetime
import tempfile
import os
import logging
from pyf.componentized.configuration.keys import SimpleKey
log = logging.getLogger(__name__)

from pyjon.utils import substitute
from pyf.componentized.components.base import Component

class Writer(Component):
    pass

class BaseFileWriter(Writer):
    configuration = [SimpleKey('encoding', default="UTF-8"),
                     SimpleKey('target_filename', label="Target filename")]
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
    
    def prepare_filename(self, base_filename, sample_item=None, **kwargs):
        target_filename = datetime.datetime.strftime(datetime.datetime.now(),
                                                     base_filename)

        def my_getter(attribute):
            if attribute in kwargs:
                return kwargs.get(attribute)
            else:
                return getattr(sample_item, attribute, None)

        target_filename = substitute(target_filename,
                                     lambda x: my_getter(x) is not None and my_getter(x) or "##%s##" % x,
                                     regex=r"##([^#]+?)##")
        target_filename = substitute(target_filename, self.get_config_key)
        
        return target_filename
    
class FileWriter(BaseFileWriter):
    gets_filename = True
    
    def __init__(self, config_node, name, target_filename):
        self.name = name
        self.config_node = config_node
        self.target_filename = target_filename
