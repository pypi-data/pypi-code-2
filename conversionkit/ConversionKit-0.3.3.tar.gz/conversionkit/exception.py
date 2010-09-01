#
# Exceptions
#

class ConversionKitError(Exception):
    pass

class ConversionError(Exception):
    def __init__(self, message, conversion):
        self.conversion = conversion
        Exception.__init__(self, message)

class APIError(Exception):
    def __init__(self, message, conversion=None):
        self.conversion = conversion
        Exception.__init__(self, message)


