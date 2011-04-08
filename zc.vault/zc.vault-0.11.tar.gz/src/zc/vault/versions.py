import sys
import persistent
import zope.interface
import zope.component
import zope.location
import zc.vault.vault
import zope.publisher.browser
import zope.publisher.interfaces
import zope.publisher.interfaces.browser
import zope.traversing.interfaces

class IReadVersions(zope.interface.Interface):
    """abstract: see IVersions"""

    vault = zope.interface.Attribute(
        """the vault that this collection of versions uses.""")

    factory = zope.interface.Attribute(
        """the (persistable) callable that gets an inventory and returns the
        persistable wrapper object that has the desired API.""")

    def __getitem__(ix):
        """return version for given index, or raise KeyError
        if no such index exists."""

    def __len__():
        """return number of versions"""

class IWriteVersions(zope.interface.Interface):
    """abstract: see IVersions"""

    def commit(version):
        """commit version"""

    def commitFrom(version):
        """commit from previous version"""

    def create():
        """create and return an editable version of the most recently
        committed."""

class IVersions(IReadVersions, IWriteVersions):
    """a collection of versions"""

class IWrapperAware(zope.interface.Interface):
    """A manifest that has a wrapper attribute pointing to it's
    desired wrapper"""

    wrapper = zope.interface.Attribute(
        """the desired wrapper""")


class Versions(persistent.Persistent, zope.location.Location):
    """Sequence of capability family versions.

    Used to implement CapabilityFamily.versions
    """
    
    zope.interface.implements(IVersions)

    def __init__(self, vault, factory, parent=None, name=None, initialize=None):
        self.vault = vault
        self.factory = factory
        if vault.__parent__ is None:
            zope.location.locate(self.vault, self, 'vault')
        elif parent is None:
            raise RuntimeError(
                "programmer error: Locate the vault, or pass a parent in, "
                "or both")
        if parent is not None:
            if name is not None:
                zope.location.locate(self, parent, name)
            else:
                self.__parent__ = parent
        for ix in range(len(vault)):
            i = vault.getInventory(ix)
            assert not IWrapperAware.providedBy(i.manifest), (
                'programmer error: manifests in vault have already been placed '
                'in a Versions container')
            i.__parent__ = self
            wrapper = self.factory(i)
            i.manifest.wrapper = wrapper
            zope.interface.directlyProvides(i.manifest, IWrapperAware)
            if zope.location.interfaces.ILocation.providedBy(wrapper):
                zope.location.locate(wrapper, self, str(i.manifest.vault_index))
        if initialize is not None:
            res = self.create()
            initialize(res)
            self.commit(res)

    def __len__(self):
        return len(self.vault)

    def __getitem__(self, idx):
        manifest = self.vault[idx]
        return manifest.wrapper

    def __iter__(self):
        for m in self.vault:
            yield m.wrapper

    def commit(self, wrapper):
        manifest = wrapper.inventory.manifest # XXX currently .inventory is
        # undocumented, hard requirement of wrapper...
        assert manifest.wrapper is wrapper, (
            'programmer error: manifest should have back reference to '
            'version')
        self.vault.commit(manifest)
        if zope.location.interfaces.ILocation.providedBy(wrapper):
            zope.location.locate(wrapper, self, str(manifest.vault_index))

    def commitFrom(self, wrapper):
        manifest = wrapper.inventory.manifest
        assert manifest.wrapper is wrapper, (
            'programmer error: manifest should have back reference to '
            'version')
        self.vault.commitFrom(manifest)
        i = self.vault.getInventory(-1)
        wrapper = self.factory(i)
        i.manifest.wrapper = wrapper
        zope.interface.directlyProvides(i.manifest, IWrapperAware)
        if zope.location.interfaces.ILocation.providedBy(wrapper):
            zope.location.locate(wrapper, self, str(i.manifest.vault_index))

    def create(self):
        inventory = zc.vault.vault.Inventory(vault=self.vault, mutable=True)
        inventory.__parent__ = self
        res = self.factory(inventory)
        inventory.manifest.wrapper = res
        zope.interface.directlyProvides(
            inventory.manifest, IWrapperAware)
        res.__parent__ = self
        return res


class deferredProperty(object):
    def __init__(self, name, initialize):
        self.name = name
        sys._getframe(1).f_locals[name] = self
        self.initialize = initialize
    def __get__(self, obj, typ=None):
        if obj is not None:
            self.initialize(obj)
            return obj.__dict__[self.name]
        return self


class Traverser(zope.publisher.browser.BrowserView):
    zope.component.adapts(
        IVersions, zope.publisher.interfaces.browser.IBrowserRequest)
    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher)

    _default = 'index.html'

    def browserDefault(self, request):
        return self.context, (self._default, )

    def publishTraverse(self, request, name):
        try:
            ix = int(name)
        except ValueError:
            pass
        else:
            try:
                v = self.context[ix]
            except IndexError:
                name = self._default
            else:
                return v
        view = zope.component.queryMultiAdapter(
            (self.context, request), name=name)
        if view is not None:
            return view
        raise zope.publisher.interfaces.NotFound(self.context, name, request)

_marker = object()

class Traversable(object):
    """Traverses containers via `getattr` and `get`."""

    zope.component.adapts(IVersions)
    zope.interface.implements(zope.traversing.interfaces.ITraversable)

    def __init__(self, context):
        self.context = context


    def traverse(self, name, furtherPath):
        try:
            ix = int(name)
        except ValueError:
            pass
        else:
            try:
                return self.context[ix]
            except IndexError:
                pass
        res = getattr(self, name, _marker)
        if res is _marker:
            raise zope.traversing.interfaces.TraversalError(name)
        return res
