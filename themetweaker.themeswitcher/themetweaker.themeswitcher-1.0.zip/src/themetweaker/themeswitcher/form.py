from zope.interface import alsoProvides, noLongerProvides
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from zope.i18nmessageid import MessageFactory


from themetweaker.themeswitcher.interfaces import IThemeSwitcherFormSchema
from themetweaker.themeswitcher.interfaces import IThemeSwitcher
from themetweaker.themeswitcher.traverser import THEMESWITCHER_ANNO
from themetweaker.themeswitcher.utils import AdapterAnnotationProperty
from themetweaker.themeswitcher.utils import BaseAdapter

from plone.app.form.base import EditForm
from plone.app.form.validators import null_validator
from plone.app.form.events import EditCancelledEvent, EditSavedEvent
import zope.event
import zope.lifecycleevent
from zope.formlib import form

_ = MessageFactory('themeswitcher')


class SwitcherForm(EditForm):
    
    form_fields = form.FormFields(IThemeSwitcherFormSchema)
    label = _(u'ThemeSwitcher Form')
    description = _(u'A form to apply a particular theme to this folder and'
                    u'its contents.')
    form_name = _(u'ThemeSwitcher Configuration')

    @form.action(_(u"label_save", default="Save"),
                 condition=form.haveInputWidgets,
                 name=u'save')
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, 
                             self.form_fields, 
                             data,
                             self.adapters):
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(self.context)
                )
            zope.event.notify(EditSavedEvent(self.context))
            
            annotation = IAnnotations(self.context)
            
            if data['themeswitcher_enable']:
                # Provide the themeswitcher interface to the context
                alsoProvides(self.context, IThemeSwitcher)
            else:
                # No longer provide the themeswitcher interface to the context
                noLongerProvides(self.context, IThemeSwitcher)
                # Clean up after yourself, hygiene is a necessity for a 
                # healthy object to grow
                del annotation[THEMESWITCHER_ANNO]
            
            # keep the object_provides index up-to-date
            self.context.reindexObject(idxs=['object_provides'])
            
            # Register the context with the themeswitcher catalog
            # zope.event.notify(ISwitchSetEvent(self.context))
            self.status = "Changes saved"
        else:
            zope.event.notify(EditCancelledEvent(self.context))
            self.status = "No changes"
            
        url = getMultiAdapter((self.context, self.request), 
                              name='absolute_url')()
        self.request.response.redirect(url)

    @form.action(_(u"label_cancel", default=u"Cancel"),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        zope.event.notify(EditCancelledEvent(self.context))
        url = getMultiAdapter((self.context, self.request), 
                              name='absolute_url')()
        self.request.response.redirect(url)


class ThemeSwitcherFormAdapter(BaseAdapter):
    
    themeswitcher_enable = AdapterAnnotationProperty(
        IThemeSwitcherFormSchema['themeswitcher_enable'],
        ns=THEMESWITCHER_ANNO
        )
    themeswitcher_skin = AdapterAnnotationProperty(
        IThemeSwitcherFormSchema['themeswitcher_skin'],
        ns=THEMESWITCHER_ANNO
        )

