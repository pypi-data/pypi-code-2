"""base/base import

these are the base import. All other examples skip the imports that are
granted by the way execfile is done in 'demo.py'.

The proxy is not needed, is just a way to pass several in a single
parameter metadata and session

Table
-----
base editing mode: table view
passing the tablename triggers the reflection of the table from the database

NOT NULL fields are rendered with columns with italic font

Right-click on the record to see what you can do: delete, add a new record or
display the record in a Mask
"""

from sqlkit.widgets import SqlTable
from sqlkit.db import proxy
import model

db = proxy.DbProxy(bind="sqlite:///model/db.sqlite")


t = SqlTable('movie',    dbproxy=db, order_by='title', )
t.reload()

