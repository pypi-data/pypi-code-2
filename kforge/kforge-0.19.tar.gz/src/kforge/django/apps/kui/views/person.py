from dm.view.base import *
from kforge.django.apps.kui.views.base import KforgeView
from kforge.django.apps.kui.views import manipulator
import kforge.command
from kforge.exceptions import KforgeCommandError
import random

class PersonView(AbstractClassView, KforgeView):

    domainClassName = 'Person'
    majorNavigationItem = '/person/'
    minorNavigationItem = '/person/'

    def __init__(self, **kwds):
        super(PersonView, self).__init__(**kwds)
        self.person = None

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Index', 'url': '/person/'},
            {'title': 'Search', 'url': '/person/search/'},
        ]
        if self.session:
            self.minorNavigation.append(
                {
                    'title': 'Register project', 
                    'url': '/project/create/'
                }
            )
            if self.isSshPluginEnabled():
                self.minorNavigation.append(
                    {
                        'title': 'Register SSH key', 
                        'url': '/person/%s/sshKeys/create/' % self.session.person.name
                    }
                )
        else:
            self.minorNavigation.append(
                {
                    'title': 'Join', 
                    'url': '/person/create/'
                }
            )

           
    def isSshPluginEnabled(self):
        if not hasattr(self, '_isSshPluginEnabled'):
            self._isSshPluginEnabled = 'ssh' in self.registry.plugins
        return self._isSshPluginEnabled

    def setContext(self):
        super(PersonView, self).setContext()
        self.context.update({
            'person'         : self.getDomainObject(),
        })

    def getDomainObject(self):
        super(PersonView, self).getDomainObject()
        self.person = self.domainObject
        return self.person

class PersonClassView(PersonView): pass

class PersonListView(PersonClassView, AbstractListView):

    templatePath = 'person/list'

    def canAccess(self):
        return self.canReadPerson()


class PersonSearchView(PersonClassView, AbstractSearchView):

    templatePath = 'person/search'
    minorNavigationItem = '/person/search/'
    
    def canAccess(self):
        return self.canReadPerson()


class PersonCreateView(PersonClassView, AbstractCreateView):

    templatePath = 'person/create'
    minorNavigationItem = '/person/create/'

    def getManipulatorClass(self):
        return manipulator.PersonCreateManipulator

    def canAccess(self):
        return self.canCreatePerson()
        
    def setContext(self):
        super(PersonCreateView, self).setContext()
        if self.dictionary[self.dictionary.words.CAPTCHA_IS_ENABLED]:
            captchaHash = self.captcha.name
            captchaUrl = self.makeCaptchaUrl(captchaHash)
            self.context.update({
                'isCaptchaEnabled'  : True,
                'captchaHash'       : captchaHash,
                'captchaUrl'        : captchaUrl,
            })
        else:
            self.context.update({
                'isCaptchaEnabled'  : False,
            })

    def makePostManipulateLocation(self):
        return '/login/'


# todo: returnPath support
# todo: captcha support


