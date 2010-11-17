from setuptools \
    import \
        setup

MAJOR = 0
MINOR = 0
MICRO = 4
RELEASE = ""
VERSION_INFO = (MAJOR, MINOR, MICRO, RELEASE)
        
NAME = "distext"
if RELEASE == "final":
    VERSION = "%s.%s.%s" % VERSION_INFO[:3]
else:
    VERSION = "%s.%s.%s%s" % VERSION_INFO

MAINTAINER = "Silveregg Technologies Ltd."
MAINTAINER_EMAIL = "dev@silveregg.co.jp"
AUTHOR = MAINTAINER
AUTHOR_EMAIL = MAINTAINER_EMAIL
DESCRIPTION = "Silveregg distutils extensions"
LONG_DESCRIPTION = open("README.rst").read()
LICENSE = "BSD"

def gen_version():
    fid = open("silveregg/distext/__gen_version.py", "w")
    try:
        fid.write("version = '%s'\n" % VERSION)
        fid.write("version_info = %s" % (VERSION_INFO,))
    finally:
        fid.close()

gen_version()

setup(name=NAME, version=VERSION,
      maintainer=MAINTAINER, maintainer_email=MAINTAINER_EMAIL,
      author=AUTHOR, author_email=AUTHOR_EMAIL,
      description=DESCRIPTION, long_description=LONG_DESCRIPTION,
      license=LICENSE,
      namespace_packages=["silveregg"],
      packages=["silveregg", "silveregg.distext", "silveregg.distext.command"],
      install_requires=["Jinja2"],
      # We don't like eggs
      zip_safe=False,
)
