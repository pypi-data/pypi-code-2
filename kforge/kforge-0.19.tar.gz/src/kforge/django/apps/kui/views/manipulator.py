from dm.view.manipulator import BaseManipulator
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
import dm.webkit as webkit
from kforge.ioc import *
from kforge.exceptions import KforgeCommandError
import re
import kforge.regexps
import kforge.command

if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':

    class PasswordField(webkit.fields.RegexField):

        widget = webkit.fields.PasswordInput

        def __init__(self, *args, **kwargs):
            kwargs['regex'] = '^\S{4,}$' 
            kwargs['min_length'] = 4 
            super(PasswordField, self).__init__(*args, **kwargs)
 

    class PasswordConfirmationField(webkit.fields.Field):

        widget = webkit.fields.PasswordInput

        def __init__(self, *args, **kwargs):
            super(PasswordConfirmationField, self).__init__(*args, **kwargs)
 

    class PersonNameField(webkit.fields.RegexField):

        def __init__(self, *args, **kwargs):
            regex = '^(?!%s)%s$' % (kforge.regexps.reservedPersonName, kforge.regexps.personName)
            kwargs['required'] = True
            kwargs['regex'] = regex 
            kwargs['min_length'] = 2
            kwargs['max_length'] = 20
            super(PersonNameField, self).__init__(*args, **kwargs)

        def clean(self, value):
            super(PersonNameField, self).clean(value)
            # Check name is available.
            command = kforge.command.AllPersonRead(value)
            try:
                command.execute()
            except KforgeCommandError:
                pass
            else:
                message = "Login name is already being used by another person."
                raise webkit.ValidationError(message)
            return value

    class SshKeyStringField(webkit.fields.RegexField):

        def __init__(self, *args, **kwargs):
            regex = '^%s$' % (kforge.regexps.sshKeyString)
            kwargs['required'] = True
            kwargs['regex'] = regex 
            kwargs['widget'] = webkit.widgets.Textarea
            super(SshKeyStringField, self).__init__(*args, **kwargs)

        def clean(self, value):
            super(SshKeyStringField, self).clean(value)
            # Check key string is available.
            value = value.strip()
            publicKey = value.split(' ')[1]
            if kforge.command.Command.registry.sshKeys.search(publicKey):
                message = "Key has already been registered on this site."
                raise webkit.ValidationError(message)
            # Check key decodes from base64.
            try:
                publicKey.decode('base64')
            except:
                message = "Key does not appear to be encoded with base64."
                raise webkit.ValidationError(message)
            return value

    class ProjectNameField(webkit.fields.RegexField):
        
        def __init__(self, *args, **kwargs):
            regex = '^(?!%s)%s$' % (kforge.regexps.reservedProjectName, kforge.regexps.projectName)
            kwargs['required'] = True
            kwargs['regex'] = regex 
            kwargs['min_length'] = 3
            kwargs['max_length'] = 15
            super(ProjectNameField, self).__init__(*args, **kwargs)

        def clean(self, value):
            super(ProjectNameField, self).clean(value)
            # Check name is available.
            command = kforge.command.AllProjectRead(value)
            try:
                command.execute()
            except KforgeCommandError:
                pass
            else:
                message = "Project name is already being used by another project."
                raise webkit.ValidationError(message)
            return value


    class ServiceNameField(webkit.fields.RegexField):
        
        def __init__(self, *args, **kwargs):
            regex = '^%s$' % (kforge.regexps.serviceName)
            kwargs['required'] = True
            kwargs['regex'] = regex 
            kwargs['min_length'] = 1
            kwargs['max_length'] = 16
            super(ServiceNameField, self).__init__(*args, **kwargs)


