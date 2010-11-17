#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from sqlalchemy            import *
from base                  import *


class Collection(Base):
    """ An OpenGroupare Collection object """
    __tablename__       = 'Collection'
    __entityName__      = 'Collection'
    __internalName__    = 'Collection'
    object_id           = Column("collection_id",
                                Integer,
                                Sequence('key_generator'),
                                ForeignKey('collection_assignment.collection_id'),
                                ForeignKey('log.object_id'),
                                ForeignKey('object_acl.object_id'),
                                primary_key=True)
    version             = Column("object_version", Integer)
    owner_id            = Column("owner_id", Integer,
                                ForeignKey('person.company_id'),
                                nullable=False)
    kind                = Column("kind", String(50))
    title               = Column("title", String(255))
    project_id          = Column("project_id", Integer,
                                 ForeignKey('project.project_id'),
                                 nullable=True)
    comment             = Column("comment", Text)

class CollectionAssignment(Base):
    __tablename__       = 'collection_assignment'
    __entityName__      = 'CollectionAssignment'
    __internalName__    = 'CollectionAssignment'

    object_id           = Column("collection_assignment_id",
                                Integer,
                                Sequence('key_generator'),
                                primary_key=True)
    collection_id       = Column('collection_id', Integer)
    assigned_id         = Column('object_id', Integer)