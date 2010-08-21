# -*- coding: iso-8859-1 -*-
"""
MoinMoin Solenoid theme

@copyright: 2007 RadomirDopieralski <moin@sheep.art.pl>, Oliver Siemoneit
            2009 Renato Silva

@license: See the README file.
"""

from MoinMoin import wikiutil, version
from MoinMoin import caching
from MoinMoin.theme import ThemeBase, modernized
from MoinMoin.Page import Page
from MoinMoin.i18n import Translation, translations, po_filename
import MoinMoin.i18n, re, os, glob
import MoinMoin
import StringIO

class Theme(ThemeBase):

    name = "solenoid"

    _ = lambda x: x

    icons = {

        # Key               Alt                        Icon filename                W   H
        # ----------------------------------------------------------------------------------
        # Navibar
        'help':             ("%(page_help_contents)s", "moin-help.png",             16, 16),
        'find':             ("%(page_find_page)s",     "moin-search.png",           16, 16),
        'diff':             (_("Diffs"),               "moin-diff.png",             20, 16),
        'info':             (_("Info"),                "moin-info.png",             16, 16),
        'edit':             (_("Edit"),                "moin-edit.png",             16, 16),
        'unsubscribe':      (_("Unsubscribe"),         "moin-unsubscribe.png",      16, 16),
        'subscribe':        (_("Subscribe"),           "moin-subscribe.png",        16, 16),
        'addquicklink':     (_("Add quicklink"),       "moin-addquicklink.png",     16, 16),
        'delquicklink':     (_("Delete quicklink"),    "moin-delquicklink.png",     16, 16),

        'raw':              (_("Raw"),                 "moin-raw.png",              16, 16),
        'xml':              (_("XML"),                 "moin-xml.png",              20, 13),
        'print':            (_("Print"),               "moin-print.png",            16, 16),
        'view':             (_("View"),                "moin-show.png",             16, 16),
        'home':             (_("Home"),                "moin-home.png",             16, 16),
        'up':               (_("Up"),                  "moin-parent.png",           16, 16),

        # FileAttach
        'attach':           ("%(attach_count)s",       "moin-attach.png",           12, 12),
        'iconattach':       ("Add/Manage files",       "moin-iconattach.png",       16, 16),

        # RecentChanges
        'rss':              (_("[RSS]"),               "moin-rss.png",              39, 14),
        'deleted':          (_("[DELETED]"),           "moin-deleted.png",          80, 16),
        'updated':          (_("[UPDATED]"),           "moin-updated.png",          80, 16),
        'renamed':          (_("[RENAMED]"),           "moin-renamed.png",          80, 16),
        'conflict':         (_("[CONFLICT]"),          "moin-conflict.png",         23, 16),
        'new':              (_("[NEW]"),               "moin-new.png",              80, 16),
        'diffrc':           (_("[DIFF]"),              "moin-diff.png",             20, 16),

        # General
        'bottom':           (_("[BOTTOM]"),            "moin-bottom.png",           12, 12),
        'top':              (_("[TOP]"),               "moin-top.png",              12, 12),
        'www':              ("[WWW]",                  "moin-www.png",              12, 12),
        'mailto':           ("[MAILTO]",               "moin-email.png",            12, 12),
        'news':             ("[NEWS]",                 "moin-news.png",             12, 12),
        'irc':              ("[IRC]",                  "moin-irc.png",              15, 15),
        'telnet':           ("[TELNET]",               "moin-telnet.png",           12, 12),
        'ftp':              ("[FTP]",                  "moin-ftp.png",              12, 12),
        'file':             ("[FILE]",                 "moin-ftp.png",              12, 12),

        # Search forms
        'searchbutton':     ("[?]",                    "moin-search.png",           16, 16),
        'interwiki':        ("[%(wikitag)s]",          "moin-inter.png",            12, 12),
        'badinterwiki':     ("[%(wikitag)s]",          "moin-badinter.png",         12, 12),

        # Smileys
        'X-(':              ("X-(",                    'angry.png',                 18, 18),
        ':D':               (":D",                     'biggrin.png',               18, 18),
        '<:(':              ("<:(",                    'frown.png',                 18, 18),
        ':o':               (":o",                     'redface.png',               18, 18),
        ':(':               (":(",                     'sad.png',                   18, 18),
        ':)':               (":)",                     'smile.png',                 18, 18),
        'B)':               ("B)",                     'smile2.png',                18, 18),
        ':))':              (":))",                    'smile3.png',                18, 18),
        ';)':               (";)",                     'smile4.png',                18, 18),
        '/!\\':             ("/!\\",                   'alert.png',                 16, 16),
        '<!>':              ("<!>",                    'attention.png',             16, 16),
        '(!)':              ("(!)",                    'idea.png',                  16, 16),
        ':-?':              (":-?",                    'tongue.png',                18, 18),
        ':\\':              (":\\",                    'ohwell.png',                18, 18),
        '>:>':              (">:>",                    'devil.png',                 18, 18),
        '|)':               ("|)",                     'tired.png',                 18, 18),
        ':-(':              (":-(",                    'sad.png',                   18, 18),
        ':-)':              (":-)",                    'smile.png',                 18, 18),
        'B-)':              ("B-)",                    'smile2.png',                18, 18),
        ':-))':             (":-))",                   'smile3.png',                18, 18),
        ';-)':              (";-)",                    'smile4.png',                18, 18),
        '|-)':              ("|-)",                    'tired.png',                 18, 18),
        '(./)':             ("(./)",                   'checkmark.png',             16, 16),
        '{OK}':             ("{OK}",                   'thumbs-up.png',             16, 16),
        '{X}':              ("{X}",                    'icon-error.png',            16, 16),
        '{i}':              ("{i}",                    'icon-info.png',             16, 16),
        '{1}':              ("{1}",                    'prio1.png',                 16, 16),
        '{2}':              ("{2}",                    'prio2.png',                 16, 16),
        '{3}':              ("{3}",                    'prio3.png',                 16, 16),
        '{*}':              ("{*}",                    'star_on.png',               16, 16),
        '{o}':              ("{o}",                    'star_off.png',              16, 16),

        # New big icons for classic theme
        'diff-big':         (_("Diffs"),               "moin-diff-big.png",         31, 25),
        'info-big':         (_("Info"),                "moin-info-big.png",         25, 25),
        'edit-big':         (_("Edit"),                "moin-edit-big.png",         25, 25),
        'unsubscribe-big':  (_("Unsubscribe"),         "moin-unsubscribe-big.png",  25, 25),
        'subscribe-big':    (_("Subscribe"),           "moin-subscribe-big.png",    25, 25),
        'raw-big':          (_("Raw"),                 "moin-raw-big.png",          25, 25),
        'print-big':        (_("Print"),               "moin-print-big.png",        25, 25),
        'view-big':         (_("View"),                "moin-show-big.png",         25, 25),
        'delquicklink-big': (_("Delete quicklink"),    "moin-delquicklink-big.png", 25, 25),
        'addquicklink-big': (_("Add quicklink"),       "moin-addquicklink-big.png", 25, 25),
        'attach-big':       (_("Add/Manage files"),    "moin-iconattach-big.png",   25, 25),
    }

    del _

    def _(self, text):
        lang = self.request.lang
        _translations = self._translations
        if lang in _translations:
            if text in _translations[lang]:
                return _translations[lang][text]
        return self.request.getText(text, formatted=False)

    def _get_config(self, source, config_name, default=None):
        return getattr(source, '%s_%s' % (self.name, config_name), default)

    def get_bool_user_config(self, config_name):
        user = self.request.user
        if not user.valid:
            return None
        user_config = self._get_config(user, config_name)
        if type(user_config) == str:
            user_config = {'1': True}.get(user_config, False)
        elif type(user_config) == int:
            user_config = bool(user_config)
        return user_config

    def get_config(self, config_name, default=None, by_user=True):
        if by_user and self.userprefs_allowed and self.get_bool_user_config('enable_prefs'):
            user_config = self.get_bool_user_config(config_name)
            if user_config is not None:
                return user_config
        return self._get_config(self.cfg, config_name, default)

    def __init__(self, request):
        ThemeBase.__init__(self, request)
        append_translation = self.get_config('append_translation', default=True, by_user=False)
        self._translations = self.theme_translations(append_translation)
        self.userprefs_allowed = self.get_config('userprefs', default=False, by_user=False)
        if self.userprefs_allowed:
            self.load_user_options()
        try:
            self.static_prefix = self.cfg.url_prefix_static
        except AttributeError:
            self.static_prefix = self.cfg.url_prefix

    def load_user_options(self):
        user = self.request.user
        self.define_user_options()
        if user.valid:
            user.save()
            user.load_from_id()

    def define_user_options(self):
        capitalized_name = self.name.capitalize()
        new_options = [
            ('%s_enable_prefs' % self.name, lambda _: self._('%s theme: enable configuration by user') % capitalized_name),
            ('%s_full_screen' % self.name, lambda _: self._('%s theme: use full screen mode') % capitalized_name),
            ('%s_clear' % self.name, lambda _: self._('%s theme: use clear style') % capitalized_name),
            ('%s_shadow' % self.name, lambda _: self._('%s theme: use shadows') % capitalized_name)
        ]

        defined_options = self.request.cfg.user_checkbox_fields
        defined_option_names = [each[0] for each in defined_options]

        for new_option in new_options:
            for defined_option in defined_options:
                if defined_option[0] == new_option[0]:
                    defined_options.remove(defined_option)
                    break
            defined_options.append(new_option)

        new_option_names = [each[0] for each in new_options]
        self.request.cfg.user_checkbox_defaults.update(dict.fromkeys(new_option_names, 0))

    def theme_translations(self, append=False):
        """Load personal translations to be used by this theme.

        @param append:  if True makes theme translation global by appending it to the default Moin translation system.
        @return: a dict (indexed by language) of translation dicts, or an empty dict if append=True.
        """
        _translations = {}
        request = self.request
        po_dir = os.path.join('i18n', 'themes', self.name)
        encoding = 'utf-8'

        for lang_file in glob.glob(po_filename(request, i18n_dir=po_dir, language='*', domain='Theme')):
            dummy_language, domain, ext = os.path.basename(lang_file).split('.')
            language = dummy_language.split('_')[0]
            t = Translation(dummy_language, domain)
            t.loadLanguage(request, trans_dir=po_dir)

            if append:
                if not language in translations:
                    translations[language] = Translation(language)
                    translations[language].loadLanguage(request)
                translations[language].raw.update(t.raw)
            else:
                _translations[language] = {}
                for key, text in t.raw.items():
                    _translations[language][key] = text

        return _translations

    def header(self, d):
        _ = self._
        wrapper_class = u'wrapper'
        sidebar = self.sidebar(d)
        if sidebar is None:
            sidebar = u''
            wrapper_class += u' no-sidebar'
        page_title = self.title(d)
        site_logo = self.logo()
        if (site_logo == ''):
            site_logo = page_title.replace('<h1>', '<div class="logo">').replace('</h1>', '</div>')
            site_logo = site_logo.replace('id="', 'id="logo_')
            site_logo = site_logo.replace("id='", "id='logo_")
            page_title = '<h1>&nbsp;</h1>'
        parts = [
            self.emit_custom_html(self.cfg.page_header1),
            u'<div class="header">',
            site_logo,
            self.searchform(d),
            self.username(d),
            self.gotobar(d),
            self.msg(d),
            self.editbar(d),
            page_title,
            self.logged_trail(d),
            u'</div>',
            self.emit_custom_html(self.cfg.page_header2),
            u'<div class="%s">' % wrapper_class,
            sidebar,
            u'<div class="content"%s>\n' % self.content_lang_attr(),
            "<!--[if lt IE 7]><div class='outdated-ie'><p><b>%s! </b>%s</p></div><![endif]-->"
                % (_("Attention"), _("You are using an outdated version of Internet Explorer "
                "which is not supported by this site. Please update your browser."))
        ]
        return u''.join(parts)

    editorheader = header

    def title(self, d):
        _ = self._
        cfg = self.request.cfg
        modernized_theme = modernized.Theme(self.request)
        if self.request.action != 'print':
            try:
                screen_title = self.title_with_separators # Moin 1.9
            except AttributeError:
                screen_title = modernized_theme.title # Moin 1.8
            return u'<h1>%s%s</h1>' % (modernized_theme.interwiki(d), screen_title(d))

        # We are in print action
        page_path = wikiutil.escape(d['title_text'].replace('/', ' / '))
        lines = d['page'].get_raw_body().split('\n')
        for line in lines:
            line = line.strip()
            if not line.startswith('#') and not line.startswith('<<') and not line == '':
                # If page starts with a title, then make page path a header before it
                if re.sub('^\s*=+\s+[^=]+\s+=+\s*$', '', line) == '':
                    return u'<span id="pagelocation">%s: %s</span>' % (_('Page Name'), page_path)
                break

        # Page does not start with a title, so we use page path as title
        interwiki_name = '%s: ' % (cfg.interwikiname or 'Wiki')
        prefix = ['', interwiki_name][cfg.show_interwiki]
        return u'<h1 id="pagelocation">%s%s</h1>' % (prefix, page_path)

    def logged_trail(self, d):
        user = self.request.user
        html = u""
        if user.valid and user.show_page_trail:
            if len(user.getTrail())>1:
                html = self.trail(d)
        return html

    def footer(self, d, **keywords):
        page = d['page']
        footer_note = self.get_config('footer_note', default='', by_user=False)
        parts = [
            u'<div id="pagebottom"></div>',
            u'</div></div>', # wrapper and content divs
             self.emit_custom_html(self.cfg.page_footer1),
            u'<div class="footer">',
            self.emit_custom_html(footer_note),
            self.pageinfo(page),
            u'</div>',
            self.emit_custom_html(self.cfg.page_footer2),
        ]
        return u''.join(parts)

    def sidebar(self, d, **keywords):
        """ Display page called SideBar as an additional element on every page

        @param d: parameter dictionary
        @rtype: string
        @return: sidebar html
        """
        request = self.request
        _ = self._
        sidebar = request.getPragma('sidebar') or u'SideBar';
        page = Page(request, sidebar)
        if not page.exists():
            return None
        import StringIO
        buff = StringIO.StringIO()
        request.redirect(buff)
        try:
            try:
                page.send_page(content_only=1, content_id="sidebar")
            except TypeError:
                page.send_page(request, content_only=1, content_id="sidebar")
        finally:
            request.redirect()
        return u'<div class="sidebar">%s<div id="sidebar-end"></div></div>' % buff.getvalue()


    def editbar(self, d, **keywords):
        page = d['page']
        if not self.shouldShowEditbar(page):
            return u''
        result = []
        enabled_items = self.request.cfg.edit_bar
        suplementation_enabled = self.request.cfg.supplementation_page
        
        if 'Edit' in enabled_items:
            result.append(self.edit_link(page))
        result.append(self.revert_link(page))

        if 'Comments' in enabled_items:
            result.append(self.toggle_comments_link(page))

        if ('Discussion' in enabled_items and
            self.request.getPragma('supplementation-page', suplementation_enabled) in
            (True, 1, 'on', '1')):
            result.append(self.supplementation_page_nameLink(page))

        if 'Info' in enabled_items:
            result.append(self.info_link(page))
        if 'Subscribe' in enabled_items:
            result.append(self.subscribeLink(page))
        if 'Quicklink' in enabled_items:
            result.append(self.quicklinkLink(page))
        if 'Attachments' in enabled_items:
            result.append(self.attach_link(page))

        if 'ActionsMenu' in enabled_items:
            result.append(self.actionsMenu(page).replace('</form>', '<input type="hidden" name="subpages_checked" value="1"></form>'))
        else:
            result.append(self.admin_link(page))
        return u'<div class="editbar"> %s </div>' % (u' '.join(result))

    def edit_link(self, page):
        if not (page.isWritable() and
                self.request.user.may.write(page.page_name)):
            return self.login_link(page)
        _ = self._
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=edit')
        text = _('Edit')
        return wikiutil.link_tag(self.request, params, text, css_class="edit", name="texteditlink")

    def login_link(self, page):
        _ = self._
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=login')
        text = _('Locked')
        return wikiutil.link_tag(self.request, params, text, css_class="password")

    def info_link(self, page):
        _ = self._
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=info')
        text = _('History')
        return wikiutil.link_tag(self.request, params, text, css_class="history")

    def revert_link(self, page):
        try:
            rev = self.request.rev
        except AttributeError:
            return u""
        if not (self.request.rev and
                page.isWritable() and
                self.request.user.may.revert(page.page_name)):
            return u''
        _ = self._
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=revert&rev=%d' % self.request.rev)
        text = _('Revert')
        return wikiutil.link_tag(self.request, params, text, css_class="revert")

    def attach_link(self, page):
        _ = self._
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=AttachFile')
        text = _('Attachments')
        return wikiutil.link_tag(self.request, params, text, css_class="attachments")

    def toggle_comments_link(self, page):
        _ = self._
        return '''<span class="toggleCommentsButton" style="display:none;">
            <a href="#" class="nbcomment" onClick="toggleComments();return false;">%s</a></span>''' % _('Comments')

    def admin_link(self, page):
        _ = self._
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=PageActions')
        text = _('All Actions')
        return wikiutil.link_tag(self.request, params, text, css_class="admin")

    def gotobar(self, d, **k):
        request = self.request
        found = {}
        items = []
        item = u'%s'
        current = d['page_name']
        if request.cfg.navi_bar:
            for text in request.cfg.navi_bar:
                #pagename, url = self.splitNaviurl(text)
                pagename, link = self.splitNavilink(text, localize=1)
                if pagename == current:
                    cls = 'wikilink current'
                else:
                    cls = 'wikilink'
                items.append(
                    '<li class="%s">%s</li>'%(cls, link)
                )
                found[pagename] = 1
        userlinks = request.user.getQuickLinks()
        for text in userlinks:
            #pagename, url = self.splitNaviurl(text, localize=0)
            pagename, link = self.splitNavilink(text, localize=0)
            if not pagename in found:
                if pagename == current:
                    cls = 'userlink current'
                else:
                    cls = 'userlink'
                items.append(
                    '<li class="%s">%s</li>' % (cls, link)
                )
                found[pagename] = 1
        return u'<ul class="gotobar">%s<li class="clear"></li></ul>' % u' '.join(items)

    def html_stylesheets(self, d):

        def ie_version_spec(ie_style): return re.compile('msie/.*_ie').sub('IE ', ie_style)
        def ie_style(style, ie_version): return 'msie/%s_ie%d' % (style, ie_version)
        def is_ie_style(style): return style.startswith('msie')

        def ie_content(content, version_spec='IE'):
            version_spec = version_spec.replace('<= ', 'lte ')
            return '<!--[if %s]>%s<![endif]-->' % (version_spec, content)

        def add_style(style):
            styles.append(style)
            for version in [7, 8]:
                styles.append(ie_style(style, version))

        clear = self.get_config('clear', default=False)
        shadow = self.get_config('shadow', default=False)
        full_screen = self.get_config('full_screen', default=False)
        print_action = self.request.action == 'print'

        tags = []
        styles = []
        add_style('style')
        if clear: add_style('clear')

        if print_action:
            add_style('print')
            try:
                media = self.request.values.get('media')
            except AttributeError:
                media = self.request.form.get('media', [None])[0]
            if media == 'projection':
                add_style('projection')
        elif full_screen: add_style('full')
        elif shadow:
            add_style('shadow')
            if clear: add_style('shadow_clear')

        static_dir = self.get_config('htdocs_dir', by_user=False)
        if static_dir is None:
            try:
                # Moin 1.9
                from MoinMoin.web.static import STATIC_FILES_PATH
                static_dir = STATIC_FILES_PATH
            except ImportError, e:
                # Moin 1.8
                moin_base = re.sub('MoinMoin$', '', self.cfg.moinmoin_dir)
                static_dir = os.path.join(moin_base, 'wiki', 'htdocs')
                if not os.path.exists(static_dir):
                    static_dir = '/usr/share/moin/htdocs'

        link_template = '<link rel="stylesheet" type="text/css" href="%s">'
        url_prefix = "%s/%s/css" % (self.static_prefix, self.name)
        css_dir = os.path.join(static_dir, self.name, 'css')
        found_css_dir = os.path.exists(css_dir)

        for style in styles:
            for namespace in ['', '/custom']:
                css_url = '%s%s/%s.css' % (url_prefix, namespace, style)
                css_file = '%s%s/%s.css' % (css_dir, namespace, style)
                if not found_css_dir or os.path.exists(css_file):
                    css_link = link_template % css_url
                    if is_ie_style(style):
                        css_link = ie_content(css_link, ie_version_spec(style))
                    tags.append(css_link)

        return '\n'.join(tags)

    def searchform(self, d):
        _ = self._
        form = self.request.form
        updates = {
            'search_label' : _('Search:'),
            'search_value': wikiutil.escape(form.get('value', [''])[0], 1),
            'search_full_label' : _('Text'),
            'search_title_label' : _('Titles'),
            }
        d.update(updates)

        return u'''
<form class="search" method="get" action="">
<p>
<input type="hidden" name="action" value="fullsearch">
<input type="hidden" name="context" value="180">
<label for="search">%(search_label)s</label>
<input id="search" type="text" name="value" value="%(search_value)s">
<input id="titlesearch" name="titlesearch" type="submit" value="%(search_title_label)s">
<input id="fullsearch" name="fullsearch" type="submit" value="%(search_full_label)s">
</p>
</form>''' % d

    def pageinfo(self, page):
        _ = self._
        html = ''
        if self.shouldShowPageinfo(page):
            info = page.lastEditInfo()
            if info:
                if info['editor']:
                    info = _("last edited %(time)s by %(editor)s") % info
                else:
                    info = _("last modified %(time)s") % info
                html = '<span class="time"%(lang)s>%(info)s</span>\n' % {
                    'lang': self.ui_lang_attr(),
                    'info': info
                    }
        return html

    def logo(self):
        logo = u''
        if self.cfg.logo_string:
            pagename = wikiutil.getFrontPage(self.request).page_name
            pagename = wikiutil.quoteWikinameURL(pagename)
            logo = wikiutil.link_tag(self.request, pagename, self.cfg.logo_string, css_class="logo")
        return logo

    def headscript(self, d):
        """Override the stupid default script with its hardcoded HTML structure"""
        return u'''<script type="text/javascript"><!--
function add_gui_editor_links() {
    // Add gui editor link after the text editor link

    // If the variable is not set or browser is not compatible, exit
    try {gui_editor_link_href}
    catch (e) {
        //alert("add_gui_editor_links: gui_editor_link_href not here");
        return
    }
    if (can_use_gui_editor() == false){
        //alert("add_gui_editor_links: can't use gui_editor");
        return;
    }
    var all = document.getElementsByName('texteditlink');
    for (i = 0; i < all.length; i++) {
        var textEditorLink = all[i];
        // Create a a link
        var guiEditorLink = document.createElement('a');
        guiEditorLink.href = gui_editor_link_href;
        guiEditorLink.className = "edit";
        var text = document.createTextNode(gui_editor_link_text);
        guiEditorLink.appendChild(text);
        // Insert in the editbar
        var editbar = textEditorLink.parentNode
        editbar.insertBefore(guiEditorLink, textEditorLink);
    }
}
--></script>
'''

    def recentchanges_entry(self, d):
        _ = self._
        if d['comments']:
            rccomm = ''
            for c in d['comments']:
                rccomm += ' <b>%d</b> ' % c[0];
                rccomm += c[1];
        else:
            rccomm = ''
        html = (u'''<li><b class="rctime">%s</b> %s %s . . . . <span class="rcauth">%s</span> <i class="rccomm">%s</i></li>''' % (
            d['time_html'],
            d['pagelink_html'],
            d['icon_html'],
            ', '.join(d['editors']),
            rccomm,
        ))
        return html

    def recentchanges_daybreak(self, d):
        return u'</ul><h3 class="rcdaybreak">%s</h3><ul>' % d['date']

    def recentchanges_header(self, d):
        return u'<div class="recentchanges"%s><ul>' % self.ui_lang_attr()

    def recentchanges_footer(self, d):
        return u'</ul></div>'


def execute(request):
    return Theme(request)