class PersonManipulator(DomainObjectManipulator):

    def isPersonName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.regexps.personName)
        if not pattern.match(field_data):
            msg = "This field can only contain alphanumerics, "
            msg += "underscores, hyphens, and dots."
            raise webkit.ValidationError(msg)

    def isReservedPersonName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.regexps.reservedPersonName)
        if pattern.match(field_data):
            msg = "This field is reserved and can not be registered."
            raise webkit.ValidationError(msg)

    def isAvailablePersonName(self, field_data, all_data):
        command = kforge.command.AllPersonRead(field_data)
        try:
            command.execute()
        except KforgeCommandError:
            pass
        else:
            message = "Login name is already being used by another person."
            raise webkit.ValidationError(message)

    def isMatchingPassword(self, field_data, all_data):
        password = all_data['password']
        passwordconfirmation = all_data['passwordconfirmation']
        if not (password == passwordconfirmation):
            raise webkit.ValidationError("Passwords do not match.")

    def isMatchingEmail(self, field_data, all_data):
        email = all_data['email']
        emailconfirmation = all_data['emailconfirmation']
        if not (email == emailconfirmation):
            raise webkit.ValidationError("Emails do not match.")

    def isCaptchaCorrect(self, field_data, all_data):
        if self.dictionary['captcha.enable']:
            word = all_data['captcha']
            hash = all_data['captchahash']
            if not word and not hash:
                raise webkit.ValidationError("Captcha failure.")
            read = kforge.command.CaptchaRead(hash)
            try:
                read.execute()
            except KforgeCommandError, inst: 
                raise webkit.ValidationError("Captcha failure.")
            captcha = read.object
            if not captcha.checkWord(word):
                raise webkit.ValidationError("Captcha failure.")

    def clean(self):
        if 'passwordconfirmation' in self.cleaned_data and 'password' in self.cleaned_data \
        and self.cleaned_data['passwordconfirmation'] != self.cleaned_data['password']:
            if 'passwordconfirmation' in self._errors:
                self._errors['passwordconfirmation'].append("Passwords do not match.")
            else:
                self._errors['passwordconfirmation'] = webkit.fields.ErrorList(["Passwords do not match."])
        if 'emailconfirmation' in self.cleaned_data and 'email' in self.cleaned_data \
        and self.cleaned_data['emailconfirmation'] != self.cleaned_data['email']:
            if 'emailconfirmation' in self._errors:
                self._errors['emailconfirmation'].append("Emails do not match.")
            else:
                self._errors['emailconfirmation'] = webkit.fields.ErrorList(["Emails do not match."])
        if self._errors:
            delattr(self, 'cleaned_data')
        else:
            return self.cleaned_data


class PersonCreateManipulator(PersonManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields = webkit.SortedDict([
                ('name', PersonNameField()),
                ('password', PasswordField()),
                ('passwordconfirmation', PasswordConfirmationField()), 
                ('fullname', webkit.Field(required=True)),
                ('email', webkit.EmailField(required=True)),
                ('emailconfirmation', webkit.Field(required=True)),
            ])
            # Todo: Fixup captcha.
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields.append(
                webkit.TextField(
                    field_name="name", 
                    is_required=True, 
                    validator_list=[
                        self.isPersonName, 
                        self.isReservedPersonName, 
                        self.isAvailablePersonName, 
                        self.isTwoCharsMin,
                        self.isTwentyCharsMax,
                    ]
                )
            )
            self.fields.append(
                webkit.PasswordField(
                    field_name="password", 
                    is_required=True, 
                    validator_list=[
                        self.isFourCharsMin,
                    ]
                )
            )
            self.fields.append(
                webkit.PasswordField(
                    field_name="passwordconfirmation", 
                    is_required=True, 
                    validator_list=[
                        self.isMatchingPassword
                    ]
                )
            )
            self.fields.append(
                webkit.TextField(
                    field_name="fullname", 
                    is_required=True
                )
            )
            self.fields.append(
                webkit.EmailField(
                    field_name="email", 
                    is_required=True
                )
            )
            self.fields.append(
                webkit.EmailField(
                    field_name="emailconfirmation", 
                    is_required=True, 
                    validator_list=[
                        self.isMatchingEmail
                    ]
                ) 
            )
            if self.dictionary['captcha.enable']:
                self.fields.append(
                    webkit.TextField(
                        field_name="captcha", 
                        is_required=isCaptchaEnabled, 
                        validator_list=[
                            self.isCaptchaCorrect
                        ]
                    ) 
                )
                self.fields.append(
                    webkit.HiddenField(
                        field_name="captchahash", 
                        is_required=False,
                    )   
                )

class PersonUpdateManipulator(PersonManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields = webkit.SortedDict([
                ('password', PasswordField(required=False)),
                ('passwordconfirmation', PasswordField(required=False)),
                ('fullname', webkit.Field(required=True)),
                ('email', webkit.EmailField(required=True)),
            ])
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields.append(
                webkit.PasswordField(
                    field_name="password", 
                    is_required=False, 
                    validator_list=[
                        self.isFourCharsMin,
                    ]
                )
            )
            self.fields.append(
                webkit.PasswordField(
                    field_name="passwordconfirmation", 
                    is_required=False, 
                    validator_list=[
                        self.isMatchingPassword
                    ]
                )
            )
            self.fields.append(
                webkit.TextField(
                    field_name="fullname", 
                    is_required=True
                )
            )
            self.fields.append(
                webkit.EmailField(
                    field_name="email", 
                    is_required=True
                )
            )


class SshKeyManipulator(HasManyManipulator):

    def isSshKey(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.regexps.sshKeyString)
        if not pattern.match(field_data):
            msg = "Enter a valid value. "
            raise webkit.ValidationError(msg)

    def isAvailableSshKey(self, field_data, all_data):
        keyString = all_data['keyString']
        keyString = keyString.strip()
        sshKeys = []
        for sshKey in self.registry.sshKeys.findDomainObjects(keyString=keyString):
            if sshKey.person != self.client.person:
                if not sshKey.isConsummated:
                    if sshKey.getDeltaSinceDateCreated().days:
                        sshKey.delete()
        if self.registry.sshKeys.findDomainObjects(keyString=keyString):
            message = "Key has already been registered."
            raise webkit.ValidationError(message)

    def isBase64Encoded(self, field_data, all_data):
        # Check key string decodes from base64.
        keyString = all_data['keyString']
        keyString = keyString.strip()
        try:
            key = keyString.split(' ')[1].decode('base64')
        except:
            message = "Key string does not appear to have base64 encoding."
            raise webkit.ValidationError(message)

    def clean(self):
        if 'keyString' in self.cleaned_data:
            keyString = self.cleaned_data['keyString']
            keyString = keyString.strip()
            if self.registry.sshKeys.findDomainObjects(keyString=keyString):
                message = "Key string has already been registered on this site."
                if 'keyString' in self._errors:
                    self._errors['keyString'].append(msg)
                else:
                    self._errors['keyString'] = webkit.fields.ErrorList([msg])
        if self._errors:
            delattr(self, 'cleaned_data')
        else:
            return self.cleaned_data


class SshKeyCreateManipulator(SshKeyManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields = webkit.SortedDict([
                ('keyString', SshKeyStringField()),
            ])
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                webkit.LargeTextField(
                    field_name="keyString", 
                    is_required=True,
                    validator_list=[
                        self.isSshKey,
                        self.isAvailableSshKey,
                    ]
                ),
            )


class ProjectManipulator(DomainObjectManipulator):

    def isProjectName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.regexps.projectName)
        if not pattern.match(field_data):
            msg = "This field can only contain lowercase letters or numbers."
            raise webkit.ValidationError(msg)

    def isReservedProjectName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.regexps.reservedProjectName)
        if pattern.match(field_data):
            msg = "This field is reserved and can not be registered."
            raise webkit.ValidationError(msg)

    def isAvailableProjectName(self, field_data, all_data):
        command = kforge.command.AllProjectRead(field_data)
        try:
            command.execute()
        except KforgeCommandError:
            pass
        else:
            message = "Project name is already being used by another project."
            raise webkit.ValidationError(message)


