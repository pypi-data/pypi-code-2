from itertools import chain

def merge( *feeds ):
    return sorted( chain( *feeds ),
                   key=lambda entry:
                        getattr( entry,
                                 getattr( entry,
                                          "sort_key",
                                          None )
                                  or "published" ),
                   reverse=True )
