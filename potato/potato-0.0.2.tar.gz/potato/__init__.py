import os, imp, re, sys, logging

from identification import class_identifier \
                         , default_validity \
                         , no_validity 

from interface.base.verify import IVerifiable
from interface.user import *

class class_registry(object):
    """
    Class registry so that objects can be loaded dynamically.
    """
    NO_CHECK = -1
    DEFAULT_CHECK = 0

    VALIDITY_CHECK = {}
    VALIDITY_CHECK[NO_CHECK] = no_validity
    VALIDITY_CHECK[DEFAULT_CHECK] = default_validity

    def __init__(self, validity_check_type, log):
        self.logger = log
        self.loaded_classes = {}
        self.loaded_modules = {}
        self.validity_check = self.VALIDITY_CHECK[validity_check_type]
    
    def generate_class_identifiers(self, path, classes):
        log = self.logger
        coll = []
        log.debug("Generating class identifier collection")
        for class_identifier_string in classes.split():
            log.debug("parsing: %s" % (class_identifier_string))
            try:
                name, version_tuple_str = class_identifier_string.split("-")
                major, minor, revision = [int(i) for i in version_tuple_str.split(".")]
                coll.append(class_identifier(path, name, major, minor, revision, self.validity_check))
            except Exception, ex:
                log.error(ex)
        return coll

    def load_classes_from_module(self, path, classes):
        """
        loads the classes from a specific module
        """

        log = self.logger
        loaded_modules = self.loaded_modules
        loaded_classes = self.loaded_classes

        clsids = self.generate_class_identifiers(path, classes)
        log.debug("Reviewing %d class identifier(s)." % (len(clsids)))

        PYTHON_FILE_EXTENSION_PATTERN = "py$"
        is_python_module = re.compile(PYTHON_FILE_EXTENSION_PATTERN, re.I)

        module = None
        module_name = None

        for clsid in clsids:

            if not os.path.exists(clsid.path):
                raise IOError("File does not exist:  %s" % (clsid.path))

            match = is_python_module.search(clsid.path)
            if not match:
                raise Exception("Must be a valid python module with file extension:  py\n\nFile Path:  %s\nFile Pattern: %s" % (clsid.path,PYTHON_FILE_EXTENSION_PATTERN))
            
            # determine what the module name is using the basename.
            module_name = os.path.basename(clsid.path).split(".py")[0]

            if module_name in loaded_modules.keys():
                log.info("Module %s is already loaded." % (clsid.path))            
            else:
                try:
                    log.debug("loading %s from %s" % (module_name, clsid.path))
                    loaded_modules[module_name] = imp.load_source(module_name, clsid.path)
                except:
                    log.error(sys.exc_info())
                    continue

            module = loaded_modules[module_name]

            # load the classes from the module according to what was requested.        
            if clsid.name in loaded_classes.keys():
                log.error("%s cannot be loaded twice." % (name))
                continue

            try:
                cls_factory = getattr(module, clsid.name)
                if clsid.is_valid(clsid, cls_factory, log):
                    loaded_classes[clsid.__name__] = (clsid, cls_factory)
            except:
                log.error(sys.exc_info())

    def instantiate(self, class_name, *args, **kwargs):

        log = self.logger
        loaded_classes = self.loaded_classes
        if class_name not in loaded_classes.keys():
            log.debug(loaded_classes.keys())
            log.error("%s is not in the list of loaded classes:  %s" % (class_name, loaded_classes.keys()))
            return None

        clsid, cls_factory = loaded_classes[class_name]
        inst = cls_factory(*args,**kwargs)
        clsid.is_valid(clsid, inst, log)
        return inst

