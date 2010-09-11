# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages

# "distribute (0.6.10)" does not handle namespace subpackages of
#   a non empty namespace package correctly (it thinks
#   the super package needs not be installed if the subpackage already is).
#   Therefore, "dm.zope.rpc" is no longer implemented as namespace
#   package and protocol plugins are put in "dm.zope.rpc_protocol"
#   rather than "dm.zope.rpc" itself
##try:
##    __import__('pkg_resources').declare_namespace(__name__)
##except ImportError:
##    from pkgutil import extend_path
##    __path__ = extend_path(__path__, __name__)
