from setuptools import setup
import nosenumpyseterr

setup(
    name='nose-numpyseterr',
    version='0.1',
    author='Takafumi Arakaki',
    author_email='aka.tkf@gmail.com',
    description=('Nose plugin to set how floating-point errors are '
                 'handled by numpy'),
    long_description=nosenumpyseterr.__doc__,
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Science/Research",
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        'Topic :: Software Development :: Testing',
        "Topic :: Scientific/Engineering",
    ],
    py_modules=['nosenumpyseterr'],
    entry_points={
        'nose.plugins.0.10': [
            'config = nosenumpyseterr:NumpySeterr',
            ],
        },
    )
