# -*- coding: utf-8 -*-
"""template-specific forms/views/actions/components"""
import datetime

from logilab.common.date import todate, last_day

from cubicweb import target
from cubicweb.view import EntityAdapter
from cubicweb.selectors import is_instance
from cubicweb.web import uicfg, action
from cubicweb.web.views import ibreadcrumbs

_ = unicode

_afs = uicfg.autoform_section
_afs.tag_object_of(('*', 'periods', 'Timeperiod'), 'main', 'attributes')
_afs.tag_object_of(('*', 'periods', 'Timeperiod'), 'muledit', 'attributes')

_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('Calendar', 'weekdays', '*'), 'hidden')
_pvs.tag_subject_of(('Calendar', 'days', '*'), 'hidden')
_pvs.tag_subject_of(('Calendar', 'periods', '*'), 'hidden')
_pvs.tag_subject_of(('Calendar', 'day_types', '*'), 'hidden')
_pvs.tag_subject_of(('Calendar', 'inherits', '*'), 'hidden')

_abaa = uicfg.actionbox_appearsin_addmenu
for rtype in ('days', 'weekdays', 'periods', 'day_types', 'inherits'):
    _abaa.tag_subject_of(('Calendar', rtype, '*'), True)
_abaa.tag_object_of(('Calendar', 'inherits', '*'), True)
_abaa.tag_object_of(('*', 'for_calendar', 'Calendar'), True)
_abaa.tag_object_of(('*', 'for_period', 'Timeperiod'), True)


def daytype_choices(form, field, limit=None):
    req = form._cw
    # FIXME: holidays should have their own type and we shuold not rely
    #        on application-defined vocabulary
    if 'holidays' in req.form:
        rset = req.execute(u'Any D,DT WHERE D is Daytype, D title DT, '
                           u'D title IN ("journée de congés", "matinée de congés", "après-midi de congés", "non travaillé", "journée de mat-paternité")')
    else:
        rset = req.execute(u'Any D,DT WHERE D is Daytype, D title DT')
    return [(e.view('combobox'), e.eid) for e in rset.entities()]

_affk = uicfg.autoform_field_kwargs
_affk.tag_subject_of(('Timeperiod', 'day_type', '*'),
                     {'choices': daytype_choices})

def _parse_datestr(datestr):
    if len(datestr) == 4:
        datestr += '0101'
    elif len(datestr) == 6:
        datestr += '01'
    return todate(datetime.datetime.strptime(datestr, '%Y%m%d'))

def get_date_range_from_reqform(reqform, autoset_lastday=False):
    lastday = None
    if 'firstday' in reqform:
        firstday = _parse_datestr(reqform['firstday'])
        if 'lastday' in reqform:
            lastday = _parse_datestr(reqform['lastday'])
    else:
        firstday = datetime.date.today()
    if lastday is None and autoset_lastday:
        lastday = last_day(firstday)
    return todate(firstday), lastday

class AskOffDays(action.LinkToEntityAction):
    __regid__ = 'ask-off-days'
    title = _('ask_off_days')
    __select__ = action.LinkToEntityAction.__select__ & is_instance('Calendar')
    target_etype = 'Timeperiod'
    role = 'subject'
    rtype = 'periods'

    def url(self):
        ttype = self.target_etype
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        linkto = '%s:%s:%s' % (self.rtype, entity.eid, target(self))
        return self._cw.build_url('add/%s' % ttype, __linkto=linkto,
                                  __redirectpath='/', holidays=1)

class TimeperiodICalendarable(EntityAdapter):
    __regid__ = 'ICalendarable'
    __select__ = is_instance('Timeperiod')
    @property
    def start(self):
        return self.entity.start
    @property
    def stop(self):
        return self.entity.stop

class CalendarIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Calendar')
    def parent_entity(self):
        parents = self.entity.inherits
        if parents:
            return parents[0]
