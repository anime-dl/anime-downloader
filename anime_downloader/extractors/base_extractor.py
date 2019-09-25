from anime_downloader.const import desktop_headers
from anime_downloader.sites.exceptions import NotFoundError


class BaseExtractor:
    def __init__(self, url, quality=None, headers=None):
        if not url.startswith('http'):
            url = 'https://' + url
        self.url = url

        # TODO: Maybe quality should be only delt with inside epiosde(?)
        self.quality = quality

        if headers is not None:
            self.headers = headers
        else:
            self.headers = desktop_headers

        self._stream_url = None
        self._referer = ''
        self._meta = None

    @property
    def stream_url(self):
        """
        URL of the video stream.
        """
        if not self._stream_url:
            self.get_data()

        return self._stream_url

    @property
    def referer(self):
        if self._referer == '':
            self.get_data()

        return self._referer

    def get_data(self):
        data = self._get_data()

        if not data['stream_url']:
            raise NotFoundError
        self._stream_url = data['stream_url']
        self._referer = data.get('referer', None)
        self.meta = data.get('meta')

    def _get_data(self):
        raise NotImplementedError
