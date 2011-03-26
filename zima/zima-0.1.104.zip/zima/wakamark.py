# -*- coding: utf-8 -*-
import re
import cgi

from pygments.lexer import RegexLexer, bygroups, include, using, this
from pygments.token import Token, Text
from pygments.formatters import HtmlFormatter
from pygments.formatter import Formatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from pygments import highlight

from zima import dispatcher, kv

class WakaLexer(RegexLexer):

    name = 'WakaMark'
    aliases = ['trac-waka', 'waka']
    filenames = []
    mimetypes = ['text/x-wakamark']
    flags = re.MULTILINE | re.IGNORECASE

    def _source(self, match):
        lexer = None
        try:
            lexer = get_lexer_by_name(match.group(1).strip())
        except ClassNotFound:
            pass
        if lexer:
            yield match.start(), Token.SourceCode, \
                lexer.get_tokens(match.group(3))
        else:
            yield match.start(), Text, match.group(3)

    def _valkey(self, match):
        yield match.start(), Token.KeyValue, \
            (match.group(2), match.group(1))

    tokens = {
        'root': [
            (r'(>>)((\S*\/)?\d+)', bygroups(
                    Token.RefProto, Token.RefPath, Token.Ignore)),
            (r'(\w+):\/\/(\S+)', bygroups(
                    Token.RefProto, Token.RefPath)),
            (r'(>)', Token.Cite, 'cite'),
            (r'cat\s*>\s*(\w+)\s*<<\s*(\w+)((?:\n.*)*?)\n\2', _source),
            (r'\.\.(\w+)(:)((?:\n.*)*?)\n\.\.', _source),
            (r'\.\.\s', Token.Ignore, 'modeline'),
            (r'\n\s*\n', Token.Paragraph),
            (r'\*\*', Token.Strong),
            (r'\*', Token.Emph),
            (r'%%', Token.Spoiler),
            # Basic text
            (r'\n', Text),
            (r'.', Text),
            ],
        'cite': [
            (r'(.*?)(\n|$)',
             bygroups(using(this, state='root'), Token.EndCite), '#pop')
            ],
        'modeline': [
            (r'(.*?)\s*:(\w+)', _valkey),
            (r'\n|$', Token.Ignore, '#pop')
            ]
        }

    def __init__(self, **options):
        RegexLexer.__init__(self, **options)

class WakaFormatter(Formatter):
    def __init__(self, resolver, emitter, **options):
        Formatter.__init__(self, **options)
        self.resolve = resolver
        self.emit = emitter
        self.html = HtmlFormatter(nowrap=True)

    def format(self, tokensource, out):
        lastval = ''
        refproto = None
        lasttype = None
        state = {'b':False, 'i':False, 'sp':False}

        out.write('<p>')
        for ttype, value in tokensource:
            if ttype == Text:
                out.write(cgi.escape(value))
            if ttype == Token.Paragraph:
                out.write('</p><p>')
            if ttype == Token.LineBreak:
                out.write('<br />')
            if ttype == Token.Strong:
                out.write(state['b'] and '</strong>' or '<strong>')
                state['b'] = not state['b']
            if ttype == Token.Emph:
                out.write(state['i'] and '</em>' or '<em>')
                state['i'] = not state['i']
            if ttype == Token.Spoiler:
                out.write(state['sp'] and '</span>' or '<span class="spoiler">')
                state['sp'] = not state['sp']
            if ttype == Token.Cite:
                out.write('<blockquote>' + cgi.escape(value))
            if ttype == Token.EndCite:
                out.write(value+'</blockquote>')
            if ttype == Token.SourceCode:
                out.write('<pre>')
                self.html.format(value, out)
                out.write('</pre>')
            if ttype == Token.RefProto:
                refproto = cgi.escape(value)
            if ttype == Token.RefPath:
                out.write(self.resolve(refproto, cgi.escape(value)))
                refproto = None
            if ttype == Token.KeyValue:
                self.emit(cgi.escape(value[0]), cgi.escape(value[1]))
        out.write('</p>')

def maker(cfg, hook, pings_cache={}):

    def A(href, title=''):
        return '<a href="%s">%s</a>' % (href, title or href)

    def markup(message):

        # TODO: Пересмотреть нахуй передачу маршрута в resolve-функции
        pings = set([])

        def resolve_reflink(path):
            " Внутрибордовая ссылка вида >>/xxx/123 "
            num, barr = path[-1], path[:-1]
            # Этот тупой if обрабатывает различные ситуации при маршрутах
            if len(barr) > 0:
                # В конце не указан / (например >>/s1212)
                # или это ссылка вида >>/2323
                if barr[-1] <> '' or len(barr) == 1:
                    barr.append('')
                # В начале не указан / (например >>s/233)
                if barr[0] <> '':
                    barr.insert(0, '')
                board = '/'.join(barr)[:-1]
            else:
                # Если перфикс не указан то это внутри бордовая ссылка
                board = message['pfx']
            pid = cfg.reftitle(cfg.host[0], '/'.join(barr), num)
            if pid not in kv:
                post = dispatcher.get_msgs(message['host'], board, num)
                if post and len(post) > 0:
                    kv[pid] = post[0]['parent']
            if pid in kv and kv[pid]:
                pings.add((message['host'], board, int(num)))
                return A(cfg.reflink(num, kv[pid], board), pid)
            else:
                return pid

        def resolve_http(path, proto):
            " http|https гиперссылка "
            if len(path) > 3 and path[2] == 'res' and (re.search(r'#\d+$', path[3]) or re.search(r'\.\w+$', path[3])):
                host, board, pnum = path[0], path[1], path[3]
                nhost = re.sub(r'^www\.', '', host)
                parent = pnum.split('.')[0]
                try:
                    num = pnum.split('#')[1]
                except IndexError:
                    num = ''
                if nhost in message['host']:
                    return resolve_reflink([board, num])
                return A(
                    cfg.reflink(num, parent, ['',board], host, proto),
                    '>>%s/%s/%s' % (nhost, board, num or parent))
            else:
                return A('%s://%s' % (proto, '/'.join(path)))

        def resolve(reftype, path):
            " Выбирает нужный ресолвер "
            if reftype == '&gt;&gt;':
                return resolve_reflink(path.split('/'))
            elif reftype in ['http', 'https']:
                return resolve_http(path.split('/'), reftype)
            else:
                print 'Unknown proto: %s' % reftype
                return path

        def emit(k, v):
            message[k] = hook('customField', (k, v.strip()))[1]

        message['html_body'] = highlight(
            message['src'],
            WakaLexer(encoding="utf-8"),
            WakaFormatter(resolve, emit, nowrap=True))

        pings_cache[message['uid']] = map(lambda (h,p,n): {'host':h, 'pfx':p, 'num':n}, pings)
        return message

    def do_pingback(message):
        if message['uid'] in pings_cache:
            dispatcher.ping_msgs(pings_cache[message['uid']],
                                 {'host':message['host'], 'pfx':message['pfx'],
                                  'num':message['num'], 'parent': message['parent']})
            del pings_cache[message['uid']]
        return message

    return [('newMessage', markup), ('savedMessage', do_pingback)]
