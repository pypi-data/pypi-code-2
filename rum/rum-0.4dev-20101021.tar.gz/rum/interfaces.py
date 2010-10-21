"""
This modules is an interface declaration which only purpose is to document them.
This code is never executed neither serves to enforce compliance to the
interface by implementators.

It is useful if you plan to extend rum.
"""

class Attribute(object):
    """I'm only useful dor documenting attributes"""
    def __init__(self, name, doc):
        self.name = name
        self.__doc__ = "Attribute(%r)" % self.name
        if doc is not None:
            self.__doc__ += ': ' + doc

class IFactory:
    def get(resource, parent=None, remote_name=None, action=None, prefix=None,
            args=None):
        """
        Returns an appropiate class for the factory to use to build its
        products.
        """

    @classmethod
    def register(target_cls, pred=(), prio=0, **kw):
        """
        Register ``target_cls`` for resources that match the given predicate.
        Both type-tuple based dispatch and full predicate dispatch are supported
        """

    def can_handle(*args, **kw):
        """
        Returns True if this factory knows how to create product for certains
        arguments.
        """

    def __call__(resource, parent=None, remote_name=None, action=None, prefix=None):
        """
        Returns an initialized product of this factory for the give arguments.
        """


# Interface declarations
class IControllerFactory(IFactory):
    def get(resource, parent=None, remote_name=None, action=None, prefix=None,
            args=None):
        """
        Returns a Controller class to be used to ``handle`` resource,
        optionally related to ``parent`` when prefix is ``prefix``.
        ``args`` is a dict that can be used to place arguments that will be
        used to instatiate the controller.
        This method is called by :meth:`__call__` and it is designed to be
        extended using generic functions to handle arbitrary resources
        """

    def __call__(resource, parent=None, remote_name=None, action=None, prefix=None):
        """
        Returns a Controller instance to be used to ``handle`` resource,
        optionally related to ``parent`` when prefix is ``prefix``.
        """

class IController:
    request = Attribute('request', 'A WSGI request object')
    app = Attribute('app',
                    'The :class:`rum.RumApp` that instantiated this '
                    'controller.')
                        
    def __call__(environ, start_response):
        """
        The WSGI callable.
        """

class IRepositoryFactory(IFactory):
    resources = Attribute('resources',
                          'A list of all resources registered in this '
                          'repository')

    def __call__(resource, parent=None, remote_name=None, action=None, prefix=None):
        """
        Returns a repository instance to be used to ``handle`` resource,
        optionally related to ``parent`` when related attribute is ``remote_name``.
        """

    def get(resource, parent=None, remote_name=None, action=None, prefix=None,
            args=None):
        """
        Returns a repository class to be used to ``handle`` resource,
        optionally related to ``parent`` when related attribute is ``remote_name``.
        ``args`` is a dict that can be used to place arguments that will be
        used to instatiate the repository.
        """

    def get_id(obj):
        """
        Returns a string representing the id for this object.
        This expression should always be True
        repository.get(repository.get_id(obj)) == obj

        This method is a shortcut for self(obj.__class__).get_id(obj)
        """

    def fields_for_resource(resource, attr=None):
        """
        Returns a list of :class:`rum.fields.Field` for a resource
        or a :class:`rum.fields.Field` for attribute ``attr`` of
        ``resource`` if ``attr`` is not ``None``.
        """

    def cleanup(app):
        """
        Liberate request-local resources if any. This method on the
        'on_end_request' event and it is passed the active app instance.
        """

    def names_for_resource(resource):
        """
        Return (singular, plural) names for resource.
        """
    
    def set_names(obj, singular, plural):
        """
        Registers the `singular` and `plural` names for `obj` and its
        instances.
        """

class IRepository:
    resource = Attribute('resource',
                         "The resource class we've been instantiated to "
                         "handle")
    parent = Attribute('parent',
                       "The parent resource which ``resource`` is related to. "
                       "It is possible that this attribute is None.")
    remote_name = Attribute('remote_name',
                     "If ``resource`` is related to a ``parent`` this is the "
                     "name of the parent's attribute that relates to "
                     "``resource``")
    factory = Attribute('factory',
                       "The :class:`IRepositoryFactory` instance that has "
                       "instantiated us, useful to have a ref. here since "
                       "the factory holds reference to DB connections, etc...")
    defaults = Attribute('defaults',
                     "A dynamically generated dict with default values to fill a new "
                     "instance of ``resource`` if none are provided. This info is "
                     "retrieved from the schema")

    def get(id):
        """
        Returns a resource instance by id. Id could be a tuple for composite
        keys in a relational database or a string as received from the routes.
        It is the responsability of the repository to convert this string to
        something meaninful, including parsing it to extract a composite key
        and not opening any security whole on the attempt.

        If the id is malformed, raise a :exc:`rum.exceptions.BadId`.
        """
        
    def get_id(obj):
        """
        Returns a string representing the id for this object.
        This expression should always be True
        repository.get(repository.get_id(obj)) == obj
        """

    def select(query=None):
        """
        Returns an iterable that yields all ``resource`` instances that match
        the criteria in ``query``. If ``query`` is None it should yield all
        possible instances.
        """

    def delete(obj):
        """
        Delete ``obj`` from the data store so it is no longer persistent.
        """

    def save(obj):
        """
        Save ``obj`` in the data store so it is persisted.
        """

    def update(obj, data):
        """
        Update ``obj`` with ``data``. Data is a map keyed by attribute names
        with coerced and validated values from the View.
        """

    def create(data):
        """
        Create a persistent new instance from ``data`` and return it.
        Data is a map keyed by attribute names with coerced and validated
        values from the View.
        """

    #
    # The following are methods implementing repoze.tm2's IDataManager
    #
    #XXX Don't be lazy and document these too...

    transaction_manager = None


    def commit(transaction):
        """ See IDataManager.
        """

    def abort(transaction):
        """ See IDataManager.
        """

    def tpc_begin(transaction):
        """ See IDataManager.
        """

    def tpc_vote(transaction):
        """ See IDataManager.
        """

    def tpc_finish(transaction):
        """ See IDataManager.
        """

    def tpc_abort(transaction):
        """ See IDataManager.
        """

    def sortKey():
        """ See IDataManager.
        """



