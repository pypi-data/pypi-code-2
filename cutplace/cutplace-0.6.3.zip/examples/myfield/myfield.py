import logging

from cutplace import data
from cutplace import fields
from cutplace import interface

class ColorFieldFormat(fields.AbstractFieldFormat):
    def __init__(self, fieldName, isAllowedToBeEmpty, length, rule, dataFormat):
        super(ColorFieldFormat, self).__init__(fieldName, isAllowedToBeEmpty, length, rule, dataFormat,
                emptyValue=(0.0, 0.0, 0.0)) # Use black as "empty" color.

    def validatedValue(self, value):
        # (Exactly same as before)
        assert value
        if value == "red":
            result = (1.0, 0.0, 0.0)
        elif value == "green":
            result = (0.0, 1.0, 0.0)
        elif value == "green":
            result = (0.0, 1.0, 0.0)
        else:
            raise fields.FieldValueError("color value is %r but must be one of: red, green, blue" % value)
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

