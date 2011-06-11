import tcp

class Protocol(tcp.Client):
    def INFO(self): # get server infos
        c, a = self.req('INFO')
        if c=='100':
            raws = list(self.readlines())
            return ' - '.join(raws[i] for i in (4,2,3))
    def NOOP(self): # NOP
        c, a = self.req('NOOP')
        assert c=='200'
    def QUIT(self): # close cnx
        c, a = self.req('QUIT')
    def CREU(self, usr, psw): # create usr
        c, a = self.req('CREU', usr, psw)
    def VALI(self, usr, level): # validate usr
        c, a = self.req('VALI', usr, level)
        return c=='200'
    def LOUT(self): # logout
        c, a = self.req('LOUT')
    def USER(self, username): # send login
        c, a = self.req('USER', username)
        return c=='300'
    def PASS(self, password): # send psw
        c, a = self.req('PASS',  password)
        return c=='200'
    def QUSR(self, usr, ignore=False): # chk usr
        if ignore: ignore='570'
        res = self.req('QUSR',  usr, ignore=ignore)
        if res: return res[1]
    def GOTO(self, room): # goto room
        c, a = self.req('GOTO',  room)
        return c=='200'
    def REGI(self, name): # set usr info
        c, a = self.req('REGI')
        if c=='400':
            lines = [name, 'adr', 'vil', 'st', '33333', 'tel', 'mail', 'fr']
            self.writelines(lines)
        else:
            self.get()
            self.writeline('000')
    def RENU(self, old, new): # chg usr login
        self.req('RENU', old, new)
    def LIST(self): # list users
        c, a = self.req('LIST')
        for lin in self.readlines():
            login, level, num, last, log, msg, psw, what = lin
            yield login, level
    def ASUP(self, usr, p, f, t, m, a, n, s, g): # set usr params
        c, a = self.req('ASUP', usr, p, f, t, m, a, n , s, g)
        return c=='200'
    def LFLR(self): # list floors
        c, a = self.req('LFLR')
        assert c=='100'
        for floor in self.readlines():
            yield (
                floor[0], # num
                floor[1], # name
                floor[2], # refcount
            )
    def LKRA(self, floor=-1): # known rooms
        c, a = self.req('LKRA %d'%floor)
        assert c=='100'
        for room in self.readlines():
            yield (
                room[0],
                room[1],
                room[2],
                room[3],
                room[4],
                room[5],
            )
    def ENT0(self, post='1', to='', anon='0', fmt='0', sbj='', usr='', confirm='0', cc='', bcc='', msg=''):
        c, a = self.req('ENT0', post, to, anon, fmt, sbj, usr, confirm, cc, bcc)
        if c=='400':
            self.writelines(msg, log=True)
        else:
            print '? ? ?', c, a
