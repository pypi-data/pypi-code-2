# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# Graph-exceptions
class GraphAlreadyExists(Exception): pass
class GraphNotFound(Exception): pass

# collection-exceptions
class CollectionAlreadyExists(Exception): pass
class NotACollection(Exception): pass
class CollectionNotFound(Exception): pass

# group
class GroupAlreadyExists(Exception): pass
class GroupNotFound(Exception): pass

# Security exceptions
class Unauthorized(Exception): pass
