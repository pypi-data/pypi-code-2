from zope import schema
from zope.interface import Interface
from Products.Quota import QuotaMessageFactory as _


class IQuotaSizer(Interface):
    """
    adapter that let us find out the size of the adapted object
    """

    def get_increment():
        """
        calculate the increment in size of the adapted object since
        the last call to adapter.get_increment() or adapter.get_size()
        """

    def get_size():
        """
        return the size of the adapted object
        """


class IQuotaRecurse(Interface):
    """
    adapter to propagate changes in size upwards in the containment
    hyerarchy so that they will reach any concerned quota aware container.
    """

    def recurse_quota(increment):
        """
        If we can be adapted to IQuotaAware, execute enforce_quota,
        else execute recurse_quota on parent.
        """


class IQuotaAware(Interface):
    """
    interface for classes that can be adapted to IQuotaEnforcer
    """

    size_limit = schema.ASCIILine(title=_(u"Size limit"),
                   description=_(u"Max size (in MB) for objects with quota"),
                                  required=False)

    size_threshold = schema.ASCIILine(title=_(u"Size threshold"),
                   description=_(u"Allowed threshold (in MB) for "
                  "size limit for objects with quota"),
                                  required=False)


class IQuotaEnforcer(Interface):
    """
    adapter that will enforce the necessary quota whenever an IQuotaRecurse
    adapter reaches an IQuotaAware container.
    """

    def get_total():
        """
        return the size of the object plus the size of all it's contained
        objects (given there is an IQuotaSizer adapter for all of them
        """

    def enforce_quota(increment):
        """
        Check that total size + increment does not go over the allowed quota.
        """


class IQuotaService(Interface):
    """A service for calculating size and size increments of Archetype objects,
       and recursing over containment to enforce quotas
    """

    def get_increment(ob):
        """Calculate the size increment of an object in bytes,
           and set it's size as an annotation
        """

    def get_size(ob):
        """Get the size of an object
        """

    def recurse_quota(container, size):
        """Recurse over containment to enforce quotas
        """

    def max_size(ob):
        """Return quota in IQuotaAware container
        """

    def size_threshold(ob):
        """Return allowed size over quota  in IQuotaAware container
        """


class IQuotaSettings(Interface):
    """Global quota settings
    """

    size_limit = schema.Int(title=_(u"Maximum size"),
                            description=_(u"Default maximum size of content "
                                          u"(MB) for quota aware containers"),
                            default=-1,
                            required=False)

    size_threshold = schema.Int(title=_(u"Size threshold"),
                                description=_(u"This value (MB) is added to "
                                              u"the previous value to make up "
                                              u"a hard maximum size"),
                                default=0,
                                required=False)

    enforce_quota = schema.Bool(title=_(u"Enforce quota"),
                                description=_(u"If checked, no quota aware "
                                              u"container will be allowed "
                                              u"to contain more than these "
                                              u"settings"),
                                default=False,
                                required=False)
