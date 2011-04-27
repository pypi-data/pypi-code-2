from distutils.core import setup

setup(
    packages = ['binstream'],

    name="binstream",
    version="1.0.3",
    author="Simon Wittber",
    author_email = 'simonwittber@gmail.com',
    maintainer="Simon Wittber",
    maintainer_email = 'simonwittber@gmail.com',
    url="http://pypi.python.org/pypi/binstream/",
    description="""Binstream is used for serializing and deserializing basic types. It is compatible with the .NET System.IO.BinaryReader and BinaryWriter classes, and is useful as a bridge when exchanging data with the .NET framework.""",
    long_description="""
|    import binstream
|
|    stream = binstream.BinaryWriter()
|    stream += 1234
|    stream += 0.0 
|    stream += "Hello, Binstream!"
|    data = stream.serial()
|    stream = binstream.BinaryReader(data)
|    print(stream.read(int))
|    print(stream.read(float))
|    print(stream.read(str))
    """,
    license="MIT"





)

    
