"""base/totals

A stupid example to show the total on an integer
"""

t = SqlTable(model.Movie,
             dbproxy=db,
             order_by='director_id',
             rows=30,
             geom=(800,600)
         )

t.totals.add_total('year')
t.totals.add_break('director_id')

t.reload()

