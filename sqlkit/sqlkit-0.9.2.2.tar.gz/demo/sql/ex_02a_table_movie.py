"""base/tree table

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
from sqlkit.widgets.table.modelproxy import Header, ModelProxy
from sqlkit.db import proxy
import model

db = proxy.DbProxy(bind="sqlite:///model/db.sqlite")

class MyModel(ModelProxy):

    def make_header_obj(self, field_value):

        return Header(self.master, 'title', self.master.gui_fields.director_id.get_human_value(field_value))


t = SqlTable('movie', dbproxy=db, order_by='title', )
t.modelproxy = t.modelproxy.copy(MyModel)
t.modelproxy.tree_field_name = 'director_id'
t.hide_fields('director_id')
t.reload()

