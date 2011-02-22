import logging

def run_server():
    from nowsync.server import NowSyncServer
    logging.basicConfig(level=logging.INFO)
    server = NowSyncServer()
    server.run()
    
def run_client():
    from nowsync import config
    from nowsync.client.client import NowSyncClient
    logging.basicConfig(level=logging.INFO)
    cfg = config.load_config()
    client = NowSyncClient(cfg)
    client.resync()
    client.run()