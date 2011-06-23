from sqlalchemy import *
from migrate import *
import migrate.changeset

from pyf.services.model import DBSession, Dispatch

import unicodedata

metadata = MetaData(migrate_engine)
dispatchs_table = Table("dispatchs", metadata, autoload=True)

def upgrade():
    # Add a new column to store the name of the dispatcher
    name_col = Column('name', Unicode(50), unique=True)
    name_col.create(dispatchs_table)

    # Put a default name based on the display_name
    connection = migrate_engine.connect()

    results = connection.execute(dispatchs_table.select())
    for row in results:
        display_name = unicode(row.display_name, "utf-8")

        name = display_name.lower().replace(' ', '_')
        nkfd_form = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in nkfd_form if not unicodedata.combining(c)])

        connection.execute("update dispatchs set name='%s' where display_name='%s'" % (name, display_name))
        
    # now we make the column mandatory
    name_col.alter(nullable=False)

def downgrade():
    name_col = dispatchs_table.columns['name']
    name_col.drop()
