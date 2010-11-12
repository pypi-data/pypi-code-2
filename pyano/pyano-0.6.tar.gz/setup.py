from setuptools import setup, find_packages

setup(name="pyano",
      version = "0.6",
      packages = find_packages(),
      license = "GPLv3",
      author = "Sean Whitbeck",
      author_email = "sean@neush.net",
      description = "Mixmaster web interface for mod_python",
      keywords = 'mixmaster remailer web interface',
      url = "http://pyanon.sourceforge.net",
      zip_safe = True,
      include_package_data = True,
      package_data = {
        # include all html files
        'pyano' : ['html/*']
        }
)
