# koboldfs
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from datetime import datetime

from sqlalchemy import CHAR, CheckConstraint, Column, DateTime, ForeignKey, \
    Index, Integer, Unicode, UniqueConstraint, and_, literal_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation


Base = declarative_base()


class Domain(Base):
    """Domain object"""

    __tablename__ = "domains"

    id = Column(Integer, primary_key=True)

    name = Column(Unicode(255), nullable=False, unique=True)

    folder = Column(Unicode(255), nullable=False)

    url = Column(Unicode(255), nullable=False)


class File(Base):
    """File object"""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True)

    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    domain = relation('Domain', uselist=False)

    key = Column(Unicode(255), nullable=False)

    bytes = Column(Integer, nullable=True)

    checksum = Column(CHAR(32), nullable=True)

    created_on = Column(DateTime, nullable=False, default=datetime.now)

    deleted_on = Column(DateTime, nullable=True)

    status = Column(CHAR(1), nullable=False, default=u'R')

    class_ = Column('class', Integer, nullable=False, default=2)

    replicas = Column(Integer, nullable=False, default=0)

    __table_args__  = (
        CheckConstraint("status in ('R', 'D', 'T')"), {},
    )

Index('files_ndx_created_on', File.created_on, File.id,
    postgresql_where=(File.status == "'R'"))

Index('files_ndx_deleted_on', File.deleted_on, File.id,
    postgresql_where=and_(File.status == "'D'", File.replicas > 0))

Index('files_ndx_domain_key_status', File.domain_id, File.key, File.status)

Index('files_ndx_replicas', File.domain_id, File.status,
    postgresql_where=(File.replicas < literal_column('class')))


class Server(Base):
    """Server object"""

    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)

    name = Column(Unicode(255), nullable=False, unique=True)

    host = Column(Unicode(255), nullable=False, unique=True)

    status = Column(CHAR(1), nullable=False, default=u'Y')

    __table_args__  = (
        CheckConstraint("status in ('Y', 'N')"), {},
    )

Index('servers_ndx_status', Server.status, Server.id)


class ServerDomain(Base):
    """Server domain object"""

    __tablename__ = "servers_domains"

    id = Column(Integer, primary_key=True)

    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    server = relation('Server', backref='domains', uselist=False)

    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    domain = relation('Domain', backref='servers', uselist=False)

    __table_args__  = (
        UniqueConstraint("server_id", "domain_id"), {},
    )


class Replica(Base):
    """Replica object"""

    __tablename__ = "replicas"

    id = Column(Integer, primary_key=True)

    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    file = relation('File', backref='replicas_', uselist=False)

    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    server = relation('Server', uselist=False)

    created_on = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__  = (
        UniqueConstraint("server_id", "file_id"), {},
    )

Index('replicas_ndx_file_id', Replica.file_id)

Index('replicas_ndx_server_id', Replica.server_id, Replica.id)
