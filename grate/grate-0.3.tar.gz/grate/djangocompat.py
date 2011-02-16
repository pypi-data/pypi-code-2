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
        """
        :returns: The full name of this user.
        :rtype: str
        """
        first = self.first_name if self.first_name else ''
        last = self.last_name if self.last_name else ''
        return ('%s %s' % (first, last)).strip()

    def is_anonymous(self):
        """
        :returns: False
        :rtype: bool
        """
        return False

    def is_authenticated(self):
        """
        :returns: True
        :rtype: bool
        """
        return True

    def set_password(self, raw_password):
        """
        Changes the user's password by storing the crypt(2) version.
        :param raw_password: The raw password.
        """
        salt = uuid.uuid4().hex
        x = hashlib.sha1(salt + raw_password)
        self.password = 'sha1$%s$%s' % (salt, x.hexdigest())

    def check_password(self, raw_password):
        """
        :param raw_password: The raw password.
        :returns: True if the given raw password matches.
        """
        if self.has_unusable_password():
            return False
        _, salt, hashed_password = self.password.split('$')
        x = hashlib.sha1(salt + raw_password)
        return x.hexdigest() == hashed_password

    def set_unusable_password(self):
        """
        Marks this user's password as invalid.
        """
        self.password = '!'

    def has_unusable_password(self):
        """
        :returns: True if this user's password cannot be used for
            authentication.
        """
        return self.password == '!'

    # TODO test me
    @classmethod
    def create_user(cls, username, password, email=None):
        """
        :param username: The username.
        :param password: The raw password.
        :param email: The email address.
        :returns: The User.
        """
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