class ProjectCreateManipulator(ProjectManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields = webkit.SortedDict([
                ('title', webkit.Field(required=True)),
                ('name', ProjectNameField()),
                ('licenses',webkit.MultipleChoiceField(required=False, 
                    choices=self.listRegisteredLicenses())),
                ('description', webkit.Field(required=True, widget=webkit.widgets.Textarea)),
            ])
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                webkit.TextField(
                    field_name="title", 
                    is_required=True
                ),
                webkit.SelectMultipleField(
                    field_name="licenses", 
                    is_required=False,
                    choices=self.listRegisteredLicenses(),
                    size=4,
                ),
                webkit.LargeTextField(
                    field_name="description", 
                    is_required=True,
                    validator_list=[
                    ]
                ),
                webkit.TextField(
                    field_name="name", 
                    is_required=True, 
                    maxlength=15,
                    validator_list=[
                        self.isProjectName, 
                        self.isAvailableProjectName, 
                        self.isReservedProjectName, 
                        self.isThreeCharsMin,
                        self.isFifteenCharsMax,
                    ]
                ),
            )

    def listRegisteredLicenses(self):
        command = kforge.command.LicenseList()
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(l.id, l.name) for l in command.licenses]


class ProjectUpdateManipulator(ProjectManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            licenses = self.listRegisteredLicenses()
            self.fields = webkit.SortedDict([
                ('title', webkit.Field(required=True)),
                ('licenses', webkit.MultipleChoiceField(required=False, choices=licenses)),
                ('description', webkit.Field(required=True, widget=webkit.widgets.Textarea)),
            ])
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                webkit.TextField(
                    field_name="title", 
                    is_required=True
                ),
                webkit.SelectMultipleField(
                    field_name="licenses", 
                    is_required=False,
                    choices=self.listRegisteredLicenses(),
                    size=4,
                ),
                webkit.LargeTextField(
                    field_name="description", 
                    is_required=True,
                    validator_list=[
                    ]
                ),
            )

    def listRegisteredLicenses(self):
        command = kforge.command.LicenseList()
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(l.id, l.name) for l in command.licenses]


class MemberManipulator(HasManyManipulator):

    def listRegisteredPersons(self):
        command = kforge.command.PersonList()
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(p.getRegisterKeyValue(), p.getLabelValue()) for p in command.persons]

    def listRegisteredRoles(self):
        command = kforge.command.RoleList()
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(r.getRegisterKeyValue(), r.getLabelValue()) for r in command.roles]


