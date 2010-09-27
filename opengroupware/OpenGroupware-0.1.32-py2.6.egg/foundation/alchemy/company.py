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


class Address(Base, KVC):
    """ An OpenGroupware Street Address Object """
    __tablename__     = 'address'
    __entityName__    = 'address'
    __internalName__  = 'Address'
    object_id   = Column("address_id", Integer, Sequence('key_generator'), primary_key=True)
    parent_id   = Column("company_id", Integer,
                         ForeignKey('person.company_id'),
                         ForeignKey('enterprise.company_id'),
                         nullable=False)
    version     =  Column("object_version", Integer)
    name1       = Column("name1", String(255))
    name2       = Column("name2", String(255))
    name3       = Column("name3", String(255))
    district    = Column("district", String(255))
    street      = Column("street", String(255))
    city        = Column("zipcity", String(255))
    province    = Column("state", String(100), quote=True)
    postal_code = Column("zip", String(50))
    country     = Column("country", String(100))
    kind        = Column("type", String(50), nullable=False)
    status      = Column("db_status", String(50))

    def __init__(self):
        self.status = 'inserted'


class Telephone(Base, KVC):
    """ An OpenGroupware Telephone Object """
    # TODO: Add "real_number" field
    __tablename__     = 'telephone'
    __entityName__    = 'telephone'
    __internalName__  = 'Telephone'
    object_id = Column('telephone_id', Integer, Sequence('key_generator'), primary_key=True)
    parent_id = Column("company_id", Integer,
                       ForeignKey('person.company_id'),
                       ForeignKey('enterprise.company_id'),
                       nullable=False)
    version  =  Column("object_version", Integer)
    number   = Column("number", String(255))
    info     = Column("info", String(255))
    kind     = Column("type", String(50), nullable=False)
    status   = Column("db_status", String(50))

    def __init__(self):
        self.status = 'inserted'


class CompanyInfo(Base, KVC):
    __tablename__       = "company_info"
    __entityName__      = "CompanyInfo"
    __internalName__    = "CompanyInfo"
    object_id     = Column("company_info_id", Integer, primary_key=True)
    parent_id     = Column("company_id", Integer,
                           ForeignKey("person.company_id"),
                           ForeignKey("enterprise.company_id"),
                           nullable=False)
    text          = Column("comment", String)
    status        = Column("db_status", String(50))

    def __init__(self):
        self.status = 'inserted'


class CompanyValue(Base, KVC):
    """ An OpenGroupware CompanyValues Object """
    __tablename__ = 'company_value'
    __entityName__       = 'companyValue'
    __internalName__     = 'CompanyValue'
    object_id     = Column("company_value_id",
                           Integer,
                           Sequence('key_generator'),
                           primary_key=True)
    parent_id     = Column("company_id", Integer,
                           ForeignKey('person.company_id'),
                           ForeignKey('enterprise.company_id'),
                           nullable=False)
    name         = Column("attribute", String(255), nullable=False)
    string_value  = Column("value_string", String(255))
    date_value    = Column("value_date", DateTime())
    integer_value = Column("value_int", Integer)
    label        = Column("label", String(255))
    uid          = Column("uid", Integer)
    widget       = Column("type", Integer)

    def __init__(self, parent_id, attribute, value):
        self.parent_id = parent_id
        self.name = attribute
        self.set_value(value)

    def set_value(self, value):
        if (value is None):
            self.string_value = None
            self.integer_value = None
        else:
            self.string_value = unicode(value)
            if (value.isdigit()):
                self.integer_value = int(value)
            else:
                self.integer_value = None
