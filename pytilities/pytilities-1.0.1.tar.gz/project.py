'''
Project deployment and testing tools

Version
  2.1.2
'''

import os
import sys

# TODO handle first release

assert sys.version_info.major >= 3, \
    'Must be ran with python3 or later'

# More imports (have to be placed after logging activation code, to detect even
# the earliest fails)
from pytilities.testing import get_recursive_package_test
import pytilities.testing

# Run unit tests
def run_tests(test_root):
    return pytilities.testing.run(
        get_recursive_package_test(
            os.path.dirname(
                os.path.join(os.getcwd(),
                             __file__)),
            test_root))

def get_packages(path):
    '''get list of all packages in `path`'''
    return [root.replace(os.path.sep, '.')
            for root, dirs, files in os.walk(path) 
            if '__init__.py' in files and root != '.svn']

def _compare_versions(a, b):
    '''
    a < b, returns -1
    a == b, returns 0
    a > b, returns 1
    '''
    a = a.split('.')
    assert len(a) == 3 # not a version of format num.num.num

    b = b.split('.')
    assert len(a) == 3 # not a version of format num.num.num

    a = tuple(map(int, a))
    b = tuple(map(int, b))
    return (a>b) - (a<b)

class ReleaseError(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class Project(object):
    def __init__(self, name, version, short_description, project_root, package_root, last,
                 doc_config, keywords, classifiers, long_description):
        '''
        name: of project
        version: of project
        project_root: where last.py ... will reside
        package_root: top of the project code
        last: a loaded module of last.py
        doc_config: loaded module of your sphinx doc config
        keywords: for pypi
        classifiers: for pypi
        long_description: displayed on pypi
        '''
        self.name = name
        self.version = version
        self.short_description = short_description
        self.project_root = project_root
        self.package_root = package_root
        self.last = last
        self.doc_config = doc_config
        self.keywords = keywords
        self.classifiers = classifiers
        self.long_description = long_description

        self.url = 'http://%s.sourceforge.net' % name
        self.all_packages = self.get_packages()

    def check_version(self):
        '''checks if last version < new'''
        if _compare_versions(self.last.dist, self.version) >= 0:
            raise ReleaseError('New version is smaller or equal to new version!!!')

        if not (self.doc_config.version == self.doc_config.release == self.version):
            raise ReleaseError("Version in api doc doesn't match version of release!!!")

        print('Versioning looks good')

    def check_long_description(self):
        '''checks if long description is correct'''
        
        with open('long_description.rst', 'w') as f:
            f.write(self.long_description)

        # does it reST compile?
        if os.system('''rst2html --halt=warning long_description.rst > /dev/null''') != 0:
            raise ReleaseError('Long description contains reST errors')

        # does it contain visible errors?
        os.system('''rst2html long_description.rst > long_description.html''')
        os.system('''firefox long_description.html''')
        print('long_description.html was opened in your firefox')
        reply = input('Does it look alright? (y/N): ')
        os.unlink(self.project_root + '/long_description.rst')  
        os.unlink(self.project_root + '/long_description.html')  
        if reply != 'y':
            raise ReleaseError('Long description fails to fully please the developer')

        print('Long description looks good')

    def check_change_log(self):
        '''check if we added our changes to the changelog for the new version'''
        # note: last entry has to be on the first line
        with open(self.project_root + '/CHANGELOG.rst') as f:
            last_entry = f.readline().strip()

        if last_entry != self.version:
            raise ReleaseError('Failed to find entry of new version in the changelog!!!')

        print('Changelog entry is in place')

    def test(self):
        '''run tests and return if all succeeded'''
        if not run_tests('%s.test' % self.name):
            raise ReleaseError('Tests failed!!!')

    def check_licenses(self):
        '''See if all files have a license on them'''
        self.clean()  # requires cleaned out project

        all_ok = True
        for path, dirs, files in os.walk(self.package_root):
            if not ('__init__.py' in files and path != '.svn'):
                continue

            for file_ in files:
                file_path = os.path.sep.join((path, file_))
                with open(file_path) as f:
                    if f.readline() != \
                        '# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>\n':
                        print('Missing license: ' + file_path)
                        all_ok = False

        if not all_ok:
            raise ReleaseError('Some files have no license')

        print('Licensing looks good')

    def generate_doc(self):
        '''generate doc'''
        os.system('''rm -rf %s/doc/*''' % self.project_root)

        if os.system('''sphinx-build -aE -b dirhtml %s/doc_source doc''' %
                     self.project_root):
            raise ReleaseError('Failed to generate docs!!!')

        print('Doc generated (possibly with errors)')

    def upload_doc(self):
        '''upload new docs to sourceforge
        
        reuploads them if they were uploaded already'''
        username = input(
            "Enter web.sourceforge.net username (without ',%s') [%s]: "
            % (self.name, os.getenv('USER')))

        if not username:
            username = os.getenv('USER')

        username += ',%s' % self.name

        if os.system("""rsync -avz --chmod=o+r --delete --delete-during doc/* %s@web.sourceforge.net:htdocs/doc/%s/""" 
                     % (username, self.version)) != 0:
            raise ReleaseError('Failed to upload doc!!!')
        else:
            print('Uploaded new api doc')

    def _generate_setup(self):
        '''generate setup.py'''

        setup_contents = '''from distutils.core import setup

setup(
    name = %s,
    packages = %s,
    provides = %s,
    version = %s,
    description = %s,
    author = 'Tim Diels',
    author_email = 'limyreth@users.sourceforge.net',
    url = %s,
    keywords = %s,
    classifiers = %s,
    long_description = %s
)
    ''' % tuple(map(repr, (self.name, self.all_packages, self.all_packages,
                           self.version, self.short_description, self.url, self.keywords,
                           self.classifiers, self.long_description)))
        
        with open(self.project_root + '/setup.py', 'w') as f:
            f.write(setup_contents)

    def clean(self):
        if os.system("find * -regex '.*\.pyc' -exec rm -v \{\} +") != 0:
            raise ReleaseError('Clean script failed to run!')

        print('Cleaned project')

    def _release(self):
        '''send source dist to PyPI, ... in order to release a new version'''
        if os.system('python setup.py sdist upload') != 0:
            raise ReleaseError('Failed to run python release')

    def release(self):
        '''
        check the project for errors and upload new release if it looks fine
        '''
        # lots of checks to make sure code is good
        self.check_version()
        self.check_change_log()
        self.check_long_description()
        self.test()
        self.clean()
        self.check_licenses()

        print()

        # gen and upload docs to SF
        if _compare_versions(self.last.doc, self.version) != 0:
            self.generate_doc()
            print()
            self.upload_doc()
            self.last.doc = self.version
            self.write_back_values_of_last()
        else:
            print("Docs were already uploaded and will not be reuploaded, if"
                  + " doc has changed you'll have to reupload using upload_doc")
        
        # PyPI
        self._generate_setup()
        self._release()

        self.last.dist = self.version

        # cleanup
        os.unlink(self.project_root + '/setup.py')  
        os.unlink(self.project_root + '/MANIFEST')  

        # write back values of last.*
        self.write_back_values_of_last()

        # say yay
        print('''
        New version released to the PyPI!
        ''')

    def write_back_values_of_last(self):
        with open(self.project_root + '/last.py', 'w') as f:
            f.write("""\
dist=%s  # version of last succesfully uploaded dist release
doc=%s  # version of last succesfully uploaded docs """
                  % tuple(map(repr, (self.last.dist, self.last.doc))))

    def get_packages(self):
        return get_packages(self.package_root)

    def print_packages(self):
        print(self.get_packages())

    def start_cli(self):
        '''reads commands from stdin indefinetely'''
        command = ''

        try:
            while True:
                if command == '':
                    print('Commands:')
                    for member in dir(self):
                        if member[0] != '_' and hasattr(getattr(self, member),
                                                        '__call__'):
                            print(member)
                else:
                    try:
                        getattr(self, command).__call__()
                    except ReleaseError as e:
                        print(e)
                        print('''

                        SOMETHING FAILED!!!

                        ''')
                print()
                command = input('Awesome command: ')
        except EOFError:
            pass


