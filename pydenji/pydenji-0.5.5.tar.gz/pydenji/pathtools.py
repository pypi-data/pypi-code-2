#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

# todo: handle non-str paths.
import os
import time


# lot of nesting here... can we reduce cyclomatic complexity of this code?
def _appender(pieces, piece):
    if pieces:
        if (pieces[-1].rstrip(os.sep) == piece):
        # don't append /path if /path/ is there.
            return
        if not piece.endswith(os.sep):
            # if there're already other pieces this piece must
            # be a dir; force it with a trailing slash.
            piece += os.sep
    pieces.append(piece)

def get_successive_path_pieces(path, force_absolute=False):
    # this will just support ABSOLUTE paths right now, either
    # passed in as such or forced.
    # think about relative path support.
    pieces = []

    if force_absolute:
        path = os.path.abspath(path)

    if not path.startswith(os.sep):
        raise IOError, "Path '%s' is not absolute and was not forced as such." % path

    parent = path

    while True:
        parent, base = os.path.split(parent)
        if (parent == os.sep):
            piece = parent + base
            _appender(pieces, piece)
            if base == "":
                break
        else:
            # if the former piece is equivalent, just with a trailing slash,
            # don't add another piece.
            piece = parent + os.sep + base
            _appender(pieces, piece)
   

    pieces.reverse()
    return pieces

class NotExistingPath(IOError):
    pass

def verify_path_existence(full_path, on_error_raise=NotExistingPath):
    """
    Verifies that full_path exists. If it doesn't, it throws a proper and clear error that
    helps understanding what's the issue with such path.
    """
    
    # quick bailout
    if os.path.exists(full_path):
        return

    # check why it does not exist.
    path_pieces = get_successive_path_pieces(full_path)

    for piece in path_pieces[:-1]:
        if not os.path.exists(piece):
            raise on_error_raise, "Directory '%s' does not exist while looking for '%s'." % (
                piece, full_path)
        if not os.path.isdir(piece):
            raise on_error_raise, "'%s' is not a directory while looking for '%s'" % (piece,
                full_path)
        if not os.access(piece, os.X_OK):
            raise on_error_raise, "Traversal (x) permission denied on '%s', can't determine '%s' existence" % (
                piece, full_path)

    if not os.path.exists(full_path):
        raise on_error_raise, "'%s' does not exist." % full_path

    # if we get here something is wrong.
    raise AssertionError, "Something is wrong with this function."


