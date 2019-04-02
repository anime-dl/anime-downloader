class AnimeDLError(Exception):
    pass


class URLError(AnimeDLError):
    pass


class NotFoundError(AnimeDLError):
    pass


class RegexChangedError(AnimeDLError):
    pass
