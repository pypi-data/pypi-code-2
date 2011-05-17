import os.path
from string import letters, digits, ascii_lowercase, ascii_uppercase
from random import choice, randint
from datetime import date

SAFE_CHARS = letters + digits
S_CHARS = 'bcdfghjklmnpqrstvwxz'
G_CHARS = 'aeiouy'
EMAIL_SERVERS = ['gmail.com', 'yahoo.com']

FILES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')

def load_file(name):
    path = os.path.join(FILES_DIR, name)
    lines = [x.strip().decode('utf-8') for x in file(path) if x.strip()]
    return lines


def random_password(min_length=8, max_length=10):
    """
    Make random password.

    Ensures that password has at least one digit, upper case letter and
    lower case letter.
    """

    chars = ''.join(map(choice, (ascii_lowercase, ascii_uppercase, digits)))
    length = range(randint(min_length, max_length) - len(chars))
    return reduce(lambda a, b: a + choice(SAFE_CHARS), length, chars)


def random_login(min_length=8, max_length=8):
    """
    Make random login.
    """

    length = randint(min_length, max_length)
    chars = []
    for x in xrange(0, length, 2):
       chars.extend((choice(G_CHARS), choice(S_CHARS)))
    return ''.join(chars[:length])


def random_birthday(start_year=1960, end_year=1990):
    """
    Make random birth date.
    """

    return date(randint(start_year, end_year), randint(1, 12), randint(1, 28))


def random_email(login=None):
    """
    Make random email.
    """

    if not login:
        login = random_login()
    return '%s@%s' % (login, choice(EMAIL_SERVERS))


def random_ru_fname():
    """
    Make random russian first name.
    """

    names = load_file('ru_fname.txt')
    return choice(names)


def random_ru_lname():
    """
    Make random russian last name.
    """

    names = load_file('ru_lname.txt')
    return choice(names)


def random_ru_city():
    """
    Make random city in Russian Federation.
    """

    names = load_file('ru_city.txt')
    return choice(names)


def random_icq():
    """
    Make random ICQ number.
    """

    return  str(randint(100000000, 999999999))


def random_en_fname():
    """
    Make random english first name.
    """

    names = load_file('en_fname.txt')
    return choice(names)


def random_phone():
    """
    Return random phone
    """

    return '+%d%d%d' % (randint(1, 9), randint(100, 999),
                        randint(1000000, 9999999))


def random_zip():
    return str(randint(10000, 99999))
