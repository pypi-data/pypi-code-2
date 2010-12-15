# -*- coding: utf-8 -*-
""" Renders localization and execution code for jQuery Datepicker """

from zope import component

from Products.CMFCore.utils import getToolByName

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

    def render(self):
        utool = getToolByName(self.context, "portal_url")
        ptool = getToolByName(self.context, "portal_properties")
        portal = utool.getPortalObject()
        first_day = ICalendarSchema(portal).firstweekday + 1
        future_years = ptool.site_properties.calendar_future_years_available
        return u"""\
    <script type="text/javascript">
    //<![CDATA[
    $(document).ready(function() {
      var options = {
          yearRange: 'c-%s:c+%s', firstDay: %s,
          showTrigger: '<button type="button" class="datepick">' +
                       '<img src="%s/popup_calendar.png" alt="" /></button>'
      };
      $.datepick.setDefaults($.datepick.regional['%s']);
      $(".date-widget, .datetime-widget").parent().datepick_z3cform(options);
      $(".overlay-ajax").bind("onLoad", function() {
        $(this).find(".date-widget, .datetime-widget")
          .parent().datepick_z3cform(options);
      });
    });
    //]]>
    </script>
""" % (future_years * 5, future_years, first_day,
       portal.absolute_url(), self.language)
