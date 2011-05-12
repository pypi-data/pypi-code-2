"""Tracking and representation of settings validation results"""

import json

# Return codes
SUCCESS_RC                   = 0
SETTINGS_VALIDATION_ERROR_RC = 1
ARG_PARSE_ERROR_RC           = 2
ARCHIVE_VALIDATION_ERROR_RC  = 3
UNEXPECTED_EXC_RC            = 4
INTERNAL_ERROR_RC            = 5

_rc_descriptions = {
    SUCCESS_RC: "Success",
    SETTINGS_VALIDATION_ERROR_RC: "Settings Validation Errors",
    ARG_PARSE_ERROR_RC: "Command Line Agument Error",
    ARCHIVE_VALIDATION_ERROR_RC: "Archive Validation Error",
    UNEXPECTED_EXC_RC: "Unexpected Exception",
    INTERNAL_ERROR_RC: "InternalError"
}

class ResultsBase(object):
    def __init__(self, version, error_messages=None, warning_messages=None,
                 exception=None):
        self.version = version
        if error_messages:
            self.error_messages = error_messages
        else:
            self.error_messages = []
        if warning_messages:
            self.warning_messages = warning_messages
        else:
            self.warning_messages = []
        self.exception = exception

    def get_return_code(self):
        pass

    def get_return_code_desc(self):
        if _rc_descriptions.has_key(self.get_return_code()):
            return  _rc_descriptions[self.get_return_code()]
        else:
            return "Unexpected Return Code"
        
    def to_json(self):
        js = { u"validator_version":self.version,
               u"return_code": self.get_return_code(),
               u"return_code_desc": self.get_return_code_desc(),
               u"error_messages": self.error_messages,
               u"warning_messages": self.warning_messages,
               u"exception": self.exception }
        return js


class ParsedJsonResults(ResultsBase):
    """This object represents the results file after it has been
    read back in and parsed. Most of the work is done in the __init__
    function which converts from a dictionary to object fields.
    """
    def __init__(self, json_obj):
        try:
            if not type(json_obj)==dict:
                raise Exception("Invalid content in results file, data was %s" %
                                json_obj.__repr__())
            props = [u"return_code", u"return_code_desc",
                     u"validator_version", u"error_messages",
                     u"warning_messages", u"exception"]
            for prop in props:
                if not json_obj.has_key(prop):
                    raise Exception("Invalid results file, missing property %s" %
                                    prop)
            ResultsBase.__init__(self,
                                 json_obj[u"validator_version"],
                                 json_obj[u"error_messages"],
                                 json_obj[u"warning_messages"],
                                 json_obj[u"exception"])
            self.return_code = json_obj[u"return_code"]
            self.return_code_desc = json_obj[u"return_code_desc"]
        except Exception, v:
            ResultsBase.__init__(self, "Unknown", [ v ], [])
            self.return_code = INTERNAL_ERROR_RC
            self.return_code_desc = _rc_descriptions[INTERNAL_ERROR_RC]

    def get_return_code(self):
        return self.return_code
    
    def run_was_successful(self):
        return self.return_code == SUCCESS_RC
    
    def get_return_code_desc(self):
        return self.return_code_desc

    def get_validator_version(self):
        return self.validator_version

    def has_error_messages(self):
        return len(self.error_messages) > 0

    def get_error_messages(self):
        return self.error_messages

    def has_warning_messages(self):
        return len(self.warning_messages) > 0

    def get_warning_messages(self):
        return self.warning_messages

    def format_messages(self):
        s = ""
        if self.has_error_messages():
            s += "Errors:\n"
            for i in range(1, len(self.error_messages)+1):
                s += "  [%02d] %s\n" % (i, self.error_messages[i-1])
        else:
            s += "Errors: None\n"
        if self.has_warning_messages():
            s += "Warnings:\n"
            for i in range(1, len(self.warning_messages)+1):
                s += "  [%02d] %s\n" % (i, self.warning_messages[i-1])
        else:
            s += "Warnings: None\n"
        return s

    def has_exception(self):
        return self.exception


class SettingValidationResults(ResultsBase):
    """This class is used for tracking the progress of the settings validation tests.
    """
    def __init__(self, version, logger):
        ResultsBase.__init__(self, version)
        self.logger = logger
        self.product = None
        self.product_version = None
        self.python_path_subdirectory = None
        self.installed_apps = None
        self.fixtures = None
        self.migration_apps = None
        self.errors = 0
        self.warnings = 0

    def error(self, msg):
        self.errors += 1
        self.error_messages.append(msg)
        self.logger.error("ERROR: " + msg + "\n")

    def warning(self, msg):
        self.warnings += 1
        self.warning_messages.append(msg)
        self.logger.warn("WARNING: " + msg + "\n")

    def has_errors(self):
        return self.errors > 0

    def has_warnings(self):
        return self.warnings > 0

    def all_checks_passed(self):
        return (self.errors == 0) and (self.warnings == 0)

    def print_final_status_message(self, logger):
        if self.all_checks_passed():
            self.logger.info("All settings checks passed\n")
        else:
            self.logger.error("%d errors, %d warnings in settings validation.\n" %
                              (self.errors, self.warnings))
        
    def get_return_code(self):
        if self.has_errors(): return SETTINGS_VALIDATION_ERROR_RC
        else: return SUCCESS_RC # if we get warnings but not errors, still return ok
