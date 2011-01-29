"""base/constraints

A table/mask can be constrained to only browse a subset of the real data.
This means that additional filters (possibly spanning joined relations) are
applied to the query when issuing.
"""

t = SqlTable('movie',
             dbproxy=db,
             order_by='title',
             geom=(800,300),
             )
t.add_constraint(year__lte=2000)

t.reload()

