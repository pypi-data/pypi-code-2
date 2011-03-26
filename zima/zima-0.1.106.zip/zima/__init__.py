# -*- coding: utf-8 -*-
import os
import sys

import bottle
from bottle import route, request, response, run, \
    debug, error

import logging

os.chdir(os.path.dirname(__file__))
sys.path.append(os.path.dirname(__file__))

import nannou
import hooks
from hooks import hook
from attaches import add_attach, del_attach
from utils import AttrWrapper, ThreadPool, flatten, currydef
from names import fpath, reflink, reftitle, uid

dispatcher, kv, cron = None, None, None

def makeCtrlDec(cfg, render):
    """ Создает контроллерный декоратор """
    def controller(rel_path, method='GET', restful=False, raw=False):
        """ Декоратор для контроллеров """

        if raw:
            def out_html(callback):
                def f(*args, **kwargs):
                    return render(callback(*args, **kwargs))
                return f
        else:
            def out_html(callback):
                def f(*args, **kwargs):
                    page = cfg._base.copy()
                    page['content'] = callback(*args, **kwargs)
                    page['menu'] = dispatcher.boards_menu()
                    return render(page)
                return f

        def out_json(callback):
            def f(*args, **kwargs):
                return callback(*args, **kwargs)
            return f

        path = cfg.prefix + rel_path
        if restful:
            def wrapper(callback):
                route(path+'.html', method=method)(out_html(callback))
                route(path+'.json', method=method)(out_json(callback))
                return callback
        else:
            def wrapper(callback):
                route(path, method=method)(out_html(callback))
                return callback
        return wrapper

    return controller


def makeRenderer(cfg, theme, root):
    """ Загружает шаблон, вспомагательные модуль к нему, компилирует
    все и возвращает функцию-рендерер.
    """
    rtl = {'cfg': cfg }
    exec(open(fpath(root, theme,'.py')).read()) in rtl, rtl
    templ = open(fpath(root, theme, '.html')).read()
    fun, src = nannou.compile(templ, rtl, debug=True)
    logging.debug('Compiled ``%s'' theme template:\n%s' % (theme, src))
    return fun

def Board (path=[]):
    """ Создет контроллер имиджборды """
    cfg = path[-1]
    cfg.prefix = '/'.join(map(lambda x: x.root, path))

    cfg.reflink = currydef(reflink, None, None, cfg.prefix, None, 'http', cfg.host)
    cfg.reftitle = currydef(reftitle, None, None, None,
                            {'host': cfg.host, 'pfx': cfg.prefix})

    exec("from backends.%s import Model" % (cfg.db.backend)) in locals()
    model = Model(cfg.db)

    # Запускаем перехватчики
    hook = hooks.init(cfg.hooks, cfg=cfg)

    # Запускаем шаблонизатор
    render = makeRenderer(cfg, cfg.theme, cfg.themesRoot)

    # Конструируем декоратор контроллеров
    controller = makeCtrlDec(cfg, render)

    def sanitize(m):
        for fk in cfg.filteredFields:
            try:
                del m[fk]
            except KeyError:
                pass
        return m

    def san_thread(thread):
        return map(sanitize, thread)

    def san_digest(digest):
        digest['op'] = sanitize(digest['op'])
        digest['tail'] = map(sanitize, digest['tail'])
        return sanitize(digest)

    @controller('/zima', restful=True)
    @controller('/')
    def digest():
        """Индексная страница"""
        index = {
            'postform': cfg._postform }
        digests = map(san_digest, model.get_digests(
                {'host':cfg.host[0], 'pfx':cfg.prefix},
                0, cfg.indexThreads+1))
        if len(digests) > cfg.indexThreads:
            index['omitted'] = True
        index['threads'] = digests[:cfg.indexThreads]
        return index

    @controller('/tail', restful=True)
    def tail():
        """Хвост - те нитки, что не дотягивают до индекса"""
        tail = {'postform': ''}
        tail['threads'] = san_digest(model.get_digests(
                {'host':cfg.host[0], 'pfx':cfg.prefix},
                cfg.indexThreads, cfg.maxThreads - cfg.indexThreads))
        return tail

    @controller('/res/:parent', restful=True)
    def thread(parent):
        """Отображение отдельной нитки"""
        thread = san_thread(model.get_msgs(
                {'host': cfg.host[0],
                 'pfx':cfg.prefix,
                 'parent': int(parent)}))
        return {'postform': cfg._postform,
                'threads': {'op': thread[0],
                            'inthread': True,
                            'tail': list(thread[1:])}
                }

    @controller('/single/:num', restful=True, raw=True)
    def single(num):
        """Отображение отдельного сообщения"""
        return san_thread(model.get_msgs(
                {'host': cfg.host[0],
                 'pfx':cfg.prefix,
                 'num': int(num)}))[0]

    @controller('/post', method='POST')
    def receive_post():
        """Обработка поступившего сообщения"""
        message = hook('newMessage', {
                'uid': uid(),
                'host': cfg.host[0],
                'pfx': cfg.prefix,
                'src': request.POST['message']
                })
        postuid = message['uid']
        attaches = []
        try:
            for k, f in request.files.iterallitems():
                fname = os.path.splitext(f.filename.decode('utf-8'))
                finfo = {
                    'data': f.file.read(),
                    'name': (fname[0], fname[1].lower())}
                if f.type:
                    finfo['mime'] = f.type
                attaches.append(
                    add_attach(cfg.attaches, postuid, finfo, model, hook))
        except Exception, exc:
            for a in attaches:
                del_attach(cfg.attaches, a, model)
            raise exc
        message['attaches'] = attaches
        model.save_msg(message)
        hook('savedMessage', message)
        if 'goto' in message:
            goto = message['goto'] == 'index' and 'index' or 'thread'
            del message['goto']
        else:
            goto = 'thread'
        if goto == 'thread':
            return {'redirect': cfg.reflink('', message['parent'])}
        else:
            return {'redirect': cfg.prefix+'/'}

    @controller('/delete', method='POST')
    def delete_msg():
        class InvalidMessagePasswordError(Exception):
            pass
        msgs = request.forms.getall('post')
        passwd = request.forms['passwd']
        try:
            for mnum in msgs:
                model.del_msgs({
                        'password':passwd,
                        'num': mnum,
                        'pfx': cfg.prefix,
                        'host': cfg.host[0]})
        except Message404Error:
            raise InvalidMessagePasswordError
        return {'m':None , 'cfg': cfg}

    dispatcher.register({
            'host': cfg.host[0],
            'pfx': cfg.prefix,
            'title': cfg._base['title'],
            'group': cfg.group,
            'description': cfg._base['description'],
            'get_msgs': model.get_msgs,
            'ping_msgs': model.ping_msgs
            })

