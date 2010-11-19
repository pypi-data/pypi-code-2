import datetime
import time

from django.template import loader, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.core.xheaders import populate_xheaders
from django.db.models.fields import DateTimeField
from django.http import Http404, HttpResponse
from django.core.paginator import QuerySetPaginator, InvalidPage


def archive_index(request, queryset, date_field, num_latest=15,
        page=None, template_name=None, template_loader=loader,
        extra_context=None, allow_empty=True, context_processors=None,
        mimetype=None, allow_future=False, template_object_name='latest'):
    """
    Generic top-level archive of date-based objects.

    A replacement for ``django.views.generic.date_based.archive_index``
    which offers result-set pagination.

    Templates: ``<app_label>/<model_name>_archive.html``
    Context:
        date_list
            List of years
        latest
            Latest N (defaults to 15) objects by date
        paginator
           ``django.core.paginator.Paginator`` object
           (if ``num_latest`` provided)
        page_obj
           ``django.core.paginator.Page`` object
           (if ``num_latest`` provided)
    """
    if extra_context is None: extra_context = {}
    model = queryset.model
    if not allow_future:
        queryset = queryset.filter(**{'%s__lte' % date_field: datetime.datetime.now()})
    date_list = queryset.dates(date_field, 'year')[::-1]
    if not date_list and not allow_empty:
        raise Http404, "No %s available" % model._meta.verbose_name

    if date_list and num_latest:
        latest = queryset.order_by('-'+date_field)
        paginator = QuerySetPaginator(latest, per_page=num_latest, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        c = RequestContext(request, {
            'date_list': date_list,
            template_object_name: page_obj.object_list,
            'paginator': paginator,
            'page_obj': page_obj,
        }, context_processors)
    else:
        latest = None
        c = RequestContext(request, {
            'date_list' : date_list,
            template_object_name : latest,
            'paginator': None,
            'page_obj': None,
        }, context_processors)
    if not template_name:
        template_name = "%s/%s_archive.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)

    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)

