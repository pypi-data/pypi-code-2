"""
Standard sake exceptions.
"""


class CoreError(RuntimeError):
    """ The base sake exception. """


class LoginError(CoreError):
    """ Raised when a failure happens in the login process. """

class NetworkError(CoreError):
    """ The base network-related exception. """
class RpcError(NetworkError):
    """ Raised when a failure in networking RPC occurs. """
class RpcTimeoutError(NetworkError):
    """ Raised when a networking RPC operation times out. """
class RpcRemoteError(NetworkError):
    """ Raised when a networking RPC operation fails on the remote endpoint. """

class ServiceNotFoundError(CoreError):
    """ Raised when a access to a non-existent service is attempted. """
class TimeoutError(CoreError):
    """ Raised when a general operation times out. """
class AccessError(CoreError):
    """ Raised when a caller does not have access to perform the call they are making. """


# TODO: Reconsider making this built-in objects.
import __builtin__
__builtin__.RpcError = RpcError
__builtin__.TimeoutError = TimeoutError
