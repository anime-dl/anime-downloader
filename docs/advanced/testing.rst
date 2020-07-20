Testing
*******

We use pytest for testing.

You can run specific tests by specifying the file; ::

    $ pytest tests/test_twistmoe.py


Mocks
*****

The tool provides a framework for easy mocking of providers.
To use it, run the tool using the new provider. In this doc, we will use the example of twist.moe.::

    $ anime -ll DEBUG dl 'shingeki no kyojin' --provider twist.moe --url -e 1
    ....
    2019-09-28 18:16:19 this anime_downloader.sites.helpers.request[521432] DEBUG HTML file temp_dir: /tmp/animedlszzxne7y
    ....


In the above output, we can see the temp directory created by the tool.
Copy this temp directory to tests/test_sites and name it test_<your provider name>.

After this, you are ready to write the tests. The twist.moe test file is given below for reference.

Remember to use the function :py:function:`configure_httpretty(<your provider name>)` to configure the mock before making any requests.

.. code:: python

    import pytest

    from anime_downloader.sites.twistmoe import TwistMoe
    from test_sites.site import configure_httpretty


    @pytest.fixture
    def anime():
        return TwistMoe('https://twist.moe/a/shingeki-no-kyojin/first')

    configure_httpretty('twistmoe')

    def test_search():
        ret = TwistMoe.search('shingeki no kyojin')
        assert len(ret) == 5
        assert ret[0].title == 'Shingeki no Kyojin'


    def test_title(anime):
        assert anime.title == 'shingeki-no-kyojin'


    def test_length(anime):
        assert len(anime) == 25


    def test_streamurl(anime):
        assert anime[0].source().stream_url == 'https://eu1.twist.moe/anime/attackontitan/[Coalgirls]_Shingeki_no_Kyojin_01_(1920x1080_Blu-ray_FLAC)_[AEF12794].mp4'
