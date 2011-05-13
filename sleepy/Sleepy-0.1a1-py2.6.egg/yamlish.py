import yaml
ConstructorError = yaml.constructor.ConstructorError

from sleepy.util import OrderedDict
from sleepy.shorties import s

def construct_odict( load,
                     node ):
    """from http://gist.github.com/317164

    >>> yaml.load( '''
    ... !!omap
    ... - foo: bar
    ... - mumble: quux
    ... - baz: gorp
    ... ''' )
    OrderedDict([('foo', 'bar'), ('mumble', 'quux'), ('baz', 'gorp')])

    >>> yaml.load( '''!!omap [ foo: bar, mumble: quux, baz: gorp ]''' )
    OrderedDict([('foo', 'bar'), ('mumble', 'quux'), ('baz', 'gorp')])
    """

    omap = OrderedDict()
    yield omap
    if not isinstance( node,
                       yaml.SequenceNode ):
        raise ConstructorError( "while constructing an ordered map",
                                node.start_mark,
                                s( "expected a sequence, but found {{ n.id }}",
                                   n=node ),
                                node.start_mark )
    for subnode in node.value:
        if not isinstance( subnode,
                           yaml.MappingNode ):
            raise ConstructorError( "while constructing an ordered map",
                                    node.start_mark,
                                    s( "expected a mapping of length 1, "
                                        "but found {{ s.id }}",
                                       s=subnode ),
                                    subnode.start_mark )
        if len( subnode.value ) != 1:
            raise ConstructorError( "while constructing an ordered map",
                                    node.start_mark,
                                    s( "expected a single mapping item, "
                                        "but found {{ num }} items",
                                       num=len( subnode.value )),
                                    subnode.start_mark )
        key_node, value_node = subnode.value[ 0 ]
        key = load.construct_object( key_node )
        value = load.construct_object( value_node )
        omap[ key ] = value

yaml.add_constructor( u"tag:yaml.org,2002:omap",
                      construct_odict )

def repr_odict( dumper,
                data ):
    """
#    >>> yaml.dump( data,
#    ...            default_flow_style=True )
#    '!!omap [foo: bar, mumble: quux, baz: gorp]\\n'

    >>> data = OrderedDict( [ ( "foo",
    ...                         "bar" ),
    ...                       ( "mumble",
    ...                         "quux" ),
    ...                       ( "baz",
    ...                         "gorp" ) ] )
    >>> yaml.dump( data,
    ...            default_flow_style=False )
    '!!omap\\n- foo: bar\\n- mumble: quux\\n- baz: gorp\\n'
    """
    return repr_pairs( dumper,
                       u"tag:yaml.org,2002:omap",
                       data.iteritems())

yaml.add_representer( OrderedDict,
                      repr_odict )

def repr_pairs( dump,
                tag,
                sequence,
                flow_style=None ):
    value = []
    node = yaml.SequenceNode( tag,
                              value,
                              flow_style=flow_style )
    if dump.alias_key is not None:
        dump.represented_objects[ dump.alias_key ] = node
    best_style = True
    for ( key,
          val ) in sequence:
        item = dump.represent_data( { key: val } )
        if not ( isinstance( item,
                             yaml.ScalarNode )
                  and not item.style ):
            best_style = False
        value.append( item )
    if flow_style is None:
        if dump.default_flow_style is not None:
            node.flow_style = dump.default_flow_style
        else:
            node.flow_style = best_style
    return node

if __name__ == "__main__":
    import doctest
    doctest.testmod()
