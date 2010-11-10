import re

from docutils import nodes, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst.roles import _role_registry

explicit_title_re = re.compile(r'^(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)


def escape(html):
    """
    Escape HTML entities
    """
    html_codes = (
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),)

    for code in html_codes:
        html = html.replace(code[0], code[1])

    return html


def split_explicit_title(text):
    """Split role content into title and target, if given."""
    match = explicit_title_re.match(text)
    if match:
        return True, match.group(1), match.group(2)
    return False, text, text


def register_canonical_role(name, role_fn):
    """
    Register an interpreted text role by its canonical name.

    :Parameters:
      - `name`: The canonical name of the interpreted role.
      - `role_fn`: The role function.  See the module docstring.
    """
    set_implicit_options(role_fn)
    _role_registry[name] = role_fn


def doc_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Provides a role for converting :doc:`a link <to_this>` into <a
    href="to_this" rel="doc-link">a link</a>
    """
    options['format'] = 'html'
    link_format = '<a href="%s" rel="doc-link">%s</a>'

    matches, title, link = split_explicit_title(text)
    # We want to make sure that the link is "somefile.rst"
    assert '.rst' in link.lower()
    link = link_format % (escape(link), title,)
    node = nodes.raw(rawtext, utils.unescape(link, 1), **options)
    return [node], []


def set_implicit_options(role_fn):
    """
    Add customization options to role functions, unless explicitly set or
    disabled.
    """
    if not hasattr(role_fn, 'options') or role_fn.options is None:
        role_fn.options = {'class': directives.class_option}
    elif 'class' not in role_fn.options:
        role_fn.options['class'] = directives.class_option

doc_role.options = {'format': directives.unchanged}

register_canonical_role('doc', doc_role)
