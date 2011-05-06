"""
Functions for testing properties of particular reaction networks.

These functions expect an object of class :py:class:`AChemKit.reactionnet.ReactionNetwork`
or subclass or something with an equivalent API. It does not enforce
this however, so you may use custom classes with the same API.

Some of these properties have logical prerequisites, but these are not tested
for explicitly.

Unlike :py:mod:`AChemKit.reactionnet.properties`, the functions here are not boolean, but rather
return grops of things

"""


def find_loops(rn):
    """
    Loops are collections of molecules where a path exists to themselves through linkages of shared
    products and reactants.
    
    For example::
    
        A -> B
        B -> C
        C -> A
    
    """
