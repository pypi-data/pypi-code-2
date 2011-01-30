# -*- coding:utf-8 -*-
#
# kurzfile/constants.py
#
"""Utility functions for the kurzfile package."""

__all__ = [
    'display_size',
    'xlate_object_id'
]

def xlate_object_id(type, id):
    """Translates a raw object ID into the number displayed in object tables.

    IDs (decimal values):

    Tables:

    ID      Table Type
    ------------------
    16      Master
    35      Macro
    36      Names
    37      Faders

    Intonation tables, velocity maps, pressure maps, QA-banks, songs:

    Raw ID       Display ID
    -----------------------
    1-75         1-75
    76-95        100-119
    96-115       200-219
    116-135      300-319
    136-155      400-419
    156-175      500-519
    176-195      600-619
    196-215      700-719
    216-235      800-819
    236-255      900-919

    Effects:

    Raw ID       Display ID
    -----------------------
    1-37         1-37
    38-47        100-109
    48-57        200-209
    58-67        300-309
    68-77        400-409
    78-87        500-509
    88-97        600-609
    98-107       700-709
    108-117      800-809
    118-127      900-909

    """
    if type == 100:
        # tables
        return id
    elif type == 113:
        # effects
        if 1 <= id <= 37:
            return id
        bank = (id - 37) / 10 + 1
        return bank * 100 + ((id - 37) % 10 - 1)
    elif type < 0x90:
        # other tables & maps, qa-banks, songs
        if 1 <= id <= 75:
            return id
        bank = (id - 75) / 20 + 1
        return bank * 100 + ((id - 75) % 20 -1)
    # all other object types
    return id

def display_size(bytes):
    """Display a size in bytes in human-readable format."""
    if bytes < 1024:
        return "%i bytes" % bytes
    elif bytes < 1024*10:
        return "%.1f KiB" % (bytes / 1024.)
    elif bytes < 1024*1024:
        return "%i KiB" % (bytes // 1024)
    else:
        return "%.1f MiB" % (bytes / (1024*1024))
