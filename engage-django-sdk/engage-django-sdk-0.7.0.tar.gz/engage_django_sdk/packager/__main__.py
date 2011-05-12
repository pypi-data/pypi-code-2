#!/usr/bin/env python
# Django application validation utility
# Copyright 2010 by genForma Corporation

import sys
import traceback
import logging

from __init__ import *

def main(argv):
    try:
        command = command_manager.parse_command_args(argv)
        root_logger = logging.getLogger()
        handler = logging.StreamHandler()
        root_logger.addHandler(handler)
        if verbose:
            root_logger.setLevel(logging.DEBUG)
            handler.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.INFO)
            handler.setLevel(logging.INFO)            
        rc = command.run()
        return rc
    except ValidationError:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, None, file=sys.stderr)
        if command.get_results_file():
            write_json(create_results_json(ARCHIVE_VALIDATION_ERROR_RC, command.get_name(), error_messages=[exc_value],
                                            exception=traceback.format_exception(exc_type, exc_value, exc_traceback)),
                        command.get_results_file())
        return ARCHIVE_VALIDATION_ERROR_RC
    except SystemExit, c:
        sys.exit(c)
    except:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
        if command.get_results_file():
            write_json(create_results_json(UNEXPECTED_EXC_RC, command.get_name(),
                                             exception=traceback.format_exception(exc_type, exc_value, exc_traceback)),
                        command.get_results_file())
        return UNEXPECTED_EXC_RC 


if __name__ == "__main__":
    sys.exit(main(sys.argv))
