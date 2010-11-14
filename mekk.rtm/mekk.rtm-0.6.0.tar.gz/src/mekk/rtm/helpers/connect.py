from __access__ import API, SEC

from mekk.rtm.connect import create_and_authorize_connector
from mekk.rtm.rtm_client import RtmClient
from base64 import decodestring as __

def create_rtm_client(app_name = "mekk-rtm", permission = "delete"):
    """
    Configures and creates connected and authorized RtmClient.
    May use browser authorization to grab necessary permissions.
    Uses embedded API key, so appropriate only for scripts embedded
    in library!
    """
    connector = create_and_authorize_connector(
        app_name, __(API), __(SEC), permission)
    client = RtmClient(connector)
    return client
