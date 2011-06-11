import api
import tpl

class Citadel(api.Protocol):
    def __init__(self, config=None):
        self.config = config
        api.Protocol.__init__(self)
    @property
    def admin_login(self):
        if not hasattr(self, '_login'):
            if hasattr(self.config, 'admin_login'):
                self._login = self.config.admin_login
            else:
                self._login = raw_input('Admin LOGIN :')
        return self._login
    @property
    def admin_psw(self):
        if not hasattr(self, '_psw'):
            if hasattr(self.config, 'admin_psw'):
                self._psw = self.config.admin_psw
            else:
                self._psw = raw_input('Admin PASSWORD :')
        return self._psw
    def admin(self):
        return self.login(self.admin_login, self.admin_psw)
    def close(self):
        self.QUIT()
        self.quit()
    def login(self, usr, psw):
        return self.USER(usr) and self.PASS(psw)
    def chku(self, usr, ignore=False):
        return self.QUSR(usr, ignore=ignore)==usr
    def creu(self, usr, psw, lvl='4'):
        if self.chku(usr, ignore=True):  return True
        self.admin()
        self.CREU(usr, psw)
        valid = self.VALI(usr, lvl)
        self.LOUT()
        return valid and self.chku(usr)
    def delu(self, usr):
        self.admin()
        c = self.ASUP(usr, '0','0','0','0','0','0','0','0')
        self.LOUT()
        return c
    def listu(self):
        for usr, level in sorted(self.LIST()):
            if not usr.startswith('SYS_') and level<'6':
                yield usr
    def mail(self, dst, sbj, txt): # post a mail
        self.GOTO('mail')
        msg = [' %s'%i for i in txt.split('\n')]
        self.ENT0(to=dst, sbj=sbj, msg=msg)
    def vcard(self, user, first, name, full): # post a vcard
        msg = tpl.vcf%(user, user, name, first, full, user)
        msg = msg.lstrip().split('\n')
        self.ENT0(fmt='4', msg=msg)
    def updusr(self, usr, psw, pre, nom, full): # update user info
        self.login(usr, psw)
        self.GOTO('My Citadel Config')
        self.vcard(usr, pre, nom, full)
        self.LOUT()
    def creuser(self, login, psw, pre, nom, full):
        if self.creu(login, psw):
            self.updusr(login, psw, pre, nom, full)

