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
from sqlalchemy                  import *
import sqlalchemy.orm            as orm
from base                        import Base, KVC
from coils.foundation.mimetypes  import *
from coils.foundation.blobmanager import BLOBManager


class Note(Base, KVC):
    """ An OpenGroupare Note object """
    __tablename__       = 'note'
    __entityName__      = 'note'
    __internalName__    = 'Note' # Correct?
    object_id           = Column("document_id",
                                Integer,
                                Sequence('key_generator'),
                                primary_key=True)
    appointment_id      = Column("date_id", Integer,
                                 ForeignKey('date_x.date_id'),
                                 nullable=True)
    project_id          = Column("project_id", Integer,
                                 ForeignKey('project.project_id'),
                                 nullable=True)
    company_id          = Column("company_id", Integer,
                                 ForeignKey('person.company_id'),
                                 ForeignKey('enterprise.company_id'),
                                 nullable=True)
    is_note             = Column("is_note", Integer, default=1)
    version             = Column("object_version", Integer)
    title               = Column("title", String(255))
    abstract            = Column("abstract", String(255))
    kind                = Column("file_type", String(255))
    status              = Column("db_status", String(50), default='inserted')
    creator_id          = Column("first_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=True)
    created             = Column("creation_date", DateTime())
    owner_id            = Column("current_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=True)
    modified            = Column("lastmodified_date", DateTime())
    categories          = Column('categories', String(255))
    caldav_uid          = Column('caldav_uid', String(128))

    def get_mimetype(self):
        return 'text/plain'

    def get_path(self):
        return 'documents/{0}.{1}'.format(self.object_id, self.kind)

    @property
    def content(self):
        if hasattr(self, '_content'):
            return self._content
        else:
            raise Exception('Note content not initialized.')

    @content.setter
    def content(self, value):
        #print 'setting note content = {0}'.format(value)
        setattr(self, '_content', value)
        

class DocumentVersion(Base):
    __tablename__       = 'document_version'
    __entityName__      = 'documentVersion'
    __internalName__    = 'documentVersion' # Correct?

    object_id           = Column("document_version_id",
                                Integer,
                                Sequence('key_generator'),
                                primary_key=True)

    document_id         = Column("document_id", Integer,
                                 ForeignKey('doc.document_id'),
                                 nullable=True)

    owner_id            = Column("last_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=False)

    version             = Column("version", Integer, nullable = False)
    packed              = Column("is_packed", Integer)
    created             = Column("creation_date", DateTime())
    name                = Column("title", String(255))
    abstract            = Column("abstract", String(255))
    archived            = Column("archive_date", DateTime())
    change_text         = Column("change_text", String)
    file_size           = Column("file_size", Integer)
    extension           = Column("file_type", String(255), nullable = False)

    def __init__(self, document, text = None):
        self.document_id = document.object_id
        self.owner_id    = document.owner_id
        self.created     = document.created
        self.version     = document.version
        self.name        = document.name
        self.abstract    = document.abstract
        self.extension   = document.extension
        self.change_text = text
        self.packed      = 0


class _Doc(Base):
    """ An OpenGroupare Document object """
    __tablename__       = 'doc'
    __entityName__      = 'Document'
    __internalName__    = 'Doc' # Correct?
    object_id           = Column("document_id",
                                Integer,
                                Sequence('key_generator'),
                                primary_key=True)
    appointment_id      = Column("date_id", Integer,

                       ForeignKey('date_x.date_id'),
                                 nullable=True)
    project_id          = Column("project_id", Integer,
                                 ForeignKey('project.project_id'),
                                 nullable=True)
    company_id          = Column("company_id", Integer,
                                 ForeignKey('person.company_id'),
                                 ForeignKey('enterprise.company_id'),
                                 nullable=True)
    folder_id           = Column("parent_document_id", Integer,
                                 ForeignKey('doc.document_id'),
                                 nullable=True)
    version             = Column("object_version", Integer)
    version_count       = Column("version_count", Integer)
    abstract            = Column("abstract", String(255))
    status              = Column("db_status", String(50))
    state               = Column("status", String(50))
    _is_folder          = Column("is_folder", Integer)
    name                = Column("title", String(255))
    creator_id          = Column("first_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=False)
    created             = Column("creation_date", DateTime())
    owner_id            = Column("current_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=False)
    modified            = Column("lastmodified_date", DateTime())
    extension           = Column("file_type", String(255), nullable = False)
    file_size           = Column("file_size", Integer)

    __mapper_args__     = {'polymorphic_on': _is_folder}

    def __init__(self):
        self.version = 1
        self.version_count = 0

    def get_mimetype(self):
        if ((self._is_folder == 1) or (self.extension is None)):
            return None
        return COILS_MIMETYPEMAP.get(self.extension, 'application/octet-stream')


class Document(_Doc, KVC):
    __entityName__  = 'File'
    __mapper_args__ = {'polymorphic_identity': 0}

    content             = ''

    def skyfs_path_to_version(self, version):
        if (self.project_id is None):
            raise Exception('Attempt to get SKYfs path for a non-project document')
        for edition in self.versions:
            if edition.version == version:
                version = edition
                break
        else:
            raise Exception('No such version as {0} for documentId#{1}'.format(version, self.object_id))
        return '/documents/{0}/{1}/{2}.{3}'.format(self.project_id,
                                                   (1000 * ( version.object_id / 1000)),
                                                   version.object_id,
                                                   version.extension)

    def create_version(self, text):
        self.version = self.version + 1
        return DocumentVersion(self, text)

    def get_display_name(self):
        if (self.extension is None):
            return self.name
        else:
            return '{0}.{1}'.format(self.name, self.extension)


class Folder(_Doc, KVC):
    __entityName__  = 'Folder'
    __mapper_args__ = {'polymorphic_identity': 1}
    
    def __init__(self):
        self.status = 'inserted'
        self.version = 0

    def get_display_name(self):
        return self.name
