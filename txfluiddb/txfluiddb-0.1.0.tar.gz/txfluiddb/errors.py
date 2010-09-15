"""
Exception classes used in txFluidDB.
"""
class InvalidName(ValueError):
    """
    An invalid name was used in a path.
    """

class InvalidTagValueType(ValueError):
    """
    An attempt was made to set a tag value using a Python value of
    unsupported type.
    """
