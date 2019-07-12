import httpretty

from ..site import MockSite


class MockNineanime(MockSite):
    def url(self):
        return 'https://'
