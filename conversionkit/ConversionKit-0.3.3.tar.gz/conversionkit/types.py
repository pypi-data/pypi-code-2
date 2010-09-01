def isInteger():
    def isInteger_converter(conversion, state=None):
        if isinstance(conversion.value, int):
            conversion.result = conversion.value
        else:
            conversion.error = 'The value is not an integer'
    return isInteger_converter

