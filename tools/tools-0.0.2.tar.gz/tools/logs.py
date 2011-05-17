import logging

def setup_logging(prefix=None, history=True, log_dir='var/log'):
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(threadName)s %(message)s'))
    logger.addHandler(handler)

    if prefix:
        handler = logging.FileHandler('%s/%s_session.log' % (log_dir, prefix), 'w')
        handler.setFormatter(logging.Formatter('%(asctime)s %(threadName)s %(message)s',
                                               '%m-%d %H:%M:%S'))
        logger.addHandler(handler)

    if prefix and history:
        handler = logging.FileHandler('%s/%s_history.log' % (log_dir, prefix), 'a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(threadName)s %(message)s',
                                               '%m-%d %H:%M:%S'))
        logger.addHandler(handler)
