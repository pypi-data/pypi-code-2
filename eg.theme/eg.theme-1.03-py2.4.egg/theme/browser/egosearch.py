# To change this template, choose Tools | Templates
# and open the template in the editor.


from zope import interface, schema
from z3c.form import form, field, button, browser, widget
from plone.z3cform.layout import wrap_form
import datetime
from z3c.form import interfaces
from z3c.form.browser import checkbox
from z3c.form.testing import TestRequest

from Products.CMFCore.utils import getToolByName


class IEgoSearch(interface.Interface):

    SearchableText = schema.TextLine(title=u"Full Text", description=u"Fulltext \
        search including title, description and text body.",
        required = False)
    author = schema.TextLine(title=u"Author", description=u"Please specify the\
        user id.",
        required = False)

    date_von = schema.Int(title=u"Startdatum", required = False,
                            description=u"Please enter a start intervall.Value must be 4 digit - e.g. '1600' or '1850'.")
    date_bis = schema.Int(title=u"Enddatum", required = False,
                            description=u"Please enter an end intervall. Value must be 4 digit - e.g. '1600' or '1850'.")


#    topic = schema.Choice(title=u"Topic", vocabulary = "eg.theme.vocabularies.topics")
#    area = schema.Choice(title=u"Area", vocabulary = "eg.theme.vocabularies.area")
    topic = schema.List (title = u"Topic", description = u"Please limit your \
        search by selecting one or multiple items from the list.",
        value_type=schema.Choice(vocabulary="eg.theme.vocabularies.topics"),
        default = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        required = False)
    area = schema.List(title = u"Area ", description = u"Please limit your \
        search by selecting one or multiple items from the list.",
        value_type=schema.Choice(vocabulary="eg.theme.vocabularies.area"),
        default = ['0', '1', '2', '3', '4', '5', '6'],
        required = False)
    thread = schema.Choice(title=u"Thread", description=u"Please specify a thread.",
        vocabulary = "eg.theme.vocabularies.thread",
        default='10',
        required = False)
#    thread = schema.List(title=u"Thread", description=u"Please specify a thread.",
#        value_type=schema.Choice(vocabulary = "eg.theme.vocabularies.thread"),
#        default=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ],
#        required = False)
#    limit_to = schema.List(title = u"Limit ", description = u"Please limit your \
#        search by selecting one or multiple items from the list",
#        value_type=schema.Choice(values=('Text', 'Video', 'Audio', 'Images')),
#        default=['Text', 'Video', 'Audio', 'Images'])
#    text = schema.Bool(default=True, title=u"Text")
#    video = schema.Bool (default=True, title = u'Video')
#    audio = schema.Bool (default=True, title = u'Audio')
#    images = schema.Bool (default=True, title = u'Images')
    item_type = schema.List(title=u"Type", description=u"Please select one or more\
        type(s) to refine your search.",
        value_type=schema.Choice(vocabulary="eg.theme.vocabularies.media"),
        default=['n', 'a', 'i', 'v', 'o'],
        required = False)


class EgoSearchForm(form.Form):

    fields = field.Fields(IEgoSearch)
    ignoreContext = True
    label = u"Ego Advanced Search"
    
#    def GetMemberFullName(self):
#        member_fullname = []
#        membership = getToolByName(self.context, 'portal_membership')
#        for member in membership.listMembers():
#            member_fullname.append(member.getProperty('fullname'))
#        return member_fullname

    def MemberList(context):
        mlist = []
        membership = getToolByName(context, 'portal_membership')
        for m in membership.listMemberIds():
            mlist.append(membership.getMemberInfo(m)['fullname'])
        return mlist


    def MyFieldWidget(field, req):
        return widget.FieldWidget(field, checkbox.SingleCheckBoxWidget(req))

#    fields['images'].widgetFactory = MyFieldWidget

    def MyMultiSelectWidget(field, req):
        return widget.FieldWidget(field, checkbox.CheckBoxWidget(req))
    
    fields['area'].widgetFactory = MyMultiSelectWidget
    fields['topic'].widgetFactory = MyMultiSelectWidget
#    fields['thread'].widgetFactory = MyMultiSelectWidget
    fields['item_type'].widgetFactory = MyMultiSelectWidget

#    def MyMultiWidget(field, req):
#        return widget.MultiWidget(field, multi.MultiWidget(req))
#
#    fields['date'].widgetFactory = MyMultiWidget

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @button.buttonAndHandler(u"Search")
    def handleSearch(self, action):
        data, errors = self.extractData()
#        am = MemberList()
        if errors:
            return
        base_url = "%s/search" % self.portal.absolute_url()
        qstring = "?portal_type=Document"
        if data['SearchableText'] is not None:
            qstring += "&SearchableText=%s" % data['SearchableText']
        else:
            qstring += "&SearchableText=%s" % ''
        if data['author'] is not None:
#            if data['author'] in am:
#                qstring+="&Test=%s" % data['author']
            qstring+="&Creator=%s" % data['author']
        else:
            qstring += "&Creator=%s" % ''
        if data['date_von'] is not None:
            qstring += "&timefrom:int=%s&timefrom_usage=range:min" % data['date_von']
        else:
            qstring = qstring
        if data['date_bis'] is not None:
            qstring += "&timeuntil:int=%s&timeuntil_usage=range:max" % data['date_bis']
        else:
            qstring = qstring
        qstring += "&topic=%s" % '+OR+'.join(data['topic'])
        qstring += "&area=%s" % '+OR+'.join(data['area'])
        if data['thread'] == '10':
            qstring += "&thread=%s" % ''
        else:
            qstring += "&thread=%s" % data['thread']
        qstring += "&mediacontent=%s" % '+OR+'.join(data ['item_type'])
        qstring += "&sort_on=effective&sort_order=descending"
        self.request.response.redirect(base_url + qstring)

EgoSearchView = wrap_form(EgoSearchForm)

#class EgoSearchForm(form.Form):
#
#    fields = field.Fields(IEgoSearch)
#    ignoreContext = True
#    label = u"Ego Advanced Search"
#
#
#    @button.buttonAndHandler(u"Search")
#    def handleSearch(self, action):
#        data, errors = self.extractData()
#        self.status = data
#
#EgoSearchView = wrap_form(EgoSearchForm)

