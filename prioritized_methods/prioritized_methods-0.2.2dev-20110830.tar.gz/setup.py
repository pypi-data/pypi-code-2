from setuptools import setup

version = '0.2.2'

def get_description():
    lines = []
    for line in open('prioritized_methods.py').readlines()[1:]:
        if line.startswith('"""'): break
        lines.append(line)
    return ''.join(lines)


setup(name='prioritized_methods',
    version=version,
    description="An extension to PEAK-Rules to prioritize methods "\
                "in order to to avoid AmbiguousMethods situations",
    long_description=get_description(),
    download_url='http://toscawidgets.org/download',
    classifiers=[],
    keywords='PEAK rules generic functions dispatch',
    author='Alberto Valverde Gonzalez',
    author_email='alberto@toscat.net',
    license='MIT',
    py_modules=["prioritized_methods"],
    test_suite = "nose.collector",
    zip_safe=True,
    install_requires=[
        "PEAK-Rules>=0.5a1.dev-r2562,==dev",
        ]
    )
