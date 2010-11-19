import datetime

from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.models import User
from django.views.generic.list_detail import object_detail
from django.views.generic import date_based

# Replacement for django.views.generic.list_detail.object_list which
# accepts lists of objects as well as querysets.
from birdland.views.object_list import object_list
# Replacements for django.views.generic.date_based which allow for pagination.
from birdland.views.date_based import archive_year, archive_month, \
        archive_week, archive_day

from birdland.models import Entry
from birdland.conf import settings

if settings.TAGGING_ENABLED:
    from tagging.models import Tag
    from tagging.views import tagged_object_list

# Common parameters

published_entries = Entry.objects.published().select_related()

# Author views

def author_list(request, template_object_name='author',
        template_name='birdland/author_list.html', **kwargs):
    """
    A wrapper around ``birdland.views.object_list.object_list`` which
    creates a ``QuerySet`` of all ``django.contrib.auth.models.User``
    objects associated with all published ``Entry`` which is passed
    to ``birdland.views.object_list.object_list``.

    Templates: ``birdland/author_list.html``

    Context:
        author_list
            list of ``django.contrib.auth.models.User`` objects

    """
    author_list = User.objects.distinct().filter(
        entries__status=Entry.PUBLISH_STATUS,
        entries__publish__lte=datetime.datetime.now()
        )
    return object_list(request,
                       author_list,
                       template_object_name=template_object_name,
                       template_name=template_name,
                       **kwargs)

def entry_archive_author(request, username=None, template_object_name='entry',
        template_name='birdland/entry_archive_author.html', **kwargs):
    """
    A wrapper around ``birdland.views.object_list.object_list`` which
    creates a ``QuerySet`` of all published ``Entry`` objects for which
    the ``django.contrib.auth.models.User`` retrieved by ``username`` is
    the ``author``.

    Templates: ``birdland/entry_archive_author.html``

    Context:
        entry_list
            list of ``Entry`` objects

        author
            the ``auth.User`` object for the author

    """
    user = get_object_or_404(User, username=username)
    author_entries = published_entries.filter(author=user)
    extra_context = kwargs.pop('extra_context', {})
    extra_context['author'] = user
    return object_list(request,
                       author_entries,
                       template_object_name=template_object_name,
                       template_name=template_name,
                       extra_context=extra_context,
                       **kwargs)

# Entry views

def entry_detail(request, slug, template_object_name='entry', **kwargs):
    """
    A wrapper around ``django.views.generic.list_detail.object_detail``
    which passes ``object_detail`` a ``QuerySet`` of all published
    entries and an ``Entry`` slug.

    Templates: ``birdland/entry_detail.html``

    Context:
        entry
            the ``Entry`` object

    """
    return object_detail(request,
                         published_entries,
                         slug=slug,
                         slug_field='slug',
                         template_object_name=template_object_name,
                         **kwargs)

def entry_list(request, template_object_name='entry', **kwargs):
    """
    A wrapper around ``birdland.views.object_list.object_list`` which
    passes ``object_list`` a ``QuerySet`` of all published ``Entry``
    objects.

    Templates: ``birdland/entry_list.html``

    Context:
        entry_list
            list of ``Entry`` objects

    """
    return object_list(request,
                       published_entries,
                       template_object_name=template_object_name,
                       **kwargs)
    
# Date-based entry views

def entry_archive_year(request, year, template_object_name='entry',
                       date_field='publish', make_object_list=True, **kwargs):
    """
    A wrapper around ``birdland.views.date_based.archive_year`` which
    passes ``archive_year`` a ``QuerySet`` of all published ``Entry``
    objects.

    Templates: ``birdland/entry_archive_year.html``

    Context:
        entry_list
            list of ``Entry`` objects

    """
    return archive_year(request,
                        year,
                        published_entries,
                        date_field=date_field,
                        template_object_name=template_object_name,
                        make_object_list=make_object_list,
                        **kwargs)

def entry_archive_month(request, year, month, template_object_name='entry',
                        date_field='publish', **kwargs):
    """
    A wrapper around ``birdland.views.date_based.archive_month`` which
    passes ``archive_month`` a ``QuerySet`` of all published ``Entry``
    objects.

    Templates: ``birdland/entry_archive_month.html``

    Context:
        entry_list
            list of ``Entry`` objects

    """
    return archive_month(request,
                         year,
                         month,
                         published_entries,
                         date_field=date_field,
                         template_object_name=template_object_name,
                         **kwargs)

def entry_archive_week(request, year, week, template_object_name='entry',
                       date_field='publish', **kwargs):
    """
    A wrapper around ``birdland.views.date_based.archive_week`` which
    passes ``archive_week`` a ``QuerySet`` of all published ``Entry``
    objects.

    Templates: ``birdland/entry_archive_week.html``

    Context:
        entry_list
            list of ``Entry`` objects

    """
    return archive_week(request,
                        year,
                        week,
                        published_entries,
                        date_field=date_field,
                        template_object_name=template_object_name,
                         **kwargs)

def entry_archive_day(request, year, month, day, date_field='publish',
                      template_object_name='entry', **kwargs):
    """
    A wrapper around ``birdland.views.date_based.archive_day`` which
    passes ``archive_day`` a ``QuerySet`` of all published ``Entry``
    objects.

    Templates: ``birdland/entry_archive_day.html``

    Context:
        entry_list
            list of ``Entry`` objects

    """
    return archive_day(request,
                       year,
                       month,
                       day,
                       published_entries,
                       date_field=date_field,
                       template_object_name=template_object_name,
                       **kwargs)

def entry_archive_today(request, **kwargs):
    """
    Returns ``entry_archive_day`` with today's date.

    """
    from datetime import date
    today = date.today()
    return entry_archive_day(request,
                             year=str(today.year),
                             month=today.strftime('%b').lower(),
                             day=str(today.day),
                             **kwargs)

def entry_archive_detail(request, year, month, day, date_field='publish',
                         template_object_name='entry', **kwargs):
    """
    Returns ``django.views.generic.date_based.object_detail`` with appropriate defaults.

    """
    return date_based.object_detail(
        request,
        year, month, day,
        published_entries,
        date_field=date_field,
        slug_field='slug',
        template_object_name=template_object_name,
        **kwargs)

# Tagging views (if tagging is enabled)

if settings.TAGGING_ENABLED:
    def entry_archive_tag(request, tag, template_object_name='entry',
            template_name='birdland/entry_archive_tag.html', **kwargs):
        """
        A wrapper around ``tagging.views.tagged_object_list`` which
        passes ``tagged_object_list`` a ``QuerySet`` of all published
        ``Entry`` objects.

        Templates: ``birdland/entry_archive_tag.html``

        Context:
            entry_list
                list of ``Entry`` objects

        """
        return tagged_object_list(request,
                                  queryset_or_model=published_entries,
                                  tag=tag,
                                  template_object_name=template_object_name,
                                  template_name=template_name,
                                  **kwargs)

    def entry_tag_list(request, template_object_name='tag',
            template_name='birdland/entry_tag_list.html', **kwargs):
        """
        A wrapper around ``birdland.views.object_list.object_list`` which
        passes a ``list`` of all ``tagging.models.Tag`` objects associated
        with published ``Entry`` objects.

        Templates: ``birdland/entry_tag_list.html``

        Context:
            tag_list
                list of ``tagging.models.Tag`` objects

        """
        tags = Tag.objects.usage_for_model(
                    Entry,
                    counts=True,
                    filters=dict(status=Entry.PUBLISH_STATUS)
        )
        return object_list(request, tags,
                           template_object_name=template_object_name,
                           template_name=template_name, **kwargs)
