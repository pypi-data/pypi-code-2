"""\
Simple helper functions for performing basic database tasks 
with DB-API 2.0 compliant connections.
"""

from databasepipe.helper import plugin
from bn import AttributeDict

def dict_fetchall(cursor):
    rows = cursor.fetchall()
    res = []
    for row in rows:
        if AttributeDict is not None:
            dictionary = AttributeDict()
        else:
            dictionary = {}
        for i in range(len(row)):
            dictionary[cursor.description[i][0]] = row[i]
        res.append(dictionary)
    return res

param_style_converters = {
    'qmark': '?'
}
def substitute_param_style(sql, param_style):
    if param_style == 'format':
        pass
    elif param_style == 'qmark':
        parts = sql.split('%%s')
        res = []
        ps = param_style_converters[param_style]
        for part in parts:
            res.append(part.replace('%s', ps))
        sql = '%s'.join(res) 
    else:
        raise Exception('Unsupported param_style %r'%(param_style,))
    return sql

def query(
    connection, 
    sql, 
    values=(), 
    format='dict', 
    fetch=True, 
    substitute=True, 
    param_style='format',
):
    '''\
    Execute ``sql`` using a cursor obtained from ``connection``. Any ``%s``
    characters in the SQL string are substituted with the values in ``values`` in a
    safe way helping you to avoid SQL injection attacks. If you need a literal
    ``%s`` in the SQL, you write it as ``%%s``. The SQL is translated to use the
    correct param_style for the underlying database which you specify as the
    ``param_style`` argument. This allows you to use ``%s`` for all SQL statements.
    To avoid this substitution you can set ``substitute`` to ``False``.
    
    If ``fetch`` is ``True`` (the default), the results from executing the query
    are returned. This is usually what you want for ``SELECT`` statements but
    probably not what you want for ``INSERT``, ``UPDATE`` or ``DELETE`` statements.
    By default the results are returned as a list of dictionaries where the keys in
    the dictionaries are the column names and the values are the values from that
    row. If you have the BareNecessities package installed the results are returned
    as a list of ``bn.AttributeDict`` objects which are like dictionaries but which
    also allow attribute access to any keys which are also valid Python names. You
    can specify ``format='list'`` to have the results returned in the format used
    by DB-API 2.0 cursor (usually a tuple of tuples).

    Here's a simple example:

    ::

        >>> rows = query(
        ...     connection,
        ...     """
        ...     SELECT 
        ...         name
        ...       , age
        ...     FROM 
        ...         person
        ...     WHERE
        ...         name=%s     
        ...     """,
        ...     (u'James',)
        ... )
        >>> print rows[0]['name']
        u'James' 
 
    .. note :: 

        When specifying values they should always be specified as a
        tuple. When using a tuple with a single value in Python you must always have a
        trailing comma so that the brackets are treated as a tuple.

    '''
    if substitute:
        sql = substitute_param_style(sql, param_style)
    cursor = connection.cursor()
    cursor.execute(sql, values)
    if fetch:
        if format == 'list':
            rows = cursor.fetchall()
        elif format == 'dict':
            rows = dict_fetchall(cursor)
        else:
            raise Exception('Unrecognised cursor fetch format %s'%(format))
    else:
        rows = []
    cursor.close()
    return rows

def update_record(
    connection, 
    table_name, 
    primary_key_column_name, 
    primary_key_value, 
    data_dict, 
    substitute=True, 
    param_style='format',
):
    '''\
    Update a single row in a table identified by a primary key. For more
    complex update operations use ``query()`` and write the required SQL by hand.

    ``connection``
        The name of the connection to use to perform the update

    ``table_name``
        The name of the table to update

    ``primary_key_column_name``
        The name of the primary key column

    ``primary_key_value``
        The ID or primary key value of the record to update 

    ``data_dict``
        A dictionary where the keys represents the columns to update and the 
        values represent the new values to use
    
    ``substitute``
        If ``True`` any ``%s`` characters will be substituted for the 
        correct param_style characters in the format specified by
        ``param_style``

    ``param_style``
        The param_style format the underlying database driver expects. Can be
        ``'format'`` for ``%s`` style or ``query`` for ``?`` style

    An example:
    
    ::

        >>> update_record(
        ...     connection,
        ...     'person',
        ...     'person_id',
        ...     34,
        ...     {'name': u'James'}
        ... )

    '''
    cursor = connection.cursor()
    columns = []
    values = []
    for k, v in data_dict.items():
        values.append(v)
        columns.append(k)
 
    columns_str = ""
    for col in columns:
        columns_str += '"%s"=%%s, '%(col)
    columns_str = columns_str[:-2]
    sql = """
        UPDATE %s SET %s WHERE "%s"=%%s;
    """ % (
        table_name,
        columns_str,
        primary_key_column_name,
    )
    if substitute:
        sql = substitute_param_style(sql, param_style)
    values.append(primary_key_value)
    cursor.execute(sql, tuple(values))
    cursor.close()
    return True

