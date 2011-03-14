#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from pkg_resources import iter_entry_points
from cocktail.modeling import classgetter
from cocktail.events import Event
from cocktail.pkgutils import resolve
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from woost.models.item import Item

def load_extensions():
    """Load all available extensions.
    
    This is tipically called during application start up, and follows this
    sequence:

        * New available extensions are installed
        * Previously installed exceptions that are no longer available are
          uninstalled
        * All installed and enabled extensions are initialized
    """
    # Add/remove extensions
    install_new_extensions()
    uninstall_missing_extensions()

    # Load enabled extensions
    NOT_YET_LOADED = object()
    LOADED = object()
    DISABLED = object()
    
    extension_state = {}

    def load(extension):
        state = extension_state.get(extension, NOT_YET_LOADED)

        # Avoid loading an extension twice
        if state is NOT_YET_LOADED:
            
            # Ignore disabled extensions, and those where its implementation is
            # no longer available
            try:
                enabled = extension.enabled
            except AttributeError:
                enabled = False

            if not enabled:
                state = DISABLED
            else:
                # Load dependencies first
                for dependency in extension.dependencies:
                    dependency = resolve(dependency)
                    if isinstance(dependency, type):
                        dependency = list(dependency.select())[0]
                    
                    if not load(dependency):
                        
                        # A dependency for the extension has been disabled; the
                        # extension (and its dependencies) won't be loaded
                        state = DISABLED
                        break
                
                # If all dependencies were loaded, load the extension
                else:
                    extension.loading()
                    extension.installed = True
                    state = LOADED

            extension_state[extension] = state
        
        return state is LOADED

    for extension in Extension.select():
        load(extension)

    datastore.commit()

def install_new_extensions():
    """Finds new available extensions and registers them with the site."""

    # Create an instance of each new extension
    installed_extension_types = \
        set(extension.__class__ for extension in Extension.select())

    extensions_installed = False

    for entry_point in iter_entry_points("woost.extensions"):
        extension_type = entry_point.load()
        if extension_type not in installed_extension_types:
            extension = extension_type()
            extension.insert()
            extensions_installed = True
        
    if extensions_installed:
        datastore.commit()

def uninstall_missing_extensions():
    """Removes installed extensions that are no longer available."""
    # TODO: implement this!

# Class stub, required by the metaclass
Extension = None

class Extension(Item):
    """Base model for all application extensions.
    
    @ivar dependencies: A sequence of other extensions that should be loaded as
        dependencies of the extension. Each dependency can be specified using a
        reference to an extension object, a reference to an extension class or
        the qualified name of an extension class.
    @type dependencies: sequence of (L{Extension}, L{Extension} subclass or
        str)
    """

    # Add a custom metaclass to hide all subclasses of Extension by default
    class __metaclass__(Item.__metaclass__):

        def __init__(cls, name, bases, members):

            if Extension is not None and "visible_from_root" not in members:
                cls.visible_from_root = False

            Item.__metaclass__.__init__(cls, name, bases, members)

    instantiable = False
    edit_node_class = "woost.controllers.backoffice.extensioneditnode." \
                      "ExtensionEditNode"

    installed = False

    member_order = (
        "extension_author",
        "license",
        "web_page",
        "description",
        "enabled"
    )

    extension_author = schema.String(
        editable = False,
        listed_by_default = False
    )

    license = schema.String(
        editable = False,
        listed_by_default = False
    )

    web_page = schema.String(
        editable = False
    )

    description = schema.String(
        editable = False,
        translated = True
    )

    enabled = schema.Boolean(
        required = True,
        default = False
    )
 
    dependencies = ()

    loading = Event("""An event triggered during application start up.""")

    @classgetter
    def instance(cls):
        return iter(cls.select()).next()

    def __translate__(self, language, **kwargs):
        return translations(self.__class__.name)

