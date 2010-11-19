import datetime
import random

from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.utils.translation import ugettext_lazy as _

from birdland.conf import settings
from birdland.models import Entry

register = Library()

class AuthorListNode(Node):
    def __init__(self, context_var):
        self.context_var = context_var

    def render(self, context):
        from django.contrib.auth.models import User
        authors = User.objects.filter(
            entries__status=Entry.PUBLISH_STATUS,
            entries__publish__lte=datetime.datetime.now()
        ).distinct()
        context[self.context_var] = authors
        return ''

class LatestEntriesNode(Node):
    def __init__(self, context_var, count):
        self.context_var = context_var
        self.count = count

    def render(self, context):
        context[self.context_var] = Entry.objects.published().all()[:self.count]
        return ''

class LatestEntriesForAuthorNode(Node):
    def __init__(self, author, context_var, count):
        self.author = Variable(author)
        self.context_var = context_var
        self.count = count

    def render(self, context):
        try:
            author = self.author.resolve(context)
            qs = Entry.objects.published().filter(author=author)[:self.count]
            context[self.context_var] = qs
        except VariableDoesNotExist:
            pass
        return ''

class RandomEntriesNode(Node):
    def __init__(self, context_var, limit):
        self.context_var = context_var
        self.limit = limit

    def render(self, context):
        qs = Entry.objects.published()
        entry_ids = qs.values_list('id', flat=True)
        count = min(limit, qs.count())
        random_ids = random.sample(entry_ids, count)
        random_entries = qs.filter(id__in=entry_ids)
        context[self.context_var] = random_entries
        return ''

class RandomEntriesForAuthorNode(Node):
    def __init__(self, author_var, context_var, limit):
        self.author_var = author_var
        self.context_var = context_var
        self.limit = limit

    def render(self, context):
        try:
            author = Variable(self.author_var).resolve(context)
            qs = Entry.objects.published().filter(author=author)
            entry_ids = qs.values_list('id', flat=True)
            count = min(limit, qs.count())
            random_ids = random.sample(entry_ids, count)
            random_entries = qs.filter(id__in=random_ids)
            context[self.context_var] = random_entries
        except VariableDoesNotExist:
            pass
        return ''

class YearListNode(Node):
    def __init__(self, context_var):
        self.context_var = context_var

    def render(self, context):
        qs = Entry.objects.published()
        context[self.context_var] = qs.dates('publish', 'year')
        return ''

class MonthListNode(Node):
    def __init__(self, year, context_var):
        self.year = year
        self.context_var = context_var

    def render(self, context):
        try:
            year = int(self.year)
        except ValueError:
            try:
                year = Variable(self.year).resolve(context)
                try:
                    year = year.year
                except AttributeError:
                    year = int(year)
            except (VariableDoesNotExist, ValueError):
                return ''
        queryset = Entry.objects.published().filter(publish__lte=datetime.datetime.now()).filter(publish__year=year)
        context[self.context_var] = queryset.dates('publish', 'month')
        return ''


def do_entry_authors_list(parser, token):
    """
    Retrieves a list of ``django.contrib.auth.models.User`` objects associated
    with all published ``Entry`` objects and stores the list in a context
    variable.

    Usage::

        {% entry_authors_list as [varname] %}

    Example::

        {% entry_authors_list as published_authors %}
        {% for author in published_authors %}
            {{ author.username }}
        {% endfor %}

    """
    try:
        tag_name, as_token, context_var = token.split_contents()
        if as_token != 'as':
            raise TemplateSyntaxError(_("first argument to %s must be 'as'") % tag_name)
        return AuthorListNode(context_var)
    except ValueError:
        raise TemplateSyntaxError(_('%s tag requires two arguments') % token.split_contents()[0])

def do_latest_entries_list(parser, token):
    """
    Retrieves a list of the latest published ``Entry`` objects and stores this
    list in a context variable.

    Usage::

        {% latest_entries_list as [varname] %}

    Extended usage::

        {% latest_entries_list as [varname] limit [num] %}

    If provided, the ``limit [num]`` option will limit the number of returned
    entries to a value less than ``[num]``.

    Examples::

        {% latest_entries_list as latest %}
        {% for post in latest %}
            {{ post.title }}
        {% endfor %}

        {% latest_entries_list as latest limit 10 %}

    """
    try:
        tag_name, as_token, context_var, limit_token, count = token.split_contents()
    except ValueError:
        try:
            tag_name, as_token, context_var = token.split_contents()
            limit_token, count = None, None
        except ValueError:
            raise TemplateSyntaxError(_('%s requires either two or four arguments') % token.split_contents()[0])
    if as_token != 'as':
        raise TemplateSyntaxError(_("first argument to %s must be 'as'") % tag_name)
    if limit_token and limit_token != 'limit':
        raise TemplateSyntaxError(_("third argument to %s must be 'limit'") % tag_name)
    return LatestEntriesNode(context_var, count)

