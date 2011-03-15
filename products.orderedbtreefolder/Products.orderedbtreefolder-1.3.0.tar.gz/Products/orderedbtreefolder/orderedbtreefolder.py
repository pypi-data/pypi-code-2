"""Ordered BTreeFolder

This folder has the advantages of a normal BTreefolder. Object
listing and access to single objects, does not load unused objects
into memory.

With the ordering support one can use this folder as a base class for
other more application oriented containers.
"""

from cgi import escape
from types import StringType

from AccessControl import Permissions, \
                          getSecurityManager, \
                          ClassSecurityInfo, \
                          Unauthorized
from BTrees.OIBTree import union
from Globals import DTMLFile, InitializeClass

try:
    from OFS.IOrderSupport import IOrderedContainer
except ImportError:
    # For Zope 2.12 compatibility
    from OFS.interfaces import IOrderedContainer

from OFS.Folder import Folder
from OFS.ObjectManager import ObjectManager
from OFS.OrderSupport import OrderSupport as OrderSupportBase
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from ZODB.PersistentList import PersistentList
import Products.ZCatalog.Lazy

# constants
OBBEGIN = 'insert at beginning'
OBEND = 'append at end'

LISTTEXT0 = '''<select name="ids:list" multiple size="%s">
'''
LISTTEXT1 = '''<option>%s</option>
'''
LISTTEXT2 = '''</select>
'''
LISTTEXT3 = '''<input type="hidden" name="%s" value="%s" />'''


# zmi constructors
manage_addOrderedBTreeFolderForm = DTMLFile('dtml/orderedFolderAdd', globals())

def manage_addOrderedBTreeFolder(dispatcher, id, title='', REQUEST=None):
    """Adds a new OrderedBTreeFolder object with id *id*.
    """
    id = str(id)
    ob = OrderedBTreeFolder(id)
    ob.title = str(title)
    dispatcher._setObject(id, ob)
    ob = dispatcher._getOb(id)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST, update_menu=1)


class OrderSupport(OrderSupportBase):
    """Mixin class which provides BTreeFolders with OrderSupport. Only some
    methods of the standard Zope ( >= v2.7) OrderSupport need to be overwritten.
    All others are using moveObjectsByDelta().
    """
    # Implementation detail:
    # Changes in ordering are more costly than the access to the
    # ordering. The order is stored in a PersistenList object.
    __implements__  = (IOrderedContainer,)

    security = ClassSecurityInfo()

    def __init__(self):
        """Sets up the needed data structure, needs to be called by the class,
        which uses this mixin.
        """
        # A list to keep the order of ids
        self._order = PersistentList()

    security.declareProtected(Permissions.manage_properties, 'moveObjectsByDelta')
    def moveObjectsByDelta(self, ids, delta, supress_events=False):
        """Move specified sub-objects by delta.
        """
        if type(ids) is StringType:
            ids = (ids,)
        min_position = 0
        # get a shorter reference not a copy as order takes care of persistence
        # changes
        objects = self._order

        # unify moving direction
        if delta > 0:
            ids = list(ids)
            ids.reverse()
            objects.reverse()
        counter = 0

        for id in ids:
            if not id in objects:
                raise (ValueError,
                       'The object with the id "%s" does not exist.' % id)
            old_position = objects.index(id)
            new_position = max( old_position - abs(delta), min_position )
            if new_position == min_position:
                min_position += 1
            if not old_position == new_position:
                objects.remove(id)
                objects.insert(new_position, id)
                counter += 1

        if counter > 0:
            if delta > 0:
                objects.reverse()

        return counter


    security.declareProtected(Permissions.copy_or_move,'getObjectPosition')
    def getObjectPosition(self, id):
        """Get the position of an object by its id.
        """
        try:
            return self._order.index(id)
        except ValueError:
            raise 'NotFound' ,'Object %s was not found'%str(id)


    security.declareProtected(Permissions.manage_properties,'moveObjectsToTop')
    def moveObjectsToTop(self, ids):
        """Move specified sub-objects to top of container.
        """
        return self.moveObjectsByDelta( ids, -len(self._order) )


    security.declareProtected(Permissions.manage_properties,
                              'moveObjectsToBottom')
    def moveObjectsToBottom(self, ids):
        """Move specified sub-objects to bottom of container.
        """
        return self.moveObjectsByDelta( ids, len(self._order) )


    security.declareProtected(Permissions.manage_properties, 'orderObjects')
    def orderObjects(self, key, reverse=None):
        """Order sub-objects by key and direction.
        """
        ids = [ id for id, obj in sort( self.objectItems(),
                                        ( (key, 'cmp', 'asc'), ) ) ]
        if reverse:
            ids.reverse()
        return self.moveObjectsByDelta( ids, -len(self._order) )


    #
    #   Override Inherited Method of ObjectManager Subclass
    #
    _old_manage_renameObject = ObjectManager.inheritedAttribute(
                                                        'manage_renameObject')
    def manage_renameObject(self, id, new_id, REQUEST=None):
        """Rename a particular sub-object without changing its position.
        """
        old_position = self.getObjectPosition(id)
        result = self._old_manage_renameObject(id, new_id, REQUEST)
        #XXX TODO self.moveObjectToPosition(new_id, old_position)
        return result


