from setuptools import setup, find_packages
import sys

scripts=['htmlist']
if sys.platform.startswith('win'):
    scripts.append("htmlist.bat")

setup(
    name = "HtmlList",
    version = "2.2.2",
    packages = find_packages(),
    package_data = {
        'htmllist': ['./the_problem.txt'],
        'htmllist.test': ['./*.html', './*.rslt'],
    },
    data_files=[('.', ['license.txt', 'README.txt'])],
    scripts=scripts,

    # metadata for uploading to PyPI
    author = "Erez Bibi",
    author_email = "erezbibi@users.sourceforge.net",
    description = "Extract information from HTML pages that have some kind of a repetitive pattern",
    keywords = "HTML list information extraction repetitive pattern",
    zip_safe = True,
    url = "http://pyhtmllist.sourceforge.net/",
    # download_url
    license = "GPL",
    long_description = """This package finds repetitive format patterns in an
HTML page that contains one or more lists and extracts the sub-html text that
creates the patterns. The idea is that in a typical HTML data page containing a
list of items, there will be a repetitive pattern for the human eye (the page
format). This pattern can be recognized automatically, and the data in the list
can be extracted.""",
    classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Text Processing :: Markup :: HTML',
    'Topic :: Utilities'
    ]
)
