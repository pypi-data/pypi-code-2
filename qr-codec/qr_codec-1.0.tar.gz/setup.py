from distutils.core import setup, Extension

encode = Extension('qr_encode',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                    include_dirs = ['./qr_enc/'],
                    sources =[
                        'qr_encode.c',
                        './qr_enc/qrencode.c',
                        './qr_enc/bitstream.c',
                        './qr_enc/qrinput.c',
                        './qr_enc/qrspec.c',
                        './qr_enc/rscode.c'])
                    #libraries = ['qrencode'],
                    #library_dirs = ['/usr/local/lib/'],

decode = Extension('qr_decode',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                    include_dirs = ['./qr_dec/','/usr/include/opencv/'],
                    libraries = ['cv','highgui'],
                    library_dirs = ['/usr/include/opencv/'],
                    sources = [
                        'qr_decode.cpp',
                        './qr_dec/bitstream.cpp',
                        './qr_dec/codedata.cpp',
                        './qr_dec/container.cpp',
                        './qr_dec/ecidecoder.cpp',
                        './qr_dec/formatinfo.cpp',
                        './qr_dec/galois.cpp',
                        './qr_dec/imagereader.cpp',
                        './qr_dec/libdecodeqr.cpp'])

setup (name = 'qr_codec',
       version = '1.0',
       description = 'Encode and decode Quick Response codes.',
       author = 'Stefano Pedemonte',
       author_email = 'stefano@pedemonte.eu',
       url = 'http://www.pedemonte.eu',
       long_description = '''Encode and decode Quick Response codes.''',
       ext_modules = [encode,decode],
       #py_modules = ['QrCodec'])
       packages=['PyQrcodec'])