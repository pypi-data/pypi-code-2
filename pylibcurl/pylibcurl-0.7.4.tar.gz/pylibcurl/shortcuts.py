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


    def add(self, url, **kwargs):
        settings = self.default_curl_settings.copy()
        settings['writefunction'] = lambda x: x
        settings.update(kwargs)
        self._multi.add_handle(Curl(url, **settings))

    # TODO: async mode
    def perform(self, async=False):
        """
            perform multi curl
            if not async:
                return list of tuple(url, headers, content, error)
        """
        sockets = set()
        complete = set() # pair(curl, socket)
        def socket_action(m, socket, event=0):
            code, running = m.socket_action(socket, event)

            # remove complete curls and sockets
            for curl, sock in complete:
                m.remove_handle(curl)
                poll.unregister(sock)

            complete.clear()

            return code, running


        def socket_cb(curl, socket, event):
            if event == const.CURL_POLL_REMOVE:
                complete.add((curl, socket))
            else:
                if socket not in sockets: 
                    sockets.add(socket)
                    poll.register(socket)

                mask = event_curl2poll.get(event, 0)
                poll.modify(socket, mask)
            
        # TODO: timer
        def timer_cb(m, timeout):
            if timeout == 0:
                code, running = m.socket_action(const.CURL_SOCKET_TIMEOUT, 0)
                

        m = self._multi
        m.socketfunction = socket_cb
        m.timerfunction = timer_cb
        
        # epoll for linux only
        poll = select.poll()


        code = const.CURLM_CALL_MULTI_SOCKET
        while code == const.CURLM_CALL_MULTI_SOCKET:
            code, running = m.socket_action(const.CURL_SOCKET_TIMEOUT, 0)
        
        #return 
        while running:
            events = poll.poll(1)
            for sock, event in events:
                mask = event_poll2curl.get(event, 0)

                if event == select.EPOLLHUP:
                    poll.unregister(sock)
                else:
                    code = const.CURLM_CALL_MULTI_SOCKET
                    while code == const.CURLM_CALL_MULTI_SOCKET:
                        code, running = socket_action(m, sock, mask)