def do_latest_entries_for_author_list(parser, token):
    """
    Retrieves a list of the latest published ``Entry`` objects for a
    ``django.contrib.auth.models.User`` instance contained in the given
    context variable and stores this list in another context variable.

    Usage::

        {% latest_entries_for_author_list [user-varname] as [varname] %}

    Extended usage::

        {% latest_entries_for_author_list [user-varname] as [varname] limit [num] %}

    If provided, the ``limit [num]`` argument will limit the length of the
    returned list to less than or equal to ``[num]``.

    Examples::

        {% latest_entries_for_author_list entry.author as author_latest %}
        {% latest_entries_for_author_list entry.author as author_latest limit 5 %}

    """
    try:
        tag_name, author, as_token, context_var, limit_token, count = token.split_contents()
    except ValueError:
        try:
            tag_name, author, as_token, context_var = token.split_contents()
            limit_token, count = None, None
        except ValueError:
            raise TemplateSyntaxError(_('%s requires either three or five arguments') % token.split_contents()[0])
    if as_token != 'as':
        raise TemplateSyntaxError(_("second argument to %s must be 'as'") % tag_name)
    if limit_token and limit_token != 'limit':
        raise TemplateSyntaxError(_("fourth argument to %s must be 'limit'") % tag_name)
    return LatestEntriesForAuthorNode(author, context_var, count)

def do_entry_years_list(parser, token):
    """
    Retrieves a list of ``datetime.datetime`` objects representing the years
    for which there are published ``Entry`` objects and stores this list in
    a context variable.

    Usage::

        {% entry_years_list as [varname] %}

    Example::

        {% entry_years_list as entry_years %}

    """
    try:
        tag_name, as_token, context_var = token.split_contents()
        if as_token != 'as':
            raise TemplateSyntaxError(_("first argument to %s must be 'as'") % tag_name)
        return YearListNode(context_var)
    except ValueError:
        raise TemplateSyntaxError(_('%s tag requires two arguments') % token.split_contents()[0])

def do_entry_months_list(parser, token):
    """
    Retrieves a list of ``datetime.datetime`` objects representing the months
    for which there are published ``Entry`` objects for a given year and
    stores this list in a context variable.

    The given year may be either the year in string format or the name of
    a context variable containing a string, integer, or ``datetime.datetime``
    object.

    Usage::

        {% entry_months_list [year-varname] as [varname] %}

    Example::

        {% entry_months_list entry.publish.year as other_months %}

    This tag may be used in conjunction with ``entry_years_list`` to build
    a date-based archive menu, as is shown in the extended example.

    Extended example::

        {% entry_years_list as entry_years %}
        <ul>
            {% for entry_year in entry_years %}
            <li>
                <h4>{{ entry_year.year }}</h4>
                <ul>
                    {% entry_months_list entry_year as entry_months %}
                    {% for entry_month in entry_months %}
                        <li>{{ entry_month|date:"M" }}</li>
                    {% endfor %}
                </ul>
            </li>
            {% endfor %}
        </ul>

    """
    try:
        tag_name, year, as_token, context_var = token.split_contents()
        if as_token != 'as':
            raise TemplateSyntaxError(_("first argument to %s must be 'as'") % tag_name)
        return MonthListNode(year, context_var)
    except ValueError:
        raise TemplateSyntaxError(_('%s tag requires three arguments') % token.split_contents()[0])


register.tag('entry_authors_list', do_entry_authors_list)
register.tag('latest_entries_list', do_latest_entries_list)
register.tag('latest_entries_for_author_list', do_latest_entries_for_author_list)
register.tag('entry_years_list', do_entry_years_list)
register.tag('entry_months_list', do_entry_months_list)

if settings.TAGGING_ENABLED:
    from birdland.templatetags import django_tagging_tags
    register.tag('tags_for_entries', django_tagging_tags.do_tags_for_entries)
    register.tag('tag_cloud_for_entries', django_tagging_tags.do_tag_cloud_for_entries)
    register.tag('tags_for_entry', django_tagging_tags.do_tags_for_entry)
    register.tag('tagged_entries', django_tagging_tags.do_tagged_entries)
    register.tag('related_for_entry', django_tagging_tags.do_related_for_entry)