def insert_record(
    connection, 
    table_name, 
    data_dict, 
    primary_key_column_name=None,
    plugin_name=None,
):
    """\
    Insert a new record into a table and return its integer primary key

    There is a different version of this function for every supported database
    and the correct format is specified by ``engine`` or inferred from the
    ``connection``.

    ``connection``
        The name of the connection to use to perform the update

    ``table_name``
        The name of the table to update

    ``data_dict``
        A dictionary where the keys represents the columns to update and the 
        values represent the new values to use
    
    ``primary_key_column_name``
        The name of the primary key column. If ``primary_key_column_name`` is
        ``None``, it is assumed you are following a naming convention where
        the primary key is the table name followed by ``_id``.

    ``plugin_name``
        The type and structure of the underlying database. This affects how the
        new ID is generated and returned since different databases handle it
        differently. Only the value ``postgresql`` is currently allowed.

    An example:

    ::

        >>> print insert_record(
        ...     connection, 
        ...      'person',
        ...     {'name': u'James'}
        ...     'person_id',
        ...     engine=None,
        ... )
        2

    """
    if not plugin.available_plugins.has_key(plugin_name):
        raise Exception('Plugin %r not found'%plugin_name)
    if not plugin.insert_record.has_key(plugin_name):
        plugin.insert_record[plugin_name] = \
           plugin.available_plugins[plugin_name]['insert_record'].load()
    # Use the insert_record_plugins plugin's insert method
    return plugin.insert_record[plugin_name](
         connection, 
         table_name, 
         data_dict,
         primary_key_column_name,
    )

def page_data(
    connection, 
    sql, 
    values, 
    page=None, 
    number=20, 
    format='list', 
    substitute=True, 
    param_style='format',
):
    """\
    Obtain a specific portion of a result set.
    """
    if page is not None:
        sql += """
            OFFSET %s
            LIMIT %s
        """
        values.append((page-1)*number)
        values.append(number)
    cursor = connection.cursor()
    if substitute:
        sql = substitute_param_style(sql, param_style)
    cursor.execute(sql, tuple(values))
    if format == 'list':
        rows = cursor.fetchall()
    elif format == 'dict':
        rows = dict_fetchall(cursor)
    else:
        raise Exception('Unrecognised cursor fetch format %s'%(format))
    cursor.close() 
    return rows

def service_extensions(bag, name):
    """\
    This function exposes the database helpers as part of the bag and
    uses the ``bag[name].connect()`` function to automatically obtain a 
    database connection from the bag when it is needed.
    """

    def bag_insert_record(*k, **p):
        args = p.copy()
        real_args = ['table_name', 'data_dict', 'primary_key_column_name']
        for i in range(len(k)):
            args[real_args[i]] = k[i]
        for arg in ['connection', 'engine']:
            if args.has_key(arg):
                raise TypeError(
                    "The %r argument is assigned automatically, you cannot "
                    "specify it"%(arg,)
                )
        args['plugin_name'] = bag.app.config[name].plugin
        args['connection'] = bag[name].connect()
        return insert_record(**args)

    def bag_update_record(*k, **p):
        args = p.copy()
        real_args = ['table_name', 'primary_key_column_name', 'primary_key_value', 'data_dict']
        for i in range(len(k)):
            args[real_args[i]] = k[i]
        for arg in ['connection', 'param_style']:
            if args.has_key(arg):
                raise TypeError(
                    "The %r argument is assigned automatically, you cannot "
                    "specify it"%(arg,)
                )
        args['param_style'] = bag.app.config[name].param_style
        args['connection'] = bag[name].connect()
        return update_record(**args)

    def bag_query(*k, **p):
        args = p.copy()
        real_args = ['sql', 'values', 'format', 'fetch', 'substitute']
        for i in range(len(k)):
            args[real_args[i]] = k[i]
        for arg in ['connection', 'param_style']:
            if args.has_key(arg):
                raise TypeError(
                    "The %r argument is assigned automatically, you cannot "
                    "specify it"%(arg,)
                )
        args['connection'] = bag[name].connect()
        args['param_style'] = bag.app.config[name].param_style
        return query(**args)

    def bag_page_data(*k, **p):
        raise Exception('Not yet implemented')
        return query(bag[name].connect(), *k, **p)

    bag[name]['insert_record'] = bag_insert_record
    bag[name]['update_record'] = bag_update_record
    bag[name]['page_data'] = bag_page_data
    bag[name]['dict_fetchall'] = dict_fetchall
    bag[name]['query'] = bag_query

