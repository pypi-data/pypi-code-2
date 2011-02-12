from setuptools import setup, find_packages

import rbacbwc
version =  rbacbwc.VERSION

setup(
    name = "RBACBWC",
    version = version,
    description = "A BlazeWeb component implimenting role based access control with SQLAlchemy",
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='https://bitbucket.org/rsyring/rbacbwc/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        'SQLAlchemyBWC>=0.1.0',
    ],
)
