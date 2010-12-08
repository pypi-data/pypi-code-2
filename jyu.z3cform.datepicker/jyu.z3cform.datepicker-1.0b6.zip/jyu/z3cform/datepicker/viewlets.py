# -*- coding: utf-8 -*-
""" Renders localization and execution code for jQuery Datepicker """

from os import path

from zope import component

from z3c.form.interfaces import IFormLayer

from Products.CMFCore.utils import getToolByName

from plone.memoize import ram

from plone.app.layout.viewlets.common import ViewletBase

from plone.app.controlpanel.calendar import ICalendarSchema


class DatepickerLocale(ViewletBase):
    """ Renders localization and execution code for jQuery Datepicker.
    """

    @property
    def language(self):
        portal_state = component.getMultiAdapter(
            (self.context, self.request), name=u"plone_portal_state")
        return portal_state.language()

    @property
    @ram.cache(lambda m, self: self.language)
    def localization(self):
        utool = getToolByName(self.context, "portal_url")
        language = self.language
        candidate = path.join(path.dirname(__file__),
                              "static/jquery.datepick-%s.js" % language)
        return path.exists(candidate) and u"""\
    <script type="text/javascript" src="%s/++resource++jyu.z3cform.datepicker/jquery.datepick-%s.js"></script>
""" % (utool.getPortalObject().absolute_url(), language) or u""

    def render(self):
        utool = getToolByName(self.context, "portal_url")
        ptool = getToolByName(self.context, "portal_properties")
        portal = utool.getPortalObject()
        first_day = ICalendarSchema(portal).firstweekday + 1
        future_years = ptool.site_properties.calendar_future_years_available
        return IFormLayer in self.request.__provides__.interfaces()\
            and self.localization + u"""\
    <script type="text/javascript">
    //<![CDATA[
    jq(document).ready(function() {
      $("div + .date-widget + .date-widget + .date-widget, "
        + "div + .datetime-widget + .datetime-widget + .datetime-widget").each(function() {
        var that = this, parent = $(that).parent(),
            day = parent.children("*[id$=day]"),
            month = parent.children("*[id$=month]"),
            year = parent.children("*[id$=year]"),
        getFormDate = function() {
          if (day.val() && month.val() && year.val()) {
            return new Date(year.val(), month.val() - 1, day.val(), 12);
          } else {
            return undefined;
          }
        },
        setFormDate = function(date) {
          day.val(date.getDate());
          month.val(date.getMonth() + 1);
          year.val(date.getFullYear());
        };
        $(that).datepick({
          yearRange: 'c-%s:c+%s',
          showOnFocus: false, showAnim: '',
          firstDay: %s,
          showTrigger: '<button type="button" class="datepick">' +
                       '<img src="%s/popup_calendar.png" alt=""/></button>',
          defaultDate: getFormDate(),
          onShow: function(picker, inst) {
            picker.css("width", null);
            $(getFormDate()).each(function() {
              picker.find(".dp" + Number(this).toString()).addClass("selected");
            });
          },
          onSelect: function(dates) {
            $(that).datepick("option", "defaultDate", dates[0]);
            return setFormDate(dates[0]);
          }
        })
        $(day.toArray().concat(month.toArray()).concat(year.toArray())).bind("change", function() {
          $(getFormDate()).each(function() {
            $(that).datepick("option", "defaultDate", this);
          });
        });
      });
    });
    //]]>
    </script>
""" % (future_years * 5, future_years, first_day, portal.absolute_url()) or u""
