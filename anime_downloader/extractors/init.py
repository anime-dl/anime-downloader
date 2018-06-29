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
]


def get_extractor(name):
    for extractor in ALL_EXTRACTORS:
        if extractor['regex'] in name:
            module = import_module('anime_downloader.extractors.{}'.format(extractor['modulename']))
            return getattr(module, extractor['class'])
