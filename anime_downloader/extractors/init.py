from importlib import import_module

ALL_EXTRACTORS = [
    {
        'sitename': 'rapidvideo',
        'modulename': 'rapidvideo',
        'regex': 'rapidvideo',
        'class': 'RapidVideo'
    },
    {
        'sitename': 'no_extractor',
        'modulename': 'fake_extractor',
        'regex': 'no_extractor',
        'class': 'AnimeVideo',
    },
    {
        'sitename': 'animeonline360',
        'modulename': 'animeonline360',
        'regex': 'animeonline360',
        'class': 'AnimeOnline360',
    },
    {
        'sitename': 'stream.moe',
        'modulename': 'moe',
        'regex': 'stream.moe',
        'class': 'StreamMoe',
    },
    {
        'sitename': 'streamango',
        'modulename': 'streamango',
        'regex': 'streamango',
        'class': 'Streamango',
    },
    {
        'sitename': 'mp4upload',
        'modulename': 'mp4upload',
        'regex': 'mp4upload',
        'class': 'MP4Upload'
    },
    {
        'sitename': 'kwik',
        'modulename': 'kwik',
        'regex': 'kwik',
        'class': 'Kwik'
    },
    {
        'sitename': 'trollvid',
        'modulename': 'trollvid',
        'regex': 'trollvid',
        'class': 'Trollvid'
    },
    {
        'sitename': 'mp4sh',
        'modulename': 'mp4sh',
        'regex': 'mp4sh',
        'class': 'MP4Sh'
    },
    {
        'sitename': 'yourupload',
        'modulename': 'yourupload',
        'regex': 'yourupload',
        'class': 'Yourupload'
    },
    {
        'sitename': 'vidstream',
        'modulename': 'vidstream',
        'regex': 'vidstream',
        'class': 'VidStream'
    },
    {
        'sitename': 'haloani',
        'modulename': 'haloani',
        'regex': 'haloani',
        'class': 'Haloani'
    },
    {
        'sitename': 'gcloud',
        'modulename': 'gcloud',
        'regex': 'gcloud',
        'class': 'Gcloud'
    },
    {
        'sitename': 'xstreamcdn',
        'modulename': 'xstreamcdn',
        'regex': 'xstreamcdn',
        'class': 'XStreamCDN'
    },
    {
        'sitename': 'cloud9',
        'modulename': 'cloud9',
        'regex': 'cloud9',
        'class': 'Cloud9'
    },
    {
        'sitename': 'hydrax',
        'modulename': 'hydrax',
        'regex': 'hydrax',
        'class': 'Hydrax'
    },
    {
        'sitename': 'streamx',
        'modulename': 'streamx',
        'regex': 'streamx',
        'class': 'StreamX'
    },
    {
        'sitename': '3rdparty',
        'modulename': '3rdparty',
        'regex': '3rdparty',
        'class': 'Thirdparty'
    },
    {
        'sitename': 'yify',
        'modulename': 'yify',
        'regex': 'yify',
        'class': 'Yify'
    },
    {
        'sitename': 'mixdrop',
        'modulename': 'mixdrop',
        'regex': 'mixdrop',
        'class': 'Mixdrop'
    },
    {
        'sitename': 'sibnet',
        'modulename': 'sibnet',
        'regex': 'sibnet',
        'class': 'SibNet'
    },
    {
        'sitename': 'uqload',
        'modulename': 'uqload',
        'regex': 'uqload',
        'class': 'Uqload'
    }
]


def get_extractor(name):
    for extractor in ALL_EXTRACTORS:
        if extractor['regex'] in name.lower():
            module = import_module(
                'anime_downloader.extractors.{}'.format(
                    extractor['modulename'])
            )
            return getattr(module, extractor['class'])
