"""
PyFactory is a model factory library.
"""

# Bring these in so they can be imported directly from the package
from error import InvalidModelBuilderError
from factory import Factory
from field import Field, association
from schema import schema

__version__ = '0.1.0'
"""The PyFactory version installed."""
