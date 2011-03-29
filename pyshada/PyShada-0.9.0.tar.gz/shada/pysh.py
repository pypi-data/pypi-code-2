import sys
import os
import comm

def _run(cmd, inplace):
    def terminate_shell(args, env, session):
        server.close()
        pass

    def terminate_shell_inplace(args, env, session):
        yield
        while True:
            data = session.recv()
            if data == None:
                break

            inplace_blks.append(data)
            yield
            pass
        session.exit(0)
        server.close()
        pass

    prev_frame = sys._getframe().f_back.f_back
    prev_locals = prev_frame.f_locals
    prev_globals = prev_frame.f_globals

    ns = dict(prev_locals)
    ns['py'] = 'python -m shada.shell_agent'
    if inplace:
        inplace_blks = []
        ns['terminate_shell'] = terminate_shell_inplace
    else:
        ns['terminate_shell'] = terminate_shell
        pass
    
    server = comm.server(ns)
    server.listen()

    server_addr = server.get_addr()
    ns['PYSHELL_SERVER'] = server_addr

    pid = os.fork()
    if pid == 0:                # child
        for key, value in ns.items():
            if isinstance(value, (str, int, float)):
                os.environ[key] = str(value)
                pass
            pass
        
        if inplace:
            os.system('(' + cmd + ')| $py terminate_shell')
        else:
            os.system(cmd + '; $py terminate_shell')
            pass
        sys.exit(0)
        pass
    
    server.handle()

    if inplace:
        return ''.join(inplace_blks)
    pass

def run(cmd):
    _run(cmd, inplace=False)
    pass

def runv(cmd):
    txt = _run(cmd, inplace=True)
    return txt

if __name__ == '__main__':
    def add_prefix(args, env, session):
        yield                   # wait data
        while True:
            data = session.recv()
            if data == None:    # no more data
                break
            session.send(args[0] + data)
            yield               # wait next data
            pass
        session.exit(0)
        pass
    
    for i in range(20):
        run('echo $i|$py add_prefix "hello: "')
        pass

    txt = runv('echo HELLO').strip()
    print 'inplace value: %s' % (txt)
    pass
