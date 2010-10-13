"""\
Parse Dreamweaver templates (``.dwt`` files) and pages. 
"""
import os.path 
import logging
import os
import posixpath
import re

from bn import relpath, uniform_path

log = logging.getLogger(__name__)

class TemplateError(Exception):
    """\
    Raised when a general Error in the templates.py module occurs.

    Attributes:

    ``msg``
        explanation of what the specific error is.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg



class DreamweaverTemplateInstance(object):
    """\
    Class to parse Macromedia Dreamweaver MX Template files and handle 
    the assignment of content to regions
    """

    def __init__(self, filename=None, template=None, version=4):
        """\
        Parse the Template and place the content of the editable regions of
        the template in a dictionary with the namesof the ediatable regions
        as the keys.
        """
        if filename and template:
            raise TemplateError(
                'You cannot specify both a file and template text to be used.'
            )
        self.instance_type = 'Unknown'
        self.page_regions = {}
        self.template_regions = []
        self.template = ''
        self.filename = filename
        self.updated_regions = []
        self.version = version
        if filename:
            fp=open(filename, "r")
            self.template = fp.read().decode('utf-8')
            fp.close()
        else:
            self.template = template
        # Check the template has <html> and </html> tags so that if it is
        # saved as a page, the BeginInstance comment can be added
        end_of_start_html_tag(self.template, self.filename)
        start_of_end_html_tag(self.template, self.filename)
        self.instance_type, template_path = determine_instance_type(
            self.template,
            self.version
        )
        if template_path is not None:
            self.template_path = os.path.abspath(
                os.path.join(os.path.dirname(filename), template_path)
            )
        else:
            if self.filename:
                self.template_path = os.path.abspath(self.filename)
            else:
                self.template_path = None
        # Now extract the regions
        if self.version == 4:
            name_regex=re.compile(
                r"<!--\s*?" + \
                self.instance_type.capitalize() + \
                r"BeginEditable\s*?name=\"(\W*\s*.*\w*)?\"\s*?-->"
            )
            content_regex=re.compile(
                r"<!--\s*?" + \
                self.instance_type.capitalize() + \
                r"EndEditable\s*?-->"
            )
        else:
            name_regex = re.compile(
                r'<!--(\s*?)#BeginEditable(\s*?)"(\W*\s*.*\w*)?\"(\s*?)-->'
            )
            content_regex=re.compile(
                r"<!--\s*?" + \
                #self.instance_type.capitalize() + \
                r"#EndEditable\s*?-->"
            )
        pos = 0
        prev_match = ''
        while 1:
            name_match = name_regex.search(self.template, pos)
            if not name_match:
                break
            begin = name_match.end(0)
            if version == 4:
                region_name = name_match.group(1)
            else:
                region_name = name_match.group(3)
            content_match = content_regex.search(
                self.template,
                begin
            )
            end = content_match.start(0)
            next_start = content_match.end(0)
            if self.page_regions.has_key(region_name):
                raise TemplateError(
                    'Bad template: Duplicate regions named %r found.'%(
                        region_name
                    )
                )
            self.template_regions.append(
                [
                    region_name,
                    prev_match,
                    self.template[pos:name_match.start(0)],
                    self.template[name_match.start(0):begin],
                ]
            )
            self.page_regions[region_name] = self.template[begin:end]
            # start next search where this one ended
            pos = next_start
            prev_match = content_match.group(0)
        self.template_regions.append(
            [
                None, 
                prev_match, 
                self.template[pos:],
                '',
            ]
        )

    def save_as_page(
        self, 
        filename=None, 
        template_path=None, 
        old_path=None, 
        new_path=None, 
        tidy=False
    ):
        """\
        Merge the Editable Regions with the information in the Template to 
        create the HTML page to be output. Returns the HTML.

        Each of the regions use InstanceBegin instead of TemplateBegin and 
        the whole document is wrapped in an 
        ``<!-- InstanceBegin template="..." -->`` comment

        Regions which have changed do not have there links updated as it is
        assumed you have updated them with the correct links already.
        """
        if self.instance_type == 'instance':
            if not old_path:
                # If it was loaded from a file, use that filename
                old_path = self.filename
                if not old_path:
                    raise TemplateError(
                        "Please specify 'old_path', the full path and "
                        "filename the page was loaded from."
                    )
            if new_path is None:
                # Assume we want to save it to the filename specified or back
                # to where it came from as a last resort
                new_path = filename or self.filename
                if new_path is None:
                    raise TemplateError(
                        "Please specify 'new_path', the full path and "
                        "filename the page should be saved to."
                    )
            if not template_path:
                # Assume the template path hasn't changed
                template_path = self.template_path
                if not template_path:
                    raise TemplateError(
                        "Please specify 'template_path', the full path and "
                        "filename of the template the page uses."
                    )
        else:
            # Assume it is a template being saved as a page for the first time
            if old_path:
                raise TemplateError( 
                    "You shouldn't specify 'old_path' when the template "
                    "instance was derived from a template because the "
                    "'template_path' is used instead"
                )
            if not template_path:
                template_path = self.template_path
                if not template_path:
                    raise TemplateError(
                        "Please specify 'template_path', the full path and "
                        "filename of the original template"
                    )
            old_path = template_path
            if new_path is None:
                new_path = filename
                if filename is None:
                    raise TemplateError(
                        "Please specify 'new_path', the full path and "
                        "filename of the new page to be created"
                    )
        output = []
        first = True
        site_root = os.path.sep.join(
            os.path.split(
                os.path.dirname(template_path)
            )[:-1]
        )
        for k, end, template_region, start in self.template_regions:
            template_region = update_links(
                site_root = site_root,
                old_path = old_path,
                new_path = new_path,
                content = template_region,
            )
            if self.instance_type == 'template':
                if first:
                    first = False
                    # Need to add the comment specifying the template the page 
                    # is using
                    pos = end_of_start_html_tag(template_region)
                    rel = relpath(
                        template_path, 
                        posixpath.dirname(new_path)
                    )
                    template_region = '%s%s%s' % (
                        template_region[:pos],
                        '<!-- InstanceBegin template="' + rel +\
                           '" codeOutsideHTMLIsLocked="false" -->',
                        template_region[pos:],
                    )
                    output.append(template_region)
                    output.append(
                        start.replace(
                            'TemplateBeginEditable',
                            'InstanceBeginEditable'
                        )
                    )
                    if k in self.updated_regions:
                        output.append(self.page_regions[k])
                    else:
                        output.append(
                            update_links(
                                site_root = site_root,
                                old_path = old_path,
                                new_path = new_path,
                                content = self.page_regions[k],
                            )
                        )
                elif k is not None:
                    # middle part
                    output.append(
                        end.replace(
                            'TemplateEndEditable', 
                            'InstanceEndEditable'
                        )
                    )
                    output.append(template_region)
                    output.append( 
                        start.replace(
                            'TemplateBeginEditable', 
                            'InstanceBeginEditable'
                        )
                    )
                    if k in self.updated_regions:
                        output.append(self.page_regions[k])
                    else:
                        output.append(
                            update_links(
                                site_root = site_root,
                                old_path = old_path,
                                new_path = new_path,
                                content = self.page_regions[k],
                            )
                        )
                else:
                    # The last part
                    pos = start_of_end_html_tag(template_region)
                    template_region = '%s%s%s' % (
                        template_region[:pos],
                        '<!-- InstanceEnd -->',
                        template_region[pos:],
                    )
                    output.append(
                        end.replace(
                            'TemplateEndEditable', 
                            'InstanceEndEditable'
                        )
                    )
                    output.append(template_region)
            else:
                # Its a page region, not a template region
                page_region = template_region
                if first:
                    first = False
                    # Need to update the comment specifying the template the
                    # page is using
                    pos = end_of_start_html_tag(page_region)
                    end_pos = page_region[pos:].find('-->')+pos+3
                    if not end_pos:
                        raise TemplateError(
                            'Could not find the end of the BeginInstance '
                            'comment specifying the template location'
                        )
                    rel = relpath(
                        template_path, 
                        posixpath.dirname(new_path)
                    )
                    page_region = '%s%s%s' % (
                        page_region[:pos],
                        '<!-- InstanceBegin template="' + rel +\
                           '" codeOutsideHTMLIsLocked="false" -->',
                        page_region[end_pos:],
                    )
                    output.append(page_region)
                    output.append(start)
                    if k in self.updated_regions:
                        output.append(self.page_regions[k])
                    else:
                        output.append(
                            update_links(
                                site_root = site_root,
                                old_path = old_path,
                                new_path = new_path,
                                content = self.page_regions[k],
                            )
                        )
                elif k is not None:
                    # middle part
                    output.append(end)
                    output.append(page_region)
                    output.append(start)
                    if k in self.updated_regions:
                        output.append(self.page_regions[k])
                    else:
                        output.append(
                            update_links(
                                site_root = site_root,
                                old_path = old_path,
                                new_path = new_path,
                                content = self.page_regions[k],
                            )
                        )
                else:
                    # The last part
                    pos = start_of_end_html_tag(page_region)
                    output.append(end)
                    output.append(page_region)
        output = ''.join(output)
        if tidy:
            output = tidy_output(output)
        if filename is not None:
            f=open(filename, 'w')
            f.write(output.encode('utf-8'))
            f.close()
        else:
            return output
    
    def save_as_template(self, filename=None, tidy=False):
        """\
        Merge the Editable Regions with the information in the Template to 
        create the HTML page to be output. Returns the HTML.
        """
        if self.instance_type == 'page':
            raise NotImplementedError('Not implemented yet')
        output = []
        for k, end, template_region, start in self.template_regions:
            output.append(end)
            output.append(template_region)
            output.append(start)
            if k is not None:
                output.append(self.page_regions[k])
        output = ''.join(output)
        if tidy:
            output = tidy_output(output)
        if filename is not None:
            f=open(filename, 'w')
            f.write(output.encode('utf-8'))
            f.close()
        else:
            return output
    
    def __repr__(self):
        return '<%s (%s), %s>' % (
            self.__class__.__name__, 
            self.instance_type,
            self.filename,
        )

    __str__ = __repr__
    
    def __getitem__(self, key):
        """\
        Simulate mapping-style access.
        """
        return self.get(key)
    
    def __setitem__(self, key, value):
        """\
        Simulate mapping-style access.
        """
        self.set(key, value)

    def get(self, key):
        """\
        Return the current value of the editable region ``key``.
        """
        # Should this return a copy?
        if self.page_regions.has_key(key):
            return self.page_regions[key]
        else:
            raise TemplateError(
                "Error, %r is not an editable region the template." % key
            )
    
    def set(self, key, value):
        """\
        Set the editable region specified by ``key`` to ``value``.
        """
        if not isinstance(value, unicode):
            value = value.decode('utf=8')
        if not isinstance(key, unicode):
            key = key.decode('utf-8')
        if self.page_regions.has_key(key):
            self.page_regions[key] = value
            if key not in self.updated_regions:
                self.updated_regions.append(key)
        else:
            raise TemplateError(
                "Error, '%s' is not an editable region of the template%s" % (
                    key, self.filename and ' '+self.filename or ''
                )
            )
        
    def append(self, key, value):
        """\
        Append ``value`` to the end of the editable region specified by 
        ``key``.
        """
        value = unicode(value)
        key = unicode(key)
        self.set(key, self.get(key)+value)

    # Simulated methods
    
    def keys(self):
        "Simulate mapping's methods"
        return self.page_regions.keys()
    
    def has_key(self, key):
        "Simulate mapping's methods"
        return key in self.page_regions.keys()
    
    def items(self):
        "Simulate mapping's methods"
        return self.page_regions.items()
    
    # Conversion Methods
    
    def to_dict(self):
        """\
        Return a dictionary containing a copy of the text in editable regions 
        of the page as it stands with the names of theeditable regions as the 
        keys.
        """
        return self.page_regions.copy()

DWT = DreamweaverTemplateInstance

# Helpers

def determine_instance_type(template, version):
    """\
    Check for the presence of an ``InstanceBegin`` comment with a 
    ``template`` attribute and if it exists, assume the instance is a
    page, otherwise assume it is a template.
    """
    if version == 4:
        regex=re.compile(
            r'''<!--\s*?InstanceBegin\s*?template\s*?=\s*?("|')'''
            r'''(.*?)("|').*?-->'''
        )
    else:
        regex=re.compile(
            r'''<!--\s*?#BeginTemplate\s*?("|')'''
            r'''(.*?)("|').*?-->'''
        )
    match = regex.search(template)
    if not match:
        return 'template', None
    else:
        return 'instance', match.group(2)

def end_of_start_html_tag(template, filename=None):
    # We need to use [^<]*? to match any character except <
    start_html_regex=re.compile(
        r"<\s*?html[^<]*?>",
        re.IGNORECASE,
    )
    start_html_match = start_html_regex.search(
        template, 
    )
    if not start_html_match:
        msg = 'No <html> tag could be found in the template'
        if filename:
            msg += ' %r'%filename
        raise TemplateError(msg)
    return start_html_match.end(0)

def start_of_end_html_tag(template, filename=None):
    end_html_regex=re.compile(
        r"</\s*?html\s*?>",
        re.IGNORECASE,
    )
    end_html_match = end_html_regex.search(
        template, 
    )
    if not end_html_match:
        msg = 'No <.html> tag could be found in the template'
        if filename:
            msg += ' %r'%filename
        raise TemplateError(msg)
    return end_html_match.start(0)
 
def tidy_output(output):
    # Tidy import 
    try:
        import tidylib
    except ImportError:
        tidy_available = False
    else:
        tidy_available = True
    if not tidy_available:
        raise TemplateError(
            "The 'tidy' module from 'pytidylib' is not available"
        )
    options = dict(
        output_xhtml=1, 
        add_xml_decl=1, 
        indent=1, 
        tidy_mark=0,
        wrap=78,
    )
    output, errors = tidylib.tidy_document(output.encode('utf-8'), options)
    return output

# Link functions

href_and_src_pattern = \
   r'''<([^>]*?)(href|src)(\s*?)=(\s*?)("|')(.*?)("|')(\s*?.*?)>'''

def update_links(site_root, old_path, new_path, content):
    site_root = uniform_path(site_root)
    add_new_path_slash = False
    if new_path.endswith('/'):
        add_new_path_slash = True
    old_path = uniform_path(old_path)
    new_path = uniform_path(new_path)
    if add_new_path_slash:
        new_path += '/'
    # First check old_path and new_path are under site root
    if not old_path.startswith(site_root):
        raise TemplateError(
            "The old_path (%r) is not under site_root (%r)."%(
                old_path, 
                site_root,
            )
        )
    elif not new_path.startswith(site_root):
        raise TemplateError(
            "The new_path (%r) is not under site_root (%r)."%(
                new_path, 
                site_root,
            )
        )

    def get_new_link(old_path, old_link, new_path):
        # Calculate the absolute path of each link from the link and the
        # old_path
        link_path = uniform_path(
            posixpath.join(posixpath.dirname(old_path), old_link)
        )
        # Calculate the new relative path from the new_path to the absolute 
        # path of the link
        new_link = relpath(link_path, posixpath.dirname(new_path))
        # If the link is a directory ensure there is a trailing slash
        if (old_link == '.' or old_link.endswith('/')) and \
           not new_link.endswith('/'):
            new_link += '/'
        return new_link

    # Handle src and html tags first
    def href_and_src_replace(match):
        found = match.group(0)
        old_link = match.group(6)
        if old_link.startswith('/') or old_link.startswith('http://') or \
           old_link.startswith('https://'):
            return found
        new_link = get_new_link(old_path, old_link, new_path)
        # Keep the old HTML spacing
        result = '<%s%s%s=%s%s%s%s%s>'%(
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
            match.group(5),
            new_link,
            match.group(7),
            match.group(8),
            #match.group(9),
        )
        return result
    content, replaced_links = re.subn(
        href_and_src_pattern, 
        href_and_src_replace, 
        content
    )

    # Now handle library item paths
    library_item_pattern = r"""<!--(\s*?)#Begin(ContextItem|LibraryItem|DynamicItem)(\s*?)"(\W*\s*.*\w*)?\"(\s*?)-->"""
    def library_item_replace(match):
        found = match.group(0)
        old_link = match.group(4)
        new_link = get_new_link(old_path, old_link, new_path)
        # Keep the old HTML spacing
        result = '<!--%s#Begin%s%s"%s"%s-->'%(
            match.group(1),
            match.group(2),
            match.group(3),
            new_link,
            match.group(5),
        )
        return result
    content, replaced_links = re.subn(
        library_item_pattern, 
        library_item_replace,
        content
    )
    return content

