from setuptools import setup, find_packages

classifiers = [
    "Framework :: Django",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Internet",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Utilities",
    
]

demo = __import__('demo')
if demo.__stage__ == 'final':
    version = demo.__version__
    classifiers.append("Development Status :: 5 - Production/Stable")
else:
    version = '%s-%s-%s' % (demo.__version__, demo.__stage__, demo.__stage_version__)
    if demo.__stage__ == 'alpha':
        classifiers.append("Development Status :: 3 - Alpha")
    else:
        classifiers.append("Development Status :: 4 - Beta")

setup(
    name='django-demo',
    version=version,
    description='Helper app to build a demo page for your django app',
    author='Jonas Obrist',
    url='http://github.com/ojii/django-demo',
    packages=find_packages(),
    zip_safe=False,
    classifiers=classifiers,
)