"""Various SQL utilities for cubes"""
import sqlalchemy.sql as sql

def coalesce_tables(tables, default_value = None):
    """Coalesce NULL values in tables.
    
    :Arguments:
    * `tables` - a dictionary with keys as SQL alchemy table objects, and values
    as specified in coalesce_columns()
    * `default_value` - default value to be used for coalesce
    """
    
    for (table, columns) in tables.items():
        coalesce_table(table, columns, default_value)

def coalesce_columns(table, columns, default_value = None):
    """Coalesce NULL values in a table. `columns` can be a dictionary or a list.
    
    If `columns` it is a dictionary, then keys are column names and values are coalesced values. If
    the coalesced value is None, then `default_value` will be used. Otherwise, if `columns` is a
    list, then list items are column references and value will be set to default_value.
    """
    
    set_values = {}

    for (key, value) in columns.items():
        column = table.c[key]
        if value is None:
            value = default_value
        coalesce = sql.functions.coalesce(column, value)
        set_values[column] = coalesce
    expression = sql.expression.update(table, values = set_values)
    print str(expression)
    expression.execute()
