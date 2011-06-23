from attest import Assert, AssertImportHook, Tests
# In Django <= 1.3 django.utils.module_loading.module_has_submodule is busted
AssertImportHook.disable()
from django.conf import settings
import mimetypes


everything = Tests()


@everything.test
def without_setting():
    Assert((None, None)) == mimetypes.guess_type("test.abc")


@everything.test
def with_setting():
    settings.configure(
        MIMETYPES = {
            ".abc": "Alpha Beta Cappa",
        },
        INSTALLED_APPS = [
            'extramimetypes',
        ],
    )
    import extramimetypes
    Assert(("Alpha Beta Cappa", None)) == mimetypes.guess_type("test.abc")