class BoardDispatcher():
    """ Диспетчеризует междудосочные вызовы """

    _menu = {}
    _boards = {}

    def register(self, board):
        self._boards[board['host']+board['pfx']] = board
        if board['group'] not in self._menu:
            self._menu[board['group']] = []
        self._menu[board['group']].append({
                'host': board['host'],
                'pfx': board['pfx'],
                'title': board['title'],
                'description': board['description'],
                })

    def get_msgs(self, host, board, num):
        bid = host+board
        if bid in self._boards:
            return self._boards[bid]['get_msgs']({'host':host, 'pfx':board, 'num':int(num)})

    def ping_msgs(self, msgs, origin):
        targets={}
        for msg in msgs:
            bid = msg['host']+msg['pfx']
            if bid not in self._boards:
                continue
            if bid not in targets:
                targets[bid] = []
            targets[bid].append(msg)
        for bid, pings in targets.items():
            self._boards[bid]['ping_msgs'](pings, origin)

    def boards_menu(self):
        return [{'group': k, 'boards':v} for k,v in self._menu.items()]

def start(config):
    """ Запуск сервера """
    config = config or __import__('config')

    cfg = AttrWrapper(config.__dict__)

    global dispatcher, kv, cron # Судя по этой конструкции я таки не могу
    import zima                 # в простоту и понятность петона
    dispatcher = zima.dispatcher = BoardDispatcher()
    kv = zima.kv = cfg.server._kv
    cron = zima.cron = ThreadPool(cfg.server.pipelineWidth)

    def makeBoards(path=[]):
        Board(path)
        for child in path[-1].children:
            makeBoards(path + [child])

    # --> Создаем доски <--
    makeBoards([cfg.board])

    # Системный рендерер шаблонов - чтобы показывать сообщения об
    # ошибках
    render = makeRenderer(cfg.board,
                          cfg.board.theme,
                          cfg.board.themesRoot)

    # Инициализируем и запускаем сервер
    host, port = cfg.server.iface.split(':')

    # Ошибки
    def error_handler(code):
        """ Генерирует сообщение об ошибке """
        def f(err):
            errPage = cfg.board._base.copy()
            errPage['title'] = err.status
            errPage['description'] = err.output
            errPage['content'] = {
                'traceback': err.traceback or ''
                }
            return render(errPage)
        error(code)(f)

    map(error_handler, [400, 401, 402, 403, 404, 405,
                        406, 407, 408, 409, 410, 411,
                        412, 413, 414, 415, 416, 417,
                        418, 422, 423, 424, 425, 426,
                        444, 449, 450, 499,
                        500, 501, 502, 503, 504, 505,
                        506, 507, 508, 509])

    hook('initDone', cfg)

    if cfg.server.frontend == 'GAE':
        from google.appengine.ext.webapp import util
        util.run_wsgi_app(bottle.default_app())
    else:
        run(host=host, port=port,
            server=cfg.server.frontend)

def __main__():
    config = None

    if len(sys.argv) > 1:
        import imp
        config = imp.load_source('config', sys.argv[1])

    start(config)

if __name__ == '__main__':
    __main__()
