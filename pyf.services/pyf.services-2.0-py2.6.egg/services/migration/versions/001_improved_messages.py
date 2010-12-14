from sqlalchemy import *
from migrate import *
import migrate.changeset

metadata = MetaData(migrate_engine)
eventhistory_table = Table("eventhistory", metadata, autoload=True)

def upgrade():
    # Add a new column to store the type of the message
    message_type_col = Column('message_type', Unicode(10), server_default='info')
    message_type_col.create(eventhistory_table)

def downgrade():
    message_type_col = eventhistory_table.columns['message_type']
    message_type_col.drop()

