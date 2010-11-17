try:
    import __gen_version
except ImportError:
    __version__ = "nobuilt"
    __version_info__ = ("nobuilt",)
else:
    __version__ = __gen_version.version
    __version_info__ = __gen_version.version_info

# Those imports are mandatory to set up monkey patching
import silveregg.distext.dist
import silveregg.distext.core
