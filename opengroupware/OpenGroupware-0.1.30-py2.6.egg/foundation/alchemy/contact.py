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
from sqlalchemy     import *
from base           import Base, KVC


class Contact(Base, KVC):
    """ An OpenGroupware Contact (Person) object """
    __tablename__        = 'person'
    __entityName__       = 'Contact'
    __internalName__     = 'Person'
    object_id            = Column("company_id",
                                  #Sequence('key_generator'),
                                  ForeignKey('log.object_id'),
                                  ForeignKey('object_acl.object_id'),
                                  primary_key=True)
    owner_id         = Column("owner_id", Integer,
                              ForeignKey('person.company_id'),
                              nullable=False)
    number               = Column("number", String(100))
    first_name           = Column("firstname", String(50))
    last_name            = Column("name", String(50))
    is_account           = Column("is_account", Integer)
    is_person            = Column("is_person", Integer)
    is_private           = Column("is_private", Integer)
    is_read_only         = Column("is_readonly", Integer)
    is_customer          = Column("is_customer", Integer)
    is_extranet_account  = Column("is_extra_account", Integer)
    is_intranet_account  = Column("is_intra_account", Integer)
    version              = Column("object_version", Integer)
    URL                  = Column("url", String(255))
    login                = Column("login", String(50))
    password             = Column("password", String(50))
    salutation           = Column("salutation", String(50))
    degree               = Column("degree", String(50))
    birth_date           = Column("birthday", DateTime())
    gender               = Column("sex", String(10))
    middle_name          = Column("middlename", String(50))
    status               = Column("db_status", String(50))
    sensitivity          = Column("sensitivity", Integer)
    boss_name            = Column("boss_name", String(255))
    partner_name         = Column("partner_name", String(255))
    assistant_name       = Column("assistant_name", String(255))
    department           = Column("department", String(255))
    display_name         = Column("description", String(255))
    office               = Column("office", String(255))
    occupation           = Column("occupation", String(255))
    anniversary          = Column("anniversary", DateTime())
    FBURL                = Column("freebusy_url", String(255))
    file_as              = Column("fileas", String(255))
    im_address           = Column("im_address", String(255))
    associated_contacts  = Column("associated_contacts", String(255))
    associated_categories= Column("associated_categories", String(255))
    associated_company   = Column("associated_company", String(255))
    birth_place          = Column("birthplace", String(255))
    birth_name           = Column("birthname", String(255))
    family_status        = Column("family_status", String(255))
    citizenship          = Column("citizenship", String(255))
    grave_date           = Column("dayofdeath", DateTime())
    keywords             = Column("keywords", String(255))
    # New
    source_url           = Column("source_url", String(255))
    ldap_url             = Column("dir_server", String(255))
    carddav_uid          = Column("carddav_uid", String(100))



    def __init__(self):
        self.is_person = 1
        self.is_account = 0
        self.is_private = 0
        self.is_read_only = 0
        self.is_customer = 0
        self.is_extranet_account = 0
        self.is_intranet_account = 0
        self.gender = 'unknown'
        self.status = 'inserted'
        self._comment = None

    @property
    def comment(self):
        return self.get_comment()

    @comment.setter
    def comment(self, value):
        self.set_comment(value)

    def get_comment(self):
        if (hasattr(self, '_comment')):
            return self._comment
        return None

    def set_comment(self, text):
        self._comment = text

    def get_company_value_text(self, name, default=None):
        for x in self.company_values:
            if x.name == name:
                if (x.string_value is not None):
                    return x.string_value
                    break
        return default
