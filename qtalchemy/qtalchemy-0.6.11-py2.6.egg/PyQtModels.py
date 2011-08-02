# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
This module brings together a number of crucial elements of the qtalchemy library.  It 
depends on the UserAttr module and builds in so widget knowledge of the UserAttr (or particular 
for foreign keys).  This requires tying in sqlalchemy data sources and makes some assumptions 
about the qtalchemy approach to building a dialog.
"""

from PyQtHelpers import *
from sqlalchemy.orm import mapper, create_session, relation, object_session, Query
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy_helper import *
import sqlalchemy
import datetime
import decimal
from qtalchemy.widgets import PBDateEdit
from user_attr import UserAttr, AttrNumeric

if sqlalchemy.__version__.split('.') < ['0', '6', '0']:
    sqlalchemy_to_python_type = [(satype,pytype) for pytype,satype in sqlalchemy.types.type_map.iteritems()]
elif sqlalchemy.__version__.split('.') < ['0', '7', '0']:
    sqlalchemy_to_python_type = [(satype.__class__,pytype) for pytype,satype in sqlalchemy.types.type_map.iteritems()]
else:
    # TODO:  if we weren't convinced before that type_map was a secret, now we should be :)
    sqlalchemy_to_python_type = [(satype.__class__,pytype) for pytype,satype in sqlalchemy.types._type_map.iteritems()]
sqlalchemy_to_python_type.append((sqlalchemy.types.String,str))

def BoundPropertyAttribute(classMember, attribute):
    """
    Abstracts out property determination code between a UserAttr and SA column.

    Attributes like the label, yoke and what's this string are kept in the 
    SA info dictionary for a column.  They are kept directly as members of the 
    descriptor class for a UserAttr.
    """

    # classMember appears like a SA column
    if hasattr(classMember,"label") and callable(classMember.label):
        col=classMember.property.columns[0]
        if hasattr(col,"info") and col.info.has_key(attribute):
            return col.info[attribute]

    try:
        # cls has an attribute col that looks like a UserAttr
        return getattr(classMember, attribute)
    except AttributeError:
        pass

    return None

def ClassAttributeWhatsThis(classMember):
    return BoundPropertyAttribute(classMember, "whats_this")

def UserLabel(identifier):
    """
    Convert a python or SQL identifier name to a user viewable label.  Essentially this makes word breaks 
    at '_' characters and uses initial caps for words.
    
    >>> UserLabel("balance_sheet")
    'Balance Sheet'
    >>> UserLabel("account")
    'Account'
    """
    return identifier.replace('_', ' ').title()

def ClassAttributeLabel(classMember):
    """
    Abstracts out the label determination code between a UserAttr and SA column.
    
    See also :ClassAttributeType
    >>> class X:
    ...     name=UserAttr(str,"First Name")
    >>> ClassAttributeLabel(X.name)
    'First Name'

    >>> from sqlalchemy import Table, Column, Integer, String, Text, Date, Boolean, Numeric, MetaData
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> metadata = MetaData()
    >>> Base = declarative_base(metadata=metadata)
    >>> class Options(Base):
    ...     __table__ = Table('options', metadata,
    ...             Column('id', Integer, primary_key=True),
    ...             Column('data_name', String(50)),
    ...             Column('company', String(50), info={"label": "Company Name"}))
    >>> ClassAttributeLabel(Options.data_name)
    'Data Name'
    >>> ClassAttributeLabel(Options.company)
    'Company Name'
    """

    # classMember appears like a SA column
    if hasattr(classMember,"label") and callable(classMember.label):
        col=classMember.property.columns[0]
        if hasattr(col,"info") and col.info.has_key("label"):
            return col.info["label"]
        else:
            return UserLabel(col.name)

    try:
        # cls has an attribute col that looks like a UserAttr
        return classMember.label
    except AttributeError:
        pass

    return None

def attrLabel(cls, col):
    """
    See also attrType and ClassAttributeLabel

    This helper function returns a label from class and attribute pair.  It handles the following cases:
     - cls is a new-style python class and col is a string representing the attribute name of a UserAttr
     - cls is a new-style python class and col is a string representing the attribute name of a SqlAlchemy column
     - cls is None and col is a ModelColumn object
    
    >>> m=ModelColumn("name",str,"First Name")
    >>> attrLabel(None,m)
    'First Name'
    """
    try:
        # col looks like a ModelColumn
        return col.label
    except AttributeError:
        assert cls is not None, "If 'col' is not (like) a ModelColumn, then cls must be specified."

    return ClassAttributeLabel(getattr(cls,col))

def ClassAttributeYoke(classMember):
    """
    :param classMember: The attribute in the class (not the instance)
    
    This function
    
    >>> class X:
    ...     name=UserAttr(str,"First Name")
    ...     age=UserAttr(AttrNumeric(3),"Precise Age")
    >>> ClassAttributeYoke(X.name)
    'line'
    >>> ClassAttributeYoke(X.age)
    'float'

    >>> from sqlalchemy import Table, Column, Integer, String, Text, Date, Time, Boolean, Numeric, MetaData
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> metadata = MetaData()
    >>> Base = declarative_base(metadata=metadata)
    >>> class Books(Base):
    ...     __table__ = Table('books', metadata,
    ...             Column('id', Integer, primary_key=True),
    ...             Column('author', String(50)),
    ...             Column('release', Date()),
    ...             Column('release_time', Time()),
    ...             Column('copies', Integer),
    ...             Column('juvenile', Boolean),
    ...             Column('review', Text),
    ...             Column('price', Numeric(precision=10,scale=2,asdecimal=True)),
    ...             Column('title', String(50), info={'yoke': 'text'}))
    >>> ClassAttributeYoke(Books.author)
    'line'
    >>> ClassAttributeYoke(Books.release)
    'date'
    >>> ClassAttributeYoke(Books.release_time)
    'time'
    >>> ClassAttributeYoke(Books.copies)
    'int'
    >>> ClassAttributeYoke(Books.price)
    'float'
    >>> ClassAttributeYoke(Books.title)
    'text'
    >>> ClassAttributeYoke(Books.review)
    'text'
    >>> ClassAttributeYoke(Books.juvenile)
    'bool'
    """

    type_=None

    try:
        # unspecified UserAttr class
        type_ = classMember.base_type
        return classMember.yoke_specifier()
    except AttributeError, e:
        pass

    if type_ is not None:
        try:
            # specified UserAttr class?
            return type_.yoke_specifier()
        except AttributeError, e:
            pass

    # classMember appears like a SA column
    if type_ is None and hasattr(classMember,"label") and callable(classMember.label):
        col=classMember.property.columns[0]
        if hasattr(col,"info") and col.info.has_key("yoke"):
            return col.info["yoke"]
        else:
            if isinstance(classMember.property.columns[0].type, sqlalchemy.types.Text):
                return "text"
            for satype,pytype in sqlalchemy_to_python_type:
                if isinstance(classMember.property.columns[0].type,satype):
                    type_ = pytype

    if type_ == datetime.date:
        return "date"
    elif type_ == datetime.time:
        return "time"
    elif type_ == bool:
        return "bool"
    elif type_ == int:
        return "int"
    elif type_ in (decimal.Decimal,float):
        return "float"
    else:
        return "line"

def attrYoke(cls, col):
    """
    See also attrType and ClassAttributeLabel

    This helper function returns a label from class and attribute pair.  It handles the following cases:
     - cls is a new-style python class and col is a string representing the attribute name of a UserAttr
     - cls is a new-style python class and col is a string representing the attribute name of a SqlAlchemy column
     - cls is None and col is a ModelColumn object
    
    >>> m=ModelColumn("name",str,"First Name")
    >>> attrYoke(None,m)
    'line'
    """
    if cls is not None:
        return ClassAttributeYoke(getattr(cls,col.attr))

    try:
        # col looks like a ModelColumn
        type_ = col.type_

        if type_ == datetime.date:
            return "date"
        elif type_ == bool:
            return "bool"
        elif type_ == int:
            return "int"
        elif type_ in (decimal.Decimal,float):
            return "float"
        else:
            return "line"
    except AttributeError:
        assert cls is not None, "If 'col' is not (like) a ModelColumn, then cls must be specified."

    #return ClassAttributeYoke(getattr(cls,col))

def ClassAttributeType(classMember):
    """
    :param classMember: The attribute in the class (not the instance)
    
    This function
    
    >>> class X:
    ...     name=UserAttr(str,"First Name")
    >>> ClassAttributeType(X.name)
    <type 'str'>

    >>> from sqlalchemy import Table, Column, Integer, String, Text, Date, Boolean, Numeric, MetaData
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> metadata = MetaData()
    >>> Base = declarative_base(metadata=metadata)
    >>> class Books(Base):
    ...     __table__ = Table('books', metadata,
    ...             Column('id', Integer, primary_key=True),
    ...             Column('author', String(50)),
    ...             Column('release', Date()),
    ...             Column('copies', Integer),
    ...             Column('juvenile', Boolean),
    ...             Column('price', Numeric(precision=10,scale=2,asdecimal=True)),
    ...             Column('title', String(50)))
    >>> ClassAttributeType(Books.author)
    <type 'str'>
    >>> ClassAttributeType(Books.release)
    <type 'datetime.date'>
    >>> ClassAttributeType(Books.copies)
    <type 'int'>
    >>> # platform confusion on the next one
    >>> ClassAttributeType(Books.price) in (decimal.Decimal, float)
    True
    >>> ClassAttributeType(Books.juvenile)
    <type 'bool'>
    """
    try:
        # cls has an attribute col that looks like a UserAttr
        return classMember.base_type
    except AttributeError:
        pass

    # cls is sqlalchemy mapped object with column col
    try:
        for satype,pytype in sqlalchemy_to_python_type:
            if isinstance(classMember.property.columns[0].type,satype):
                return pytype
    except AttributeError:
        pass

    return None # we don't know

def attrType(cls, col):
    """
    See also attrLabel

    This helper function returns a type from class and attribute pair.  It handles the following cases:
     - cls is a new-style python class and col is a string representing the attribute name of a UserAttr
     - cls is a new-style python class and col is a string representing the attribute name of a SqlAlchemy column
     - cls is None and col is a ModelColumn object
    
    >>> m=ModelColumn("name",str,"First Name")
    >>> attrType(None,m)
    <type 'str'>
    """
    try:
        # col looks like a ModelColumn
        return col.type_
    except AttributeError:
        assert cls is not None, "If 'col' is not (like) a ModelColumn, then cls must be specified."

    return ClassAttributeType(getattr(cls,col))

def attrReadonly(cls, col):
    try:
        return col.readonly
    except AttributeError:
        pass
    try:
        return getattr(cls,col).readonly
    except AttributeError:
        pass
    return False


class AlchemyModelDelegate(QtGui.QStyledItemDelegate):
    def setEditorData(self,editor,index):
        try:
            cls = index.model().cls
            if cls:
                c = index.model().columns[index.column()]
                userattr = getattr(cls,c.attr if hasattr(c,"attr") else c)
                if userattr is not None and hasattr(userattr,"WidgetBind"):
                    userattr.WidgetBind(editor,index.model().row_object(index.row()))
        except AttributeError, e:
            pass

        # http://bugreports.qt.nokia.com/browse/QTBUG-428 - combo boxes don't play nice with qdatawidget mapper 
        if isinstance(editor,QtGui.QComboBox):
            text = index.data()
            if text == None:
                text = ""
            if editor.isEditable():
                editor.setEditText(text)
            else:
                editor.setCurrentIndex(editor.findText(text))
        else:
            QtGui.QStyledItemDelegate.setEditorData(self,editor,index)

    def setModelData(self,editor,model,index):
        if isinstance(editor,QtGui.QComboBox):
            model.setData(index,editor.currentText())
        else:
            QtGui.QStyledItemDelegate.setModelData(self,editor,model,index)

    def createEditor(self,parent,option,index):
        try:
            cls = index.model().cls
            if cls:
                c = index.model().columns[index.column()]
                userattr = getattr(cls,c.attr if hasattr(c,"attr") else c)
                if userattr is not None and hasattr(userattr,"WidgetFactory"):
                    return userattr.WidgetFactory(parent, index)
        except AttributeError, e:
            pass
        return QtGui.QStyledItemDelegate.createEditor(self,parent,option,index)

def AttrWidgetFactory(userattr,parent=None, index=None):
    if hasattr(userattr,"WidgetFactory"):
        return userattr.WidgetFactory(parent, index)
    myAttrType = ClassAttributeType(userattr)
    if myAttrType == datetime.date:
        w = PBDateEdit(parent)
        #w = QtGui.QDateEdit(parent)
        #w.setCalendarPopup(True)
        return w
    elif myAttrType == bool:
        return QtGui.QCheckBox(ClassAttributeLabel(userattr), parent)
    elif myAttrType == int:
        w = QtGui.QLineEdit(parent)
        w.setValidator(QtGui.QIntValidator())
        return w
    elif myAttrType in (decimal.Decimal,float):
        w = QtGui.QLineEdit(parent)
        w.setValidator(QtGui.QDoubleValidator(parent))
        return w
    else:
        return QtGui.QLineEdit(parent)

class ModelColumn:
    def __init__(self,attr,type_,label=None,readonly=False):
        self.attr = attr
        if label is None:
            self.label = attr.title().replace("_"," ")
        else:
            self.label = label
        self.type_ = type_
        self.readonly = readonly


class SACollectionManagerForModel:
    """
    Provide semi-hookable functions from PBTableModel for adding and deleting
    rows.

    The PBTableModel includes an additional blank (or multiple blank) row at the
    bottom of the list of existing lines. This line is not the SQLAlchemy
    session (or other collection class), but it is there for a user convenience
    to add a new line.
    """
    def __init__(self,klass,collection=None,session=None,fixed_rows=False):
        self.klass = klass
        self.fixed_rows = fixed_rows
        self.reset(collection, session)

    def reset(self,collection,session):
        self.session = session
        self.collection = collection

        # TODO: consider getting the session via:
        #self.session = object_session(self.collection._sa_adapter.owner_state.obj())

    def add_flipper_row(self):
        """
        Create a new row, but do not add it to the sqlalchemy session.
        
        A 'flipper row' is a row typically at the bottom of the list which is
        not yet in the (sql-alchemy) collection, but appears visually.
        """
        r = self.klass()
        # The object is not added to the session, but we like to pretend that it is.
        if self.session is not None:
            self.session.npadd(r)
        return r

    def join_flipper(self, flipper):
        """
        Add a pre-existing object to the collection
        """
        self.collection += [flipper]

    def add_row(self):
        """
        Make a new row object, add it to the collection and return it.
        
        Note that in the usual (?) PBTableModel use case, a new row passes through 
        a flipper row stage.  The add_row method can be viewed as the sum of 
        add_flipper_row and join_flipper.
        """
        r = self.klass()
        # implicitly added to the session when added to the collection
        self.collection += [r]
        return r

    def delete_row(self, row):
        """
        Remove the row object from the collection.  Return True if successful, False otherwise.
        """
        try:
            self.collection.remove(row)
            # we must explicitly delete the row from the session to remove it from the database
            session = object_session(self.collection._sa_adapter.owner_state.obj())
            if session is not None:
                session.delete(row)
            return True
        except InvalidRequestError as e:
            session.expunge(row)
            return True
        except Exception as e:
            return False

def ClassTableModel(cls, attributes, readonly=True, fixed_rows=False, row_manager=None, objectConverter=None):
    """
    Create a :class:`PBTableModel` exposing a list of objects of a particular python class.
    
    Example:
        >>> from sqlalchemy import Table, Column, Integer, String, Text, Date, Boolean, Numeric, MetaData, ForeignKey, create_engine, select, join
        >>> from sqlalchemy.orm import Query
        >>> from sqlalchemy.ext.declarative import declarative_base
        >>> 
        >>> from qtalchemy import QueryTableModel, PBSessionMaker, ModelObject
        >>> from PyQt4 import QtCore, QtGui
        >>> 
        >>> metadata = MetaData()
        >>> Base = declarative_base(metadata=metadata,cls=ModelObject)
        >>> 
        >>> class Person(Base):
        ...     __table__ = Table('person',metadata,
        ...         Column('id', Integer, primary_key=True),
        ...         Column('name', String(50)))
        ...     nicks = relation("Nicks", backref="Person")
        ... 
        >>> class Nicks(Base):
        ...     __table__ = Table('nicks',metadata,
        ...         Column('id', Integer, primary_key=True),
        ...         Column('person_id', Integer, ForeignKey('person.id')),
        ...         Column('nick', String(50)))
        ...     def __repr__(self):
        ...         return "Nick:  %s" % (self.nick,)
        ... 
        >>> engine = create_engine("sqlite://")
        >>> metadata.bind = engine
        >>> metadata.create_all()
        >>> Session = PBSessionMaker(bind=engine)
        >>> session = Session()
        >>> p=Person()
        >>> session.add(p)
        >>> p.nicks
        []
        >>> model=ClassTableModel(Nicks,["nick"],readonly=False)
        >>> model.reset_content_from_list(p.nicks,session)
        >>> model.rowCount(None)
        1
        >>> index = model.index(0,0,None)
        >>> index.internalPointer()
        Nick:  None
        >>> index.internalPointer().session() is not None
        True
        >>> model.data(index,QtCore.Qt.DisplayRole)
        ''
        >>> model.setData(index,"sam",QtCore.Qt.EditRole)
        True
        >>> p.nicks
        [Nick:  sam]
        >>> index = model.index(1,0,None)
        >>> model.setData(index,"jack",QtCore.Qt.EditRole)
        True
        >>> p.nicks
        [Nick:  sam, Nick:  jack]
    """
    def makeModelColumn(cls, attr):
        ua = getattr(cls, attr)
        return ModelColumn(attr, ClassAttributeType(ua), ClassAttributeLabel(ua), readonly=attrReadonly(cls, attr))
    cols = [makeModelColumn(cls, a) for a in attributes]
    return PBTableModel(cols, cls=cls, readonly=readonly, fixed_rows=fixed_rows, row_manager=row_manager, objectConverter=objectConverter)


def QueryClassTableModel(cls, attributes, query, ssrc, objectConverter=None):
    """
    Construct a :class:`PBTableModel` from a sqlalchemy query returning a mapped 
    class.
    
    :param cls:  The mapped class which is returned
    :param attributes:  attributes to display
    :param query: the query object
    :param ssrc:  the session maker
    :param objectConverter: function taking an instance of cls and returning the primary key for use
    """
    def makeModelColumn(cls, attr):
        ua = getattr(cls, attr)
        return ModelColumn(attr, ClassAttributeType(ua), ClassAttributeLabel(ua), readonly=attrReadonly(cls, attr))
    cols = [makeModelColumn(cls, a) for a in attributes]
    return PBTableModel(cols, query=query, cls=cls, ssrc=ssrc, objectConverter=objectConverter)

def QueryTableModel(q, cols=None, include_uuid=False, ssrc=None, objectConverter=None):
    """
    This helper function constructs an :class:`PBTableModel` from a sqlalchemy query.  It can
    auto-detect the columns and types or take a list of column names from the query.
    
    :param q: A sqlalchemy.orm.query.Query object
    :param cols: an optional list of columns (if not specified, it displays all subject to include_uuid)
    :param include_uuid: optional parameter defaulting to False.  If include_uuid is true, then the generated
        table will include the uuids.  Generally, we only desire to have the uuid's around for use in the handlers.
    """
    model_cols = []
    uuid_cols = []
    sq = q.subquery() # need this to get column types
    for col in sq.columns:
        if col.name.startswith("_hidden_"):
            pass
        elif isinstance(col.type,UUID):
            if include_uuid:
                model_cols.append(ModelColumn(UserLabel(col.name),str))
            uuid_cols.append(col)
        else:
            match = False
            for satype,pytype in sqlalchemy_to_python_type:
                if isinstance(col.type,satype):
                    model_cols.append(ModelColumn(col.name,pytype))
                    match=True
                    break
            assert match, "The sqlalchemy type %s was not known for mapping to a python type." % col.type

    if objectConverter is None and len(uuid_cols)>0:
        # we take the first UUID as the key column.
        # It is a basic assumption of qtalchemy that everything has a UUID pk
        objectConverter = lambda x, col=uuid_cols[0]: getattr(x, col.name)

    if q.session is None:
        return PBTableModel(model_cols, query=q, ssrc=ssrc, objectConverter=objectConverter)
    else:
        return PBTableModel(model_cols, rows=q.all(), objectConverter=objectConverter)

class PBTableModel(QtCore.QAbstractTableModel):
    """
    A PyQt/PySide model for objects with :class:`UserAttr`.
    """
    def __init__(self, columns, cls=None, rows=None, query=None, ssrc=None, parent=None, readonly=True, row_manager=None, fixed_rows=False, objectConverter=None):
        """
        All parameters other than columns are optional.

        :param columns:  A list of columns.  These could be attribute names or ModelColumn objects.  Both methods can be used in the same model instance.
        :param query:  This could be SA Query object or a list of row objects
        :param cls:  The class of objects in the row list.
        :param ssrc:  A sqlalchemy sessionmaker.
        :param objectConverter: Callable taking row objects to unique keys in the application domain
        """
        QtCore.QAbstractTableModel.__init__(self,parent)
        self.columns = columns
        self.cls = cls

        self.objectConverter = (lambda x: x) if objectConverter is None else objectConverter

        self.query = query
        self.ssrc = ssrc

        self.row_list = rows
        self.readonly=readonly
        if row_manager is None:
            row_manager = SACollectionManagerForModel(self.cls, fixed_rows=fixed_rows)
        self.row_manager = row_manager

        self.setRoleNames(dict([(QtCore.Qt.UserRole+i,self.columns[i].attr) for i in range(len(columns))]))

        # making new rows and being readonly seems contradictory to me.
        assert not self.row_manager.fixed_rows or not self.readonly, "I'm not sure what a non-sessioned query means with an editable table."
        assert not self.row_manager.fixed_rows or self.query is None, "I'm not sure what a non-sessioned query means with an editable table."

        # The "flipper row" is the new row at the bottom of the list.
        self.flipper_rows = []
        if not self.readonly and not self.row_manager.fixed_rows and len(self.flipper_rows) == 0:
            self.flipper_rows.append(self.row_manager.add_flipper_row())

    def reset_content_from_list(self, rows, session=None):
        self.beginResetModel()
        self.row_list = rows

        # TODO:  Here is a dilemma:
        #  pull #1)  I'd like to keep requirements for classes with UserAttr and 
        #            hooking a model very slim
        #  pull #2)  I need some instrumentation to notify the PBTableModel
        #            of changes at the python object level
        #
        # Potential Fix:  Have the PBTableModel add an instrumentation object when 
        # needed.
        if self.cls is not None and issubclass(self.cls, ModelObject):
            for r in rows:
                instanceEvent(r, "set", "")(self.row_object_change)

        if self.row_manager is not None:
            self.row_manager.reset(self.row_list,session)
        self.flipper_rows = []
        if not self.readonly and not self.row_manager.fixed_rows and len(self.flipper_rows) == 0:
            self.flipper_rows.append(self.row_manager.add_flipper_row())
        self.endResetModel()

    def reset_content_from_session(self):
        """
        Reload the query from the session source 'ssrc' passed at object invocation.
        """
        if self.ssrc is None:
            return  # we don't know how to reload; make it a no-op for now
        
        q2 = self.query
        q2.session = self.ssrc()
        self.reset_content_from_list(q2.all())
        q2.session.close()
        q2.session = None

    def rowReverseIndex(self, row_obj):
        for i in range(self.rowCount(None)):
            row = self.row_object(i)
            if row is row_obj:
                return i
        return -1

    def rowEmitChange(self, row_obj, col):
        """
        Emit change events for the row and column indexes indicated.
        
        :param row_obj: The object in the list of rows changed
        :param col: a column index or the string 'all' indicating 0 .. columnCount()-1
        """
        if col == "all":
            col1 = 0
            col2 = self.columnCount(None)-1
        else:
            col1 = col2 = col
        i = self.rowReverseIndex(row_obj)
        if i != -1:
            self.dataChanged.emit(self.index(i,col1,None),self.index(i,col2,None))

    def row_object_change(self, row_obj, key, oldvalue):
        col_changed = -1
        for i in range(len(self.columns)):
            if self.columns[i].attr == key:
                col_changed = i
                break
        if col_changed == -1:
            return  # if the changing key is not a member of this model, then nothing to do here
        self.rowEmitChange(row_obj, col_changed)

    def row_object(self,row):
        if self.row_list is None or row < 0:
            return None

        if row < len(self.row_list):
            return self.row_list[row]
        else:
            return self.flipper_rows[row - len(self.row_list)]

    def index(self,row,column,parent):
        return self.createIndex(row,column,self.row_object(row))

    def columnCount(self,parent):
        #print "columnCount", len(self.columns)
        return len(self.columns)

    def rowCount(self,parent):
        if self.row_list is None:
            return 0

        #print "rowCount", len(self.row_list)
        if self.row_manager.fixed_rows:
            return len(self.row_list)
        else:
            return len(self.row_list) + len(self.flipper_rows)

    def removeRows(self,row,count,parent):
        """
        :param row: int offset of first row to remove
        :param count: int quantity of rows to remove
        """
        if self.row_manager is None or self.row_manager.fixed_rows:
            return False
        else:
            self.beginRemoveRows(parent,row,row+count-1)
            for i in range(count):
                row_obj = self.row_object(row)
                if row_obj in self.row_list:
                    self.row_manager.delete_row(row_obj)
            self.endRemoveRows()
            return True

    def headerData(self, col, orientation, role):
        if ( orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole ):
            return attrLabel(self.cls, self.columns[col])
        return None

    def data(self, index, role):
        c = self.columns[index.column()]
        r = self.row_object(index.row())
        if not index.isValid():
            return None

        primary_value = getattr(r,c.attr if hasattr(c, "attr") else c)
        primary_type = attrType(self.cls, c)
        primary_yoke = attrYoke(self.cls, c)

        if role == QtCore.Qt.DisplayRole:
            if primary_yoke != 'bool':
                return toQType(primary_value,suggested=primary_type)
        elif role == QtCore.Qt.EditRole:
            return toQType(primary_value,suggested=primary_type)
        elif role == QtCore.Qt.CheckStateRole:
            if primary_yoke == 'bool':
                return QtCore.Qt.Checked if primary_value else QtCore.Qt.Unchecked
        elif role == QtCore.Qt.TextAlignmentRole:
            if hasattr(r,"textAlignmentRole"):
                return r.textAlignmentRole(c)
            if primary_yoke in ('int','float'):
                return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        elif role == QtCore.Qt.FontRole:
            if hasattr(r,"fontRole"):
                return r.fontRole(c)
        elif role == QtCore.Qt.ForegroundRole:
            if hasattr(r,"foregroundRole"):
                return r.foregroundRole(c)
        elif role == QtCore.Qt.BackgroundRole:
            if hasattr(r,"backgroundRole"):
                return r.backgroundRole(c)
        elif role == QtCore.Qt.BackgroundRole:
                return r.foreground_role(c)
        elif role >= QtCore.Qt.UserRole:
            assert QtCore.Qt.UserRole <= role < QtCore.Qt.UserRole+len(self.columns)
            roles = self.roleNames()
            c = self.columns[role - QtCore.Qt.UserRole]
            return toQType(primary_value,suggested=primary_type)

        return None

    def ensureNoFlipper(self, index):
        if index.row() >= len(self.row_list):
            self.row_manager.join_flipper(self.flipper_rows[0])
            del self.flipper_rows[0]
            if not self.row_manager.fixed_rows and len(self.flipper_rows) == 0:
                self.beginInsertRows(QtCore.QModelIndex(),len(self.row_list),len(self.row_list))
                self.flipper_rows.append(self.row_manager.add_flipper_row())
                self.endInsertRows()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        #print value
        if not index.isValid():
            return None
        #elif role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            #return None

        c = self.columns[index.column()]
        r = self.row_object(index.row())
        newValue = fromQType(value, attrType(self.cls, c))
        oldValue = getattr(r, c.attr if hasattr(c, "attr") else c)
        #print attrType(self.cls, c), newValue, oldValue
        #  The None/"" dichotomy is a frightening mess -- we need to think carefully about all that.
        if oldValue is None:
            oldValue = toQType(oldValue, attrType(self.cls, c))
        if newValue != oldValue:
            self.ensureNoFlipper(index)

            setattr(r, c.attr if hasattr(c, "attr") else c, newValue)
        return True

    def flags(self,index):
        result = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        c = self.columns[index.column()]
        if not self.readonly and not attrReadonly(self.cls, c):
            if attrYoke(self.cls, c) == 'bool':
                result |= QtCore.Qt.ItemIsUserCheckable
            else:
                result |= QtCore.Qt.ItemIsEditable
        return result

class WidgetAttributeMapper(object):
    """
    This class provides a hook between widgets in the graphical toolkit and 
    attributes on a python object.

    The widgets created are selected by the sub-classes of InputYoke which 
    are assigned in the yokes_dict function in input_yoke.py.  TODO:  We 
    aim to expose the initialization of this dictionary to the application 
    programmer to allow widget types to be entirely replaced through-out the 
    application.

    It is encouraged that all widgets be created dynamically as Qt's layout 
    engine is extremely robust and configurable.  However, the bind member 
    function of WidgetAttributeMapper provides the ability to take a widget 
    created through other means and connect it to this mapping with a yoke.  
    This may be used with widgets generated via Qt designer tool.
    
    :param cls:  class we are mapping; we look for python descriptors in 
        this class (both UserAttr and sqlalchemy properties)
    :param objectConverter:  a callable taking an instance of type cls and 
        returning an id/handle as appropriate for any bound CommandMenu 
        entities.
    """
    
    def __init__(self, cls, obj=None, objectConverter=None):
        self.cls = cls
        self.obj = obj
        self.objectConverter = objectConverter
        self.widgets = []
        self.yokes = []
        self.attribute_map = {}

    def connect_instance(self,obj):
        self.obj = obj
        if issubclass(self.cls, ModelObject):
            instanceEvent(self.obj, "set", "")(self.row_object_change)
        for y in self.yokes:
            y.Bind()

    def reverse_yoke(self,attr,yoke):
        if attr not in self.attribute_map:
            self.attribute_map[attr] = []
        self.attribute_map[attr].append(yoke)

    def getObjectAttr(self,attr):
        return getattr(self.obj,attr)

    def setObjectAttr(self,attr,value):
        setattr(self.obj,attr,value)

    def row_object_change(self, obj, attr, oldvalue):
        assert obj is self.obj
        if attr not in self.attribute_map:
            return
        for y in self.attribute_map[attr]:
            y.Update(attr)

    def addBoundForm(self,layout,attrs):
        """
        Creates a QFormLayout and adds a collection of labeled fields.
        
        :param attrs:  a list of property names of the class specified with `cls` in __init__.
        """
        grid = LayoutLayout(layout,QtGui.QFormLayout())

        for a in attrs:
            self.addBoundField(grid,a)

    def labelAlignment(self,layout,labelPos):
        parent = layout.parentWidget()
        if parent is None:
            style = QtGui.QApplication.style()
        else:
            style = parent.style()
        if style is not None and labelPos == "l":
            return QtCore.Qt.Alignment(style.styleHint(QtGui.QStyle.SH_FormLayoutLabelAlignment))
        return None

    def addBoundFieldGrid(self,grid,attr,row,column,rowSpan=1,columnSpan=1,labelPos="left"):
        """
        :param labelPos:  label can be one of the following
         - left:  label in cell (row,column) and edit widget in cell (row,column+1)
         - above, top:  label in cell (row,column) and edit widget in cell (row,column+1)
         - right:  edit widget in cell (row,column) and label in cell (row+1,column)
         - below, bottom:  edit widget in cell (row,column) and label in cell (row,column+1)
         - None, '':  no label and edit widget in cell (row,column)
        :param rowSpan:  The span of 
        """
        import input_yoke

        y = input_yoke.YokeFactory(self.cls,attr, self)
        self.yokes.append(y)
        w = y.Factory()

        if labelPos not in ['',None]:
            label_key = labelPos[0].lower()
            label_cell = {'l': (row,column), 'a': (row,column), 't': (row,column), 'r': (row,column+1), 'b': (row+1,column)}.get(label_key)
            widget_cell = {'l': (row,column+1), 'a': (row+1,column), 't': (row+1,column), 'r': (row,column), 'b': (row,column)}.get(label_key)

            label = QtGui.QLabel(attrLabel(self.cls,attr))
            align = self.labelAlignment(grid,label_key)
            if align is not None:
                label_cell += (align,)
            grid.addWidget(label, *label_cell)
            label.setBuddy(w)
        else:
            widget_cell = (row,column)
        widget_cell_span = widget_cell + (rowSpan, columnSpan)
        grid.addWidget(w, *widget_cell_span)
        return w

    def addBoundField(self,layout,attr):
        """
        Adds a labeled field to a layout.
        """
        import input_yoke

        y = input_yoke.YokeFactory(self.cls,attr, self)
        self.yokes.append(y)
        w = y.Factory()

        if isinstance(layout,QtGui.QFormLayout):
            if y.LabelStyle() == input_yoke.InputYoke.Label.Internal:
                layout.addRow("",w)
            else:
                layout.addRow(attrLabel(self.cls,attr),w)
        else:
            layout.addWidget(w)
        
        return w

    def addColumn(self,attr):
        colIndex = -1
        for i in range(len(self.columns)):
            if self.columns[i] == attr:
                colIndex = i
        if colIndex == -1:
            colIndex = len(self.columns)
            self.columns.append(attr)
        return colIndex

    def submit(self):
        for y in self.yokes:
            y.Save()

    def bind(self, widget, attr, yoke_factory=None):
        import input_yoke

        if yoke_factory is None:
            y = input_yoke.YokeFactory(self.cls, attr, self)
        else:
            y = yoke_factory(self, attr)
        y.AdoptWidget(widget)
        self.yokes.append(y)

class MapperMixin(object):
    """
    :class:`MapperMixin` holds a list of :class:`WidgetAttributeMapper` classes and 
    provides helpers to ensure that the whole collection is synchronized before save.
    """
    def init_mapper_list(self):
        if not hasattr(self,"_mapper_list"):
            self._mapper_list = []

    def mapClass(self, cls, objectConverter=None):
        self.init_mapper_list()
        m = WidgetAttributeMapper(cls, objectConverter=objectConverter)
        self._mapper_list.append(m)
        return m

    def mapper(self,obj):
        self.init_mapper_list()
        m = WidgetAttributeMapper(None,obj)
        self._mapper_list.append(m)
        return m

    def submit(self):
        if not hasattr(self,"_mapper_list"):
            return

        for m in self._mapper_list:
            m.submit()
