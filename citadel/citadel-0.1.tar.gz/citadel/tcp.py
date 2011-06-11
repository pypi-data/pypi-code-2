import socket

class Client(object):
    def __init__(self):
        cfg = self.config
        self.logfil = hasattr(cfg, 'log') and cfg.log
        adr = hasattr(cfg, 'server_adr') and cfg.server_adr or '127.0.0.1'
        prt = hasattr(cfg, 'server_prt') and cfg.server_prt or 504
        self.sock = self.connect(adr, prt)
        rf = self.sock.makefile('rb', -1)
        wf = self.sock.makefile('wb', 0)
        self.read = rf.readline
        self.write = wf.write
        c, a = self.get()
        self.log(a[0], 'w')
    def log(self, txt, mode='a'):
        if hasattr(self, 'logfil'):
            log = open(self.logf, mode)
            log.write('%s\n'%txt)
            log.close
    def connect(self, adr, port):
        for af, socktype, proto, cn, sa in socket.getaddrinfo(
            adr , port , 0 , socket.SOCK_STREAM
        ):
            try:
                sock = None
                sock = socket.socket(af, socktype, proto)
                sock.connect(sa)
                break
            except socket.error:
                if sock: sock.close()
        else:
            raise socket.error
        return sock
    def quit(self):
        self.sock.close()
        self.sock = None
    def readline(self, log=True):
        line = self.read().rstrip('\n')
        if log: self.log('<-   %s'%line)
        return line
    def readlines(self):
        while True:
            line = self.readline(log=False)
            if line=='000': break
            data =  line.split('|')
            yield data[0] if len(data)==1 else data
    def writeline(self, line, log=True):
        if log: self.log('  -> %s'%line)
        self.write(u'%s\n' % unicode(line))
    def writelines(self, lines, log=False):
        for line in lines:
            self.writeline(line, log)
        self.writeline('000', log)
    def get(self):
        code, args = self.readline().split(' ', 1)
        return code, args.split('|')
    def req(self, *arg, **kw):
        ignore = kw.get('ignore')
        cmd = '%s %s' % (arg[0], '|'.join(arg[1:]))
        self.writeline(cmd)
        c, a = self.get()
        if len(a)==1: a=a[0]
        if c.startswith('5') and c!=ignore:
            print '\n! ! ! ERROR %s : %s ! ! !\n' % (c, a)
            return None, None
        else:
            return c, a
