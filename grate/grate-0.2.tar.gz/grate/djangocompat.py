import hashlib
import uuid
from datetime import datetime
from mongoengine import StringField, BooleanField, DateTimeField
from grate.access import Entity


class DjangoUser(Entity):
    username = StringField(min_length=1, max_length=50, unique=True,
        required=True)
    # Start Django-compat
    first_name = StringField(max_length=30)
    last_name = StringField(max_length=30)
    email = StringField()
    password = StringField(max_length=128)
    is_staff = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_superuser = BooleanField(default=False)
    last_login = DateTimeField(default=datetime.now)
    date_joined = DateTimeField(default=datetime.now)

    def get_full_name(self):
        first = self.first_name if self.first_name else ''
        last = self.last_name if self.last_name else ''
        return ('%s %s' % (first, last)).strip()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        salt = uuid.uuid4().hex
        x = hashlib.sha1(salt + raw_password)
        self.password = 'sha1$%s$%s' % (salt, x.hexdigest())

    def check_password(self, raw_password):
        if self.has_unusable_password():
            return False
        _, salt, hashed_password = self.password.split('$')
        x = hashlib.sha1(salt + raw_password)
        return x.hexdigest() == hashed_password

    def set_unusable_password(self):
        self.password = '!'

    def has_unusable_password(self):
        return self.password == '!'

    # TODO test me
    @classmethod
    def create_user(cls, username, password, email=None):
        u = cls(username=username, email=email)
        if password:
            u.set_password(password)
        else:
            u.set_unusable_password()
        return u

    def __repr__(self):
        return '<User %s>' % self.username

    def __unicode__(self):
        return self.username

    __str__ = __unicode__