class IViewFactory(IFactory):

    def __call__(resource, parent=None, remote_name=None, action=None, prefix=None):
        """
        Return a IView instance suitable for displaying ``obj`` or
        attribute ``remote_name`` from ``obj`` in action ``action``.

        Note that there's no requirement on the type of these parameters as long
        as :meth:`get_view` is extended (via generic functions) to handle
        them.
        """

    def get(resource, parent=None, remote_name=None, action=None, prefix=None,
            args=None):
        """
        Returns a class implementing IView for viewing
        ``obj`` (or attribute ``remote_name`` of ``obj`` if ``remote_name`` is None) in
        action ``action``.

        Depending on the action (update,create,preview) I should return
        IValidator implementations.

        ``args`` is a dictionary with keyword arguments that will be used to
        initialize the View in :meth:`__call__`. This is useful to write
        ``before`` or ``after`` methods that have a chance to alter them
        depending on the ``obj``, ``remote_name`` and/or ``action`` they're being
        called with.
        """

class IView:
    
    def __call__(obj, **kwargs):
        """
        Render a representation of ``obj``
        """

class IInputView(IView):
    def validate(value, state=None):
        """
        Validate and coerce strings to python objects from a a HTTP request.
        """

class IRouter:
    def resource(resource, parent=None, prefix=None, remote_name=None):
        """
        Register ``resource``, optinally attached to ``parent`` at attribute
        ``remote_name``.
        ``prefix`` will be pre-pended to the URL endpoint so a resource
        can be regsitered at multiple end points to be handled by different
        :class:`IController`
        """
    
    def dispatch(environ):
        """
        Match PATH_INFO and possibly REQUEST_METHOD.
        """

    def match(url):
        """
        Try to match ``url`` against registered resources and return a routes
        dict if succesful.
        """
    
    def url_for(*args, **kw):
        """
        Generate a URL for the routes whose dict most closely resembles ``kw``.
        raise a RoutesException if no url could be generated.
        """

    def connect(*args, **kw):
        """
        Manually connect a controller class (passed as the ``controller``
        keyword argument) to a URL specification. See Routes manual for more
        info.
        """

class IRenderer:
    """
    An object used to render a given template(s) using data.

    **Arguments**

        `search_path`
            A list of locations in the filesystem where the template loader
            should look for templates.
        `auto_reload`
            Should the loader automatically reload a template if it is modified?
            Note that not all loaders might support this feature. If it doesn't
            then it will have no effect.
        `cache_dir`
            A directory where the template loader may save compiled templates
    """
    def render(data, posssible_templates):
        """
        Return a rendered template with variables from ``data``

        ``possible_tempplates`` is a list of relative to templates which will
        be looked up in the current search_path. The resulting list of
        absolute paths is the cartesian product of ``search_path`` and
        ``possible_templates``.
        """
            
class IPolicy:
    """
    Controls access to resources
    """

    def check(obj, action, attr=None, user=None):
        """
        Checks if `user` allowed to perform `action` on `obj`? Optional `attr`
        is the name of an attribute from `obj` which if present means the
        query is on that attribute, else it's on the whole `obj`.

        If `user` is None then the currently logged in user will be used.

        Raises a :exc:`SecurityDenial` if access is denied
        """

    def has_permission(obj, action, attr=None, user=None):
        """
        Is `user` allowed to perform `action` on `obj`? Optional `attr`
        is the name of an attribute from `obj` which if present means the
        query is on that attribute, else it's on the whole `obj`.

        If `user` is None then the currently logged in user will be used.

        Returns True or a :class:`Denial` instance.
        """

    def require(predicate, obj=None, action=None, attr=None):
        """
        Registers a `predicate` callable to be evaluated when
        :meth:`has_permission` is called with `obj`, `action`, and `attr` as
        arguments. `predicate` should be a callable that accepts the same
        arguments as :meth:`has_permission` and return True/Denial
        """
        
    def filter(iterable, action, user=None):
        """
        Filters an iterable removing any instance `user` is not allowed to
        "see" for `action`
        """

__all__  = [k for k in locals().keys() if k.startswith('I')]
