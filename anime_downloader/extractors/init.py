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
]


def get_extractor(name):
    for extractor in ALL_EXTRACTORS:
        if extractor['regex'] in name.lower():
            module = import_module(
                'anime_downloader.extractors.{}'.format(
                    extractor['modulename'])
            )
            return getattr(module, extractor['class'])