class MemberCreateManipulator(MemberManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            persons = self.listRegisteredPersons()
            roles = self.listRegisteredRoles()
            self.fields = webkit.SortedDict([
                ('person', webkit.ChoiceField(required=True, choices=persons)),
                ('role', webkit.ChoiceField(required=True, choices=roles)),
            ])
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                webkit.SelectField(
                    field_name="person", 
                    is_required=True,
                    choices=self.listRegisteredPersons(),
                    validator_list=[
                        self.isAvailableMember, 
                    ]
                ),
                webkit.SelectField(
                    field_name="role", 
                    is_required=True,
                    choices=self.listRegisteredRoles(),
                ),
            )
    
    def isAvailableMember(self, field_data, all_data):
        personName = all_data['person']
        person = self.registry.persons[personName]
        project = self.objectRegister.owner
        if not person in project.members:
            return True
        else:
            message = "%s is already a member of this project." % (person.getLabelValue())
            message += " Please choose another person."
            raise webkit.ValidationError(message)

    def clean(self):
        if 'person' in self.cleaned_data:
            personName = self.cleaned_data['person']
            person = self.registry.persons[personName]
            project = self.objectRegister.owner
            if person in project.members:
                msg = u"%s is already a member of this project." % person.getLabelValue()
                if 'person' in self._errors:
                    self._errors['person'].append(msg)
                else:
                    self._errors['person'] = webkit.fields.ErrorList([msg])
        if self._errors:
            delattr(self, 'cleaned_data')
        else:
            return self.cleaned_data

class MemberUpdateManipulator(MemberManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            persons = self.listRegisteredPersons()
            roles = self.listRegisteredRoles()
            self.fields = webkit.SortedDict([
                ('role', webkit.ChoiceField(required=True, choices=roles)),
            ])
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                webkit.SelectField(
                    field_name="role", 
                    is_required=True,
                    choices=self.listRegisteredRoles(),
                ),
            )


class ServiceManipulator(HasManyManipulator):

    def isServiceName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.regexps.serviceName)
        if not pattern.match(field_data):
            msg = "Enter a valid value. "
            raise webkit.ValidationError(msg)

    def isAvailableServiceName(self, field_data, all_data):
        serviceName = all_data['name']
        service = self.domainObject
        if self.domainObject and (service.name == serviceName):
            return True
        project = self.objectRegister.owner
        if not serviceName in project.services:
            return True
        else:
            message = "A service called '%s' already exists." % (serviceName)
            message += " Please choose another service name."
            raise webkit.ValidationError(message)

    def clean(self):
        if 'name' in self.cleaned_data:
            serviceName = self.cleaned_data['name']
            service = self.domainObject
            project = self.objectRegister.owner
            if serviceName in project.services and \
            not (service and (service.name == serviceName)):
                msg = u"A service called '%s' already exists." % (serviceName)
                msg += u" Please choose another service name."
                if 'name' in self._errors:
                    self._errors['name'].append(msg)
                else:
                    self._errors['name'] = webkit.fields.ErrorList([msg])
        if self._errors:
            delattr(self, 'cleaned_data')
        else:
            return self.cleaned_data


class ServiceCreateManipulator(ServiceManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            plugins = self.listPlugins()
            self.fields = webkit.SortedDict([
                ('name', ServiceNameField()),
                ('plugin', webkit.ChoiceField(required=True, choices=plugins)),
            ])
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                webkit.SelectField(
                    field_name="plugin", 
                    is_required=True,
                    choices=self.listPlugins(),
                ),
                webkit.TextField(
                    field_name="name", 
                    is_required=True,
                    validator_list=[
                        self.isServiceName,
                        self.isAvailableServiceName,
                    ]
                ),
            )

    def listPlugins(self):
        command = kforge.command.ProjectPluginList(self.objectRegister.owner)
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(p.name, p.name) for p in command.results]


class ServiceUpdateManipulator(ServiceManipulator):

    def buildFields(self):
        if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
            self.fields = webkit.SortedDict([
                ('name', ServiceNameField()),
            ])
        elif webkit.webkitName == 'django' and webkit.webkitVersion == '0.96':
            self.fields = (
                webkit.TextField(
                    field_name="name", 
                    is_required=True,
                    validator_list=[
                        self.isServiceName,
                        self.isAvailableServiceName,
                    ]
                ),
            )


class ServiceExtnManipulator(HasManyManipulator):

    def isAttrExcluded(self, metaAttr):
        # super() doesn't work, hence:
        if HasManyManipulator.isAttrExcluded(self, metaAttr):
            return True 
        if metaAttr.name == 'service':
            return True
        return False

    def create(self, data):
        # extn object created by plugin event handlers
        self.update(data)  

