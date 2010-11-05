# coding: utf-8
import select
from pylibcurl import Multi, Curl, const

event_epoll2curl = {
    select.EPOLLIN: const.CURL_CSELECT_IN,
    select.EPOLLOUT: const.CURL_CSELECT_OUT,
    select.EPOLLERR: const.CURL_CSELECT_ERR,
}

event_curl2epoll = {
    const.CURL_POLL_IN: select.EPOLLIN,
    const.CURL_POLL_OUT: select.EPOLLOUT,
    const.CURL_POLL_INOUT: select.EPOLLIN | select.EPOLLOUT,
}

event_epoll_verbose = {
    select.EPOLLIN: 'READ (Available for read)',
    select.EPOLLOUT: 'WRITE (Available for write)',
    select.EPOLLPRI: 'Urgent data for read',
    select.EPOLLERR: 'ERROR (Error condition happened on the assoc. fd)',
    select.EPOLLHUP: 'Hang up happened on the assoc. fd',
    select.EPOLLET: 'Set Edge Trigger behavior, the default is Level Trigger behavior',
}

event_curl_verbose = {
    const.CURL_POLL_NONE: 'register, not interested in readiness (yet)',
    const.CURL_POLL_IN: 'READ (register, interested in read readiness)',
    const.CURL_POLL_OUT: 'WRITE (register, interested in write readiness)',
    const.CURL_POLL_INOUT: 'READ/WRITE (register, interested in both read and write readiness)',
    const.CURL_POLL_REMOVE: 'unregister',
}

event_poll2curl = {
    select.POLLIN: const.CURL_CSELECT_IN,
    select.POLLOUT: const.CURL_CSELECT_OUT,
    select.POLLERR: const.CURL_CSELECT_ERR,
}

event_curl2poll = {
    const.CURL_POLL_IN: select.POLLIN,
    const.CURL_POLL_OUT: select.POLLOUT,
    const.CURL_POLL_INOUT: select.POLLIN | select.POLLOUT,
}


class Pool(object):
    default_curl_settings = dict(
        useragent='Mozilla 6', 
        autoreferer=1, 
        followlocation=1,
        maxredirs=20, 
        encoding='',
    )

    def __init__(self, maxconnects, *args, **kwargs):
        self._multi = Multi(*args, **kwargs)
        self._multi.maxconnects = maxconnects

        self._data = {}
        self._poll = select.poll()
        self._sockets = set()
        self._complete = set() # pair(curl, socket)

        def socket_cb(curl, socket, event):
            if event == const.CURL_POLL_REMOVE:
                self._complete.add((curl, socket))
            else:
                if socket not in self._sockets: 
                    self._sockets.add(socket)
                    self._poll.register(socket)

                mask = event_curl2poll.get(event, 0)
                self._poll.modify(socket, mask)
            
        # TODO: timer
        def timer_cb(m, timeout):
            if timeout == 0:
                code, running = m.socket_action(const.CURL_SOCKET_TIMEOUT, 0)
            
        self._multi.socketfunction = socket_cb
        self._multi.timerfunction = timer_cb

    def _socket_action(self, socket, event=0):
        code, running = self._multi.socket_action(socket, event)

        # remove complete curls and sockets
        for curl, sock in self._complete:
            self._multi.remove_handle(curl)
            self._poll.unregister(sock)
            self._sockets.remove(sock)

        self._complete.clear()

        return code, running


    def _run(self):
        code = const.CURLM_CALL_MULTI_SOCKET
        while code == const.CURLM_CALL_MULTI_SOCKET:
            code, running = self._multi.socket_action(const.CURL_SOCKET_TIMEOUT, 0)
        
        #return 
        while running:
            events = self._poll.poll(1)
            for sock, event in events:
                mask = event_poll2curl.get(event, 0)

                if event == select.POLLHUP:
                    self._poll.unregister(sock)
                else:
                    code = const.CURLM_CALL_MULTI_SOCKET
                    while code == const.CURLM_CALL_MULTI_SOCKET:
                        code, running = self._socket_action(sock, mask)

    def add(self, url, **kwargs):
        settings = self.default_curl_settings.copy()
        settings.update(kwargs)

        header = []
        body = []
        error = None

        def headerfunction(v):
            v = v.strip()
            if v:
                header.append(v)

        def writefunction(v):
            body.append(v)

        settings['headerfunction'] = headerfunction
        settings['writefunction'] = writefunction

        
        c = Curl(url, **settings)
        self._data[c] = (url, header, body, error)
        self._multi.add_handle(c)

    # TODO: async mode
    def perform(self, async=False):
        """
            perform multi curl
            if not async:
                return list of tuple(url, headers, content, error)
        """

        if async:
            return 
        else:
            self._run()
            data = [(url, header, ''.join(body), error) 
                for url, header, body, error in self._data.values()]
            self._data.clear()
            return data
