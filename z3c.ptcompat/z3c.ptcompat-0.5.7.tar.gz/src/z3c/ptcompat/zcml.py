import os
import sys
from new import function

from zope.interface import classImplements
from zope.viewlet import viewlet
from zope.viewlet import manager
from zope.viewlet import metaconfigure as viewletmeta
from zope.viewlet.interfaces import IViewletManager
from zope.app.publisher.browser import viewmeta
from zope.app.pagetemplate import simpleviewclass

from z3c.ptcompat import ViewPageTemplateFile
from z3c.ptcompat import config

def package_home(gdict):
    filename = gdict["__file__"]
    return os.path.dirname(filename)

def clone_and_replace_globals(func, new_globals):
    func_globals = func.func_globals.copy()
    func_globals.update(new_globals)
    func_defaults = func.func_defaults or ()
    new_func = function(func.func_code, func_globals,
                        func.func_name, func_defaults)
    new_func.__doc__ = getattr(func, '__doc__', '')
    func_dict = getattr(func, '__dict__', None)
    if func_dict is not None:
        new_func.__dict__ = func_dict.copy()
    return new_func

def SimpleViewClass(src, offering=None, used_for=None, bases=(), name=u''):
    if offering is None:
        offering = sys._getframe(1).f_globals

    if isinstance(offering, dict):
        offering = package_home(offering)

    bases += (simpleviewclass.simple, )

    class_ = type("SimpleViewClass from %s" % src, bases,
                  {'index': ViewPageTemplateFile(src, offering),
                   '__name__': name})

    if used_for is not None:
        class_.__used_for__ = used_for

    return class_

def SimpleViewletClass(src, offering=None, bases=(),
                       attributes=None, name=u''):
    if offering is None:
        offering = sys._getframe(1).f_globals

    if isinstance(offering, dict):
        offering = package_home(offering)

    # Create the base class hierarchy
    bases += (viewlet.simple, viewlet.ViewletBase)

    attrs = {'index' : ViewPageTemplateFile(src, offering),
             '__name__' : name}
    if attributes:
        attrs.update(attributes)

    # Generate a derived view class.
    class_ = type("SimpleViewletClass from %s" % src, bases, attrs)

    return class_

def ViewletManager(name, interface, template=None, bases=()):
    attrs = {'__name__' : name}
    if template is not None:
        attrs['template'] = ViewPageTemplateFile(template)

    if manager.ViewletManagerBase not in bases:
        # Make sure that we do not get a default viewlet manager mixin, if the
        # provided base is already a full viewlet manager implementation.
        if not (len(bases) == 1 and
                IViewletManager.implementedBy(bases[0])):
            bases = bases + (manager.ViewletManagerBase,)

    ViewletManager = type(
        '<ViewletManager providing %s>' % interface.getName(), bases, attrs)
    classImplements(ViewletManager, interface)
    return ViewletManager

def page_directive(_context, name, *args, **kwargs):
    class_ = kwargs.get('class_')
    template = kwargs.get('template')

    if template:
        bases = class_ and (class_,) or ()
        kwargs['class_'] = SimpleViewClass(str(template), bases=bases,
                                           name=name)
        del kwargs['template']

    return viewmeta.page(_context, name, *args, **kwargs)

new_page_globals = dict(page=page_directive)
class pages_directive(viewmeta.pages):

    page = clone_and_replace_globals(viewmeta.pages.page.im_func,
                                     new_page_globals)

def viewlet_directive(_context, name, *args, **kwargs):
    class_ = kwargs.get('class_')
    template = kwargs.get('template')

    if template:
        bases = class_ and (class_,) or ()
        kwargs['class_'] = SimpleViewletClass(str(template),
                                              bases=bases, name=name)
        del kwargs['template']

    return viewletmeta.viewletDirective(_context, name, *args, **kwargs)

def viewlet_manager_directive(_context, name, *args, **kwargs):
    class_ = kwargs.get('class_')
    template = kwargs.get('template')
    provides = kwargs.setdefault('provides', IViewletManager)

    if template:
        bases = class_ and (class_,) or ()
        kwargs['class_'] = ViewletManager(
            name, provides, template=str(template), bases=bases)
        del kwargs['template']

    return viewletmeta.viewletManagerDirective(_context, name, *args, **kwargs)

try:
    # Make zope.app.form a soft-dependency. We only register custom
    # directives if it is available.
    from zope.app.form.browser import metaconfigure as formmeta
except ImportError:
    pass
else:
    if config.PREFER_Z3C_PT:
        # Replace globals in *Factory by the ones from our package, cloning
        # the existing functions so we don't have to re-define them.
        new_factory_globals = dict(ViewPageTemplateFile=ViewPageTemplateFile,
                                   SimpleViewClass=SimpleViewClass)

        AddViewFactory = clone_and_replace_globals(formmeta.AddViewFactory,
                                                   new_factory_globals)
        EditViewFactory = clone_and_replace_globals(formmeta.EditViewFactory,
                                                    new_factory_globals)
        DisplayViewFactory = clone_and_replace_globals(formmeta.DisplayViewFactory,
                                                       new_factory_globals)

        # Now, replace globals in the directive handlers' __call__ by our own
        # factories that were cloned right above.
        new_form_globals = dict(AddViewFactory=AddViewFactory,
                                EditViewFactory=EditViewFactory,
                                DisplayViewFactory=DisplayViewFactory)

        class AddFormDirective(formmeta.AddFormDirective):
            __call__ = clone_and_replace_globals(
                formmeta.AddFormDirective.__call__.im_func,
                new_form_globals)

        class EditFormDirective(formmeta.EditFormDirective):
            __call__ = clone_and_replace_globals(
                formmeta.EditFormDirective.__call__.im_func,
                new_form_globals)

        class FormDirective(formmeta.FormDirective):
            __call__ = clone_and_replace_globals(
                formmeta.FormDirective.__call__.im_func,
                new_form_globals)

        class SubeditFormDirective(formmeta.SubeditFormDirective):
            __call__ = clone_and_replace_globals(
                formmeta.SubeditFormDirective.__call__.im_func,
                new_form_globals)

        class SchemaDisplayDirective(formmeta.SchemaDisplayDirective):
            __call__ = clone_and_replace_globals(
                formmeta.SchemaDisplayDirective.__call__.im_func,
                new_form_globals)
    else:
        AddViewFactory = formmeta.AddViewFactory
        EditViewFactory = formmeta.EditViewFactory
        DisplayViewFactory = formmeta.DisplayViewFactory

        AddFormDirective = formmeta.AddFormDirective
        EditFormDirective = formmeta.EditFormDirective
        FormDirective = formmeta.FormDirective
        SubeditFormDirective = formmeta.SubeditFormDirective
        SchemaDisplayDirective = formmeta.SchemaDisplayDirective
