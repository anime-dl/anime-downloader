import logging

def setup_logger(log_level):
    if log_level == 'DEBUG':
        format = '%(levelname)s %(name)s: %(message)s'
    else:
        format = '%(levelname)s:%(message)s'

    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format=format
    )
