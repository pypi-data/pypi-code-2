"""
Turns a filename into a list of deserialized items based upon yaml data
"""
import sys
import yaml

def parse(raw_file):
    """
    Given a filename, will load it and attempt to de-serialize the yaml
    therein.

    Also makes sure we have a non-empty list as a result
    """
    data = yaml.load(raw_file.read())
    if not isinstance(data, list):
        raise TypeError('The yaml file *MUST* supply a list of items to be'\
                        ' turned into objects in FluidDB')
    if len(data) > 0:
        return data
    else:
        raise ValueError('No records found')
