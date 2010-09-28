from Products.PluginIndexes.DateRangeIndex.DateRangeIndex import DateRangeIndex

from types import IntType, TupleType
from BTrees.IIBTree import IISet
import BTrees.Length


def _insertForwardIndexEntry( self, since, until, documentId ):
    """
        Insert 'documentId' into the appropriate set based on
        'datum'.
    """
    if since is None and until is None:
         self._always.insert( documentId )
    elif since is None:
        set = self._until_only.get( until, None )
        if set is None:
            self._until_only[ until ] = documentId
        else:
            if type(set) == IntType:
                set = self._until_only[ until ] = IISet((set, documentId))
            else:
                set.insert( documentId )
    elif until is None:
        set = self._since_only.get( since, None )
        if set is None:
            self._since_only[ since ] = documentId
        else:
            if type(set) == IntType:
                set = self._since_only[ since ] = IISet((set, documentId))
            else:
                set.insert( documentId )

    else:

        set = self._since.get( since, None )
        if set is None:
            self._since[ since ] = documentId
        else:
            if type(set) == IntType:
                set = self._since[ since ] = IISet((set, documentId))
            else:              
                set.insert( documentId )

        set = self._until.get( until, None )
        if set is None:
            self._until[ until ] = documentId
        else:
            if type(set) == IntType:
                set = self._until[ until ] = IISet((set, documentId))
            else:
                set.insert( documentId )

def _removeForwardIndexEntry( self, since, until, documentId ):
    """
        Remove 'documentId' from the appropriate set based on
        'datum'.
    """
    if since is None and until is None:

        self._always.remove( documentId )

    elif since is None:

        set = self._until_only.get( until, None )
        if set is not None:

            if type(set) == IntType:
                del self._until_only[until]
            else:
                set.remove( documentId )

                if not set:
                    del self._until_only[ until ]

    elif until is None:

        set = self._since_only.get( since, None )
        if set is not None:

            if type(set) == IntType:
                del self._since_only[ since ]
            else:
                set.remove( documentId )

                if not set:
                    del self._since_only[ since ]

    else:

        set = self._since.get( since, None )
        if set is not None:

            if type(set) == IntType:
                del self._since[ since ]
            else:
                set.remove( documentId )

                if not set:
                    del self._since[ since ]

        set = self._until.get( until, None )
        if set is not None:

            if type(set) == IntType:
                del self._until[ until ]
            else:
                set.remove( documentId )

                if not set:
                    del self._until[ until ]

def applyPatch():
    """ apply the monkey patch """
    DateRangeIndex._insertForwardIndexEntry = _insertForwardIndexEntry
    DateRangeIndex._removeForwardIndexEntry = _removeForwardIndexEntry
