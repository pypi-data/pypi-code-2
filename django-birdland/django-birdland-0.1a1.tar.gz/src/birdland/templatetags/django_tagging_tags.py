from django.template import Node, Variable, TemplateSyntaxError, VariableDoesNotExist
from django.utils.translation import ugettext_lazy as _
from tagging.templatetags.tagging_tags import TagsForObjectNode
from tagging.models import TaggedItem, Tag
from birdland.models import Entry

# tagging-dependent template tags

class TagsForEntriesNode(Node):
    def __init__(self, context_var, counts):
        self.context_var = context_var
        self.counts = counts

    def render(self, context):
        context[self.context_var] = Tag.objects.usage_for_queryset(Entry.objects.published(), counts=self.counts)
        return ''

class TagCloudForEntriesNode(Node):
    def __init__(self, context_var, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):
        self.kwargs = dict(self.kwargs, filters={'status': Entry.PUBLISH_STATUS})
        context[self.context_var] = \
            Tag.objects.cloud_for_model(Entry, **self.kwargs)
        return ''

class TaggedEntriesNode(Node):
    def __init__(self, tag, context_var):
        self.tag = Variable(tag)
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = \
            TaggedItem.objects.get_by_model(Entry.objects.published(), self.tag.resolve(context))
        return ''

class RelatedEntriesNode(Node):
    def __init__(self, entry, context_var, limit):
        self.entry = Variable(entry)
        self.context_var = context_var
        self.limit = limit

    def render(self, context):
        try:
            entry = self.entry.resolve(context)
        except VariableDoesNotExist:
            return ''
        related_entries = TaggedItem.objects.get_related(entry, Entry.objects.published(), num=self.limit)
        context[self.context_var] = related_entries
        return ''


def do_tags_for_entries(parser, token):
    """
    Retrieves a list of ``Tag`` objects associated with any Entry object
    and stores them in a context variable.

    Usage::

       {% tags_for_entries as [varname] %}

    Extended usage::

       {% tags_for_entries as [varname] with counts %}

    If specified - by providing extra ``with counts`` arguments - adds
    a ``count`` attribute to each tag containing the number of Entry
    instances which have been tagged with it.

    Examples::

       {% tags_for_entries as blog_tags %}
       {% tags_for_entries as blog_tags with counts %}

    This is a slight reworking of django-tagging's ``tags_for_model`` tag.

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits not in (3, 5):
        raise TemplateSyntaxError(_('%s tag requires either two or four arguments') % bits[0])
    if bits[1] != 'as':
        raise TemplateSyntaxError(_("first argument to %s tag must be 'as'") % bits[0])
    if len_bits == 5:
        if bits[3] != 'with':
            raise TemplateSyntaxError(_("if given, third argument to %s tag must be 'with'") % bits[0])
        if bits[4] != 'counts':
            raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'counts'") % bits[0])
    if len_bits == 3:
        return TagsForEntriesNode(bits[2], counts=False)
    else:
        return TagsForEntriesNode(bits[2], counts=True)

def do_tag_cloud_for_entries(parser, token):
    """
    Retrieves a list of ``Tag`` objects for entries, with tag
    cloud attributes set, and stores them in a context variable.

    Usage::

       {% tag_cloud_for_entries as [varname] %}

    Extended usage::

       {% tag_cloud_for_entries as [varname] with [options] %}

    Extra options can be provided after an optional ``with`` argument,
    with each option being specified in ``[name]=[value]`` format. Valid
    extra options are:

       ``steps``
          Integer. Defines the range of font sizes.

       ``min_count``
          Integer. Defines the minimum number of times a tag must have
          been used to appear in the cloud.

       ``distribution``
          One of ``linear`` or ``log``. Defines the font-size
          distribution algorithm to use when generating the tag cloud.

    Examples::

       {% tag_cloud_for_entries as blog_tags %}
       {% tag_cloud_for_entries as blog_tags with steps=9 min_count=3 distribution=log %}

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 3 and len_bits not in range(5, 8):
        raise TemplateSyntaxError(_('%s tag requires either two or between four and six arguments') % bits[0])
    if bits[1] != 'as':
        raise TemplateSyntaxError(_("first argument to %s tag must be 'as'") % bits[0])
    kwargs = {}
    if len_bits > 4:
        if bits[3] != 'with':
            raise TemplateSyntaxError(_("if given, third argument to %s tag must be 'with'") % bits[0])
        for i in range(4, len_bits):
            try:
                name, value = bits[i].split('=')
                if name == 'steps' or name == 'min_count':
                    try:
                        kwargs[str(name)] = int(value)
                    except ValueError:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                elif name == 'distribution':
                    if value in ['linear', 'log']:
                        kwargs[str(name)] = {'linear': LINEAR, 'log': LOGARITHMIC}[value]
                    else:
                        raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid choice: '%(value)s'") % {
                            'tag': bits[0],
                            'option': name,
                            'value': value,
                        })
                else:
                    raise TemplateSyntaxError(_("%(tag)s tag was given an invalid option: '%(option)s'") % {
                        'tag': bits[0],
                        'option': name,
                    })
            except ValueError:
                raise TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': bits[i],
                })
    return TagCloudForEntriesNode(bits[2], **kwargs)

def do_tags_for_entry(parser, token):
    """
    Retrieves a list of ``Tag`` objects associated with an entry and
    stores them in a context variable.

    Usage::

       {% tags_for_entry [entry] as [varname] %}

    Example::

        {% tags_for_entry foo_object as tag_list %}

    This is a light wrapper around django-tagging's ``tags_for_object`` tag.

    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(_('%s tag requires exactly three arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    return TagsForObjectNode(bits[1], bits[3])

def do_tagged_entries(parser, token):
    """
    Retrieves a list of entries which are tagged with a given ``Tag``
    and stores them in a context variable.

    Usage::

       {% tagged_entries [tag] as [varname] %}

    The model is specified in ``[appname].[modelname]`` format.

    The tag must be an instance of a ``Tag``, not the name of a tag.

    Example::

        {% tagged_entries comedy_tag as comedies %}

    This is a light wrapper around django-tagging's ``tagged_objects`` tag.

    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(_('%s tag requires exactly three arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    return TaggedEntriesNode(bits[1], bits[3])

def do_related_for_entry(parser, token):
    """
    Retrieves a list of ``Entry`` objects which have one or more tags in
    common with the given ``Entry`` object.

    Usage::

        {% related_for_entry [entry] as [varname] %}

    Extended Usage::

        {% related_for_entry [entry] as [varname] limit [num] %}

    If specified - an extra ``limit`` option will limit the number of returned
    ``Entry`` objects to a quantity less than or equal to the provided ``num``.

    Examples::

        {% related_for_entry [entry] as related_posts %}
        {% related_for_entry [entry] as related_posts limit 5 %}

    """
    bits = token.split_contents()
    bits_len = len(bits)
    if bits_len not in (4, 6):
        raise TemplateSyntaxError(_('%s tag requires three or five arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    limit = None
    if bits_len == 6:
        if bits[4] != 'limit':
            raise TemplateSyntaxError(_("fourth argument to %s tag must be 'limit'") % bits[0])
        try:
            limit = int(bits[5])
        except ValueError:
            raise TemplateSyntaxError(_("the argument after 'limit' must be a positive integer"))
    return RelatedEntriesNode(bits[1], bits[3], limit)
