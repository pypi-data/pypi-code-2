from distutils.core import setup

setup(
    name='syscon-nc',
    version='0.4',
    author='syscon',
    author_email='py.syscon@googlemail.com',
    packages=['syscon-nc'],
    scripts=[],
    url='',
    license='GNU General Public License v2.0',
    description='System remote control via local network',
    long_description="""=========
syscon-nc
=========

syscon-nc is just the same as <`syscon <http://pypi.python.org/pypi/syscon>`_ in the same version, only without the cryptographic functions.

You should only use syscon-nc, if you are not allowed to use strong cryptography (AES) or if you want to analyse the data sent by syscon. Otherwise, it is much safer to use normal syscon

.. WARNING::
   THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE."""
)
