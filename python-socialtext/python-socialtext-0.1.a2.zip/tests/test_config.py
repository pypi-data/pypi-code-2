from nose.tools import assert_equal, raises
from fakeserver import FakeServer
from utils import assert_isinstance
from socialtext import ApplianceConfiguration

st = FakeServer()

def test_get_config():
    config = st.config.get()
    st.assert_called('GET', '/data/config')
    assert_isinstance(config, ApplianceConfiguration)
    
    config.get()
    st.assert_called('GET', '/data/config')
    assert_isinstance(config, ApplianceConfiguration)