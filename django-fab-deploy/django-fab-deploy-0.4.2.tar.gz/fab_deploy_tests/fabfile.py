from fab_deploy import *

def foo_node():
    env.hosts = ['foo@127.0.0.1:2222']
    env.conf = dict(
        DB_PASSWORD = '1234',
        OS = env._OS,
    )
    update_env()
