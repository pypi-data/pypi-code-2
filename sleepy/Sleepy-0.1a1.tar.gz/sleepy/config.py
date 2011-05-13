from os.path import dirname, abspath, join

import yaml
loader = yaml.load

from sleepy.shorties import s
from sleepy.exceptions import NotFoundException

def tipes_load_dir():
    return join( dirname( abspath( __file__ )),
                 "yaml",
                 "tipes" )

def loaded_tipe_node( tipe ):
    try:
        return loader( open( join( tipes_load_dir(),
                                   s( "{{ tipename }}.yaml",
                                      tipename=tipe.__class__
                                                   .__name__
                                                   .lower())))
                           .read())
    except IOError:
        raise NotFoundException()

def static_dir():
    return join( dirname( abspath( __file__ )),
                 "static" )

def templates_dir():
    return join( dirname( abspath( __file__ )),
                 "templates" )
