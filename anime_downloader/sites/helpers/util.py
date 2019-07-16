import logging


def not_working(message):
    orig_message = message
    message += " You can use `anime -ll DEBUG` to use it."
    def wrapper(cls):
        class NotWorking:
            """Site is not working"""
            def __init__(self, *args, **kwargs):
                raise RuntimeError(message)
            def search(cls, *args, **kwargs):
                raise RuntimeError(message)

        NotWorking.__doc__ = orig_message
        logger = logging.getLogger("anime_downloader")
        if logger.level == logging.DEBUG:
            return cls
        return NotWorking
    return wrapper
