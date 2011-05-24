from distutils.core import setup

setup(
    name = "pywalk",
    version = "0.0.1",
    description = "Recursively walk through and manipulate dict/list/tuple "
                + "trees",
    author = "Joshua Holbrook",
    author_email = "josh.holbrook@gmail.com",
    url = "https://github.com/jesusabdullah/pywalk",
    keywords = ["traverse", "walk", "tree"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7", #only one tested
        "Topic :: Other/Nonlisted Topic"
    ],
    long_description = """\
Pywalk
======

Pywalk is a python module written for traversing trees built of
dictionaries, lists and tuples in a breadth-first manner.

This module is still under development. If you're used to mature,
polished python libraries you may want to avoid pywalk. Additionally, it
has only been tested against Python 2.7.1+ (what happens to be what's on
my computer) so it may not work as expected in Python 3.x. However, if
you're a more adventurous developer with an urge (or need) for
manipulating nested data structures, this just might be the library for
you!

Pywalk is a spiritual port of
`js-traverse <https://github.com/substack/js-traverse>`_, in that it's
meant to solve similar problems.

How It Works:
-------------

``walk(tree)`` returns a decorator that applies a callback to each node
in the tree, in a breadth-first manner. For example:

::

    tree = {'a': 1, 'b': [9, 9, 6, 7, 6]}

    print("Tree before: "+repr(tree))

    @walk(tree)
    def that_aint_my_zip_code(node):
        if node.value == [9, 9, 6, 7, 6] :
            node.set([9, 9, 7, 7, 5])

    print("Tree after: "+repr(tree))

For more, visit https://github.com/jesusabdullah/pywalk .
    """
)
