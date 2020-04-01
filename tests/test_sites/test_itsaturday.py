import pytest

from anime_downloader.sites.itsaturday import Itsaturday
from test_sites.site import configure_httpretty


@pytest.fixture
def anime():
    return Itsaturday('http://www.itsaturday.com/Star-Wars-The-Clone-Wars-2008---2015-Full-Episodes')

configure_httpretty('itsaturday')

def test_search():
    ret = Itsaturday.search('star wars')
    assert len(ret) == 16
    assert ret[0].title == 'Star Wars: The Clone Wars (2008 - 2015)'


def test_title(anime):
    assert anime.title == 'Star Wars: The Clone Wars '


def test_length(anime):
    assert len(anime) == 115


def test_streamurl(anime):
    assert anime[0].source().stream_url == 'http://www.itsaturday.com/watch.php?url=https://2.bp.blogspot.com/STnnqTh7VY1AKmgvX3DlY_ofRpg26WwLW8a85YP4AihSCrianZGNVtzwIi0cPXiw26jd1yoDfU3XMrWQ7Fq4A99KzeJpaBE8SMP16an1E4NsgvpF_mZlpGyfhOuqTCU3Ux0DRnw8=m18&extra=.mp4'
