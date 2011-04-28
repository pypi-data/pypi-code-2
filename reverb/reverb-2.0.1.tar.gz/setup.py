
from distutils.core import setup
import sys

py_version_t = sys.version_info[:2]
py_version_s = ".".join([str(x) for x in py_version_t])


if __name__ == '__main__':
    setup(
        name = 'reverb',
        version = '2.0.1',
        description = 're module wrapper for writing regular expressions in functional style',
        author = 'Kay Schluehr',
        author_email = 'kay@fiber-space.de',
        url = 'http://www.fiber-space.de/',
        download_url = 'http://pypi.python.org/pypi/reverb/2.0',
        license = "BSD",
        packages = ['.'],
    )