def archive_year(request, year, queryset, date_field, template_name=None,
        template_loader=loader, extra_context=None, allow_empty=False,
        context_processors=None, template_object_name='object', mimetype=None,
        make_object_list=False, allow_future=False, paginate_by=None, page=None):
    """
    Generic yearly archive view.

    A replacement for ``django.views.generic.date_based.archive_year``
    which offers result-set pagination.

    Templates: ``<app_label>/<model_name>_archive_year.html``
    Context:
        date_list
            List of months in this year with objects
        year
            This year
        object_list
            List of objects published in the given month
            (Only available if make_object_list argument is True)
        paginator
            ``django.core.paginator.Paginator`` object
            (Only available if make_object_list argument is True)
        page_obj
            ``django.core.paginator.Page`` object
            (Only available if make_object_list argument is True)
    """
    if extra_context is None: extra_context = {}
    model = queryset.model
    now = datetime.datetime.now()

    lookup_kwargs = {'%s__year' % date_field: year}

    # Only bother to check current date if the year isn't in the past and future objects aren't requested.
    if int(year) >= now.year and not allow_future:
        lookup_kwargs['%s__lte' % date_field] = now
    date_list = queryset.filter(**lookup_kwargs).dates(date_field, 'month')
    if not date_list and not allow_empty:
        raise Http404

    if make_object_list:
        object_list = queryset.filter(**lookup_kwargs)
        paginator = QuerySetPaginator(object_list, per_page=paginate_by, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        c = RequestContext(request, {
            'date_list': date_list,
            'year': year,
            '%s_list' % template_object_name: page_obj.object_list,
            'paginator': paginator,
            'page_obj': page_obj,
        }, context_processors)
    else:
        object_list = []
        c = RequestContext(request, {
            'date_list': date_list,
            'year': year,
            '%s_list' % template_object_name: object_list,
            'paginator': None,
            'page_obj': None,
        }, context_processors)

    if not template_name:
        template_name = "%s/%s_archive_year.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)

def archive_month(request, year, month, queryset, date_field, paginate_by=None,
        page=None, month_format='%b', template_name=None, template_loader=loader,
        extra_context=None, allow_empty=False, context_processors=None,
        template_object_name='object', mimetype=None, allow_future=False):
    """
    Generic monthly archive view.

    A replacement for ``django.views.generic.date_based.archive_month``
    which offers result-set pagination.

    Templates: ``<app_label>/<model_name>_archive_month.html``
    Context:
        month:
            (date) this month
        next_month:
            (date) the first day of the next month, or None if the next month is in the future
        previous_month:
            (date) the first day of the previous month
        object_list:
            list of objects published in the given month
        paginator:
            ``django.core.paginator.Paginator`` object
            (Available only if paginate_by and page provided)
        page_obj:
            ``django.core.paginator.Page`` object
            (Available only if paginate_by and page provided)
    """
    if extra_context is None: extra_context = {}
    try:
        date = datetime.date(*time.strptime(year+month, '%Y'+month_format)[:3])
    except ValueError:
        raise Http404

    model = queryset.model
    now = datetime.datetime.now()

    # Calculate first and last day of month, for use in a date-range lookup.
    first_day = date.replace(day=1)
    if first_day.month == 12:
        last_day = first_day.replace(year=first_day.year + 1, month=1)
    else:
        last_day = first_day.replace(month=first_day.month + 1)
    lookup_kwargs = {'%s__range' % date_field: (first_day, last_day)}

    # Only bother to check current date if the month isn't in the past and future objects are requested.
    if last_day >= now.date() and not allow_future:
        lookup_kwargs['%s__lte' % date_field] = now
    object_list = queryset.filter(**lookup_kwargs)
    if not object_list and not allow_empty:
        raise Http404

    # Calculate the next month, if applicable.
    if allow_future:
        next_month = last_day + datetime.timedelta(days=1)
    elif last_day < datetime.date.today():
        next_month = last_day + datetime.timedelta(days=1)
    else:
        next_month = None

    if paginate_by:
        paginator = QuerySetPaginator(object_list, per_page=paginate_by, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        c = RequestContext(request, {
            'month': date,
            'next_month': next_month,
            'previous_month': first_day - datetime.timedelta(days=1),
            '%s_list' % template_object_name: page_obj.object_list,
            'paginator': paginator,
            'page_obj': page_obj,
        }, context_processors)
    else:
        c = RequestContext(request, {
            '%s_list' % template_object_name: object_list,
            'month': date,
            'next_month': next_month,
            'previous_month': first_day - datetime.timedelta(days=1),
            'paginator': None,
            'page_obj': None,
        }, context_processors)

    if not template_name:
        template_name = "%s/%s_archive_month.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)

    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)

def archive_week(request, year, week, queryset, date_field, paginate_by=None,
        page=None, template_name=None, template_loader=loader,
        extra_context=None, allow_empty=True, context_processors=None,
        template_object_name='object', mimetype=None, allow_future=False):
    """
    Generic weekly archive view.

    A replacement for ``django.views.generic.date_based.archive_week``
    which offers result-set pagination.

    Templates: ``<app_label>/<model_name>_archive_week.html``
    Context:
        week:
            (date) this week
        object_list:
            list of objects published in the given week
        paginator:
            ``django.core.paginator.Paginator`` object
            (Available only if paginate_by and page are provided)
        page_obj:
            ``django.core.paginator.Page`` object
            (Available only if paginate_by and page are provided)
    """
    if extra_context is None: extra_context = {}
    try:
        date = datetime.date(*time.strptime(year+'-0-'+week, '%Y-%w-%U')[:3])
    except ValueError:
        raise Http404

    model = queryset.model
    now = datetime.datetime.now()

    # Calculate first and last day of week, for use in a date-range lookup.
    first_day = date
    last_day = date + datetime.timedelta(days=7)
    lookup_kwargs = {'%s__range' % date_field: (first_day, last_day)}

    # Only bother to check current date if the week isn't in the past and future objects aren't requested.
    if last_day >= now.date() and not allow_future:
        lookup_kwargs['%s__lte' % date_field] = now
    object_list = queryset.filter(**lookup_kwargs)
    if not object_list and not allow_empty:
        raise Http404

    if paginate_by:
        paginator = QuerySetPaginator(object_list, per_page=paginate_by, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        c = RequestContext(request, {
            'week': date,
            '%s_list' % template_object_name: page_obj.object_list,
            'paginator': paginator,
            'page_obj': page_obj,
        }, context_processors)
    else:
        c = RequestContext(request, {
            '%s_list' % template_object_name: object_list,
            'week': date,
            'paginator': None,
            'page_obj': None,
        }, context_processors)

    if not template_name:
        template_name = "%s/%s_archive_week.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)

    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)

def archive_day(request, year, month, day, queryset, date_field,
        paginate_by=None, page=None,
        month_format='%b', day_format='%d', template_name=None,
        template_loader=loader, extra_context=None, allow_empty=False,
        context_processors=None, template_object_name='object',
        mimetype=None, allow_future=False):
    """
    Generic daily archive view.

    A replacement for ``django.views.generic.date_based.archive_day``
    which offers result-set pagination.

    Templates: ``<app_label>/<model_name>_archive_day.html``
    Context:
        object_list:
            list of objects published that day
        day:
            (datetime) the day
        previous_day
            (datetime) the previous day
        next_day
            (datetime) the next day, or None if the current day is today
        paginator:
            ``django.core.paginator.Paginator`` object
            (Available only if paginate_by and page are provided)
        page_obj:
            ``django.core.paginator.Page`` object
            (Available only if paginate_by and page are provided)
    """
    if extra_context is None: extra_context = {}
    try:
        date = datetime.date(*time.strptime(year+month+day, '%Y'+month_format+day_format)[:3])
    except ValueError:
        raise Http404

    model = queryset.model
    now = datetime.datetime.now()

    if isinstance(model._meta.get_field(date_field), DateTimeField):
        lookup_kwargs = {'%s__range' % date_field: (datetime.datetime.combine(date, datetime.time.min), datetime.datetime.combine(date, datetime.time.max))}
    else:
        lookup_kwargs = {date_field: date}

    # Only bother to check current date if the date isn't in the past and future objects aren't requested.
    if date >= now.date() and not allow_future:
        lookup_kwargs['%s__lte' % date_field] = now
    object_list = queryset.filter(**lookup_kwargs)
    if not allow_empty and not object_list:
        raise Http404

    # Calculate the next day, if applicable.
    if allow_future:
        next_day = date + datetime.timedelta(days=1)
    elif date < datetime.date.today():
        next_day = date + datetime.timedelta(days=1)
    else:
        next_day = None

    if paginate_by:
        paginator = QuerySetPaginator(object_list, per_page=paginate_by, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        c = RequestContext(request, {
            'day': date,
            'previous_day': date - datetime.timedelta(days=1),
            'next_day': next_day,
            '%s_list' % template_object_name: page_obj.object_list,
            'paginator': paginator,
            'page_obj': page_obj,
        }, context_processors)
    else:
        c = RequestContext(request, {
            '%s_list' % template_object_name: object_list,
            'day': date,
            'previous_day': date - datetime.timedelta(days=1),
            'next_day': next_day,
            'paginator': None,
            'page_obj': None,
        }, context_processors)


    if not template_name:
        template_name = "%s/%s_archive_day.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)

    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)
