import pytest

from anime_downloader.sites.itsaturday import Itsaturday
from test_sites.site import configure_httpretty

configure_httpretty('itsaturday')

@pytest.fixture
def anime():
    return Itsaturday('http://www.itsaturday.com/Star-Wars-The-Clone-Wars-2008---2015-Full-Episodes')


def test_search():
    ret = Itsaturday.search('star wars')
