import logging


def not_working(message):
    message += " You can use `anime -ll DEBUG` to use it."
    def wrapper(cls):
        class NotWorking:
            def __init__(self, *args, **kwargs):
                raise RuntimeError(message)
            def search(cls, *args, **kwargs):
                raise RuntimeError(message)

        logger = logging.getLogger("anime_downloader")
        if logger.level == logging.DEBUG:
            return cls
        return NotWorking
    return wrapper
