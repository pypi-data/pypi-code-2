# coding: utf-8
import select, threading
from pylibcurl import Multi, Curl, const
from Queue import Queue, Empty

try:
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
except AttributeError:
    pass


class Pool(threading.Thread):
    """
        Pool work as like Thread and Queue
    """
    default_curl_settings = dict(
        useragent='Mozilla 6', 
        autoreferer=1, 
        followlocation=1,
        maxredirs=20, 
        encoding='',
    )

    def __init__(self, maxconnects, qsize=0, **kwargs):
        self._multi = Multi(**kwargs)
        self._multi.maxconnects = maxconnects
        self._queue = Queue(qsize)
        self._size = maxconnects

        self._data = {}
        self._sockets = set()
        self._complete = set() # pair(curl, socket)


        def socket_cb(curl, socket, event):
            if event == const.CURL_POLL_REMOVE:
                self._complete.add((curl, socket))
            elif socket not in self._sockets:
                self._sockets.add(socket)
            
        # TODO: timer
        def timer_cb(m, timeout):
            if timeout == 0:
                code, running = m.socket_action(const.CURL_SOCKET_TIMEOUT, 0)
            
        self._multi.socketfunction = socket_cb
        self._multi.timerfunction = timer_cb

        super(Pool, self).__init__()

    def _do_socket_action(self, socket, event=0):
        code = const.CURLM_CALL_MULTI_SOCKET
        while code == const.CURLM_CALL_MULTI_SOCKET:
            code, running = self._multi.socket_action(socket, event)
        
        return running

    def _do_remove(self):
        # remove complete curls and sockets
        for curl, sock in self._complete:
            self._multi.remove_handle(curl)
            self._sockets.remove(sock)
            
            # call callback
            url, header, body, callback = self._data[curl]
            body = ''.join(body)

            if self._Thread__started.is_set():
                del self._data[curl]
            else:
                self._data[curl][2] = body

            if callback:
                callback(curl, url, header, body)
            
            # task done
            self._queue.task_done()

        removed = len(self._complete) > 0
        if removed:
            self._complete.clear()

        return removed

    
    def _do_add(self):
        start_event = self._Thread__started
        added = False

        while len(self._multi._handles) < self._size:
            block = False
            
            # thread mode and daemon and empty
            if self.isDaemon() and start_event.is_set() and not self._multi._handles: 
                block = True
            
            try:
                data = self._queue.get(block=block)
            except Empty:
                break
            else:
                added = True
                url, kwargs, callback = data
                c = self._create_curl(url, callback, **kwargs)
                self._multi.add_handle(c)


        if added:
            code = const.CURLM_CALL_MULTI_SOCKET
            while code:
                code, running = self._multi.socket_action(const.CURL_SOCKET_TIMEOUT, 0)

        return added

    def _create_curl(self, url, callback, **kwargs):
        settings = self.default_curl_settings.copy()
        settings.update(kwargs)

        header = []
        body = []

        def headerfunction(v):
            v = v.strip()
            if v:
                header.append(v)

        def writefunction(v):
            body.append(v)

        settings['headerfunction'] = headerfunction
        settings['writefunction'] = writefunction

        
        c = Curl(url, **settings)
        self._data[c] = [url, header, body, callback]
        return c



    def run(self):
        """
            for threading mode use "start" method
            for non-threading mode use "run" method
        """
        start_event = self._Thread__started
        self._do_add()
        running = 1

        while True:
            
            while running:
                (r, w, e) = select.select(self._sockets, self._sockets, self._sockets, 1)

                sockets = set(r + w + e)
                for sock in sockets:
                    running = self._do_socket_action(sock, 0)
                    self._do_remove()


                self._do_add()

            # check loop
            started = start_event.is_set()
            if not started and not self.isDaemon():
                break

        # for non-threading mode
        if not start_event.is_set():
            data = [(curl, v[0], v[1], v[2]) 
                for curl, v in self._data.items()]
            self._data.clear()
            return data

    def add(self, url, callback=None, **kwargs):
        """
            put values to queue

            callback prototype:
                def callback(curl, start_url, header, body):
                    [code]
        """
        self._queue.put((url, kwargs, callback))


    def join(self, timeout=None):
        """
            if thread is daemon then run loop forever
        """
        if self.isDaemon():
            self._queue.join()
        else:
            super(Pool, self).join(timeout)





