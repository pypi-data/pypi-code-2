from sqlalchemy import *
from migrate import *
import migrate.changeset

metadata = MetaData(migrate_engine)

def upgrade():
    # Add a new column to store the type of the message
    connection = migrate_engine.connect()
    connection.execute("ALTER TABLE tubes ALTER COLUMN payload TYPE character varying(524288)")

def downgrade():
    connection = migrate_engine.connect()
    connection.execute("ALTER TABLE tubes ALTER COLUMN payload TYPE character varying(65536)")