InitializeClass(OrderSupport)


class OrderedBTreeFolderBase(OrderSupport, BTreeFolder2Base):
    """Base class which allows ordering of folder contents. For this some
    methods of the BTreeFolder2Base need to be overwritten.
    """
    __implements__  = OrderSupport.__implements__

    security = ClassSecurityInfo()

    insertmodii = [OBBEGIN, OBEND]

    def __init__(self, id, title=''):
        """Just call the inits of the mixin classes.
        """
        self.insertmodus = OBBEGIN

        BTreeFolder2Base.__init__(self, id)
        OrderSupport.__init__(self)

        self.title = title


    def _delOb(self, id):
        """Remove the id from the order list, before it's completly removed.
        """
        try:
            id_index = self._order.index(id)
        except ValueError:
            raise 'Not Found', ('Cannot find object with id:  "%s"' % (id,))
        # first look if object can be removed
        BTreeFolder2Base._delOb(self, id)
        self._order.pop(id_index)


    def _setOb(self, id, object):
        """Store the named object in the folder and insert it at the
        beginning of order.
        """
        # try if it can be added
        BTreeFolder2Base._setOb(self, id, object)
        # then add to the order list.
        # This is a policy, which needs perhaps to be configurable.
        # Here every new object is placed at the top.
        if self.insertmodus == OBBEGIN:
            self._order.insert(0,id)
        else:
            self._order.append(id)


    security.declareProtected(Permissions.access_contents_information,
                              'objectIds')
    def objectIds(self, spec=None):
        # Returns a list of subobject ids of the current object.
        # If 'spec' is specified, returns objects whose meta_type
        # matches 'spec'. Both cases return the ids according to
        # the current order.
        if spec is not None:
            if isinstance(spec, StringType):
                spec = [spec]
            mti = self._mt_index
            set = None
            for meta_type in spec:
                ids = mti.get(meta_type, None)
                if ids is not None:
                    set = union(set, ids)
            if set is None:
                return ()
            else:
                # Filter the order list by result
                return [id for id in self._order if set.has_key(id)]
        else:
            # make a copy
            return list(self._order)

    keys = objectIds

InitializeClass(OrderedBTreeFolderBase)


class OrderedBTreeFolder(OrderedBTreeFolderBase, Folder):
    """A BTreefolder, which keeps the order of added objects
    """
    meta_type = 'Ordered BTreeFolder'

    security = ClassSecurityInfo()

    _properties=({'id':'title', 'type': 'string','mode':'wd'},
                 {'id':'insertmodus',
                  'type':'selection',
                  'mode':'w',
                  'select_variable':'insertmodii'},
                 )

    manage_options=(
        ({'label':'Contents', 'action':'manage_main',},
         ) + Folder.manage_options[1:]
        )

    manage_main = DTMLFile('dtml/orderedBTFolderMain', globals())


    def _checkId(self, id, allow_dup=0):
        Folder._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)


    def manage_changeOrder(self, REQUEST):
        """Called by the main management screen. Only one selected element can
        be changed at the moment.
        """
        # XXX suboptimal, should be replaced by a totally different approach.
        form = REQUEST.form
        del form['ids']; del form['manage_changeOrder']
        for key, value in form.items():
            self.moveObjectToPosition(key, int(value))

        return self.manage_main(self,REQUEST)


    # security.declareProtected(view_management_screens, 'getBatchObjectListing')
    def getBatchObjectListing(self, REQUEST=None):
        """Return a structure for a page template to show the list of objects.
        """
        if REQUEST is None:
            REQUEST = {}
        pref_rows = int(REQUEST.get('dtpref_rows', 20))
        b_start = int(REQUEST.get('b_start', 1))
        b_count = int(REQUEST.get('b_count', 1000))
        b_end = b_start + b_count - 1
        url = self.absolute_url() + '/manage_main'
        idlist = self.objectIds()  # Pre-sorted.
        count = self.objectCount()

        if b_end < count:
            next_url = url + '?b_start=%d' % (b_start + b_count)
        else:
            b_end = count
            next_url = ''

        if b_start > 1:
            prev_url = url + '?b_start=%d' % max(b_start - b_count, 1)
        else:
            prev_url = ''

        formatted = []
        for i in range(b_start -1, b_end):
            formatted.append(LISTTEXT3 % (escape(idlist[i]), i))

        formatted.append(LISTTEXT0 % pref_rows)
        for i in range(b_start - 1, b_end):
            formatted.append(LISTTEXT1 % escape(idlist[i]))
        formatted.append(LISTTEXT2)
        return {'b_start': b_start, 'b_end': b_end,
                'prev_batch_url': prev_url,
                'next_batch_url': next_url,
                'formatted_list': ''.join(formatted)}


InitializeClass(OrderedBTreeFolder)