#    def makeForm(self):
#        if self.dictionary['captcha.enable']:
#            if self.requestParams.get('captchahash', False):
#                hash = self.requestParams['captchahash']
#                try:
#                    self.captcha = self.registry.captchas[hash]
#                except:
#                    self.makeCaptcha()
#                    self.requestParams['captchahash'] = self.captcha.name
#                    self.requestParams['captcha'] = ''
#            else:
#                self.makeCaptcha()
#                self.requestParams['captchahash'] = self.captcha.name
#                self.requestParams['captcha'] = ''
#                
#        self.form = manipulator.FormWrapper(
#            self.manipulator, self.requestParams, self.formErrors
#        )
#
#    # todo: delete old and deleted captchas, and their image files - cron job?
#
#    def makeCaptcha(self):
#        word = self.makeCaptchaWord()
#        hash = self.makeCaptchaHash(word)
#        try:
#            self.captcha = self.registry.captchas.create(hash, word=word)
#        except:
#            hash = self.makeCaptchaHash(word)
#            self.captcha = self.registry.captchas.create(hash, word=word)
#        
#        fontPath = self.dictionary['captcha.font_path']
#        if not fontPath:  # todo: instead, check file exists
#            raise Exception("No 'captcha.font_path' in system dictionary.")
#        fontSize = int(self.dictionary['captcha.font_size'])
#        path = self.makeCaptchaPath(hash)
#        import kforge.utils.captcha
#        kforge.utils.captcha.gen_captcha(word, fontPath, fontSize, path)
#
#    def makeCaptchaWord(self):
#        wordlength = 5
#        word = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ', wordlength))
#        return word
#
#    def makeCaptchaHash(self, word):
#        return self.makeCheckString(word)
#
#    def makeCaptchaPath(self, captchaHash):
#        mediaRoot = self.dictionary['www.media_root']
#        captchaRoot = mediaRoot + '/images/captchas'
#        captchaPath = captchaRoot + '/%s.png' % captchaHash
#        return captchaPath
#
#    def makeCaptchaUrl(self, captchaHash):
#        mediaHost = self.dictionary['www.media_host']
#        mediaPort = self.dictionary['www.media_port']
#        captchaUrl = 'http://%s:%s/images/captchas/%s.png' % (
#            mediaHost,
#            mediaPort,
#            captchaHash,
#        )
#        return captchaUrl
#
#    def createPerson(self):
#        personName = self.requestParams.get('name', '')
#        command = kforge.command.PersonCreate(personName)
#        try:
#            command.execute()
#        except:
#            # todo: log error
#            self.person = None
#            return None
#        else:
#            command.person.fullname = self.requestParams.get('fullname', '')
#            command.person.email = self.requestParams.get('email', '')
#            command.person.setPassword(self.requestParams.get('password', ''))
#            command.person.save()
#            self.person = command.person
#        return self.person


class PersonInstanceView(PersonView):

    def canUpdatePerson(self):
        if self.person == None:
            self.getDomainObject()
        return super(PersonInstanceView, self).canUpdatePerson()


class PersonReadView(PersonInstanceView, AbstractReadView):

    templatePath = 'person/read'

    def getDomainObject(self):
        if self.path == '/person/home/' and self.session:
            self.domainObject = self.session.person
            self.person = self.domainObject
        else:
            super(PersonReadView, self).getDomainObject()
        if self.session and self.session.person == self.domainObject:
            self.majorNavigationItem = '/person/home/'
            self.minorNavigationItem = '/person/home/'
        return self.domainObject

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canReadPerson()

    def setContext(self):
        super(PersonReadView, self).setContext()
        self.context.update({
            'isSessionPerson': self.isSessionPerson()
        })

    def isSessionPerson(self):
        if self.session and self.domainObject:
            return self.session.person == self.domainObject
        else:
            return False


class PersonUpdateView(PersonInstanceView, AbstractUpdateView):

    templatePath = 'person/update'

    def getManipulatorClass(self):
        return manipulator.PersonUpdateManipulator

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canUpdatePerson()

    def makePostManipulateLocation(self):
        return '/person/home/'


class PersonDeleteView(PersonInstanceView, AbstractDeleteView):

    templatePath = 'person/delete'
    
    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canDeletePerson()

    def manipulateDomainObject(self):
        super(PersonDeleteView, self).manipulateDomainObject()
        if self.session:
            if self.getDomainObject() == self.session.person:
                self.stopSession()

    def makePostManipulateLocation(self):
        return '/person/'


def list(request):
    view = PersonListView(request=request)
    return view.getResponse()
    
def search(request, startsWith=''):
    view = PersonSearchView(request=request, startsWith=startsWith)
    return view.getResponse()
    
def create(request, returnPath=''):   
    view = PersonCreateView(request=request)
    return view.getResponse()

def read(request, personName=''):
    view = PersonReadView(request=request, domainObjectKey=personName)
    return view.getResponse()

def update(request, personName):
    view = PersonUpdateView(request=request, domainObjectKey=personName)
    return view.getResponse()

def delete(request, personName):
    view = PersonDeleteView(request=request, domainObjectKey=personName)
    return view.getResponse()

